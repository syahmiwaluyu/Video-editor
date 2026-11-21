# VGC-FT01 — Simulation (8 s motion ad, PREVIEW v01)

Status: **preview only, waiting for approval**. Not a final export.

## Brief as used
- 1920×1080, 30 fps, 8.0 s (240 frames). 100% motion, text-led, **no voice-over** (no VO supplied; no TTS used).
- Objective: Awareness–Edutainment. Audience: healthcare staff (chosen by the student).
- Topic source: a Drive video (role-play/simulation conversation). Only the Drive transcript snippet was read.
  **No video frames or audio from it were viewed or used.**
- Visual direction: Playful Vector Explainer, toned down for a sensitive topic (calm motion, modest squash-and-stretch on graphics only).

## On-screen copy (edit in `source/src/theme.ts` → `copy`)
1. Hook (0–2.4 s): "Pesakit tak dapat diselamatkan." + ECG line that goes flat
2. Explain (2.4–4.8 s): chips "Rasa bersalah", "Susah tidur" → accent box "Itu bukan tanda lemah."
3. Takeaway/CTA (4.8–8.0 s): "Anda manusia dahulu." + "Bercakaplah dengan seseorang yang anda percaya."

Assumptions to confirm:
- **CTA wording is a DRAFT.** No CTA text was supplied.
- The 5-part awareness flow (Hook → Persoalan → Penerangan → Contoh → Takeaway) is **compressed into 3 beats** to fit 8 s. "Persoalan" is only implied.
- Chip and statement wording is adapted from ideas in the role-play transcript (guilt, poor sleep, "not weak"). These are not statistics or clinical claims.
- Colours are the visual-direction defaults (#182951 / #f6efff / #ffba50). No brand assets were supplied.
- Font: Nunito (SIL OFL, via @fontsource, bundled locally). Read the licence yourself before commercial use.

## Audio
Procedural only (`source/scripts/make_audio.py`, numpy, fixed seed): Karplus-Strong plucked synth, 96 BPM,
Bm → G → A → D, soft taps, soft pops on chips and bubbles, soft whoosh on the zoom cut, a gentle flat tone (not an
alarm) on the flatline, and a two-note confirmation tone on the CTA. Cues come from `source/timing.json`, the same file
the visuals use. No dialogue, so no ducking was needed.

## Rebuild (from `source/`)
```
npm install
python3 -I scripts/make_audio.py
npm run render
bash scripts/finalize.sh ../VGC-FT01_simulation_preview_v01.mp4
```
Remotion 4.0.545 is installed locally in `source/node_modules`. The render script points at this container's
preinstalled headless Chromium; change that path in `package.json` on another computer.

## Checks performed (on the exported MP4)
- ffprobe: 1920×1080, 30/1 fps, 240 frames, 8.000 s, H.264 High, yuv420p, BT.709 TV range tagged, AAC-LC 48 kHz stereo 256 kb/s, faststart.
- Loudness (ebur128): −14.0 LUFS integrated, true peak −1.7 dBFS. No silence > 0.3 s below −50 dB.
- blackdetect: 0 black segments.
- Visual: contact sheet every 0.5 s and frame strips around both cuts (`qc/`). Text matches `copy`; no overflow or overlap seen; no placeholder text on screen.
- Colour: background measured 22,39,79 vs design 24,41,81 (a few /255).

## NOT checked / unverified
- **Nobody has listened to the audio yet.** Only levels were measured.
- Not tested on a phone screen or in any platform app.
- Remotion licence terms: **unverified**, check remotion.dev.
- Whether topic, tone and CTA suit the real audience and the sensitivity of the subject.

## Files
- `VGC-FT01_simulation_preview_v01.mp4` — preview
- `out/` — muted render, raw mix, mastered mix
- `qc/` — contact sheet and cut strips
- `archive/` — earlier v01 mux with a colour-range error (kept, not overwritten)
