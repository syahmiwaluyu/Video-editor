"""Procedural soundtrack + SFX for VGC-FT01 (no samples, no external services).

Reads the same timing.json as the Remotion composition so audio hits match visual cues.
Output: ../out/mix_raw.wav (48 kHz, stereo, float -> 16-bit). Loudness is normalised later with ffmpeg.
Run: python3 -I scripts/make_audio.py  (from the source/ folder)
"""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T = json.load(open(os.path.join(ROOT, "timing.json")))
SR = 48000
FPS = T["fps"]
DUR = T["durationInFrames"] / FPS
N = int(DUR * SR)
rng = np.random.default_rng(7)  # fixed seed -> reproducible


def sec(frame):
    return frame / FPS


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def pluck(freq, dur=1.6, bright=0.5):
    """Karplus-Strong plucked string."""
    n = int(dur * SR)
    period = int(SR / freq)
    buf = rng.uniform(-1, 1, period)
    buf = lowpass(buf, 2000 + 6000 * bright)
    out = np.empty(n)
    for i in range(n):
        j = i % period
        out[i] = buf[j]
        buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % period])
    env = np.minimum(1, np.arange(n) / (0.003 * SR))
    return out * env


def sine_tone(freq, dur, attack=0.01, decay=0.5, partials=((1, 1.0), (2, 0.25), (3, 0.08))):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in partials)
    env = np.minimum(1, t / attack) * np.exp(-t / decay)
    return s * env


def tap(dur=0.12, cutoff=1800):
    """Gentle percussive tap: short filtered noise + soft body."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = lowpass(rng.uniform(-1, 1, n), cutoff) * np.exp(-t / 0.018)
    body = np.sin(2 * np.pi * 180 * t * np.exp(-t * 8)) * np.exp(-t / 0.04)
    return 0.8 * noise + 0.6 * body


def pop(freq=900, dur=0.09):
    t = np.arange(int(dur * SR)) / SR
    f = freq * (1 + 1.2 * np.exp(-t / 0.01))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.025)


def whoosh(dur=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    # rising-then-falling brightness via two filtered layers crossfaded
    lo = lowpass(noise, 600)
    hi = noise - lowpass(noise, 2500)
    shape = np.sin(np.pi * t / dur) ** 2
    mix = lo * (1 - t / dur) + 0.5 * hi * (t / dur)
    return mix * shape


L = np.zeros(N)
R = np.zeros(N)


def place(sig, at_sec, gain=1.0, pan=0.0):
    i = int(at_sec * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


C = T["cues"]
sc = T["scenes"]
BPM = 96
beat = 60 / BPM
eighth = beat / 2

# ---------- music: light plucked synth with progression hook -> explain -> takeaway ----------
# Hook (sombre, sparse): B minor colour.
hook_notes = [59, 66, 62, 66]  # B3 F#4 D4 F#4
for k, n in enumerate(hook_notes):
    place(pluck(midi(n), 1.8, 0.35), k * beat, 0.32, pan=-0.2 + 0.13 * k)
place(pluck(midi(47), 2.4, 0.2), 0.0, 0.30)  # low B2 root

# Explain: G major arpeggio in eighths, a little more movement.
t0 = sec(sc["explain"]["from"])
exp_notes = [55, 62, 67, 71, 67, 62, 59, 62]
for k, n in enumerate(exp_notes):
    place(pluck(midi(n), 1.4, 0.45), t0 + k * 0.3, 0.26, pan=0.25 * np.sin(k))
place(pluck(midi(43), 2.4, 0.2), t0, 0.28)  # G2 root
# gentle percussive taps on the beat
for k in range(4):
    place(tap(), t0 + k * beat, 0.16, pan=0.1)

# Takeaway: A -> D resolution, brighter, then sustain.
t1 = sec(sc["takeaway"]["from"])
for k, n in enumerate([57, 61, 64]):  # A3 C#4 E4
    place(pluck(midi(n), 1.2, 0.5), t1 + k * 0.08, 0.24)
place(pluck(midi(45), 1.4, 0.2), t1, 0.26)
t_res = t1 + beat * 1.2
for k, n in enumerate([62, 66, 69, 74]):  # D4 F#4 A4 D5
    place(pluck(midi(n), 2.6, 0.55), t_res + k * eighth * 0.6, 0.24, pan=-0.3 + 0.2 * k)
place(pluck(midi(38), 3.0, 0.2), t_res, 0.30)  # D2 root
for k in range(3):
    place(tap(cutoff=1400), t_res + k * beat, 0.10, pan=-0.1)

# ---------- SFX (one per visual event) ----------
place(sine_tone(659.25, 1.2, attack=0.02, decay=0.6, partials=((1, 1.0),)), sec(C["flatline"]), 0.10)  # soft flat tone, not an alarm
place(whoosh(0.32), sec(C["cut1"]) - 0.16, 0.20)  # zoom-through
place(pop(820), sec(C["chip1"]), 0.20, pan=0.3)
place(pop(980), sec(C["chip2"]), 0.20, pan=0.3)
place(tap(0.16, 1200), sec(C["statement"]), 0.40, pan=0.2)  # box lands
place(pop(700), sec(C["bubble1"]), 0.16, pan=-0.3)
place(pop(900), sec(C["bubble2"]), 0.16, pan=-0.2)
# soft confirmation tone on the CTA landing (two notes, D5 -> A5)
place(sine_tone(midi(74), 0.9, decay=0.35), sec(C["cta"]), 0.12, pan=0.2)
place(sine_tone(midi(81), 1.2, decay=0.45), sec(C["cta"]) + 0.11, 0.10, pan=0.2)

# tail fade 300 ms
fade = int(0.3 * SR)
ramp = np.linspace(1, 0, fade)
L[-fade:] *= ramp
R[-fade:] *= ramp

stereo = np.stack([L, R], axis=1)
peak = np.max(np.abs(stereo))
stereo = stereo / peak * 0.7  # headroom before loudnorm
os.makedirs(os.path.join(os.path.dirname(ROOT), "out"), exist_ok=True)
path = os.path.join(os.path.dirname(ROOT), "out", "mix_raw.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype("<i2").tobytes())
print("wrote", path, "raw peak", round(float(peak), 3), "dur", DUR)
