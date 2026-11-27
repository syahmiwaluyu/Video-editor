// Edit decision list. ALL times are SOURCE seconds of
// "Copy of 20261127_112144.mp4" unless stated otherwise.
// Slide boxes are in 1280x720 slide units.

// ---------- switches ----------
// Cold-open teaser (repeat of the scenario clip before the lecture starts).
// ASSUMPTION: student's reply was read as "yes"; set false to remove it.
export const TEASER_ON = true;

// Approved trims: start at the greeting, end after "Terima kasih".
export const LECTURE_IN = 45.3;
export const LECTURE_OUT_FULL = 983.4;
// Preview v01 covered chapters 1-3 only.
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
  CLOSE_R: { cx: 1180, cy: 560, z: 1.5 }, // presenter standing right of centre
  DEMO: { cx: 1200, cy: 580, z: 1.6 }, // presenter at the manikin
  AED: { cx: 1480, cy: 540, z: 1.5 }, // presenter + defibrillator on the trolley
  SCREEN: { cx: 1440, cy: 345, z: 3.0 }, // only used underneath a slide fade
} satisfies Record<string, Shot>;
export type ShotName = keyof typeof SHOTS;
type Key = { t: number; shot: ShotName; dur?: number };

// Manual camera moves (between slide inserts).
const MOVES: Key[] = [
  { t: 0, shot: "WIDE" },
  { t: 46.0, shot: "MED", dur: 2.5 }, // slow settle after the greeting
  { t: 58.3, shot: "CLOSE" }, // self-introduction
  { t: 79.6, shot: "MED" },
  { t: 80.4, shot: "CLOSE", dur: 0.6 }, // "apabila berlakunya kecemasan"
  { t: 111.0, shot: "MED" },
  { t: 161.0, shot: "CLOSE" }, // "sebelum kita mula tu"
  { t: 209.3, shot: "CLOSE" }, // "sudden cardiac arrest, apa maksudnya?"
  { t: 309.4, shot: "MED" }, // code blue / emergency trolley
  { t: 326.4, shot: "CLOSE" },
  { t: 351.0, shot: "DEMO", dur: 0.6 }, // airway on the manikin
  { t: 409.4, shot: "CLOSE_R" },
  { t: 477.3, shot: "CLOSE" }, // "dia ada 5 elemen"
  { t: 546.2, shot: "DEMO", dur: 0.6 }, // compression demo
  { t: 582.0, shot: "MED" },
  { t: 605.6, shot: "CLOSE_R" }, // survival figures (spoken only)
  { t: 619.4, shot: "AED", dur: 0.6 }, // "contohnya ini cardiac monitor"
  { t: 682.2, shot: "AED" },
  { t: 889.4, shot: "MED" },
  { t: 893.0, shot: "CLOSE" }, // recovery position
  { t: 910.6, shot: "MED" },
  { t: 974.6, shot: "WIDE", dur: 1.2 }, // "ada apa-apa soalan"
];

// ---------- slide inserts (crisp images from the student's PPTX) ----------
export type Rect = [number, number, number]; // x, y, w (height follows 16:9)
export type Box = [number, number, number, number];
export type Insert = {
  slide: number;
  in: number;
  out: number;
  after: ShotName; // camera cut when the slide fades out
  focus: { t: number; rect: Rect }[];
  spots: { t0: number; t1: number; box: Box }[];
  covers?: { until: number; box: Box }[]; // quiz answers hidden until spoken
};

const FULL: Rect = [0, 0, 1280];
// slide 6 rows (D R S A B C D)
const row6 = (i: number): Box => [56, 188 + i * 74.6, 1164, 74];
// slide 13 quiz rows
const qy = [173, 279, 384, 486, 591];
const qRow = (i: number): Box => [34, qy[i] - 4, 1212, 96];
const qAns = (i: number): Box => [896, qy[i] - 2, 350, 92];

export const INSERTS: Insert[] = [
  {
    slide: 2, in: 85.4, out: 97.3, after: "WIDE",
    focus: [{ t: 85.4, rect: FULL }, { t: 85.6, rect: [200, 50, 1070] }],
    spots: [
      { t0: 85.7, t1: 88.6, box: [548, 252, 664, 88] },
      { t0: 88.7, t1: 91.5, box: [548, 355, 664, 86] },
      { t0: 91.6, t1: 94.5, box: [548, 458, 664, 86] },
      { t0: 94.6, t1: 97.3, box: [548, 560, 664, 86] },
    ],
  },
  {
    slide: 3, in: 113.3, out: 158.6, after: "MED",
    focus: [
      { t: 113.3, rect: FULL },
      { t: 115.4, rect: [0, 115, 960] },
      { t: 128.6, rect: [160, 115, 960] },
      { t: 147.8, rect: [320, 115, 960] },
      { t: 157.6, rect: FULL },
    ],
    spots: [
      { t0: 115.6, t1: 121.1, box: [62, 180, 366, 470] },
      { t0: 121.2, t1: 128.5, box: [62, 475, 366, 175] },
      { t0: 128.8, t1: 134.9, box: [457, 180, 366, 470] },
      { t0: 135.0, t1: 147.7, box: [457, 475, 366, 175] },
      { t0: 148.0, t1: 152.8, box: [852, 180, 366, 470] },
      { t0: 152.9, t1: 157.5, box: [852, 475, 366, 175] },
    ],
  },
  {
    // Chain of Survival
    slide: 4, in: 166.4, out: 205.6, after: "MED",
    focus: [
      { t: 166.4, rect: FULL },
      { t: 173.3, rect: [0, 140, 1000] },
      { t: 191.3, rect: [280, 140, 1000] },
      { t: 199.8, rect: FULL },
    ],
    spots: [
      { t0: 173.6, t1: 183.3, box: [32, 300, 350, 330] },
      { t0: 183.4, t1: 191.4, box: [314, 300, 346, 330] },
      { t0: 191.5, t1: 195.7, box: [595, 300, 346, 330] },
      { t0: 195.8, t1: 199.8, box: [877, 300, 372, 330] },
    ],
  },
  {
    // Sudden cardiac arrest
    slide: 5, in: 217.6, out: 255.4, after: "MED",
    focus: [{ t: 217.6, rect: FULL }],
    spots: [
      { t0: 217.9, t1: 227.1, box: [180, 168, 932, 112] },
      { t0: 227.2, t1: 238.2, box: [180, 292, 932, 68] },
      { t0: 238.3, t1: 247.8, box: [180, 472, 932, 112] },
      { t0: 247.9, t1: 255.4, box: [180, 598, 932, 58] },
    ],
  },
  // DRSABCD list: a short visit to the list at each letter, presenter in between
  { slide: 6, in: 255.6, out: 262.0, after: "CLOSE", focus: [{ t: 255.6, rect: FULL }], spots: [{ t0: 257.4, t1: 262.0, box: row6(0) }] },
  { slide: 6, in: 287.4, out: 293.6, after: "CLOSE", focus: [{ t: 287.4, rect: FULL }], spots: [{ t0: 287.6, t1: 293.6, box: row6(1) }] },
  { slide: 6, in: 304.2, out: 309.2, after: "CLOSE", focus: [{ t: 304.2, rect: FULL }], spots: [{ t0: 304.4, t1: 309.2, box: row6(2) }] },
  { slide: 6, in: 337.8, out: 346.2, after: "CLOSE_R", focus: [{ t: 337.8, rect: FULL }], spots: [{ t0: 337.9, t1: 346.2, box: row6(3) }] },
  { slide: 6, in: 424.5, out: 431.4, after: "MED", focus: [{ t: 424.5, rect: FULL }], spots: [{ t0: 424.7, t1: 431.4, box: row6(6) }] },
  {
    // Recap D-R-S (slide on screen from ~430.5)
    slide: 7, in: 436.8, out: 453.1, after: "MED",
    focus: [{ t: 436.8, rect: FULL }],
    spots: [
      { t0: 437.4, t1: 443.6, box: [40, 180, 390, 490] },
      { t0: 443.7, t1: 447.0, box: [440, 180, 410, 490] },
      { t0: 447.1, t1: 453.1, box: [862, 180, 410, 490] },
    ],
  },
  {
    // Recap A-B-C
    slide: 8, in: 453.1, out: 475.0, after: "MED",
    focus: [{ t: 453.1, rect: FULL }],
    spots: [
      { t0: 453.5, t1: 458.9, box: [50, 220, 400, 440] },
      { t0: 459.0, t1: 464.8, box: [450, 220, 400, 440] },
      { t0: 464.9, t1: 475.0, box: [860, 220, 410, 440] },
    ],
  },
  {
    // High-quality CPR: ratio, rate, depth
    slide: 9, in: 494.0, out: 509.2, after: "CLOSE",
    focus: [{ t: 494.0, rect: FULL }],
    spots: [
      { t0: 494.5, t1: 498.3, box: [66, 438, 560, 224] },
      { t0: 498.4, t1: 504.3, box: [66, 198, 560, 218] },
      { t0: 504.4, t1: 509.2, box: [652, 198, 560, 218] },
    ],
  },
  { slide: 9, in: 519.6, out: 524.8, after: "CLOSE", focus: [{ t: 519.6, rect: FULL }], spots: [{ t0: 519.8, t1: 524.8, box: [652, 438, 560, 224] }] },
  {
    // Demo slide 30:2
    slide: 10, in: 539.8, out: 546.0, after: "DEMO",
    focus: [{ t: 539.8, rect: FULL }],
    spots: [
      { t0: 540.0, t1: 542.9, box: [70, 170, 500, 500] },
      { t0: 543.0, t1: 546.0, box: [700, 170, 510, 500] },
    ],
  },
  {
    // AED definition
    slide: 11, in: 589.8, out: 605.4, after: "CLOSE_R",
    focus: [{ t: 589.8, rect: FULL }],
    spots: [{ t0: 594.6, t1: 605.4, box: [62, 215, 385, 200] }],
  },
  {
    // Attach pads -> prompts -> nobody touches the patient
    slide: 11, in: 664.4, out: 682.0, after: "AED",
    focus: [{ t: 664.4, rect: FULL }],
    spots: [
      { t0: 664.7, t1: 669.9, box: [62, 455, 390, 195] },
      { t0: 670.0, t1: 682.0, box: [822, 435, 395, 232] },
    ],
  },
  {
    // After AED analysis (part 1)
    slide: 12, in: 697.7, out: 713.2, after: "CLOSE",
    focus: [{ t: 697.7, rect: FULL }],
    spots: [
      { t0: 698.0, t1: 704.9, box: [448, 186, 385, 112] },
      { t0: 705.0, t1: 713.2, box: [62, 316, 500, 182] },
    ],
  },
  {
    // After AED analysis (part 2)
    slide: 12, in: 717.0, out: 749.0, after: "MED",
    focus: [{ t: 717.0, rect: FULL }],
    spots: [
      { t0: 717.2, t1: 733.8, box: [62, 520, 316, 176] },
      { t0: 733.9, t1: 738.5, box: [428, 586, 425, 112] },
      { t0: 738.6, t1: 741.8, box: [756, 316, 460, 220] },
      { t0: 741.9, t1: 749.0, box: [428, 586, 425, 112] },
    ],
  },
  {
    // Oral quiz: answers stay covered until the participants answer
    slide: 13, in: 751.2, out: 808.0, after: "MED",
    focus: [{ t: 751.2, rect: FULL }],
    spots: [
      { t0: 755.3, t1: 761.7, box: qRow(0) },
      { t0: 761.8, t1: 768.3, box: qRow(1) },
      { t0: 768.4, t1: 775.5, box: qRow(2) },
      { t0: 775.6, t1: 784.5, box: qRow(3) },
      { t0: 784.6, t1: 808.0, box: qRow(4) },
    ],
    covers: [
      { until: 758.2, box: qAns(0) },
      { until: 764.9, box: qAns(1) },
      { until: 773.3, box: qAns(2) },
      { until: 784.0, box: qAns(3) }, // ASSUMPTION: Q4 answer not clearly audible; revealed before Q5
      { until: 790.5, box: qAns(4) },
    ],
  },
  {
    // Summary (part 1)
    slide: 14, in: 816.4, out: 849.6, after: "CLOSE",
    focus: [{ t: 816.4, rect: FULL }],
    spots: [
      { t0: 819.0, t1: 832.3, box: [190, 212, 400, 120] },
      { t0: 832.4, t1: 849.6, box: [690, 262, 490, 135] },
    ],
  },
  {
    // Summary (part 2)
    slide: 14, in: 861.0, out: 889.2, after: "MED",
    focus: [{ t: 861.0, rect: FULL }],
    spots: [
      { t0: 861.0, t1: 878.5, box: [690, 262, 490, 135] },
      { t0: 878.6, t1: 889.2, box: [76, 520, 1130, 70] },
    ],
  },
  {
    // References
    slide: 15, in: 933.4, out: 971.0, after: "MED",
    focus: [{ t: 933.4, rect: FULL }],
    spots: [
      { t0: 937.1, t1: 942.1, box: [90, 275, 1120, 92] },
      { t0: 942.2, t1: 950.1, box: [90, 366, 1120, 50] },
      { t0: 950.2, t1: 954.4, box: [90, 423, 1120, 50] },
      { t0: 954.5, t1: 960.9, box: [90, 481, 1120, 56] },
      { t0: 961.0, t1: 966.3, box: [90, 538, 1120, 90] },
    ],
  },
];

// Camera = manual moves + a push into the projector before each slide
// (skipped when the previous slide ends right before) + a cut when it ends.
export const CAMERA: Key[] = (() => {
  const keys: Key[] = [...MOVES];
  INSERTS.forEach((ins, i) => {
    const prev = INSERTS[i - 1];
    const chained = prev && ins.in - prev.out < 0.5;
    if (!chained) keys.push({ t: ins.in - 0.4, shot: "SCREEN", dur: 0.5 });
    const next = INSERTS[i + 1];
    if (!(next && next.in - ins.out < 0.5)) keys.push({ t: ins.out, shot: ins.after, dur: 0.01 });
  });
  return keys.sort((a, b) => a.t - b.t);
})();

// ---------- point label (top-left) ----------
export const LABELS: { t: number; num?: string; text: string }[] = [
  { t: 0, text: "Basic Life Support untuk Petugas Kesihatan" },
  { t: 80.4, num: "!", text: "Situasi kecemasan" },
  { t: 111.0, num: "1", text: "Objektif · Urutan Adult BLS (DRSABCD)" },
  { t: 128.6, num: "2", text: "Objektif · CPR berkualiti tinggi" },
  { t: 147.8, num: "3", text: "Objektif · Penggunaan AED yang selamat" },
  { t: 158.6, num: "✓", text: "Objektif pembelajaran" },
  { t: 161.0, text: "Chain of Survival" },
  { t: 173.6, num: "1", text: "Chain of Survival · Early access" },
  { t: 183.4, num: "2", text: "Chain of Survival · Early CPR" },
  { t: 191.5, num: "3", text: "Chain of Survival · Early defibrillation" },
  { t: 195.8, num: "4", text: "Chain of Survival · Early ALS / post-resuscitation care" },
  { t: 207.5, text: "Sudden Cardiac Arrest" },
  { t: 255.5, text: "Urutan DRSABCD" },
  { t: 257.4, num: "D", text: "Danger" },
  { t: 287.6, num: "R", text: "Response" },
  { t: 304.4, num: "S", text: "Shout for help" },
  { t: 337.9, num: "A", text: "Airway" },
  { t: 383.1, num: "B", text: "Breathing" },
  { t: 395.8, num: "C", text: "Circulation" },
  { t: 424.7, num: "D", text: "Defibrillation" },
  { t: 436.8, text: "Ulang kaji · D · R · S" },
  { t: 453.1, text: "Ulang kaji · A · B · C" },
  { t: 477.3, text: "CPR dewasa berkualiti tinggi" },
  { t: 534.4, text: "Demonstrasi CPR pada manikin" },
  { t: 584.4, num: "D", text: "Defibrillation · Penggunaan AED" },
  { t: 697.7, text: "Tindakan selepas analisis AED" },
  { t: 713.4, num: "!", text: "You clear · I clear · Everybody clear" },
  { t: 717.0, text: "Tindakan selepas analisis AED" },
  { t: 749.3, num: "?", text: "Uji diri anda · Kuiz lisan" },
  { t: 812.0, text: "Rumusan" },
  { t: 889.4, text: "Recovery position" },
  { t: 932.0, text: "Rujukan" },
  { t: 974.6, text: "Basic Life Support untuk Petugas Kesihatan" },
];

// ---------- lower thirds (wording copied from the title slide) ----------
export const LOWER_THIRDS: { t0: number; t1: number; title: string; sub: string }[] = [
  { t0: 59.0, t1: 66.0, title: "Muhammad Syahmi bin Mohd Sani", sub: "Penceramah · Bachelor of Medical and Health Science with Honour" },
  { t0: 66.2, t1: 72.8, title: "NBMH4143", sub: "Teaching for Healthcare Personnel" },
  { t0: 72.9, t1: 79.5, title: "Sir Sivabalan A/L Rajagopal", sub: "Tutor" },
];
