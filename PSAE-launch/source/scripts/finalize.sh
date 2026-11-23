#!/usr/bin/env bash
# Two-pass loudnorm (-16 LUFS, -1.5 dBTP) then mux with the muted Remotion render.
# Usage (from source/): bash scripts/finalize.sh <output.mp4>
set -euo pipefail
OUT_DIR="$(cd "$(dirname "$0")/../.." && pwd)/out"
FINAL="${1:?output mp4 path}"
M=$(ffmpeg -hide_banner -nostats -i "$OUT_DIR/mix_raw.wav" -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$M" | python3 -I -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -hide_banner -loglevel error -i "$OUT_DIR/mix_raw.wav" -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.82:level=false,aresample=48000" -ar 48000 "$OUT_DIR/mix_master.wav"
ffmpeg -y -hide_banner -loglevel error -i "$OUT_DIR/video_muted.mp4" -i "$OUT_DIR/mix_master.wav" -map 0:v:0 -map 1:a:0 \
  -vf "scale=in_range=tv:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709,format=yuv420p" -c:v libx264 -profile:v high -preset slow -crf 16 -r 30 -g 60 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest -movflags +faststart "$FINAL"
echo "wrote $FINAL"
