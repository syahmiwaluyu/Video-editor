// Edit decision list. ALL times are SOURCE seconds of
// "Copy of 20261127_112144.mp4" unless stated otherwise.

// ---------- switches ----------
// Cold-open teaser (repeat of the scenario clip before the lecture starts).
// ASSUMPTION: student's reply was read as "yes"; set false to remove it.
export const TEASER_ON = true;

// Approved trims: start at the greeting, end after "Terima kasih".
export const LECTURE_IN = 45.3;
export const LECTURE_OUT_FULL = 982.9;
// Preview v01 covers chapters 1-3 only.
export const PREVIEW_OUT = 160.3;

export const TEASER = { in: 80.4, out: 96.9 };
export const TITLE_CARD_SEC = 1.6;

// ---------- camera (digital framing on the static wide shot) ----------
// cx, cy = centre of the window in source pixels; z = zoom (1 = 1920 px wide window).
export type Shot = { cx: number; cy: number; z: number };
export const SHOTS = {
  WIDE: { cx: 1168, cy: 540, z: 1 },
  MED: { cx: 1240, cy: 520, z: 1.25 },
  CLOSE: { cx: 1010, cy: 560, z: 1.5 },
  SCREEN: { cx: 1440, cy: 345, z: 3.0 }, // only used underneath a slide fade
} satisfies Record<string, Shot>;
export type ShotName = keyof typeof SHOTS;

// Each key: at time t start easing to shot over dur seconds (default 0.5).
export const CAMERA: { t: number; shot: ShotName; dur?: number }[] = [
  { t: 0, shot: "WIDE" },
  { t: 46.0, shot: "MED", dur: 2.5 }, // slow settle after the greeting
  { t: 58.3, shot: "CLOSE" }, // self-introduction
  { t: 79.6, shot: "MED" },
  { t: 80.4, shot: "CLOSE", dur: 0.6 }, // "apabila berlakunya kecemasan"
  { t: 85.0, shot: "SCREEN", dur: 0.5 }, // push into the projector -> slide 2
  { t: 97.3, shot: "WIDE", dur: 0.01 }, // after slide 2: room + participants answering
  { t: 111.0, shot: "MED" },
  { t: 112.9, shot: "SCREEN", dur: 0.5 }, // -> slide 3
  { t: 158.6, shot: "MED", dur: 0.01 },
];

// ---------- slide inserts (crisp images from the student's PPTX) ----------
// rect = [x, y, w] in 1280x720 slide units; height follows 16:9.
export type Focus = { t: number; rect: [number, number, number] };
export type Spot = { t0: number; t1: number; box: [number, number, number, number] };
export type Insert = { slide: number; in: number; out: number; focus: Focus[]; spots: Spot[] };

const FULL: [number, number, number] = [0, 0, 1280];

export const INSERTS: Insert[] = [
  {
    // "Situasi kecemasan" — each bullet lights up as it is spoken.
    slide: 2,
    in: 85.4,
    out: 97.3,
    focus: [
      { t: 85.4, rect: FULL },
      { t: 85.6, rect: [200, 50, 1070] },
    ],
    spots: [
      { t0: 85.7, t1: 88.6, box: [548, 252, 664, 88] }, // seorang lelaki dewasa rebah di klinik
      { t0: 88.7, t1: 91.5, box: [548, 355, 664, 86] }, // tidak responsif, tidak bernafas
      { t0: 91.6, t1: 94.5, box: [548, 458, 664, 86] }, // anda petugas kesihatan
      { t0: 94.6, t1: 97.3, box: [548, 560, 664, 86] }, // apakah tindakan pertama
    ],
  },
  {
    // "Objektif pembelajaran" — one card at a time.
    slide: 3,
    in: 113.3,
    out: 158.6,
    focus: [
      { t: 113.3, rect: FULL },
      { t: 115.4, rect: [0, 115, 960] }, // card 1
      { t: 128.6, rect: [160, 115, 960] }, // card 2
      { t: 147.8, rect: [320, 115, 960] }, // card 3
      { t: 157.6, rect: FULL },
    ],
    spots: [
      { t0: 115.6, t1: 121.1, box: [62, 180, 366, 470] }, // card 1
      { t0: 121.2, t1: 128.5, box: [62, 475, 366, 175] }, // card 1 detail
      { t0: 128.8, t1: 134.9, box: [457, 180, 366, 470] }, // card 2
      { t0: 135.0, t1: 147.7, box: [457, 475, 366, 175] }, // card 2 detail
      { t0: 148.0, t1: 152.8, box: [852, 180, 366, 470] }, // card 3
      { t0: 152.9, t1: 157.5, box: [852, 475, 366, 175] }, // card 3 detail
    ],
  },
];

// ---------- point label (top-left) ----------
export const LABELS: { t: number; num?: string; text: string }[] = [
  { t: 0, text: "Basic Life Support untuk Petugas Kesihatan" },
  { t: 80.4, num: "!", text: "Situasi kecemasan" },
  { t: 111.0, num: "1", text: "Objektif · Urutan Adult BLS (DRSABCD)" },
  { t: 128.6, num: "2", text: "Objektif · CPR berkualiti tinggi" },
  { t: 147.8, num: "3", text: "Objektif · Penggunaan AED yang selamat" },
  { t: 158.6, num: "✓", text: "Objektif pembelajaran" },
];

// ---------- lower thirds (wording copied from the title slide) ----------
export const LOWER_THIRDS: { t0: number; t1: number; title: string; sub: string }[] = [
  { t0: 59.0, t1: 66.0, title: "Muhammad Syahmi bin Mohd Sani", sub: "Penceramah · Bachelor of Medical and Health Science with Honour" },
  { t0: 66.2, t1: 72.8, title: "NBMH4143", sub: "Teaching for Healthcare Personnel" },
  { t0: 72.9, t1: 79.5, title: "Sir Sivabalan A/L Rajagopal", sub: "Tutor" },
];
