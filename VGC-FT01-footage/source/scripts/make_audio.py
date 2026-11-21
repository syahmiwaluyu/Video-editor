"""Procedural soundtrack + SFX + dialogue mix for VGC-FT01 footage preview.

Inputs : ../work/voice_clean.wav (48 kHz mono, produced by prep_voice.sh), ../timing.json
Outputs: ../out/music.wav, ../out/sfx.wav, ../out/mix_raw.wav
No samples, no external music. Fixed seed -> reproducible.
Audio direction: dry paper ticks, soft percussion, one restrained paper accent per reveal.
"""
import json, wave, sys
from pathlib import Path
import numpy as np

SR = 48000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
T = json.load(open(ROOT / "timing.json"))
OUT = ROOT.parent / "out"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(20261121)

def read_mono(p):
    w = wave.open(str(p))
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2:
        a = a.reshape(-1, 2).mean(1)
    assert w.getframerate() == SR
    return a

def write(p, x):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    w = wave.open(str(p), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()

def db(x): return 10 ** (x / 20)

def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)

N = int(round(T["durationSec"] * SR))
voice = read_mono(ROOT.parent / "work" / T.get("voiceFile", "voice_clean.wav"))
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]

# ---------------- music ----------------
BPM = 74.0
beat = 60 / BPM
bar = beat * 4
# Original progression (F major area): Fmaj7 | Dm7 | Bbmaj7 | Csus4 -> C
def midi(n): return 440 * 2 ** ((n - 69) / 12)
CHORDS = [[53, 57, 60, 64], [50, 53, 57, 60], [46, 50, 53, 57], [48, 53, 55, 60]]
MOTIF = [72, 69, 67, 69, 65, 67, 64, 65]  # sparse felt-pluck line, one note per beat-and-a-half

music = np.zeros(N, np.float32)
t_all = np.arange(N) / SR
end_s = T["end"]["s"]

def env_ar(n, a, r):
    e = np.ones(n, np.float32)
    na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (r * SR))
    return e

def add(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]

def felt(freq, dur, vel):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * tt) + 0.35 * np.sin(2 * np.pi * 2 * freq * tt) * np.exp(-tt * 6)
         + 0.12 * np.sin(2 * np.pi * 3.01 * freq * tt) * np.exp(-tt * 9))
    return (s * env_ar(n, 0.006, 0.9) * vel).astype(np.float32)

def pad(freqs, dur, vel):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for d in (-0.12, 0.12):
            ph = rng.random() * 6.28
            s += np.sin(2 * np.pi * f * (1 + d / 100) * tt + ph) + 0.18 * np.sin(2 * np.pi * 2 * f * tt + ph)
    a = min(1.2, dur / 3)
    e = np.minimum(1, np.minimum(tt / a, (dur - tt) / a))
    return (s * e * vel / len(freqs)).astype(np.float32)

nbars = int(np.ceil(T["durationSec"] / bar))
hook_e = T["hook"]["e"]
for b in range(nbars):
    t0 = b * bar
    if t0 >= end_s + 6: break
    ch = CHORDS[b % 4]
    in_end = t0 >= end_s - bar
    # section intensity: hook sparse -> body adds pad + percussion -> end resolves
    body = t0 >= hook_e
    music_pad = pad([midi(n) for n in ch], bar + 0.6, 0.10 if body else 0.05)
    add(music, t0, music_pad)
    # bass note on beat 1
    add(music, t0, felt(midi(ch[0] - 12), bar, 0.16))
    # motif: 2 notes per bar, varies by bar
    for k in range(2):
        n = MOTIF[(b * 2 + k) % len(MOTIF)] - (12 if b % 8 >= 4 else 0)
        add(music, t0 + k * beat * 2 + (beat if k else 0) * 0.5, felt(midi(n), 2.2, 0.10))
    # soft percussion (brushed noise on beats 2 & 4, light tick on offbeats) after hook
    if body and not in_end:
        for k in range(4):
            if k in (1, 3):
                n = int(0.09 * SR); nz = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (0.025 * SR))
                nz = nz - onepole_lp(nz, 1800)
                add(music, t0 + k * beat, (nz * 0.035).astype(np.float32))
            n = int(0.02 * SR); tk = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (0.004 * SR))
            tk = tk - onepole_lp(tk, 4000)
            add(music, t0 + k * beat + beat / 2, (tk * 0.012).astype(np.float32))

# final resolve chord on end card
add(music, end_s + 0.15, pad([midi(n) for n in [53, 57, 60, 65]], 5.0, 0.14))
add(music, end_s + 0.15, felt(midi(41), 4.5, 0.2))
music = onepole_lp(music, 7000).astype(np.float32)

# ---------------- sfx ----------------
sfx = np.zeros(N, np.float32)
def paper(dur=0.16, lvl=0.05, bright=2500):
    n = int(dur * SR)
    nz = rng.normal(0, 1, n)
    crackle = (rng.random(n) < 0.004) * rng.normal(0, 3, n)
    s = nz * 0.5 + crackle
    s = s - onepole_lp(s, bright)
    s = onepole_lp(s, 9000)
    e = np.minimum(1, np.arange(n) / (0.01 * SR)) * np.exp(-np.arange(n) / (dur * 0.35 * SR))
    return (s * e * lvl).astype(np.float32)
def tick(lvl=0.06):
    n = int(0.03 * SR); s = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (0.003 * SR))
    s = s - onepole_lp(s, 3000)
    return (s * lvl).astype(np.float32)

cues = []
prev_mode = None
for sc in T["scenes"]:
    key = (sc["mode"], sc.get("spk"))
    if key != prev_mode and sc["s"] > 0.5 and sc["mode"] != "full":
        cues.append(("paper", sc["s"]))
    prev_mode = key
for c in T["chapters"]:
    cues.append(("tick", c["s"] + 5 / 30))
for nt in T["notes"]:
    cues.append(("tick", nt["s"] + 6 / 30))
cues.append(("paper", T["end"]["s"] + 0.1))
for i, (kind, ts) in enumerate(cues):
    add(sfx, ts, paper() if kind == "paper" else tick())
# hook: one paper accent per line (lines enter 9 frames apart)
for i, _ in enumerate(T["hook"]["lines"]):
    add(sfx, i * 9 / 30, paper(0.12, 0.035))

# ---------------- ducking (voice-envelope driven) ----------------
from scipy.signal import lfilter
hop = 480
v = voice[: len(voice) // hop * hop].reshape(-1, hop)
rms = np.sqrt((v ** 2).mean(1) + 1e-12)
vdb = 20 * np.log10(rms)
active = (vdb > -45).astype(np.float32)
# attack fast (~30 ms), release slow (~450 ms)
g = np.zeros_like(active); s = 0.0
for i, a in enumerate(active):
    s = s + (a - s) * (0.5 if a > s else 0.022)
    g[i] = s
gain_m = db(-14) * g + 1.0 * (1 - g)   # music ~14 dB down while speaking
gain_s = db(-3) * g + 1.0 * (1 - g)    # sfx ~3 dB down while speaking
gm = np.repeat(gain_m, hop); gs = np.repeat(gain_s, hop)
gm = np.pad(gm, (0, N - len(gm)), constant_values=gm[-1]); gs = np.pad(gs, (0, N - len(gs)), constant_values=gs[-1])

MUSIC_LVL = db(-2)
music_d = music * gm * MUSIC_LVL
sfx_d = sfx * gs
mix = voice + music_d + sfx_d
# tail fade 300 ms
f = int(0.3 * SR); mix[-f:] *= np.linspace(1, 0, f)
write(OUT / "music.wav", music_d)
write(OUT / "sfx.wav", sfx_d)
write(OUT / "mix_raw.wav", mix)
json.dump({"cues": cues}, open(OUT / "audio_cues.json", "w"), indent=1)
print("peak raw mix", 20 * np.log10(np.abs(mix).max() + 1e-9), "dBFS; cues", len(cues))
