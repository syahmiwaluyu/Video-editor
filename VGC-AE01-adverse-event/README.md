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

---

# Gemini cut v01 — A → B → C joined (16:9, ~29.5 s)

File: `VGC-AE01_gemini_cut_v01.mp4`. Build: `bash source/scripts/build_gemini_cut.sh` (usage in the script header).
Sources (the user's Gemini outputs, copied unchanged to `source/assets/gemini/`): each is 1280×720, 24 fps, 10 s.

| Output time | Source | Notes |
|---|---|---|
| 0.0–10.0 s | A `A_alone_whisper.mp4` 0–10 s | Burned-in subtitle (frames 121–178, 5.04–7.46 s) covered with `delogo` over x306–980, y626–680 |
| 9.5–10.0 s | dissolve A → B (0.5 s) | |
| 10.0–18.5 s | B `B_colleague_support.mp4` 1.0–10 s | First 1 s skipped: it repeats A's opening wide shot |
| 18.0–18.5 s | dissolve B → C (0.5 s) | |
| 18.5–29.5 s | C `C_team_code_lavender.mp4` 0–10 s | Last 1.5 s (end card) at half speed (frame-blended), so the end card is readable for ~3 s |

Decisions confirmed by the user: order A → B → C, keep 16:9, softly cover the subtitle.
**Change from the agreed plan:** I said I would trim each clip's lavender ending (target ~22–25 s). I did **not** trim
the A and B cards: Gemini's cards are only fully readable for ~1.0–1.25 s, so cutting them would make the text
unreadable. The only cut is B's repeated first second. Ask if you want a shorter version anyway.

Audio: each clip's own Gemini audio, gain-matched to −20 LUFS, joined with 0.5 s crossfades. C's slowed tail uses
`atempo=0.5` (pitch kept). Master: two-pass loudnorm + limiter, 0.4 s fade-out.
Video: re-encoded H.264 High, 24 fps (kept the source rate; not converted to 30), BT.601 → BT.709 matrix, tagged.

## Checks performed (Gemini cut)
- ffprobe: 1280×720, 24 fps, 707 frames, 29.48 s, H.264 High, BT.709 tagged, AAC 48 kHz stereo, 13.7 MB.
- Loudness: −14.6 LUFS integrated (the limiter pulled it 0.6 LU under target), true peak −1.7 dBFS.
- silencedetect (−50 dB, 0.3 s): none. blackdetect: none.
- Visual: 1 fps contact sheet and stills at 5.5 s and 6.8 s (`qc/gemini/`). Subtitle no longer visible; a faint smooth patch remains.

## NOT checked (Gemini cut)
- **Audio not listened to, and not transcribed** (no speech-recognition tool here). I don't know whether the Gemini
  audio really contains the whisper "Adakah aku sudah melakukan yang terbaik?", or what B/C say, if anything.
- How the slowed C tail sounds (time-stretched music can warble).
- The on-screen text in B and C was written by Gemini, not by you: "YOU ARE NOT ALONE", "CODE LAVENDER — PEER SUPPORT
  AFTER ADVERSE EVENTS — WE CARE. WE SUPPORT. WE HEAL TOGETHER. — Jangan berdiam diri. Hulurkan sokongan. Dapatkan
  bantuan." Confirm that your hospital actually runs a Code Lavender / peer-support programme before publishing. The CTA
  gives no contact point.
- Usage terms for Gemini-generated video in your context: unverified.
- Not tested on a phone or in any platform app.
