"""Derive pause-trim cuts from the audio itself (not from ASR word times).

A frame is 'sound' if the cleaned dialogue is above THRESH dBFS (20 ms windows). Sound is protected with PAD on
both sides (breaths, 'um', 'hmm', soft words are kept). Only silent runs longer than KEEP are shortened, leaving
KEEP seconds of the silent run in place (split evenly around the cut). Output: out/cut_list_v02.csv (source times,
frame-quantised at 30 fps).
Usage: python derive_silence_cuts.py [KEEP_SECONDS]
"""
import csv, sys, wave, json
from pathlib import Path
import numpy as np

FPS = 30; SR = 48000
PRJ = Path(__file__).resolve().parents[2]
THRESH = -34.0; PAD = 0.12; WIN = 0.02
KEEP = float(sys.argv[1]) if len(sys.argv) > 1 else 1.2
END_LIMIT = 513.4          # last dialogue (start of end card, source time)

w = wave.open(str(PRJ / "work" / "voice_clean.wav"))
v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
if w.getnchannels() == 2: v = v.reshape(-1, 2).mean(1)
hop = int(WIN * SR)
x = v[: len(v) // hop * hop].reshape(-1, hop)
db = 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)
act = db > THRESH
p = int(round(PAD / WIN))
dil = act.copy()
for k in range(1, p + 1):
    dil[k:] |= act[:-k]; dil[:-k] |= act[k:]

rows = []; i = 0; n = len(dil)
first_sound = np.argmax(act) * WIN
while i < n:
    if not dil[i]:
        j = i
        while j < n and not dil[j]: j += 1
        s, e = i * WIN, j * WIN
        if s > first_sound and e < END_LIMIT and e - s > KEEP + 0.2:
            a = int(round((s + KEEP / 2) * FPS)); b = int(round((e - KEEP / 2) * FPS))
            if b - a >= 6:   # at least 0.2 s worth removing
                rows.append((a, b, round(s, 2), round(e, 2)))
        i = j
    else:
        i += 1
tot = sum(b - a for a, b, _, _ in rows) / FPS
with open(PRJ / "out" / "cut_list_v02.csv", "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["id", "source_start_s", "source_end_s", "remove_s", "silent_run_start_s", "silent_run_end_s", "note"])
    for k, (a, b, s, e) in enumerate(rows, 1):
        wr.writerow([f"S{k:02d}", f"{a / FPS:.4f}", f"{b / FPS:.4f}", f"{(b - a) / FPS:.2f}", s, e,
                     f"silent run shortened to {KEEP} s; sound kept with {PAD} s guard"])
print(f"KEEP={KEEP}: {len(rows)} cuts, remove {tot:.2f} s -> total ~{518.0 - tot:.1f} s")
