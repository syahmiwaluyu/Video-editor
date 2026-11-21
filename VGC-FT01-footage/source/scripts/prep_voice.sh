#!/usr/bin/env bash
# Dialogue cleanup on a COPY of the original audio. Original footage is never modified.
# Usage: bash prep_voice.sh /path/to/original.mp4
set -euo pipefail
SRC="$1"; W="$(cd "$(dirname "$0")/../.." && pwd)/work"; mkdir -p "$W"
ffmpeg -v error -y -i "$SRC" -vn -ac 1 -ar 48000 \
  -af "highpass=f=80,afftdn=nr=8:nf=-42,equalizer=f=245:t=q:w=1.2:g=-2.2,equalizer=f=3300:t=q:w=1.4:g=2.5,highshelf=f=9000:g=1,acompressor=threshold=-24dB:ratio=3:attack=5:release=120:makeup=2,loudnorm=I=-16:TP=-2:LRA=9" \
  -ar 48000 "$W/voice_clean.wav"
echo "voice_clean.wav ready"
# Compensate filter-chain latency measured by envelope cross-correlation (~1192 samples = 24.8 ms at 48 kHz).
LAG=${VOICE_LAG_SAMPLES:-1192}
ffmpeg -v error -y -i "$W/voice_clean.wav" -af "atrim=start_sample=$LAG,asetpts=PTS-STARTPTS,apad=pad_len=$LAG" "$W/voice_clean_sync.wav"
mv "$W/voice_clean_sync.wav" "$W/voice_clean.wav"
echo "latency compensated by $LAG samples"
