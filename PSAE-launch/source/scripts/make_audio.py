"""Procedural score for the launch preview (numpy only, fixed seed).

Calm cinematic pad + soft piano-like notes, 72 BPM, one chord per bar.
Reflective (darker, sparse) in the opening/emotional scenes, warmer and fuller in the
peer-support scenes, then a swell and shimmer on the title reveal. Cues come from timing.json.
Writes ../out/mix_raw.wav (48 kHz, 16-bit stereo).
"""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "..", "timing.json")))
SR = 48000
FPS = T["fps"]
DUR = T["durationInFrames"] / FPS
N = int(DUR * SR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def f2s(frame):
    return frame / FPS


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def add(sig, start_s, pan=0.0, gain=1.0):
    i = int(start_s * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def onepole_lp(x, cutoff):
    # first-order low-pass applied in the frequency domain (H = 1 / (1 + j f/fc))
    nfft = 1 << (len(x) - 1).bit_length()
    f = np.fft.rfftfreq(nfft, 1 / SR)
    return np.fft.irfft(np.fft.rfft(x, nfft) / (1 + 1j * f / cutoff), nfft)[: len(x)]


def pad_note(freq, length, bright):
    t = np.arange(int(length * SR)) / SR
    sig = np.zeros_like(t)
    nh = 6 + int(bright * 6)
    for det in (-0.06, 0.0, 0.07):
        f = freq * 2 ** (det / 12)
        for h in range(1, nh + 1):
            sig += np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.28)) / (h ** 1.6)
    env = np.minimum(1, t / 1.4) * np.minimum(1, (length - t) / 1.6).clip(0)
    return sig * env * 0.05


def piano(freq, length=3.5):
    t = np.arange(int(length * SR)) / SR
    sig = np.zeros_like(t)
    for h, a in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)):
        sig += a * np.sin(2 * np.pi * freq * h * t) * np.exp(-t * (1.6 + h * 0.9))
    attack = np.minimum(1, t / 0.006)
    return sig * attack * 0.11


def swell(length, lo=300, hi=3000):
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    sig = onepole_lp(noise, lo) * 0.6 + (onepole_lp(noise, hi) - onepole_lp(noise, lo)) * 0.4
    env = (t / length) ** 2.2 * np.minimum(1, (length - t) / 0.08)
    return sig * env * 0.06


def chime(freq, length=4.0):
    t = np.arange(int(length * SR)) / SR
    sig = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t * d) for r, a, d in ((1, 1, 1.2), (2.76, 0.4, 2.0), (5.4, 0.2, 3.0)))
    return sig * np.minimum(1, t / 0.004) * 0.05


# ---- harmony ----
BAR = 60 / 72 * 4  # 3.333 s
chords = {
    "Bm": [47, 54, 59, 62, 66],
    "G": [43, 50, 55, 59, 62],
    "D": [50, 57, 62, 66, 69],
    "A": [45, 52, 57, 61, 64],
    "Em": [40, 47, 55, 59, 64],
}
prog = ["Bm", "G", "D", "A", "Bm", "G", "Em", "A",   # reflective
        "D", "A", "Bm", "G", "D", "A", "G", "A",     # warmer
        "D", "D"]                                     # title / resolve
peer_start = f2s(T["scenes"]["peer"][0])
aware_start = f2s(T["scenes"]["awareness"][0])
title_start = f2s(T["scenes"]["title"][0])

for b, name in enumerate(prog):
    t0 = b * BAR
    if t0 >= DUR:
        break
    warm = 0.0 if t0 < aware_start else (0.5 if t0 < peer_start else 1.0)
    length = min(BAR + 1.6, DUR - t0)
    for k, n in enumerate(chords[name]):
        add(pad_note(midi(n), length, warm), t0, pan=(k - 2) * 0.25, gain=0.7 + 0.3 * warm)
    # soft piano: sparse when reflective, gentle arpeggio when warm
    tones = chords[name][2:] + [chords[name][2] + 12]
    steps = [0, 2] if warm == 0 else ([0, 1, 2, 3] if warm < 1 else [0, 1, 2, 3, 4, 5])
    for s_i, s in enumerate(steps):
        n = tones[s_i % len(tones)] + 12
        add(piano(midi(n)), t0 + s * BAR / (4 if warm == 0 else len(steps)),
            pan=rng.uniform(-0.4, 0.4), gain=0.8 + 0.3 * warm)

# low root drone for warmth under everything
t = np.arange(N) / SR
drone = np.sin(2 * np.pi * midi(38) * t) * 0.025 * np.minimum(1, t / 4)
L += drone
R += drone

# ---- transitions & title ----
for scene in ("emotional", "awareness", "peer"):
    at = f2s(T["scenes"][scene][0])
    add(swell(1.8), at - 1.8, pan=-0.2)
add(swell(3.0, 400, 5000), f2s(T["cues"]["title_main"]) - 3.0, gain=1.5)
for i, n in enumerate([74, 78, 81, 86]):
    add(chime(midi(n)), f2s(T["cues"]["title_main"]) + i * 0.12, pan=-0.3 + i * 0.2)
for i, n in enumerate([81, 86]):
    add(chime(midi(n)), f2s(T["cues"]["title_meta"]) + i * 0.18, pan=0.2 - i * 0.4, gain=0.6)

# ---- simple reverb (exponential noise IR, FFT convolution) ----
ir_len = int(2.8 * SR)
ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / SR * 2.4)
ir = onepole_lp(ir, 5000)
ir /= np.sqrt(np.sum(ir ** 2))


def conv(x):
    n = len(x) + ir_len
    nfft = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]


Lw, Rw = L + conv(L) * 0.35, R + conv(np.roll(R, 480)) * 0.35

# fade in / out
fade = np.ones(N)
fade[: int(1.5 * SR)] = np.linspace(0, 1, int(1.5 * SR))
fo = int(f2s(T["cues"]["fade_out"]) * SR) - int(1.0 * SR)
fade[fo:] = np.linspace(1, 0, N - fo) ** 1.5
out = np.stack([Lw * fade, Rw * fade], 1)
out /= max(1e-9, np.abs(out).max()) / 0.7

os.makedirs(os.path.join(HERE, "..", "..", "out"), exist_ok=True)
with wave.open(os.path.join(HERE, "..", "..", "out", "mix_raw.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("wrote out/mix_raw.wav", round(DUR, 2), "s")
