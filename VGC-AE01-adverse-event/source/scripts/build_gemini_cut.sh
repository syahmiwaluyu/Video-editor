#!/usr/bin/env bash
# VGC-AE01 — join the three Gemini clips A -> B -> C (16:9, 1280x720, 24 fps).
# Usage (from source/): bash scripts/build_gemini_cut.sh <clipA.mp4> <clipB.mp4> <clipC.mp4> <output.mp4>
#   A = doctor alone + whisper + "Behind every adverse event..." card
#   B = colleague comforts her + "YOU ARE NOT ALONE" card
#   C = team + "CODE LAVENDER" end card
set -euo pipefail
A="${1:?clip A}"; B="${2:?clip B}"; C="${3:?clip C}"; FINAL="${4:?output}"
OUT="$(cd "$(dirname "$0")/../.." && pwd)/out/gemini"
mkdir -p "$OUT"
XF=0.5            # cross-dissolve length (s)
B_IN=1.0          # B opens on the same wide shot A opens on; skip that repeat
C_SLOW_FROM=8.5   # C end card is only ~1.75 s readable; play its last 1.5 s at half speed
# Burned-in subtitle in A: frames 121-178 (5.042-7.458 s), text bbox x324-961 y638-667 (measured)
SUB="delogo=x=306:y=626:w=674:h=54:enable='between(t,5.03,7.47)'"
VENC=(-c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -r 24)
ff(){ ffmpeg -y -hide_banner -loglevel error "$@"; }

# 1) video segments
ff -i "$A" -vf "$SUB,setpts=PTS-STARTPTS" -an "${VENC[@]}" "$OUT/segA.mp4"
ff -ss "$B_IN" -i "$B" -vf "setpts=PTS-STARTPTS" -an "${VENC[@]}" "$OUT/segB.mp4"
ff -i "$C" -filter_complex \
  "[0:v]split[a][b];[a]trim=0:$C_SLOW_FROM,setpts=PTS-STARTPTS[h];[b]trim=$C_SLOW_FROM,setpts=2*(PTS-STARTPTS),framerate=fps=24[t];[h][t]concat=n=2:v=1[v]" \
  -map "[v]" -an "${VENC[@]}" "$OUT/segC.mp4"

# 2) audio segments, each gain-matched to -20 LUFS before joining
gain(){ # $1 in.wav -> prints dB to reach -20 LUFS
  local I; I=$(ffmpeg -hide_banner -nostats -i "$1" -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
  python3 -I -c "print(round(-20-($I),2))"; }
ff -i "$A" -t 10 -vn -ar 48000 -ac 2 "$OUT/audA_raw.wav"
ff -ss "$B_IN" -i "$B" -t 9 -vn -ar 48000 -ac 2 "$OUT/audB_raw.wav"
ff -i "$C" -filter_complex \
  "[0:a]asplit[a][b];[a]atrim=0:$C_SLOW_FROM,asetpts=PTS-STARTPTS[h];[b]atrim=$C_SLOW_FROM:10,asetpts=PTS-STARTPTS,atempo=0.5[t];[h][t]concat=n=2:v=0:a=1[o]" \
  -map "[o]" -ar 48000 -ac 2 "$OUT/audC_raw.wav"
for s in A B C; do
  g=$(gain "$OUT/aud${s}_raw.wav"); echo "aud$s gain ${g} dB"
  ff -i "$OUT/aud${s}_raw.wav" -af "volume=${g}dB" "$OUT/aud${s}.wav"
done

# 3) join with dissolves
DA=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/segA.mp4")
DB=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/segB.mp4")
O1=$(python3 -I -c "print(round($DA-$XF,4))"); O2=$(python3 -I -c "print(round($DA+$DB-2*$XF,4))")
echo "A=${DA}s B=${DB}s offsets $O1 $O2"
ff -i "$OUT/segA.mp4" -i "$OUT/segB.mp4" -i "$OUT/segC.mp4" -i "$OUT/audA.wav" -i "$OUT/audB.wav" -i "$OUT/audC.wav" -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=$XF:offset=$O1[v1];[v1][2:v]xfade=transition=fade:duration=$XF:offset=$O2[v];\
   [3:a][4:a]acrossfade=d=$XF[a1];[a1][5:a]acrossfade=d=$XF[a]" \
  -map "[v]" -map "[a]" "${VENC[@]}" -c:a pcm_s16le "$OUT/joined.mov"

# 4) master audio (two-pass loudnorm -14 LUFS / -1.5 dBTP, 0.4 s tail fade) and final encode (BT.601 -> BT.709)
TOT=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/joined.mov")
FS=$(python3 -I -c "print(round($TOT-0.4,3))")
ff -i "$OUT/joined.mov" -vn -af "afade=t=out:st=$FS:d=0.4" "$OUT/mix_raw.wav"
M=$(ffmpeg -hide_banner -nostats -i "$OUT/mix_raw.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$M" | python3 -I -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ff -i "$OUT/mix_raw.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.82:level=false,aresample=48000" -ar 48000 "$OUT/mix_master.wav"
ff -i "$OUT/joined.mov" -i "$OUT/mix_master.wav" -map 0:v:0 -map 1:a:0 \
  -vf "scale=in_range=tv:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709,format=yuv420p" \
  -c:v libx264 -profile:v high -preset slow -crf 16 -r 24 -g 48 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest -movflags +faststart "$FINAL"
echo "wrote $FINAL (${TOT}s)"
