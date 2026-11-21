#!/usr/bin/env bash
# Two-pass loudnorm master (-14 LUFS, <= -1.5 dBTP) + mux with silent Remotion render.
# Usage: bash finalize.sh <output.mp4>
set -euo pipefail
cd "$(dirname "$0")/../../out"
J=$(ffmpeg -hide_banner -i mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i mix_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.84:level=false" -ar 48000 mix_master.wav
ls -l --time-style=full-iso video_muted.mp4 mix_master.wav
ffmpeg -v error -y -i video_muted.mp4 -i mix_master.wav -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -profile:v high -preset slow -crf 16 -r 30 -g 60 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest -movflags +faststart "$1"
echo "muxed -> $1"
