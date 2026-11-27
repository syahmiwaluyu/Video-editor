import React from "react";
import "@fontsource/montserrat/500.css";
import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/700.css";
import "@fontsource/montserrat/800.css";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { CAMERA, INSERTS, LABELS, LOWER_THIRDS, SHOTS, Shot } from "./edl";
import { SUBS } from "./subs";
import { FPS, H, MEDIA_BASE, SRC_H, SRC_W, W, theme } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);

export type Seg =
  | { kind: "video"; srcIn: number; srcOut: number; fadeIn?: boolean; fadeOut?: boolean }
  | { kind: "title"; sec: number };

export const segFrames = (s: Seg) =>
  s.kind === "video" ? Math.round((s.srcOut - s.srcIn) * FPS) : Math.round(s.sec * FPS);

// ---------- camera ----------
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const cameraAt = (t: number): Shot => {
  let state: Shot = SHOTS.WIDE;
  for (const k of CAMERA) {
    if (t < k.t) break;
    const to = SHOTS[k.shot];
    const p = ease(Math.min(1, (t - k.t) / (k.dur ?? 0.5)));
    state = { cx: lerp(state.cx, to.cx, p), cy: lerp(state.cy, to.cy, p), z: lerp(state.z, to.z, p) };
  }
  // keep the window inside the recorded frame (no invented edges)
  const w = W / state.z;
  const h = H / state.z;
  return {
    z: state.z,
    cx: Math.min(Math.max(state.cx, w / 2), SRC_W - w / 2),
    cy: Math.min(Math.max(state.cy, h / 2), SRC_H - h / 2),
  };
};

// ---------- slide insert ----------
const FRAME = { x: 258, y: 100, w: 1404, h: 790 }; // leaves a band at the bottom for subtitles
const FADE = 0.35;

const SlideInsert: React.FC<{ t: number }> = ({ t }) => {
  const ins = INSERTS.find((i) => t >= i.in - FADE && t <= i.out + FADE);
  if (!ins) return null;
  const opacity = Math.min(
    interpolate(t, [ins.in - FADE, ins.in], [0, 1], clamp),
    interpolate(t, [ins.out, ins.out + FADE], [1, 0], clamp),
  );
  const pop = interpolate(t, [ins.in - FADE, ins.in], [0.94, 1], { ...clamp, easing: Easing.out(Easing.cubic) });

  // focus rectangle (slide units, 1280 wide), eased 0.5 s between keys
  let [fx, fy, fw] = ins.focus[0].rect;
  for (const f of ins.focus) {
    if (t < f.t) break;
    const p = ease(Math.min(1, (t - f.t) / 0.5));
    fx = lerp(fx, f.rect[0], p);
    fy = lerp(fy, f.rect[1], p);
    fw = lerp(fw, f.rect[2], p);
  }
  const k = FRAME.w / 1280;
  const s = 1280 / fw;

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, ${theme.navy2}, ${theme.navy})` }} />
      <div
        style={{
          position: "absolute",
          left: FRAME.x,
          top: FRAME.y,
          width: FRAME.w,
          height: FRAME.h,
          overflow: "hidden",
          borderRadius: 18,
          boxShadow: "0 18px 60px rgba(0,0,0,0.55)",
          transform: `scale(${pop})`,
        }}
      >
        <div
          style={{
            position: "absolute",
            width: FRAME.w,
            height: FRAME.h,
            transformOrigin: "0 0",
            transform: `scale(${s}) translate(${-fx * k}px, ${-fy * k}px)`,
          }}
        >
          <Img src={staticFile(`slides/slide${String(ins.slide).padStart(2, "0")}.png`)} style={{ width: FRAME.w, height: FRAME.h }} />
          {ins.spots.map((sp, i) => {
            const o = Math.min(
              interpolate(t, [sp.t0, sp.t0 + 0.2], [0, 1], clamp),
              interpolate(t, [sp.t1, sp.t1 + 0.2], [1, 0], clamp),
            );
            if (o <= 0) return null;
            const [bx, by, bw, bh] = sp.box;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: bx * k,
                  top: by * k,
                  width: bw * k,
                  height: bh * k,
                  borderRadius: 12,
                  border: `3px solid ${theme.teal}`,
                  boxShadow: `0 0 0 4000px rgba(4,10,24,0.5), 0 0 22px ${theme.teal}`,
                  opacity: o,
                }}
              />
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- point label ----------
const PointLabel: React.FC<{ t: number; tIn: number }> = ({ t, tIn }) => {
  let idx = 0;
  LABELS.forEach((l, i) => {
    if (t >= l.t) idx = i;
  });
  const l = LABELS[idx];
  const since = t - Math.max(l.t, tIn);
  const o = interpolate(since, [0, 0.3], [0, 1], clamp);
  const x = interpolate(since, [0, 0.3], [-18, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <div
      style={{
        position: "absolute",
        left: theme.safeX,
        top: 40,
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "10px 22px 10px 12px",
        borderRadius: 40,
        background: "rgba(8,18,38,0.82)",
        border: `2px solid rgba(63,214,200,0.55)`,
        opacity: o,
        transform: `translateX(${x}px)`,
        fontFamily: theme.font,
      }}
    >
      {l.num ? (
        <div
          style={{
            width: 42,
            height: 42,
            borderRadius: 21,
            background: l.num === "!" ? theme.red : theme.teal,
            color: theme.navy,
            fontWeight: 800,
            fontSize: 24,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {l.num === "!" ? <span style={{ color: theme.white }}>!</span> : l.num}
        </div>
      ) : (
        <div style={{ width: 10, height: 10, borderRadius: 5, background: theme.teal, marginLeft: 10 }} />
      )}
      <div style={{ color: theme.white, fontWeight: 700, fontSize: 28 }}>{l.text}</div>
    </div>
  );
};

// ---------- lower third ----------
const LowerThird: React.FC<{ t: number }> = ({ t }) => {
  const lt = LOWER_THIRDS.find((x) => t >= x.t0 && t <= x.t1 + 0.3);
  if (!lt) return null;
  const o = Math.min(interpolate(t, [lt.t0, lt.t0 + 0.3], [0, 1], clamp), interpolate(t, [lt.t1, lt.t1 + 0.3], [1, 0], clamp));
  const x = interpolate(t, [lt.t0, lt.t0 + 0.35], [-24, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <div style={{ position: "absolute", left: theme.safeX, bottom: 200, opacity: o, transform: `translateX(${x}px)`, fontFamily: theme.font }}>
      <div style={{ display: "flex" }}>
        <div style={{ width: 6, background: theme.teal, borderRadius: 3, marginRight: 16 }} />
        <div style={{ background: "rgba(8,18,38,0.85)", padding: "12px 24px", borderRadius: 10 }}>
          <div style={{ color: theme.white, fontWeight: 800, fontSize: 34 }}>{lt.title}</div>
          <div style={{ color: theme.muted, fontWeight: 600, fontSize: 22, marginTop: 4 }}>{lt.sub}</div>
        </div>
      </div>
    </div>
  );
};

// ---------- subtitles ----------
const Subtitle: React.FC<{ t: number }> = ({ t }) => {
  const s = SUBS.find((x) => t >= x.t0 && t < x.t1);
  if (!s) return null;
  const isNote = s.text.startsWith("(");
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 52, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          maxWidth: 1480,
          textAlign: "center",
          background: theme.subBg,
          color: isNote ? theme.muted : theme.white,
          fontStyle: isNote ? "italic" : "normal",
          fontFamily: theme.font,
          fontWeight: 600,
          fontSize: 40,
          lineHeight: 1.3,
          padding: "8px 24px",
          borderRadius: 10,
        }}
      >
        {s.text}
      </div>
    </div>
  );
};

// ---------- segments ----------
const VideoSeg: React.FC<{ seg: Extract<Seg, { kind: "video" }>; video: string }> = ({ seg, video }) => {
  const f = useCurrentFrame();
  const n = segFrames(seg);
  const t = seg.srcIn + f / FPS;
  const cam = cameraAt(t);
  const dip = Math.min(
    seg.fadeIn ? interpolate(f, [0, 8], [0, 1], clamp) : 1,
    seg.fadeOut ? interpolate(f, [n - 8, n], [1, 0], clamp) : 1,
  );
  const startFrom = Math.round((seg.srcIn - MEDIA_BASE) * FPS);
  return (
    <AbsoluteFill style={{ background: theme.navy }}>
      <AbsoluteFill style={{ opacity: dip }}>
        <OffthreadVideo
          src={staticFile(video)}
          startFrom={startFrom}
          endAt={startFrom + n}
          muted
          style={{
            position: "absolute",
            width: SRC_W,
            height: SRC_H,
            left: W / 2 - cam.cx * cam.z,
            top: H / 2 - cam.cy * cam.z,
            transformOrigin: "0 0",
            transform: `scale(${cam.z})`,
          }}
        />
        <SlideInsert t={t} />
        <LowerThird t={t} />
        <PointLabel t={t} tIn={seg.srcIn} />
        <Subtitle t={t} />
      </AbsoluteFill>
      <Audio
        src={staticFile("audio_44.wav")}
        startFrom={startFrom}
        endAt={startFrom + n}
        volume={(fr) => Math.min(interpolate(fr, [0, 4], [0, 1], clamp), interpolate(fr, [n - 6, n], [1, 0], clamp))}
      />
    </AbsoluteFill>
  );
};

const TitleCard: React.FC<{ sec: number }> = ({ sec }) => {
  const f = useCurrentFrame();
  const n = Math.round(sec * FPS);
  const o = Math.min(interpolate(f, [0, 8], [0, 1], clamp), interpolate(f, [n - 8, n], [1, 0], clamp));
  const y = interpolate(f, [0, 14], [16, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 45%, ${theme.navy2}, ${theme.navy})`, justifyContent: "center", alignItems: "center", fontFamily: theme.font }}>
      <div style={{ opacity: o, transform: `translateY(${y}px)`, textAlign: "center" }}>
        <div style={{ color: theme.white, fontWeight: 800, fontSize: 84, letterSpacing: 1 }}>BASIC LIFE SUPPORT (BLS)</div>
        <div style={{ color: theme.muted, fontWeight: 600, fontSize: 44, marginTop: 8 }}>Untuk Petugas Kesihatan</div>
        <div style={{ color: theme.teal, fontWeight: 700, fontSize: 34, marginTop: 28 }}>Adult BLS • CPR • AED</div>
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC<{ segs: Seg[]; video: string }> = ({ segs, video }) => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: theme.navy }}>
      {segs.map((s, i) => {
        const n = segFrames(s);
        const el = (
          <Sequence key={i} from={from} durationInFrames={n}>
            {s.kind === "video" ? <VideoSeg seg={s} video={video} /> : <TitleCard sec={s.sec} />}
          </Sequence>
        );
        from += n;
        return el;
      })}
    </AbsoluteFill>
  );
};
