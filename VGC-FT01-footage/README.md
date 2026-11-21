# VGC-FT01 — Edit Footage (Fast Track) · PREVIEW v01

Status: **preview, waiting for approval.** Not a final export. No cuts applied yet.

## Source
- `VID20261120154047.mp4` from Google Drive (2,595,744,183 bytes, matches Drive metadata). Downloaded to
  `/home/user/vgc_src/` **outside the repo**; the original was not modified. Only a working proxy
  (`source/public/footage.mp4`, git-ignored, 30 fps CFR, BT.601 full range → BT.709 TV range) is used for rendering.
- Probe: 2520×1080 (21:9 phone, recorded upside-down; rotation flag −180° auto-applied), ~30 fps VFR, 515.7 s,
  AAC 48 kHz stereo (both channels identical = effectively mono).
- One static wide shot: two people at a table, laptop in the middle. No B-roll, logo, VO or music supplied.

## Content (what the footage is)
A role-play conversation between Farhan (left, purple scrubs; the dialogue refers to him as an anaesthesiologist and to the operation theatre) and a
supporter (right, hijab) after a patient died unexpectedly during resuscitation. **The dialogue is in English**, not
Malay (measured: English decoding confidence −0.27 vs Malay −0.46 avg log-prob on the same clip; the Malay pass was a
machine translation, not the spoken words).

## Brief as used (assumptions marked)
- 16:9, 1920×1080, 30 fps. Target 480 s. Audience: healthcare workers.
- **Objective: assumed Awareness–Edutainment** (field was left as a template placeholder). Flow mapped onto the
  recorded conversation without reordering: Hook overlay → chapters 01–06 → takeaway card.
- **Topic / product: not supplied** (placeholder). No product, offer or price shown.
- **CTA: not supplied** (placeholder). The end card has a takeaway only, **no CTA**. Text paraphrases two lines that
  are spoken in the footage: "sometimes we forget that we also need care" (≈461 s) and "Seeking support is not a sign
  of incompetence" (≈323 s).
- **Brand: none supplied.** Temporary theme = visual-direction defaults: paper #e9dfc9, ink #22211f, accent #e95632.
  Fonts Archivo (headlines/captions) + Caveat (marker annotations), both SIL OFL 1.1 via @fontsource, bundled locally.
- Speaker label for the person on the right = **"Penyokong"** (her role/name is never stated; she says "I'm here to
  listen and support you"). Change in `source/src/theme.ts`.

## Editing choices (Scrapbook Documentary, adapted to one static wide shot)
- Three compositions, switched by meaning, never stretched (every crop keeps its aspect ratio):
  1. **Photo print** – 16:9 two-shot as a taped print on warm paper, subtitles underneath.
  2. **Speaker card** – 4:5 print of whoever is talking + one marker annotation + subtitles in the free column.
  3. **Full frame** – full-bleed two-shot with subtitles on a torn paper strip (used for heavier moments).
- Stop-start paper entrances (move · short hold · settle), slow 4% push in every scene, hard cuts otherwise.
- 6 chapter labels (BM), 20 marker annotations (BM) describing what is said / the support technique heard at that
  moment. **These labels are editorial interpretation — please review the wording** (`source/edit_plan.json`).
- Subtitles: original English, verbatim from ASR, max 2 lines × 42 chars, also exported as `out/subtitles_v01.srt`.
- Hook overlay (0–5.4 s, on the empty table area, no faces covered): "Pesakit tak dapat diselamatkan." /
  "Bagaimana pula petugasnya?" – based on what Farhan says at 55–63 s.

## Audio
- Original dialogue kept, not regenerated, not sped up. Cleanup chain on a copy: high-pass 80 Hz, light FFT denoise,
  −2.2 dB @245 Hz, +2.5 dB @3.3 kHz, +1 dB shelf @9 kHz, 3:1 compression. The chain delayed the voice by 1192
  samples (24.8 ms, measured by envelope cross-correlation); this is compensated.
- Procedural soundtrack (numpy/scipy, fixed seed, no samples): 74 BPM, original Fmaj7–Dm7–B♭maj7–Csus progression,
  soft felt-pluck motif + pad, brushed-noise percussion from the end of the hook, resolve chord on the end card.
- SFX: dry paper rustle on composition changes, small paper tick on chapter labels and annotations, one paper accent
  per hook line. Cue times come from `source/timing.json` (same file as the visuals).
- Ducking driven by the voice envelope: music −14 dB while speaking (measured median 21.5 dB under the voice),
  SFX −3 dB. Master: two-pass loudnorm −14 LUFS, true-peak target −1.5 dBTP, then limiter.

## Cut proposal to reach 480 s (NOT applied — needs your approval)
Source + end card = 518.0 s. `out/cut_proposal_v01.csv` lists **38 pauses** (source timecodes) that would be
shortened to 1.2 s each → **≈479 s**. No words removed, order unchanged. Pauses in an emotional conversation carry
meaning; you may want to keep some of the longest ones (e.g. 176–179 s after "…not competent", 471–474 s).

## Rebuild (from `source/`)
```
npm install
bash scripts/prep_voice.sh /path/to/VID20261120154047.mp4
python scripts/build_timing.py      # needs ../work/transcript.json
python scripts/make_audio.py        # numpy + scipy
npm run render
bash scripts/finalize.sh ../VGC-FT01_footage_preview_v01.mp4
```
Proxy: `ffmpeg -i ORIGINAL.mp4 -an -vf "fps=30,scale=2520:1080:in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p" -c:v libx264 -crf 17 -g 10 source/public/footage.mp4`. Transcription used faster-whisper large-v3 (CPU, int8)
in a local virtualenv (`/home/user/vgc_venv`, outside the repo). Render script points at this container's headless
Chromium; change the path in `package.json` on another computer.

## Files
- `VGC-FT01_footage_preview_v01.mp4` – review copy (2-pass ~1.25 Mb/s, 92 MB so it fits in git; −14.0 LUFS, peak −1.3 dBFS; text checked sharp at 300 s).
- `VGC-FT01_footage_preview_v01_master.mp4` – CRF 16 master of the same preview (≈410 MB, git-ignored, local only).
- `out/subtitles_v01.srt`, `out/cut_proposal_v01.csv`, `out/audio_cues.json`.
- `source/` editable project: `src/Main.tsx` (compositions), `src/theme.ts` (colours, fonts, crops, speaker names),
  `edit_plan.json` (turns, scenes, notes, chapters, hook, end card, caption fixes), `timing.json` (generated),
  `scripts/` (voice prep, timing, audio, finalize).
- `work/transcript.json` (word-level ASR), `qc/` (contact sheet, cut strips, stills).

## Checks actually performed (on the exported master MP4 unless noted)
- Specs: 1920×1080, 30 fps CFR, H.264 yuv420p, BT.709 TV range tagged, AAC 48 kHz stereo, 518.0 s.
- Loudness: −14.0 LUFS integrated; peak −1.4 dBFS (0.1 dB above the −1.5 dBTP target after AAC encoding). No clipping.
- Music vs voice (pre-master stems): music median 21.5 dB under the voice while speaking (5th percentile 7.5 dB).
- Sync: final audio vs original audio cross-correlation = 5 ms lag at 40 s, 250 s, 480 s (AAC priming).
- Clarity: re-transcribed the final mix at 0–36 s, 160–190 s, 455–513 s with the same ASR; wording matched the
  source transcript (the music did not change any recognised word in those samples).
- Colour: wall and scrubs patches compared source vs output frame at 20 s – within ~4 levels (no colour shift).
- Visual: contact sheet every 4 s (`qc/contact_sheet_v01.jpg`) and frames −2/0/+1/+3 around all 49 scene cuts
  (`qc/cut_strips_v01_*.jpg`): no black or empty frames found; captions max 2 lines × 42 chars, no caption overlaps
  in timing data; hook and labels do not cover faces in the stills checked.

## NOT verified – please check
- **I did not listen to the audio.** Only measurements and ASR were used. Please listen to the whole mix, especially
  whether the music/paper SFX feel appropriate for this sensitive topic.
- **Speaker attribution is inferred from content**, not diarisation (both mics are mixed to one channel). The last
  "Okay, thank you." / "Thank you." (510–513 s) attribution is a guess.
- **Subtitles are ASR, not human-verified.** Doubtful lines (left verbatim, please confirm):
  18 s "I **can** stop thinking about that case" (meaning would reverse if it is "can't"); 30 s "…do this thing to
  me…"; 47 s "Even the procedure has ended."; 307 s "Maybe to **render** whether you are ready…"; 418 s "we try
  **not** to recognize them without judging yourself". Corrections applied: "Everything is fine." at 55 s removed
  (did not reappear on re-transcription); "Hoi Han"/"for Han" → "Farhan"; 242 s "I almost call in sick tomorrow";
  500 s "lighter"; 509 s "I really need that support." (from the first pass). 25 captions contain words the ASR
  scored < 0.5 confidence (listed in `source/timing.json` → `lowconf`).
- Annotation and chapter wording (BM) is my editorial reading of the conversation.
- Third-party marks visible in the real footage (laptop brand, lanyard print) were left as recorded – decide if you
  want them softened.
- Remotion licence terms, font licences and in-app platform playback were not verified.
