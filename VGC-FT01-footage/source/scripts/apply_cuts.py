"""Apply the approved pause trim (out/cut_list_v02.csv, silence-only) to make version v02.

Everything is quantised to whole frames (30 fps) so picture and sound stay locked.
Outputs (source timecodes -> output timecodes):
  work/transcript_cut.json      word timestamps remapped
  source/edit_plan_cut.json     edit plan remapped (+ "jumps": cut points that fall inside a scene)
  work/keep_frames.json         kept source frame ranges [a, b) (used for video + audio)
  work/voice_clean_cut.wav      cleaned dialogue with pauses shortened (5 ms fades at every join, in silence)
  source/public/footage_cut.mp4 picture proxy with the same frames removed
Original footage and the v01 proxy are not modified.
"""
import csv, json, subprocess, wave, sys
from pathlib import Path
import numpy as np

FPS = 30; SR = 48000; SPF = SR // FPS
ROOT = Path(__file__).resolve().parents[1]          # source/
PRJ = ROOT.parent
plan = json.load(open(ROOT / "edit_plan.json"))
tr = json.load(open(PRJ / "work" / "transcript.json"))
CUTFILE = "cut_list_v02.csv"   # energy-based list (derive_silence_cuts.py); v01 ASR-based proposal kept for reference
rows = list(csv.DictReader(open(PRJ / "out" / CUTFILE)))

SRC_FRAMES = 15471                                   # frames in footage.mp4 proxy (ffprobe)
cuts = []                                            # removed source frame ranges [a, b)
for r in rows:
    a = int(round(float(r["source_start_s"]) * FPS)); b = int(round(float(r["source_end_s"]) * FPS))
    if b > a: cuts.append((a, b, r["id"]))
cuts.sort()
keeps = []; cur = 0
for a, b, _ in cuts:
    keeps.append((cur, a)); cur = b
keeps.append((cur, SRC_FRAMES))
removed = sum(b - a for a, b, _ in cuts)

def m(t):
    """source seconds -> output seconds (times inside a removed range snap to the join)."""
    f = t * FPS; out = f
    for a, b, _ in cuts:
        if f >= b: out -= (b - a)
        elif f > a: out -= (f - a); break
        else: break
    return out / FPS

# join points on the output timeline
joins = []
acc = 0
for a, b, cid in cuts:
    joins.append((round((a - acc) / FPS, 4), cid)); acc += b - a

# ---- remap transcript ----
for seg in tr:
    seg["start"] = m(seg["start"]); seg["end"] = m(seg["end"])
    for w in seg["words"]:
        w["s"] = m(w["s"]); w["e"] = m(w["e"])
json.dump(tr, open(PRJ / "work" / "transcript_cut.json", "w"), ensure_ascii=False, indent=1)

# ---- remap plan ----
p = json.loads(json.dumps(plan))
p["turns"] = [[round(m(t), 3), s] for t, s in p["turns"]]
for k in ("scenes", "notes", "chapters"):
    for x in p[k]:
        x["s"] = round(m(x["s"]), 3); x["e"] = round(m(x["e"]), 3)
p["end"]["s"] = round(m(p["end"]["s"]), 3)
p["footageEndSec"] = round(m(plan["footageEndSec"]), 3)
# snap scene boundaries onto a nearby join (a cut hidden by a composition change)
jt = [j for j, _ in joins]
for i in range(1, len(p["scenes"])):
    s = p["scenes"][i]["s"]
    near = [j for j in jt if 0 <= s - j <= 1.2]
    if near:
        j = max(near); p["scenes"][i]["s"] = j; p["scenes"][i - 1]["e"] = j
# merge fragments shorter than 2.5 s (left over after trimming) into the previous scene
merged = []
for sc in p["scenes"]:
    if merged and sc["e"] - sc["s"] < 2.5:
        merged[-1]["e"] = sc["e"]
    else:
        merged.append(sc)
p["scenes"] = merged
# joins that still land inside a scene get a punch-in toggle in the renderer
bounds = [sc["s"] for sc in p["scenes"]]
p["jumps"] = [j for j in jt if all(abs(j - b) > 1 / FPS for b in bounds) and j < p["end"]["s"]]
p["footageFile"] = "footage_cut.mp4"
p["voiceFile"] = "voice_clean_cut.wav"
p["version"] = "v02"
json.dump(p, open(ROOT / "edit_plan_cut.json", "w"), ensure_ascii=False, indent=1)
json.dump({"keeps": keeps, "cuts": cuts, "joins": joins}, open(PRJ / "work" / "keep_frames.json", "w"), indent=1)

# ---- audio ----
w = wave.open(str(PRJ / "work" / "voice_clean.wav"))
assert w.getframerate() == SR
v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
if w.getnchannels() == 2: v = v.reshape(-1, 2).mean(1)
v = np.pad(v, (0, max(0, SRC_FRAMES * SPF - len(v))))
F = int(0.005 * SR); ramp = np.linspace(0, 1, F, dtype=np.float32)
parts = []
for a, b in keeps:
    x = v[a * SPF:b * SPF].copy()
    if a > 0: x[:F] *= ramp
    if b < SRC_FRAMES: x[-F:] *= ramp[::-1]
    parts.append(x)
y = np.concatenate(parts)
o = wave.open(str(PRJ / "work" / "voice_clean_cut.wav"), "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
o.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); o.close()

# ---- video (frame-exact select on the v01 proxy) ----
expr = "+".join(f"between(n\\,{a}\\,{b - 1})" for a, b in keeps)
if "--no-video" not in sys.argv:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "public" / "footage.mp4"),
        "-vf", f"select='{expr}',setpts=N/{FPS}/TB", "-an", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "17", "-g", "10", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-color_range", "tv", str(ROOT / "public" / "footage_cut.mp4")], check=True)

print(f"{len(cuts)} cuts, removed {removed} frames = {removed / FPS:.2f} s; output footage {(SRC_FRAMES - removed) / FPS:.2f} s;"
      f" end card at {p['end']['s']} s; total {p['end']['s'] + p['end']['hold']:.2f} s; jumps inside scenes: {len(p['jumps'])}")
