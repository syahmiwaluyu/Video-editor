# VGC-FT02 — BLS lecture, Point-by-Point Explainer (16:9)

Status: **full-length preview v02, waiting for review**. Not a final export.

## Source and approved decisions
- Source: `Copy of 20261127_112144.mp4` (Google Drive, 2336×1080 HEVC 30 fps, 16:41, Samsung phone). Original untouched;
  a working copy was downloaded to the session scratchpad only.
- Slides: student's own PPTX (15 image slides), rendered to PNG in `source/public/slides/`.
  **Matric number blurred** on slide 1 and on the projector screen in the footage.
- Kept: full lecture, original order. Trim in = **0:45.3** (greeting), trim out = **16:23.4** (after "Terima kasih").
  "Action!" and pre-roll chatter removed; "Stop, stop…" after the thanks removed.
- 16:9, 1920×1080, 30 fps.
- **Cold-open teaser** (source 1:20.4–1:36.9, repeated before the lecture) + 1.6 s title card.
  ASSUMPTION: the student's reply was read as "yes". Remove with `TEASER_ON = false` in `source/src/edl.ts`.

## Treatment
- Digital framing on the single static wide shot (WIDE / MED 1.25× / CLOSE 1.5× / DEMO 1.6× / AED 1.5×). No upscale
  beyond 1.6×, no invented areas (window clamped inside the recorded frame).
- Push into the projector, crossfade to the crisp slide; spotlight (dim + teal outline) follows what is spoken;
  zoom in/out on slide regions; cut back to the presenter.
- Point label top-left (chapter / DRSABCD letter); lower thirds use the wording on the title slide.
- Quiz (slide 13): answers covered with "?" until the participants answer. Q4 answer timing is an ASSUMPTION
  (not clearly audible), revealed just before Q5.
- Subtitles: burned in, Malay as spoken, technical terms corrected where they match the slides.
  Unclear phrases are **left without subtitles** rather than guessed.
- Light grade (contrast 1.06, saturation 1.12). Audio: high-pass 80 Hz, light FFT denoise, gentle compression,
  two-pass loudnorm to −16 LUFS / −1.5 dBTP. No music, no SFX.

## Files
- `out/full_v02_raw.mp4` — full preview (not committed; large)
- `out/preview_v01_raw.mp4` — chapters 1–3 preview (not committed)
- `BLS_full_subtitles_draft.srt` — subtitles on the output timeline (reference / for correction)
- `SUBTITLE_CHECKLIST.md` — lines marked CHECK that need a human listener
- `qc/` — stills, contact sheets, blur check
- `source/src/edl.ts` — every cut, camera move, slide insert, spotlight, label (source seconds)
- `source/src/subs.ts` — subtitles (source seconds)

## Rebuild (from `source/`)
Media are not in git. Recreate them from the original video (path to your copy as `$SRC`):
```
ffmpeg -ss 44.0 -to 990 -i "$SRC" -an -filter_complex "[0:v]eq=contrast=1.06:brightness=0.01:saturation=1.12,split[a][b];[b]crop=172:16:1328:452,gblur=sigma=6[bl];[a][bl]overlay=1328:452:enable='lt(t,38)',format=yuv420p" -c:v libx264 -preset veryfast -crf 17 -g 30 -r 30 public/proxy_full.mp4
```
Audio: same `-ss 44.0 -to 990`, filters `highpass=f=80,lowpass=f=12000,afftdn=nr=10:nf=-42,acompressor=threshold=-28dB:ratio=2.5:attack=15:release=250:makeup=2`,
then two-pass `loudnorm=I=-16:TP=-1.5:LRA=11` → `public/audio_44.wav` (48 kHz stereo).
Then `npm install`, `npm run render:full`, and `python3 -I scripts/export_srt.py` after editing subtitles.
The render script points at this container's headless Chromium; change the path on another computer.

## Not verified
- **Nobody has listened to the processed audio.** Only levels were measured.
- 69 subtitle lines marked CHECK (names, course code, several clinical phrases, the spoken survival figures
  70–80 % vs 5–6 %, depth "5–6 cm"). Some sentences have no subtitle because the transcript was unclear.
- Whether the spoken clinical content matches current guidelines was **not** reviewed; only the slides were used as
  reference for spelling.
- Participants' faces (side profiles) are visible in wide shots; consent was not checked here.
- Remotion licence terms: unverified (see remotion.dev).
