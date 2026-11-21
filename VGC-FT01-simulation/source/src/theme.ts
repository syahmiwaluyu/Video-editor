// Single theme file: colour roles, font, safe area.
// Colours are the visual-direction starting point (no student brand assets were supplied).
export const theme = {
  background: "#182951",
  surface: "#22376a",
  text: "#f6efff",
  mutedText: "#b9b3d6",
  structure: "#7f95cf",
  accent: "#ffba50",
  accentInk: "#182951", // dark text on the accent box
  font: "'Nunito', sans-serif",
  safeX: 120,
  safeY: 90,
  outline: 6,
};

// All on-screen wording lives here so it can be edited without touching animation code.
export const copy = {
  hook: "Pesakit tak dapat diselamatkan.",
  chip1: "Rasa bersalah",
  chip2: "Susah tidur",
  statement: "Itu bukan tanda lemah.",
  human: "Anda manusia dahulu.",
  // DRAFT CTA — not supplied by the student; must be approved or replaced.
  cta: ["Bercakaplah dengan", "seseorang yang", "anda percaya."],
};
