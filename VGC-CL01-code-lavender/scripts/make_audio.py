"""Procedural score for VGC-CL01 (24 s = 3 x 8 s). No samples, no external services, fixed seed.

0-8 s   sparse soft piano, A minor, faint hospital room tone
8-16 s  warmer piano, C major, slowly building
16-24 s piano + string-like pad, crescendo peaking ~21 s, resolves on C by 24 s
No dialogue is generated. Output: out/music.wav (48 kHz stereo 16-bit). Loudness is set later by assemble.sh.
Run from the project folder: python3 -I scripts/make_audio.py
"""
import os
import wave
import numpy as np

SR, DUR = 48000, 24.0
N = int(SR * DUR)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(m, dur=3.5, vel=0.5):
    """Simple piano-like tone: slightly inharmonic partials, fast attack, two-stage decay, softer when quiet."""
    t = np.arange(int(dur * SR)) / SR
    f = hz(m); B = 0.0004
    s = np.zeros_like(t)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > SR / 2.2:
            break
        amp = (1 / k ** (1.6 - 0.6 * vel)) * np.exp(-t * (0.6 + 0.35 * k))
        s += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    env = np.minimum(1, t / 0.004) * (0.6 * np.exp(-t / 0.35) + 0.4 * np.exp(-t / 2.2))
    rel = np.minimum(1, (dur - t) / 0.3)
    return s * env * rel * vel


def pad(ms, t0, t1, peak_at, vol):
    """Detuned saw-ish string pad, low-passed, swelling to peak_at then easing off."""
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ms:
        for det in (-0.12, 0.0, 0.11):
            f = hz(m + det)
            s += sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 7))
    s /= len(ms) * 3
    # one-pole low-pass via FFT-free cumulative smoothing (vectorised exponential moving average)
    a = np.exp(-2 * np.pi * 1800 / SR)
    s = np.real(np.fft.irfft(np.fft.rfft(s) / (1 - a * np.exp(-2j * np.pi * np.fft.rfftfreq(n, 1 / SR) / SR)) * (1 - a), n))
    p = (peak_at - t0)
    env = np.where(t < p, (t / p) ** 2, 1 - 0.55 * ((t - p) / (t1 - t0 - p)))
    env *= np.minimum(1, (t1 - t0 - t) / 0.8)
    return s * env * vol


def add(sig, at, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig)); sig = sig[: j - i]
    L[i:j] += sig * (1 - pan) * 0.5 ** 0.5 * 1.0; R[i:j] += sig * (1 + pan) * 0.5 ** 0.5 * 1.0


# --- 0-8 s: Am(add9) -> Fmaj7, sparse broken chords
for at, notes, v in [(0.3, [45, 57], 0.35), (0.9, [64], 0.25), (1.5, [71], 0.22), (2.4, [72], 0.2),
                     (4.0, [41, 53], 0.33), (4.6, [64], 0.22), (5.2, [69], 0.2), (6.2, [67], 0.18)]:
    for m in notes:
        add(piano(m, 4.5, v), at, pan=(m - 60) / 60)
# --- 8-16 s: C -> G/B -> Am -> F, more motion, building
for bar, (bass, ch) in enumerate([(48, [60, 64, 67]), (47, [62, 67, 71]), (45, [60, 64, 69]), (41, [60, 65, 69])]):
    t0 = 8.0 + bar * 2.0; v = 0.30 + bar * 0.05
    add(piano(bass, 3.0, v + 0.05), t0, -0.3)
    for k, m in enumerate(ch + [ch[1] + 12]):
        add(piano(m, 2.5, v * 0.7), t0 + 0.25 + k * 0.4, (m - 60) / 50)
# --- 16-24 s: F -> G -> C, pad swell + fuller piano
for t0, bass, ch in [(16.0, 41, [65, 69, 72]), (18.0, 43, [67, 71, 74]), (20.0, 48, [64, 67, 72, 76]), (22.0, 48, [67, 72, 76])]:
    add(piano(bass, 3.0, 0.55), t0, -0.3); add(piano(bass + 12, 3.0, 0.4), t0, -0.2)
    for k, m in enumerate(ch):
        add(piano(m, 2.6, 0.42), t0 + k * 0.05, (m - 64) / 40)
add(pad([53, 60, 65, 69], 16.0, 18.0, 17.9, 0.10), 16.0, -0.2)
add(pad([55, 62, 67, 71], 18.0, 20.0, 19.9, 0.16), 18.0, 0.2)
add(pad([48, 55, 64, 67, 72], 20.0, 24.0, 21.0, 0.22), 20.0)
# --- room tone 0-16 s (very quiet filtered noise), fades out as clip 3 starts
noise = rng.standard_normal(int(16.5 * SR))
F = np.fft.rfftfreq(len(noise), 1 / SR)
noise = np.fft.irfft(np.fft.rfft(noise) / (1 + (F / 300) ** 2), len(noise)) * 0.012
noise *= np.minimum(1, np.minimum(np.arange(len(noise)) / SR / 1.0, (16.5 - np.arange(len(noise)) / SR) / 0.8))
L[: len(noise)] += noise; R[: len(noise)] += np.roll(noise, 900)

mix = np.stack([L, R], 1)
mix *= np.minimum(1, np.minimum(np.arange(N) / (0.05 * SR), (N - np.arange(N)) / (1.2 * SR)))[:, None]
mix /= np.max(np.abs(mix)) / 0.8
os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
with wave.open(os.path.join(ROOT, "out", "music.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote out/music.wav")
