"""Export src/subs.ts to SRT on the OUTPUT timeline of BLS-Full, plus a CHECK list.
Usage (from source/): python3 -I scripts/export_srt.py"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
subs = root / "src" / "subs.ts"
edl = (root / "src" / "edl.ts").read_text()
num = lambda name: float(re.search(rf"{name}\s*=\s*([\d.]+)", edl).group(1))
teaser_on = "TEASER_ON = true" in edl
T_IN, T_OUT = map(float, re.search(r"TEASER = \{ in: ([\d.]+), out: ([\d.]+) \}", edl).groups())
TITLE, L_IN, L_OUT = num("TITLE_CARD_SEC"), num("LECTURE_IN"), num("LECTURE_OUT_FULL")
FPS = 30
pre = (round((T_OUT - T_IN) * FPS) + round(TITLE * FPS)) / FPS if teaser_on else 0.0
rows = []
for line in subs.read_text().splitlines():
    m = re.search(r't0: ([\d.]+), t1: ([\d.]+), text: "((?:[^"\\]|\\.)*)" \}(.*)', line)
    if m:
        rows.append((float(m[1]), float(m[2]), m[3].replace('\\"', '"'), "CHECK" in m[4], m[4].split("//")[-1].strip()))
def ts(x):
    ms = round(x * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
out, checks = [], []
def add(a, b, text):
    out.append(f"{len(out)+1}\n{ts(a)} --> {ts(b)}\n{text}\n")
for t0, t1, text, chk, note in rows:
    if teaser_on and t0 >= T_IN and t1 <= T_OUT:
        add(t0 - T_IN, t1 - T_IN, text)
for t0, t1, text, chk, note in rows:
    if t0 >= L_IN and t1 <= L_OUT:
        a, b = pre + t0 - L_IN, pre + t1 - L_IN
        add(a, b, text)
        if chk:
            checks.append(f"- output {ts(a)[:8]} | sumber {int(t0//60)}:{t0%60:04.1f} | \"{text}\"  ({note})")
(root.parent / "BLS_full_subtitles_draft.srt").write_text("\n".join(out), encoding="utf-8")
(root.parent / "SUBTITLE_CHECKLIST.md").write_text(
    "# Subtitle yang perlu didengar & disahkan\n\nDraf daripada transkripsi automatik. Betulkan dalam `source/src/subs.ts` (masa sumber) atau terus dalam SRT.\n\n"
    + "\n".join(checks) + "\n", encoding="utf-8")
print(len(out), "cues;", len(checks), "to check")
