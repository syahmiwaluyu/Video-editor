#!/usr/bin/env bash
# VGC-AE01 — combine the Gemini cut (story) with the event recap video.
# Usage (from source/): bash scripts/build_combined.sh <gemini_cut.mp4> <event_recap.mp4> <output.mp4>
# Output: 1280x720, 30 fps CFR (recap is variable-frame-rate ~30; Gemini cut is 24 -> frames repeated to 30).
set -euo pipefail
G="${1:?gemini cut}"; R="${2:?event recap}"; FINAL="${3:?output}"
OUT="$(cd "$(dirname "$0")/../.." && pwd)/out/combined"
mkdir -p "$OUT"
XF=0.75   # dissolve between CODE LAVENDER end card and the recap's opening poster
ff(){ ffmpeg -y -hide_banner -loglevel error "$@"; }
dur(){ ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
VNORM="scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p"
VENC=(-c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -r 30)

# 1) normalise video (both already BT.709-tagged) and audio (48 kHz, gain-matched to -20 LUFS)
ff -i "$G" -vf "$VNORM,setpts=PTS-STARTPTS" -an "${VENC[@]}" "$OUT/segG.mp4"
ff -i "$R" -vf "$VNORM,setpts=PTS-STARTPTS" -an "${VENC[@]}" "$OUT/segR.mp4"
gain(){ local I; I=$(ffmpeg -hide_banner -nostats -i "$1" -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
  python3 -I -c "print(round(-20-($I),2))"; }
for s in G R; do
  src=$G; [ $s = R ] && src=$R
  ff -i "$src" -vn -t "$(dur "$OUT/seg$s.mp4")" -ar 48000 -ac 2 "$OUT/aud${s}_raw.wav"
  g=$(gain "$OUT/aud${s}_raw.wav"); echo "aud$s gain ${g} dB"
  ff -i "$OUT/aud${s}_raw.wav" -af "volume=${g}dB" "$OUT/aud$s.wav"
done

# 2) join
DG=$(dur "$OUT/segG.mp4"); O=$(python3 -I -c "print(round($DG-$XF,4))")
echo "Gemini cut ${DG}s, recap $(dur "$OUT/segR.mp4")s, dissolve at ${O}s"
ff -i "$OUT/segG.mp4" -i "$OUT/segR.mp4" -i "$OUT/audG.wav" -i "$OUT/audR.wav" -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=$XF:offset=$O[v];[2:a][3:a]acrossfade=d=$XF[a]" \
  -map "[v]" -map "[a]" "${VENC[@]}" -c:a pcm_s16le "$OUT/joined.mov"

# 3) master (-14 LUFS / -1.5 dBTP two-pass, 0.5 s tail fade) + final encode
TOT=$(dur "$OUT/joined.mov"); FS=$(python3 -I -c "print(round($TOT-0.5,3))")
ff -i "$OUT/joined.mov" -vn -af "afade=t=out:st=$FS:d=0.5" "$OUT/mix_raw.wav"
M=$(ffmpeg -hide_banner -nostats -i "$OUT/mix_raw.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$M" | python3 -I -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ff -i "$OUT/mix_raw.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.82:level=false,aresample=48000" -ar 48000 "$OUT/mix_master.wav"
ff -i "$OUT/joined.mov" -i "$OUT/mix_master.wav" -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -profile:v high -preset slow -crf 17 -r 30 -g 60 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest -movflags +faststart "$FINAL"
echo "wrote $FINAL (${TOT}s)"
