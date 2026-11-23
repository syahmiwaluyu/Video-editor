"""VGC-AE01 — procedural audio: soft piano + quiet hospital room tone. numpy only, fixed seed.

No voice is generated here. The whispered line is left as an empty slot (see VO_SLOT)
so a real recording can be dropped in later.

Usage (from source/): python3 -I scripts/make_audio.py
"""
from pathlib import Path
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "mix_raw.wav"
SR, DUR = 48000, 8.0
N = int(SR * DUR)
VO_SLOT = (2.6, 4.2)   # seconds, where "Adakah aku sudah melakukan yang terbaik?" would sit
rng = np.random.default_rng(20261123)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(m, dur, vel):
    """Additive soft piano-like tone: decaying harmonics, slight inharmonicity, felt attack."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = midi_hz(m)
    out = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 12000:
            break
        amp = 1 / k ** 1.8
        dec = 1.2 + 0.9 * k + f / 400
        out += amp * np.exp(-t * dec) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    att = np.minimum(t / 0.012, 1)
    rel = np.minimum((n - np.arange(n)) / (0.08 * SR), 1)
    return out * att * rel * vel


def place(buf, sig, t0, pan=0.0):
    i = int(t0 * SR)
    j = min(i + len(sig), N)
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:j, 0] += sig[: j - i] * gl
    buf[i:j, 1] += sig[: j - i] * gr


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def reverb(x, rt=2.2, mix=0.28):
    n = int(SR * rt)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-t * 6.9 / rt)[:, None]
    ir[:, 0] = onepole_lp(ir[:, 0], 5000)
    ir[:, 1] = onepole_lp(ir[:, 1], 5000)
    ir /= np.sqrt((ir ** 2).sum(0))
    L = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], L) * np.fft.rfft(ir[:, c], L), L)[: len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix * 3.0


music = np.zeros((N, 2))
beat = 60 / 64  # 64 BPM
# A minor -> F -> C (resolve lands on the lavender glow / text at ~4.8 s)
chords = [
    (0.00, 45, [57, 60, 64]),   # Am
    (2.40, 41, [57, 60, 65]),   # F
    (4.80, 36, [55, 60, 64]),   # C
]
for t0, bass, tri in chords:
    place(music, piano(bass, 3.2, 0.32), t0 + 0.02, -0.15)
    place(music, piano(bass + 12, 3.0, 0.16), t0 + 0.03, -0.1)
    for k, m in enumerate(tri):
        t = t0 + 0.04 + k * beat * 0.5
        quiet = VO_SLOT[0] - 0.1 < t < VO_SLOT[1]
        place(music, piano(m, 2.6, 0.12 if quiet else 0.2), t, -0.3 + 0.3 * k)
# sparse melody, kept out of the whisper slot
for t0, m, v in [(0.95, 72, 0.22), (1.90, 71, 0.18), (4.80, 72, 0.24), (5.75, 76, 0.2), (6.70, 74, 0.16)]:
    place(music, piano(m, 3.0, v), t0, 0.2)

music = reverb(music)

# room tone: soft filtered noise + very low ventilation hum, ducked as the glow comes in
t = np.arange(N) / SR
noise = rng.normal(0, 1, (N, 2))
room = np.stack([onepole_lp(onepole_lp(noise[:, c], 900), 900) for c in range(2)], 1)
room /= np.abs(room).max()
hum = 0.25 * np.sin(2 * np.pi * 100 * t) + 0.1 * np.sin(2 * np.pi * 200 * t)
room = room * 0.9 + hum[:, None] * 0.35
room_env = 1 - 0.7 * np.clip((t - 4.3) / 1.0, 0, 1)
room *= room_env[:, None]

mix = music / np.abs(music).max() * 0.7 + room * 0.035
fade_in = np.clip(t / 0.25, 0, 1)
fade_out = np.clip((DUR - t) / 0.35, 0, 1)
mix *= (fade_in * fade_out)[:, None]
mix /= np.abs(mix).max() / 0.8

with wave.open(str(OUT), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", OUT)
