"""Builds source/timing.json (single timing source for visuals + audio) from:
  - work/transcript.json  (word-level ASR, faster-whisper large-v3)
  - source/edit_plan.json (human edit decisions: speaker turns, scenes, notes, chapters, hook, end card,
                           caption text corrections)
Timecodes in v01 = source timecodes (no cuts applied).
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
CUT = "--cut" in sys.argv   # v02: use the pause-trimmed timeline produced by apply_cuts.py
tr = json.load(open(ROOT.parent / "work" / ("transcript_cut.json" if CUT else "transcript.json")))
plan = json.load(open(ROOT / ("edit_plan_cut.json" if CUT else "edit_plan.json")))

words = []
# tail pass has phrase-level punctuation; keep order strictly by time
for seg in tr:
    for w in sorted(seg["words"], key=lambda w: w["s"]):
        words.append({"w": w["w"].strip(), "s": w["s"], "e": w["e"], "p": w["p"]})

# speaker turns: list of [start_sec, spk]; a word belongs to the latest turn starting <= word midpoint
turns = sorted(plan["turns"], key=lambda x: x[0])
def spk_at(t):
    cur = turns[0][1]
    for ts, s in turns:
        if ts <= t + 1e-6: cur = s
    return cur

MAXL = 42
def wrap2(text):
    ws = text.split(); lines = [""]
    for w in ws:
        cand = (lines[-1] + " " + w).strip()
        if len(cand) <= MAXL or not lines[-1]: lines[-1] = cand
        else: lines.append(w)
    return lines

caps = []; cur = []
def flush():
    global cur
    if cur:
        caps.append(cur); cur = []
for i, w in enumerate(words):
    sp = spk_at((w["s"] + w["e"]) / 2)
    if cur:
        prev = cur[-1]
        gap = w["s"] - prev["e"]
        text = " ".join(x["w"] for x in cur + [w])
        if sp != prev["spk"] or (gap > 0.6 and len(cur) > 1) or len(wrap2(text)) > 2 or (re.search(r"[.?!]$", prev["w"]) and len(" ".join(x["w"] for x in cur)) > 18):
            flush()
    cur.append({**w, "spk": sp})
flush()

fixes = plan.get("caption_fixes", {})
out = []
caps = [c for c in caps if c]
for k, c in enumerate(caps):
    text = " ".join(x["w"] for x in c)
    for a, b in fixes.items():
        text = text.replace(a, b)
    s = c[0]["s"]; e = c[-1]["e"] + 0.35
    if k + 1 < len(caps): e = min(e, caps[k + 1][0]["s"])
    e = max(e, s + 1.0)
    low = [x["w"] for x in c if x["p"] < 0.5]
    if not text.strip():
        continue
    parts = [text]
    if len(wrap2(text)) > 2:  # after punctuation fixes: split at the sentence boundary nearest the middle
        cands = [m.end() for m in re.finditer(r"[.?!] ", text)]
        if cands:
            k2 = min(cands, key=lambda x: abs(x - len(text) / 2))
            parts = [text[:k2].strip(), text[k2:].strip()]
    t0 = s
    for j, ptxt in enumerate(parts):
        t1 = e if j == len(parts) - 1 else s + (e - s) * len(ptxt) / len(text)
        out.append({"s": round(t0, 3), "e": round(t1, 3), "text": "\n".join(wrap2(ptxt)), "spk": c[0]["spk"], "lowconf": low})
        t0 = t1
# enforce no overlap
for a, b in zip(out, out[1:]):
    if a["e"] > b["s"]: a["e"] = b["s"]

dur = plan["end"]["s"] + plan["end"]["hold"]
timing = {
    "durationSec": round(dur, 3),
    "footageEndSec": plan["footageEndSec"],
    "hook": plan["hook"],
    "scenes": plan["scenes"],
    "captions": out,
    "notes": plan["notes"],
    "chapters": plan["chapters"],
    "end": {"s": plan["end"]["s"], "e": round(dur, 3), "title": plan["end"]["title"], "sub": plan["end"]["sub"]},
    "jumps": plan.get("jumps", []),
    "footageFile": plan.get("footageFile", "footage.mp4"),
    "voiceFile": plan.get("voiceFile", "voice_clean.wav"),
    "version": plan.get("version", "v01"),
}
json.dump(timing, open(ROOT / "timing.json", "w"), ensure_ascii=False, indent=1)
# SRT export (original-language subtitles)
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
with open(ROOT.parent / "out" / f"subtitles_{timing['version']}.srt", "w") as f:
    for i, c in enumerate(out, 1):
        f.write(f"{i}\n{ts(c['s'])} --> {ts(c['e'])}\n{c['text']}\n\n")
print(len(out), "captions;", sum(1 for c in out if c["lowconf"]), "with low-confidence words; duration", dur)
