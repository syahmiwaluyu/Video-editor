# VGC-CL01 Code Lavender: generator prompt pack (v01)

Paste these into the AI video generator you use, one 8-second clip at a time, in 9:16 format.
They are your brief, tightened for consistency. **All on-screen text has been taken OUT of the generator prompts.**
It is added afterwards by `scripts/assemble.sh` so the spelling is exact (generators often misspell text).
The dialogue is unchanged, word for word.

If your tool supports a reference image or "ingredients", generate the two doctors as stills first (character
sheets below), approve them, then attach those images to every clip. Reusing the same text block alone does not
guarantee the same face across clips.

---

## Locked identity (paste at the start of every clip)

```
CHARACTER A — female doctor: Malaysian Malay woman, early-to-mid 30s, warm medium-brown skin, oval face, dark brown eyes,
neutral makeup, dark hair fully covered by a plain light-grey tudung (hijab) tucked into the collar, modest long-sleeved
navy-blue undershirt under ceiling-blue short-sleeved medical scrubs, white lanyard with a plain blank ID badge (no
readable text, no logo), black slip-on clinic shoes.
CHARACTER B — male doctor: Malaysian man, mid-30s, short neat black hair, clean-shaven, light-brown skin, rimless
glasses, white doctor's coat over a light-blue collared shirt and dark trousers, plain blank ID badge on the coat
pocket (no readable text, no logo), stethoscope around the neck.
SETTING — modern Malaysian government hospital ward corridor at night: polished cream vinyl floor, pale-green and white
walls, wooden handrail along the wall, row of grey steel waiting chairs/bench, closed ward doors, cool fluorescent
ceiling panels with a few dimmed, distant nurse station glow at the far end, a figure walking past far in the background,
out of focus. No signage with readable text, no logos.
STYLE — ultra-realistic, cinematic, 35 mm look, shallow depth of field, soft film grain, natural skin texture, realistic
subtle facial acting, no exaggerated emotion. Vertical 9:16. No on-screen text, no subtitles, no captions, no
watermark, no logos.
```

> Assumption: the tudung, glasses and colours are my choices to make the characters easier to keep consistent.
> Your brief only says "modest blue scrubs" and "professional hospital attire". Change them if you want, but keep them
> identical across clips.

---

## Clip 1 (8 s): "Behind every adverse event"

```
[paste LOCKED IDENTITY]

SCENE: Night. Character A sits alone on the steel bench in the quiet corridor, head slightly bowed, hands clasped
between her knees, emotionally exhausted and reflective, eyes glistening but no crying. Subtle background activity
far down the corridor, out of focus. No patients, no blood, no medical equipment in distress, nothing graphic.

CAMERA: 0–3 s wide establishing shot, symmetrical corridor, she is small in frame on the bench. 3–8 s slow, steady
dolly forward ending on a medium close-up of her face and shoulders, face in the upper half of the frame.
Shallow depth of field, cool fluorescent light with soft warm practical light on her face.

DIALOGUE (Bahasa Melayu, natural Malaysian accent, soft whisper, around 4.5–6.5 s, lips barely moving):
"Adakah aku sudah melakukan yang terbaik?"

AUDIO: soft emotional solo piano, quiet hospital ambience (distant ventilation hum, faint footsteps far away),
no dramatic sound effects, no music swell.

ENDING: in the last 1.5 s the image softly fades into a gentle lavender-purple glow. Keep the lower third of the
frame calm and uncluttered (text will be added there later).
```

## Clip 2 (8 s): "YOU ARE NOT ALONE"

```
[paste LOCKED IDENTITY]

SCENE: Continuation of the previous shot, same corridor, same bench, same lighting, same clothes. Character A is
seated with head bowed. Character B walks in gently from the right, sits beside her, and places a reassuring hand on
her shoulder. She slowly looks up at him. They share a warm, understanding look; she gives a small tired smile.
Restrained, natural acting.

CAMERA: start with a medium side shot of both on the bench, slow push-in to a medium two-shot that captures the hand
on the shoulder and both faces. Soft lavender light gradually enters the scene from the end of the corridor.

DIALOGUE (Bahasa Melayu, natural Malaysian accent, gentle and sincere):
Character B, around 2–4.5 s: "Kita hadapi bersama. Awak tidak keseorangan."
Character A, softly, around 5–6 s: "Terima kasih."

AUDIO: warm, uplifting piano that slowly builds, quiet hospital ambience under the dialogue.

ENDING: in the last 2 s the corridor becomes brighter and warmer, with a subtle lavender-purple light. Keep the lower
middle of the frame uncluttered (text will be added there later).
```

## Clip 3 (8 s): "Code Lavender" launch

```
[STYLE and SETTING lines from LOCKED IDENTITY, but daytime, bright modern hospital atrium/lobby]
Optionally include Characters A and B in the team, in the same clothes.

SCENE: a diverse team of 8–10 Malaysian healthcare professionals (Malay, Chinese and Indian, women and men, doctors in
white coats and nurses in uniform, some in tudung) stand together confidently in a semi-circle facing the camera.
Warm, compassionate, united expressions. Soft lavender light gradually illuminates the background. Prestigious,
hopeful atmosphere like an official hospital programme launch. No logos, no banners, no readable signage.

CAMERA: 0–1.5 s medium shot moving across individual faces, 1.5–4 s smooth pull-back revealing the whole team,
4 s onwards a powerful symmetrical wide shot, held steady.

DIALOGUE (Bahasa Melayu, all together, strong, confident and clear, around 1.5–4 s):
"Kita saling menyokong. Kita tidak bersendirian!"

AUDIO: inspirational orchestral music with a gentle uplifting crescendo, peaking around 5 s and resolving by 8 s.

ENDING: from about 4.5 s, lavender light floods and fills the frame. Do not generate any text or title card.
```

---

## Things to check in each generated clip before assembling
- Same faces, tudung, glasses and clothes in clips 1–2 (and 3 if the doctors appear).
- Hands (fingers, the hand on the shoulder), badges blank, no fake text or logos anywhere in the frame.
- Malay pronunciation and lip-sync. Listen with a native speaker. Regenerate rather than "fixing" a wrong line.
- Clip 1: dialogue finishes before ~5.0 s (the text appears at 5.0 s). Clip 3: chant finishes before ~4.3 s.
  If not, change the timings in `scripts/assemble.sh`.
