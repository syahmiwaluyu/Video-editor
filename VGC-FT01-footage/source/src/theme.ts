// Single theme file: colours, fonts, geometry. Visual direction: Scrapbook Documentary.
export const C = {
  paper: "#e9dfc9",   // background (brief starting point)
  ink: "#22211f",     // text
  accent: "#e95632",  // accent
  print: "#f8f3e7",   // photo-print border / paper slips
  muted: "#6e665a",
  tape: "rgba(236, 222, 178, 0.82)",
};
export const FONT_HEAD = "Archivo";   // bold editorial sans (SIL OFL)
export const FONT_NOTE = "Caveat";    // marker-like annotation (SIL OFL)
export const FPS = 30;
export const W = 1920;
export const H = 1080;
export const SRC_W = 2520;            // proxy of the original 21:9 footage
export const SRC_H = 1080;

// Source rectangles (in source pixels) used for re-composition. Never stretched: every rect
// matches the aspect ratio of the box it fills.
export const RECT = {
  two: { x: 260, y: 0, w: 1920, h: 1080 },     // 16:9 two-shot
  F: { x: 180, y: 50, w: 760, h: 950 },        // Farhan (left, purple scrubs) 4:5
  K: { x: 1440, y: 90, w: 760, h: 950 },       // speaker on the right (hijab) 4:5
};
export const SPEAKER_NAME: Record<string, string> = { F: "Farhan", K: "Penyokong" };
