# VGC-AE01 — Adverse event awareness (8 s, 9:16, PREVIEW v01)

Status: **preview only, waiting for approval.** Not a final export.

## What this is (and is not)
- Built from **one supplied still photo** (`source/assets/doctor_still.jpg`) using a simulated camera move.
  **No AI video was generated**: this session has no video-generation model, and the person is not animated.
- The photo does not match every part of the brief:
  - she sits **on the floor** against a glass wall, not on a bench
  - her head is **tilted up with eyes closed**, not bowed with hands clasped
  - it is **daytime/bright** in the original. The grade darkens and cools it, but it is not a true night scene
  - **no ID badge** is visible, and nothing in the photo shows it is a Malaysian government hospital
  - she has no lip movement, so she cannot be shown speaking
- **No voice.** The line "Adakah aku sudah melakukan yang terbaik?" is **not** in the audio: there was no recording,
  and no TTS was approved. A gap is left for it at **2.6–4.2 s** (the piano gets quieter there).

## Timeline (30 fps, 240 frames)
| Time | Picture | Audio |
|---|---|---|
| 0.0–4.5 s | Wide on the corridor (right side of the photo: her shoes, the floor, the lit wall). The camera eases left and pushes into a medium close-up of her face. She faces right, so the space is left on that side | Am → F, soft piano, quiet room tone |
| 2.6–4.2 s | (dolly continues) | **Empty slot for the whispered line** |
| 4.3–5.3 s | Picture blurs and fades into a lavender-purple glow, still faintly visible underneath | C chord resolves; room tone dips |
| 4.6–5.0 s | Text fades in (slight rise), holds to 8.0 s (~3 s readable) | melody continues, 0.35 s fade-out |

On-screen text (exactly as given): "Behind every adverse event, there may be a healthcare worker silently struggling."
I chose the line breaks (4 lines) and the italic on "silently struggling." You can change these.

## Locked look (reuse for the next clip)
In `source/scripts/render_video.py`:
- `LOOK`: exposure 0.66, RGB gain (0.90, 0.98, 1.10), saturation 0.82, highlight knee 0.55, vignette 0.42, grain 1.5
- Glow: #C9B6E8 centre to #7A5CAA edge, 76% over a 14 px blurred picture
- Text: Inter SemiBold / SemiBold Italic, 63 px, #2E1A47, centred near 46% of frame height, widest line ≤ 880 px
- Font licence: Inter is SIL OFL (system font in this container). Check the licence yourself before commercial use.

## Audio
Procedural only (`source/scripts/make_audio.py`, numpy, fixed seed): additive piano-like tones at 64 BPM, Am–F–C,
synthetic reverb, low filtered-noise room tone + 100 Hz ventilation hum. No samples, no third-party music, no SFX.

## Rebuild (from `source/`)
```
python3 -I scripts/render_video.py
python3 -I scripts/make_audio.py
bash scripts/finalize.sh ../VGC-AE01_adverse_event_preview_v01.mp4
```

## Checks performed (on the exported MP4)
- ffprobe: 1080×1920, 30 fps, 240 frames, 8.000 s, H.264 High yuv420p, BT.709 TV range tagged, AAC-LC 48 kHz stereo ~250 kb/s, faststart, 5.6 MB.
- Loudness (ebur128): −14.1 LUFS integrated, true peak −1.6 dBFS.
- silencedetect (−50 dB, 0.3 s): none. blackdetect: none.
- Visual: contact sheet every 0.5 s plus stills at 4.5 s and 7.0 s (`qc/`). Text matches the brief, sits inside the 9:16 safe area, does not overflow and does not cover the face.

## NOT checked / unverified
- **Nobody has listened to the audio.** Only levels were measured.
- Not tested on a phone or in any platform app.
- The image has no licence or source info. **Check that you have the rights to use this photo** before publishing.
- The picture is upscaled up to ~2.4× during the close-up, so it may look soft on large screens.
- Whether the tone suits healthcare staff audiences (psychological safety / second-victim framing).
