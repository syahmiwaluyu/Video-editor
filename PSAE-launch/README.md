# Peer Support After Adverse Events — launch video (PREVIEW v01)

Status: **preview only, waiting for approval**. Not a final export.

## What it is
- 1920×1080, 30 fps, 60.0 s (1800 frames). Photo-led motion piece, **no voice-over** (none supplied; no TTS used).
- Source: the 20 photos in the shared Drive folder (event "Awareness on Peer Support After Adverse Events:
  A Focus on Second Victim", 23 November 2026, Auditorium, Hospital Putrajaya — read from the banner in the photos).
- Visual theme: Elegant Lavender (deep plum, lavender, soft lilac, pale lavender, silver and champagne accents),
  as briefed. Colours live in `source/src/theme.ts`.

## Structure
| Time | Scene | Grade | Photos |
|---|---|---|---|
| 0–7.2 s | Opening on plum gradient + particles | — | none |
| 7.2–18 s | Emotional | muted lavender, desaturated, heavy vignette | role-play still (cinematic band), "Recognising signs of distress" slide |
| 18–32 s | Awareness | warming gradually | hall, speaker at podium, audience, speaker on stage |
| 32–48 s | Peer support | warmer lavender + soft champagne light | audience session, peer-support slide, smiling speaker, balloon arch, group photo with banner |
| 48–60 s | Title reveal | deep lavender/plum, silver serif type, glowing particles | none |

Transitions are crossfades with a soft lavender light sweep. Each photo has a slow push-in (1.00 → 1.07).

## On-screen copy (edit in `source/src/theme.ts` → `copy`)
Taken from the event materials in the photos (verbatim):
- "Recognising signs of distress" (slide, WA0174)
- "23 November 2026 · Auditorium, Hospital Putrajaya" and the title "Awareness on Peer Support After Adverse Events" / "A Focus on Second Victim" (banner, WA0214/WA0198)
- "We support. We care. We heal." (banner tagline, WA0214)

**DRAFT — written by the editor, not supplied, need approval:**
- "Behind every adverse event, / there is a healthcare worker who carries it too."
- "The second victim." / "Often unseen. Often unspoken."
- "No one should carry it alone."

## Assumptions to confirm
- Length 60 s and 16:9 were **my choice**; no duration or format was given.
- The "programme title" for the final reveal is assumed to be the event title on the banner. If the programme has
  a different official name, tagline or logo, send it and it will replace this.
- No logos are used (hospital, ministry, UM, collaborators): no logo files were supplied, and I did not lift them from photos.
- Photos left out on purpose: `IMG20261123083230.jpg` (behind-the-scenes selfie at an editing desk),
  the screenshot of the earlier VGC-FT01 ad, the second hall-wide shot, the registration desk, the token-of-appreciation
  photo and two audience shots (only so the cut stays at 60 s — easy to swap in, see `timing.json` → `shots`).
- The role-play still is a 1080×610 frame; it was cropped to remove letterbox bars and the burned-in subtitle and
  is shown as a cinematic band because it is too low-resolution to fill the frame sharply.
- Phone-camera watermark strips ("NOTE 40 …") were cropped off WA0180 and WA0181.
- Consent: the photos show identifiable staff and attendees. **I don't know** whether consent for use in a published
  video exists — please confirm before release.

## Audio
Procedural only (`source/scripts/make_audio.py`, numpy, fixed seed): soft pad + piano-like notes at 72 BPM,
Bm–G–D–A in the reflective half, warmer and fuller in the peer-support half, filtered-noise swells into each scene,
a chime cluster on the title. Mastered to −16 LUFS integrated (calmer than a social ad).

## Rebuild (from `source/`)
```
npm install
# photos are not committed; put the prepared JPGs in source/public/photos/ (names listed in timing.json → shots)
python3 -I scripts/make_audio.py
npm run render
bash scripts/finalize.sh ../PSAE_launch_preview_v01.mp4
```
Photo prep (crop/resize) was a one-off Pillow step: EXIF rotate, crop bars, max width 2560.
Raw photos are git-ignored (`source/public/photos/`) so the attendees' photos are not stored in the repo as separate files.

## Files
- `PSAE_launch_preview_v01.mp4` — preview
- `out/` — muted render, raw and mastered audio
- `qc/` — contact sheet
