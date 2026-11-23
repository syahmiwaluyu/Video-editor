"""VGC-AE01 — combined v02: Gemini cut + compact highlight montage from BOTH event recaps.

Music: recap 1's own track only (about 60 BPM, beat period 0.998 s, first beat 0.081 s, measured
by spectral-flux autocorrelation). Shot lengths are snapped DOWN to whole half-beats, so the hard cuts
fall on the music's half-beat grid. The poster closes the video, once.

Usage (from source/): python3 -I scripts/build_montage.py ../VGC-AE01_gemini_cut_v01.mp4 ../VGC-AE01_combined_v02.mp4
"""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "source" / "assets"
OUT = ROOT / "out" / "montage"
OUT.mkdir(parents=True, exist_ok=True)
R1, R2 = A / "event_recap.mp4", A / "event_recap2.mov"
BEAT, BEAT0 = 0.998, 0.081
HB = BEAT / 2
R1_END = 63.43          # end of recap 1 audio
XF = 0.75               # dissolve Gemini cut -> montage

# (label, source, in, out) — picked from 1 fps contact sheets + scene-cut times (qc/drive/*_cuts.txt)
SHOTS = [
    ("wide auditorium",          R1,  5.60,  8.40),
    ("registration desk",        R1,  9.20, 11.60),
    ("committee, balloons",      R2, 10.20, 12.00),
    ("audience",                 R2,  3.40,  5.10),
    ("speaker at podium",        R1, 12.50, 13.80),
    ("'Care for the caregiver'", R2, 21.10, 23.00),
    ("speaker in blue + slide",  R1, 16.20, 18.60),
    ("audience gesture",         R1, 20.00, 22.60),
    ("speaker + slide",          R1, 23.60, 26.00),
    ("speaker with audience",    R2, 25.20, 27.20),
    ("audience Q&A with mic",    R1, 30.30, 33.30),
    ("audience",                 R2, 30.00, 31.80),
    ("care packs",               R1, 33.80, 36.80),
    ("audience, rear view",      R1, 54.20, 57.00),
    ("token of appreciation",    R1, 41.00, 43.80),
    ("group with poster",        R2, 36.20, 38.20),
    ("full group photo",         R1, 48.20, 51.40),
]
POSTER = (R1, 59.20)    # held to the end of the music

VF = ("scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
      "setsar=1,fps=30,format=yuv420p")
VENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-r", "30"]


def run(*a):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *a], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode())


def main():
    gem, final = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    # snap shot lengths to half-beats (frames at 30 fps)
    plan = []
    for label, src, i, o in SHOTS:
        n = max(2, math.floor((o - i) / HB))
        plan.append((label, src, i, round(n * HB * 30) / 30))
    body = sum(p[3] for p in plan)
    # music start on a beat so the montage+poster ends at R1_END with a poster of >= 3.5 s
    a0 = BEAT0 + math.floor((R1_END - body - 3.5 - BEAT0) / BEAT) * BEAT
    poster = round((R1_END - a0 - body) * 30) / 30
    plan.append(("event poster (end)", POSTER[0], POSTER[1], poster))
    total = sum(p[3] for p in plan)
    print(f"montage {total:.2f}s, poster {poster:.2f}s, music from recap 1 {a0:.3f}-{a0 + total:.3f}s")

    segs, t = [], 0.0
    for k, (label, src, i, d) in enumerate(plan):
        seg = OUT / f"shot{k:02d}.mp4"
        run("-ss", f"{i:.3f}", "-i", str(src), "-t", f"{d:.4f}", "-vf", VF + ",setpts=PTS-STARTPTS",
            "-an", *VENC, str(seg))
        segs.append(seg)
        print(f"{t:6.2f}s  {d:4.2f}s  {src.stem:13s} {i:6.2f}-{i + d:6.2f}  {label}")
        t += d
    (OUT / "list.txt").write_text("".join(f"file '{s}'\n" for s in segs))
    run("-f", "concat", "-safe", "0", "-i", str(OUT / "list.txt"), "-c", "copy", str(OUT / "montage_v.mp4"))
    run("-ss", f"{a0:.3f}", "-i", str(R1), "-t", f"{total:.3f}", "-vn", "-ar", "48000", "-ac", "2",
        "-af", "afade=t=in:d=0.2", str(OUT / "montage_a.wav"))

    # Gemini cut + montage
    run("-i", str(gem), "-vf", VF, "-an", *VENC, str(OUT / "gem_v.mp4"))
    run("-i", str(gem), "-vn", "-ar", "48000", "-ac", "2", "-t", f"{dur(OUT / 'gem_v.mp4'):.4f}", str(OUT / "gem_a.wav"))

    def lufs(p):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        return float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    gg, gm = -20 - lufs(OUT / "gem_a.wav"), -20 - lufs(OUT / "montage_a.wav")
    print(f"gain: gemini {gg:+.1f} dB, montage music {gm:+.1f} dB")
    off = dur(OUT / "gem_v.mp4") - XF
    run("-i", str(OUT / "gem_v.mp4"), "-i", str(OUT / "montage_v.mp4"), "-i", str(OUT / "gem_a.wav"),
        "-i", str(OUT / "montage_a.wav"), "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={off:.4f}[v];"
        f"[2:a]volume={gg:.2f}dB[g];[3:a]volume={gm:.2f}dB[m];[g][m]acrossfade=d={XF}[a]",
        "-map", "[v]", "-map", "[a]", *VENC, "-c:a", "pcm_s16le", str(OUT / "joined.mov"))

    # master + final encode
    T = dur(OUT / "joined.mov")
    run("-i", str(OUT / "joined.mov"), "-vf", f"fade=t=out:st={T - 0.6:.3f}:d=0.6", "-af",
        f"afade=t=out:st={T - 0.6:.3f}:d=0.6", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
        "-c:a", "pcm_s16le", str(OUT / "joined_fade.mov"))
    run("-i", str(OUT / "joined_fade.mov"), "-vn", str(OUT / "mix_raw.wav"))
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(OUT / "mix_raw.wav"), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    run("-i", str(OUT / "mix_raw.wav"), "-af",
        f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
        f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
        "alimiter=limit=0.82:level=false,aresample=48000", "-ar", "48000", str(OUT / "mix_master.wav"))
    run("-i", str(OUT / "joined_fade.mov"), "-i", str(OUT / "mix_master.wav"), "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "17", "-r", "30", "-g", "60",
        "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-shortest",
        "-movflags", "+faststart", str(final))
    print(f"wrote {final} ({T:.2f}s)")


if __name__ == "__main__":
    main()
