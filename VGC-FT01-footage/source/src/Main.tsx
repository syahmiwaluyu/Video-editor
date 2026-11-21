import React from "react";
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  Easing,
} from "remotion";
import "@fontsource/archivo/600.css";
import "@fontsource/archivo/800.css";
import "@fontsource/caveat/600.css";
import "@fontsource/caveat/700.css";
import { C, FONT_HEAD, FONT_NOTE, FPS, H, RECT, SPEAKER_NAME, SRC_H, SRC_W, W } from "./theme";
import timing from "../timing.json";

type Rect = { x: number; y: number; w: number; h: number };
type Scene = { s: number; e: number; mode: "two" | "full" | "spk"; spk?: "F" | "K" };
type Cap = { s: number; e: number; text: string; spk: "F" | "K" };
type Note = { s: number; e: number; text: string };
type Chapter = { s: number; e: number; n: string; title: string };
type Timing = {
  durationSec: number;
  footageEndSec: number;
  hook: { s: number; e: number; lines: string[] };
  scenes: Scene[];
  captions: Cap[];
  notes: Note[];
  chapters: Chapter[];
  end: { s: number; e: number; title: string[]; sub: string };
  jumps?: number[];
  footageFile?: string;
};
const T = timing as unknown as Timing;

// ---------- helpers ----------
const sec = (f: number) => f / FPS;
// deterministic pseudo random
const rnd = (seed: number) => {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};
// stop-start paper move: travel 65%, short hold, settle. Returns 1 -> 0 progress of offset.
const stopStart = (lf: number) =>
  interpolate(lf, [0, 5, 8, 13], [1, 0.35, 0.35, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
// torn edge polygon for clip-path, jagged on chosen sides
const torn = (seed: number, sides: { top?: boolean; bottom?: boolean; left?: boolean; right?: boolean }, amp = 1.1) => {
  const pts: string[] = [];
  const n = 26;
  const j = (i: number, k: number) => (rnd(seed * 31 + i * 7 + k) * amp).toFixed(2);
  for (let i = 0; i <= n; i++) pts.push(`${((i / n) * 100).toFixed(2)}% ${sides.top ? j(i, 1) : 0}%`);
  for (let i = 1; i <= n; i++) pts.push(`${sides.right ? (100 - +j(i, 2)).toFixed(2) : 100}% ${((i / n) * 100).toFixed(2)}%`);
  for (let i = n - 1; i >= 0; i--) pts.push(`${((i / n) * 100).toFixed(2)}% ${sides.bottom ? (100 - +j(i, 3)).toFixed(2) : 100}%`);
  for (let i = n - 1; i >= 1; i--) pts.push(`${sides.left ? j(i, 4) : 0}% ${((i / n) * 100).toFixed(2)}%`);
  return `polygon(${pts.join(",")})`;
};

// ---------- building blocks ----------
const PaperBg: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.paper }}>
    <Img src={staticFile("paper.png")} style={{ width: W, height: H, opacity: 0.55, mixBlendMode: "multiply" }} />
  </AbsoluteFill>
);

// Shows the given source rect of the footage inside a box of size w x h (same aspect ratio).
// Jump cuts left by the pause trim (v02) inside a scene: alternate framing 1.0x / 1.07x so each join reads as an
// intentional punch-in instead of a skip.
const punchAt = (sceneStart: number, t: number) => {
  const k = (T.jumps ?? []).filter((j) => j > sceneStart + 1e-3 && j <= t + 1e-6).length;
  return k % 2 === 1 ? 0.07 : 0;
};

const Footage: React.FC<{ rect: Rect; w: number; h: number; push: number; punch?: number }> = ({ rect, w, h, push, punch = 0 }) => {
  // push: 0..1 -> up to 4% slow push towards rect centre
  const z = 1 + 0.04 * push + punch;
  const rw = rect.w / z, rh = rect.h / z;
  const rx = rect.x + (rect.w - rw) / 2, ry = rect.y + (rect.h - rh) / 2;
  const k = w / rw;
  return (
    <div style={{ width: w, height: h, overflow: "hidden", position: "relative", backgroundColor: "#bbb" }}>
      <OffthreadVideo
        src={staticFile(T.footageFile ?? "footage.mp4")}
        muted
        style={{ position: "absolute", width: SRC_W * k, height: SRC_H * k, left: -rx * k, top: -ry * k, maxWidth: "none" }}
      />
    </div>
  );
};

const Tape: React.FC<{ x: number; y: number; rot: number; w?: number; seed: number }> = ({ x, y, rot, w = 170, seed }) => (
  <div
    style={{
      position: "absolute", left: x, top: y, width: w, height: 46, background: C.tape,
      transform: `rotate(${rot}deg)`, clipPath: torn(seed, { left: true, right: true }, 6),
      boxShadow: "0 1px 2px rgba(0,0,0,0.08)",
    }}
  />
);

// Photo print: footage with paper border, tape, soft shadow, stop-start entrance.
const Print: React.FC<{
  rect: Rect; x: number; y: number; w: number; h: number; rot: number; lf: number; push: number; seed: number; from: "left" | "right" | "up"; punch?: number;
}> = ({ rect, x, y, w, h, rot, lf, push, seed, from, punch = 0 }) => {
  const p = stopStart(lf);
  const dx = from === "left" ? -140 * p : from === "right" ? 140 * p : 0;
  const dy = from === "up" ? -90 * p : 0;
  const b = 16;
  return (
    <div style={{ position: "absolute", left: x + dx, top: y + dy, transform: `rotate(${rot + p * (from === "right" ? 2 : -2)}deg)` }}>
      <div style={{ padding: b, background: C.print, boxShadow: "0 10px 26px rgba(40,30,10,0.22), 0 2px 4px rgba(40,30,10,0.18)" }}>
        <Footage rect={rect} w={w} h={h} push={push} punch={punch} />
      </div>
      <Tape x={-40} y={-18} rot={-32} seed={seed + 1} />
      <Tape x={w + b * 2 - 130} y={-18} rot={28} seed={seed + 2} />
    </div>
  );
};

const NameTag: React.FC<{ spk: "F" | "K"; size?: number }> = ({ spk, size = 38 }) => (
  <span style={{ fontFamily: FONT_NOTE, fontWeight: 700, fontSize: size, color: spk === "F" ? C.accent : C.muted, marginRight: 10 }}>
    {SPEAKER_NAME[spk]}:
  </span>
);

const CaptionText: React.FC<{ cap: Cap; lf: number; align: "center" | "left"; size?: number }> = ({ cap, lf, align, size = 38 }) => {
  const o = interpolate(lf, [0, 4], [0, 1], { extrapolateRight: "clamp" });
  const y = interpolate(lf, [0, 5], [6, 0], { extrapolateRight: "clamp" });
  return (
    <div style={{ opacity: o, transform: `translateY(${y}px)`, textAlign: align }}>
      <NameTag spk={cap.spk} />
      <span style={{ fontFamily: FONT_HEAD, fontWeight: 600, fontSize: size, lineHeight: 1.28, color: C.ink, whiteSpace: "pre-line" }}>
        {cap.text}
      </span>
    </div>
  );
};

const activeCap = (t: number) => T.captions.find((c) => t >= c.s && t < c.e);

// ---------- scenes ----------
const SceneTwo: React.FC<{ sc: Scene; t: number; lf: number; full: boolean; seed: number }> = ({ sc, t, lf, full, seed }) => {
  const push = (t - sc.s) / Math.max(1, sc.e - sc.s);
  const cap = activeCap(t);
  if (full) {
    return (
      <AbsoluteFill>
        <Footage rect={RECT.two} w={W} h={H} push={push} punch={punchAt(sc.s, t)} />
        {cap && (
          <div
            style={{
              position: "absolute", left: 210, right: 210, bottom: 44, padding: "18px 40px 22px",
              background: C.print, clipPath: torn(seed + 9, { top: true, bottom: true }, 7),
              boxShadow: "0 6px 16px rgba(0,0,0,0.25)",
            }}
          >
            <CaptionText cap={cap} lf={(t - cap.s) * FPS} align="center" />
          </div>
        )}
      </AbsoluteFill>
    );
  }
  const w = 1488, h = 837;
  return (
    <AbsoluteFill>
      <Print rect={RECT.two} x={(W - w) / 2 - 16} y={30} w={w} h={h} rot={-0.6} lf={lf} push={push} seed={seed} from="up" punch={punchAt(sc.s, t)} />
      {cap && (
        <div style={{ position: "absolute", left: 150, right: 150, top: 912, height: 150, display: "flex", alignItems: "flex-start", justifyContent: "center" }}>
          <CaptionText cap={cap} lf={(t - cap.s) * FPS} align="center" />
        </div>
      )}
    </AbsoluteFill>
  );
};

const SceneSpk: React.FC<{ sc: Scene; t: number; lf: number; seed: number }> = ({ sc, t, lf, seed }) => {
  const spk = sc.spk ?? "F";
  const left = spk === "F";
  const push = (t - sc.s) / Math.max(1, sc.e - sc.s);
  const cw = 608, ch = 760;
  const cap = activeCap(t);
  const note = T.notes.find((n) => t >= n.s && t < n.e && n.s >= sc.s - 0.01);
  const colX = left ? 860 : 150;
  return (
    <AbsoluteFill>
      <Print
        rect={RECT[spk]} x={left ? 150 : W - 150 - cw - 32} y={110} w={cw} h={ch}
        rot={left ? -1.6 : 1.4} lf={lf} push={push} seed={seed} from={left ? "left" : "right"} punch={punchAt(sc.s, t)}
      />
      {note && <NoteBlock note={note} t={t} x={colX} pointLeft={left} seed={seed} />}
      {cap && (
        <div style={{ position: "absolute", left: colX, width: 900, top: 650 }}>
          <div style={{ width: 120, height: 6, background: C.ink, marginBottom: 22 }} />
          <CaptionText cap={cap} lf={(t - cap.s) * FPS} align="left" size={40} />
        </div>
      )}
    </AbsoluteFill>
  );
};

// Marker annotation with a hand-drawn underline + arrow toward the photo.
const NoteBlock: React.FC<{ note: Note; t: number; x: number; pointLeft: boolean; seed: number }> = ({ note, t, x, pointLeft, seed }) => {
  const lf = (t - note.s) * FPS;
  const p = stopStart(lf);
  const draw = interpolate(lf, [6, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) });
  return (
    <div style={{ position: "absolute", left: x, top: 210 - 40 * p, width: 900, opacity: 1 - p }}>
      <div style={{ fontFamily: FONT_NOTE, fontWeight: 700, fontSize: 76, lineHeight: 1.0, color: C.accent, transform: `rotate(${pointLeft ? -1.5 : 1.5}deg)` }}>
        {note.text}
      </div>
      <svg width={900} height={70} style={{ display: "block", marginTop: 6 }}>
        <path
          d={pointLeft ? "M 560 20 C 420 40, 200 10, 40 34 M 40 34 L 72 14 M 40 34 L 74 52" : "M 20 20 C 160 40, 380 10, 540 34 M 540 34 L 508 14 M 540 34 L 506 52"}
          stroke={C.ink} strokeWidth={5} fill="none" strokeLinecap="round" strokeLinejoin="round"
          pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw}
        />
      </svg>
    </div>
  );
};

const ChapterLabel: React.FC<{ ch: Chapter; t: number; right: boolean }> = ({ ch, t, right }) => {
  const lf = (t - ch.s) * FPS;
  const outF = (ch.e - t) * FPS;
  const p = stopStart(lf);
  const out = interpolate(outF, [0, 5], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute", top: 54 - 60 * out, ...(right ? { right: 250 } : { left: 250 }),
        transform: `translateX(${(right ? 120 : -120) * p}px) rotate(${right ? 1.2 : -1.2}deg)`,
        opacity: 1 - out,
      }}
    >
      <div style={{ position: "relative", background: C.print, padding: "16px 34px 18px", clipPath: torn(ch.n.charCodeAt(1) * 3, { left: true, right: true }, 2), boxShadow: "0 6px 14px rgba(0,0,0,0.2)", display: "flex", alignItems: "baseline", gap: 18 }}>
        <span style={{ fontFamily: FONT_HEAD, fontWeight: 800, fontSize: 40, color: C.accent }}>{ch.n}</span>
        <span style={{ fontFamily: FONT_HEAD, fontWeight: 800, fontSize: 40, color: C.ink, letterSpacing: "-0.01em", textTransform: "uppercase" }}>{ch.title}</span>
      </div>
    </div>
  );
};

const Hook: React.FC<{ t: number }> = ({ t }) => {
  const lf = t * FPS;
  const outF = (T.hook.e - t) * FPS;
  const out = interpolate(outF, [0, 5], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: 236, top: 640, width: 1000, opacity: 1 - out, transform: `translateY(${50 * out}px)` }}>
      {T.hook.lines.map((l, i) => {
        const p = stopStart(lf - i * 9);
        return (
          <div key={i} style={{ transform: `translateX(${-100 * p}px) rotate(${i % 2 ? 0.8 : -0.8}deg)`, opacity: 1 - p, marginBottom: 10, display: "flex", justifyContent: "flex-start" }}>
            <span style={{ background: i === T.hook.lines.length - 1 ? C.ink : C.print, color: i === T.hook.lines.length - 1 ? C.print : C.ink, fontFamily: FONT_HEAD, fontWeight: 800, fontSize: 50, lineHeight: 1.1, whiteSpace: "nowrap", padding: "10px 22px 12px", letterSpacing: "-0.015em", boxShadow: "0 6px 14px rgba(0,0,0,0.22)" }}>
              {l}
            </span>
          </div>
        );
      })}
    </div>
  );
};

const EndCard: React.FC<{ t: number }> = ({ t }) => {
  const lf = (t - T.end.s) * FPS;
  return (
    <AbsoluteFill>
      <PaperBg />
      <div style={{ position: "absolute", left: 230, top: 330, width: 1460 }}>
        {T.end.title.map((l, i) => {
          const p = stopStart(lf - 4 - i * 10);
          return (
            <div key={i} style={{ transform: `translateY(${50 * p}px)`, opacity: 1 - p, fontFamily: FONT_HEAD, fontWeight: 800, fontSize: 96, lineHeight: 1.04, letterSpacing: "-0.02em", color: i === T.end.title.length - 1 ? C.accent : C.ink }}>
              {l}
            </div>
          );
        })}
        <div style={{ marginTop: 40, fontFamily: FONT_NOTE, fontWeight: 600, fontSize: 52, color: C.muted, opacity: interpolate(lf, [30, 42], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          {T.end.sub}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- main ----------
export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const t = sec(frame);
  if (t >= T.end.s) return <EndCard t={t} />;
  const idx = T.scenes.findIndex((s) => t >= s.s && t < s.e);
  const sc = T.scenes[Math.max(0, idx)];
  const lf = (t - sc.s) * FPS;
  const ch = T.chapters.find((c) => t >= c.s && t < c.e);
  return (
    <AbsoluteFill>
      <PaperBg />
      {sc.mode === "spk" ? (
        <SceneSpk sc={sc} t={t} lf={lf} seed={idx * 5 + 3} />
      ) : (
        <SceneTwo sc={sc} t={t} lf={lf} full={sc.mode === "full"} seed={idx * 5 + 3} />
      )}
      {t < T.hook.e && <Hook t={t} />}
      {ch && sc.mode !== "full" && <ChapterLabel ch={ch} t={t} right={sc.mode !== "spk" || sc.spk === "F"} />}
    </AbsoluteFill>
  );
};
