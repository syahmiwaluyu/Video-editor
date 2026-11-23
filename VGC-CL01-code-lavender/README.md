# VGC-CL01 — Code Lavender (3 × 8 s, 9:16)

## NEW: stills preview v01 (from the 3 images you supplied)
`../VGC-CL01_code-lavender_stills_preview_v01.mp4`: 24 s, 1080×1920, 30 fps. **Preview only, waiting for approval.**
- Clip 1 = `assets/still1_alone.jpg` (woman in blue scrubs, seated alone). Slow push-in, darker/cooler grade to suggest night.
- Clip 2 = `assets/still2_support.jpg` (colleague's hand on her shoulder). Slow push-in.
- Clip 3 = `assets/still3_team.jpg` (team). Push from the centre face out to the full team by 4.3 s, then lavender title card.
- Camera moves are crops of the stills (`scripts/render_stills.py`). Where the crop is wider than 9:16, a blurred copy
  fills above and below. No pixels were AI-generated, and nobody moves or speaks.
- Music: `scripts/make_audio.py` (procedural piano + string pad, crescendo in clip 3) plus quiet room tone. **No dialogue.**
  The three Malay lines are not in this preview. They need recorded voices (yours or approved talent).

Rebuild: `python3 -I scripts/render_stills.py && python3 -I scripts/make_audio.py && MUSIC=out/music.wav bash scripts/assemble.sh ../VGC-CL01_code-lavender_stills_preview_v01.mp4`

### Issues with the supplied stills (not fixed — your call)
- **Not the same woman** in clip 1 (blue scrubs, sitting on the floor) and clip 2 (white coat, on a chair). The brief asks for one continuous character.
- Clip 1 still is **daytime, on the floor, eyes closed, head tilted up**, not night, not on a bench, not head bowed. The grade only darkens it.
- Clip 2 still: the male colleague **leans over her** rather than sitting beside her.
- Clip 3 still appears AI-generated (assumption: decorative molecule graphics on the glass, a uniform look). It includes a manikin on a bed and an
  anatomical model in the background, which the brief did not ask for. Whether the team reads as the Malay/Chinese/Indian mix you want is for you
  to judge; I can't verify it.
- **Licence unknown.** Stills 1–2 look like stock photos (assumption). Confirm you have the right to use all three in a public campaign.

## Checks performed on the stills preview
- ffprobe: 1080×1920, 30/1 fps, 720 frames, 24.000 s, H.264, tv range, AAC 48 kHz stereo.
- Loudness: −13.6 LUFS integrated, true peak −1.4 dBFS (target −14 / −1.5; 0.1 dB over on peak, acceptable for preview).
- blackdetect: 0. silencedetect (−50 dB, 0.3 s): only 0–0.3 s before the first piano note.
- Visual: `qc/contact_sheet_stills_v01.png`, `qc/stills_moves.png`, `qc/ends.png`. Fixed the first framing pass, which cut faces at the edges in clips 1–2.
- **Not checked:** nobody has listened to the music; not viewed on a phone.

---

# Original kit (for AI-generated clips)

Status: **no real footage yet.** This container cannot generate photoreal video or voices. This folder holds:

1. `PROMPT_PACK.md` — your three prompts, tightened for an AI video generator, with on-screen text removed.
2. `scripts/make_overlays.py` → `overlays/*.png` — every on-screen text plus the lavender glow and title-card layers, exact spelling.
3. `scripts/assemble.sh` — fits the three clips to 1080×1920 at 30 fps, adds text and lavender layers, joins them (24 s), loudness −14 LUFS.
4. `out/CL01_LAYOUT_TEST_placeholders.mp4` — **layout test only** on grey placeholder clips. Not a preview of the campaign.

## Workflow
1. Generate clip 1, 2, 3 with `PROMPT_PACK.md`. Save as `clips/clip1.mp4`, `clips/clip2.mp4`, `clips/clip3.mp4`.
2. From this folder:
   ```
   bash scripts/assemble.sh out/CL01_preview_v01.mp4
   ```
3. Watch it on a phone with sound. Adjust timings in `assemble.sh` if text overlaps dialogue or faces.

## On-screen copy (verbatim from the brief; edit in `make_overlays.py` → `COPY`)
| Clip | Text | Draft timing |
|---|---|---|
| 1 | Behind every adverse event, / there may be a healthcare worker / silently struggling. | 5.0–8.0 s, lavender glow from 5.6 s |
| 2 | YOU ARE NOT ALONE. | 6.0–8.0 s, light lavender glow from 4.0 s |
| 3 | CODE LAVENDER / PEER SUPPORT AFTER ADVERSE EVENTS / WE CARE. WE SUPPORT. WE HEAL TOGETHER. / Jangan berdiam diri. Hulurkan sokongan. Dapatkan bantuan. | lavender fill 4.3 s, then staggered 5.0 / 5.4 / 5.9 / 6.4 s → 8.0 s |

## Risks and assumptions to confirm
- **Reading time is tight.** Clip 1 line (79 characters) gets 3 s. In clip 3 the CTA stays on screen for only 1.6 s. Suggest holding the final title card
  for 2–3 s more (total ~26–27 s), or extending clip 3. Not done because you specified 8 s.
- **No helpline or contact in the CTA.** "Dapatkan bantuan" does not say where to get help. Consider adding your hospital's real
  Code Lavender channel. I have not invented one.
- Text mixes English and Malay, as in your brief. Kept verbatim.
- Colours (#4A3078 deep lavender, #B59ADE lavender, #F0E8FC light) and font Inter (SIL OFL 1.1) are my choices; no brand file was supplied.
- Characters' tudung, glasses and clothing details in the prompt pack are my additions for consistency.
- Hard cuts between clips; no crossfade.
- If you use a real hospital's name, logo or staff likeness, get permission first. AI-generated "real-looking" staff in an official-looking
  campaign: whether you must label it as AI-generated depends on your institution's rules and the platform. I don't know your institution's rules.

## Checks performed (placeholder layout test only)
- ffprobe: 1080×1920, 30 fps, H.264 + AAC, 24.0 s.
- Visual: contact sheet `qc/contact_sheet_v01.png`, final frame `qc/title_card_final_frame.png`. Text spelled as in brief, inside x ≈ 110–970 / y ≈ 520–1435.
  The first render had a low-contrast subtitle. Fixed (white text + soft shadow, dimmer centre glow).
- blackdetect: 0 segments.
- Audio path: placeholders are silent, so loudnorm was skipped by the fallback. **Loudness mastering not tested with real audio.**

## NOT checked
- Any real footage, faces, lip-sync, Malay pronunciation, music. Text legibility on real (busy) footage. Phone and platform UI.
