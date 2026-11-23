#!/usr/bin/env bash
# Add the exact on-screen text + lavender layers to three generated 8 s clips, join them, master the audio.
# Put clips in ../clips as clip1.mp4, clip2.mp4, clip3.mp4 (any size; they are cropped/scaled to 1080x1920).
# Usage (from the project folder): bash scripts/assemble.sh out/CL01_preview_v01.mp4
#   with the procedural score:     MUSIC=out/music.wav bash scripts/assemble.sh out/CL01_preview_v01.mp4
# Timings below are DRAFTS. Adjust them to the real dialogue in your clips (see README).
set -euo pipefail
cd "$(dirname "$0")/.."
FINAL="${1:?output mp4 path}"
O=overlays; T=out/tmp; mkdir -p "$T"
FIT="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p"
ENC=(-c:v libx264 -profile:v high -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -ac 2)

# Clips without an audio track get silence so the join does not fail.
withaudio(){ ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$1" | grep -q .; }
audio_in(){ if withaudio "$1"; then echo "-i $1"; else echo "-f lavfi -t 8 -i anullsrc=r=48000:cl=stereo"; fi; }

# loop an RGBA still for 8 s and fade it in/out (st = start, d = duration)
lay(){ echo "movie=$O/$1,loop=-1:1:0,trim=duration=8,fps=30,format=rgba,fade=in:st=$2:d=$3:alpha=1${4:+,fade=out:st=$4:d=$5:alpha=1}"; }

# Clip 1: lavender glow from 5.6 s, text from 5.0 s (holds to the end)
ffmpeg -y -hide_banner -loglevel error -t 8 -i clips/clip1.mp4 $(audio_in clips/clip1.mp4) -filter_complex \
"[0:v]$FIT[v];$(lay c1_glow.png 5.6 2.0)[g];$(lay c1_text.png 5.0 0.6)[t];[v][g]overlay[a];[a][t]overlay,format=yuv420p[vo];[1:a]aresample=48000,apad,atrim=0:8[ao]" \
 -map "[vo]" -map "[ao]" -t 8 "${ENC[@]}" "$T/c1.mp4"

# Clip 2: subtle lavender glow from 4.0 s, text from 6.0 s
ffmpeg -y -hide_banner -loglevel error -t 8 -i clips/clip2.mp4 $(audio_in clips/clip2.mp4) -filter_complex \
"[0:v]$FIT[v];$(lay c2_glow.png 4.0 2.5)[g];$(lay c2_text.png 6.0 0.4)[t];[v][g]overlay[a];[a][t]overlay,format=yuv420p[vo];[1:a]aresample=48000,apad,atrim=0:8[ao]" \
 -map "[vo]" -map "[ao]" -t 8 "${ENC[@]}" "$T/c2.mp4"

# Clip 3: lavender fills the screen 4.3-5.0 s, then the title card builds up to 8.0 s
ffmpeg -y -hide_banner -loglevel error -t 8 -i clips/clip3.mp4 $(audio_in clips/clip3.mp4) -filter_complex \
"[0:v]$FIT[v];$(lay c3_bg.png 4.3 0.7)[b];$(lay c3_title.png 5.0 0.4)[t1];$(lay c3_sub.png 5.4 0.4)[t2];$(lay c3_tag.png 5.9 0.4)[t3];$(lay c3_cta.png 6.4 0.4)[t4];\
[v][b]overlay[a1];[a1][t1]overlay[a2];[a2][t2]overlay[a3];[a3][t3]overlay[a4];[a4][t4]overlay,format=yuv420p[vo];[1:a]aresample=48000,apad,atrim=0:8[ao]" \
 -map "[vo]" -map "[ao]" -t 8 "${ENC[@]}" "$T/c3.mp4"

# Join (hard cuts), then two-pass loudnorm to -14 LUFS / -1.5 dBTP
ffmpeg -y -hide_banner -loglevel error -i "$T/c1.mp4" -i "$T/c2.mp4" -i "$T/c3.mp4" -filter_complex \
"[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" -map "[v]" -map "[a]" "${ENC[@]}" "$T/joined.mp4"
# Optional music bed: MUSIC=out/music.wav bash scripts/assemble.sh ...  (mixed under the clips' own audio)
if [ -n "${MUSIC:-}" ]; then
  ffmpeg -y -hide_banner -loglevel error -i "$T/joined.mp4" -i "$MUSIC" -filter_complex \
  "[1:a]aresample=48000,volume=0.9[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -ar 48000 -ac 2 "$T/joined_m.mp4" && mv "$T/joined_m.mp4" "$T/joined.mp4"
fi
M=$(ffmpeg -hide_banner -nostats -i "$T/joined.mp4" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$M" | python3 -I -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -hide_banner -loglevel error -i "$T/joined.mp4" -map 0:v -map 0:a -c:v copy \
 -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
 -c:a aac -b:a 256k -ar 48000 -ac 2 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart "$FINAL" \
 || { echo "audio is silent or unmeasurable; muxing without loudnorm"; ffmpeg -y -hide_banner -loglevel error -i "$T/joined.mp4" -c copy -movflags +faststart "$FINAL"; }
echo "wrote $FINAL"
