import React from "react";
import "@fontsource/nunito/700.css";
import "@fontsource/nunito/800.css";
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import timing from "../timing.json";
import { copy, theme } from "./theme";

const C = timing.cues;
const S = timing.scenes;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ---------- motion helpers ----------

// Pop entrance: scale 0.55 -> 1 with slight overshoot, blur 10 -> 0 (~0.3 s).
const usePop = (start: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - start, fps, config: { damping: 11, stiffness: 190, mass: 0.8 } });
  const scale = interpolate(s, [0, 1], [0.55, 1]);
  const blur = interpolate(frame - start, [0, 8], [10, 0], clamp);
  const opacity = interpolate(frame - start, [0, 4], [0, 1], clamp);
  return { transform: `scale(${scale})`, filter: `blur(${blur}px)`, opacity };
};

// Modest squash-and-stretch landing (~0.4 s).
const useSquash = (start: number) => {
  const frame = useCurrentFrame();
  const t = frame - start;
  const sy = interpolate(t, [0, 4, 8, 12], [0.4, 1.08, 0.96, 1], { ...clamp, easing: Easing.out(Easing.quad) });
  const sx = interpolate(t, [0, 4, 8, 12], [0.4, 0.94, 1.03, 1], { ...clamp, easing: Easing.out(Easing.quad) });
  const opacity = interpolate(t, [0, 3], [0, 1], clamp);
  return { transform: `scale(${sx}, ${sy})`, opacity };
};

// Slow push for the whole scene + quick hand-off push on the last 4 frames.
const useCamera = (from: number, to: number, handoff: boolean) => {
  const frame = useCurrentFrame();
  const local = frame; // inside a Sequence, frame is already local
  const len = to - from;
  const push = interpolate(local, [0, len], [1, 1.04], clamp);
  const out = handoff ? interpolate(local, [len - 4, len], [1, 1.09], clamp) : 1;
  const blur = handoff ? interpolate(local, [len - 4, len], [0, 6], clamp) : 0;
  return { transform: `scale(${push * out})`, filter: `blur(${blur}px)` };
};

// Zoom-through landing: enters from 1.14x with blur, settles in ~0.3 s.
const useZoomIn = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 9], [1.14, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const blur = interpolate(frame, [0, 9], [8, 0], clamp);
  return { transform: `scale(${scale})`, filter: `blur(${blur}px)` };
};

// ---------- shared pieces ----------

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = frame * 0.25;
  return (
    <AbsoluteFill style={{ backgroundColor: theme.background }}>
      <AbsoluteFill
        style={{
          backgroundImage: `radial-gradient(${theme.structure}22 2.5px, transparent 2.5px)`,
          backgroundSize: "48px 48px",
          backgroundPosition: `${drift}px ${drift * 0.5}px`,
        }}
      />
    </AbsoluteFill>
  );
};

const Text: React.FC<{ size: number; weight?: number; color?: string; style?: React.CSSProperties; children: React.ReactNode }> = ({
  size,
  weight = 800,
  color = theme.text,
  style,
  children,
}) => (
  <div
    style={{
      fontFamily: theme.font,
      fontSize: size,
      fontWeight: weight,
      color,
      lineHeight: 1.08,
      letterSpacing: "-0.01em",
      ...style,
    }}
  >
    {children}
  </div>
);

// ECG trace: three pulses, then flat from x = 430.
const ECG_POINTS = (() => {
  const pts: [number, number][] = [[0, 120]];
  for (const px of [70, 200, 330]) {
    pts.push([px, 120], [px + 12, 104], [px + 22, 120], [px + 32, 120], [px + 40, 150], [px + 52, 30], [px + 64, 170], [px + 74, 120], [px + 92, 120], [px + 104, 100], [px + 118, 120]);
  }
  pts.push([680, 120]);
  return pts;
})();
const ECG_PATH = ECG_POINTS.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x} ${y}`).join(" ");
const ecgY = (x: number) => {
  for (let i = 1; i < ECG_POINTS.length; i++) {
    const [x0, y0] = ECG_POINTS[i - 1];
    const [x1, y1] = ECG_POINTS[i];
    if (x <= x1) return x1 === x0 ? y1 : y0 + ((x - x0) / (x1 - x0)) * (y1 - y0);
  }
  return 120;
};

const Monitor: React.FC<{ reveal: number; flat: number; w?: number }> = ({ reveal, flat, w = 760 }) => {
  const k = w / 760;
  const lineColor = flat > 0.5 ? theme.mutedText : theme.structure;
  return (
    <svg width={760 * k} height={520 * k} viewBox="0 0 760 520" style={{ overflow: "visible" }}>
      <rect x="20" y="20" width="720" height="400" rx="44" fill={theme.surface} stroke={theme.structure} strokeWidth={theme.outline} />
      <rect x="330" y="420" width="100" height="50" fill={theme.structure} />
      <rect x="250" y="466" width="260" height="22" rx="11" fill={theme.structure} />
      <g transform="translate(40 100)">
        <defs>
          <clipPath id={`reveal-${w}`}>
            <rect x="0" y="-20" width={reveal} height="240" />
          </clipPath>
        </defs>
        <path d={ECG_PATH} fill="none" stroke={lineColor} strokeWidth="8" strokeLinejoin="round" strokeLinecap="round" clipPath={`url(#reveal-${w})`} />
        {reveal < 680 && <circle cx={reveal} cy={ecgY(reveal)} r="11" fill={theme.text} />}
      </g>
    </svg>
  );
};

// ---------- scenes ----------

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = useCamera(S.hook.from, S.hook.to, true);
  const reveal = interpolate(frame, [0, C.flatline, 60], [230, 430, 680], clamp);
  const flat = interpolate(frame, [C.flatline, C.flatline + 6], [0, 1], clamp);
  const pop = usePop(C.hookText);
  return (
    <AbsoluteFill style={cam}>
      <div style={{ position: "absolute", left: 150, top: 250 }}>
        <Monitor reveal={reveal} flat={flat} />
      </div>
      <div style={{ position: "absolute", left: 1010, top: 410, width: 800, transformOrigin: "left center", ...pop }}>
        <Text size={84}>
          Pesakit tak dapat
          <br />
          diselamatkan.
        </Text>
      </div>
    </AbsoluteFill>
  );
};

const Chip: React.FC<{ start: number; label: string }> = ({ start, label }) => {
  const pop = usePop(start);
  return (
    <div
      style={{
        display: "inline-block",
        padding: "18px 34px",
        borderRadius: 999,
        border: `${theme.outline}px solid ${theme.structure}`,
        background: theme.surface,
        transformOrigin: "left center",
        ...pop,
      }}
    >
      <Text size={50} weight={700}>
        {label}
      </Text>
    </div>
  );
};

const Explain: React.FC = () => {
  const frame = useCurrentFrame();
  const enter = useZoomIn();
  const cam = useCamera(S.explain.from, S.explain.to, true);
  const local = (abs: number) => abs - S.explain.from;
  const ring = frame * -2.2; // replay loop turning
  const box = useSquash(local(C.statement));
  return (
    <AbsoluteFill style={enter}>
      <AbsoluteFill style={cam}>
        {/* Replay loop: the same monitor keeps circling in the mind */}
        <div style={{ position: "absolute", left: 230, top: 250, width: 580, height: 580 }}>
          <svg width="580" height="580" viewBox="0 0 580 580" style={{ position: "absolute", transform: `rotate(${ring}deg)` }}>
            <circle cx="290" cy="290" r="250" fill="none" stroke={theme.structure} strokeWidth={theme.outline} strokeDasharray="70 34" strokeLinecap="round" />
            <polygon points="540,262 568,318 512,318" fill={theme.structure} />
            <polygon points="40,318 12,262 68,262" fill={theme.structure} />
          </svg>
          <div style={{ position: "absolute", left: 140, top: 180 }}>
            <Monitor reveal={680} flat={1} w={300} />
          </div>
        </div>
        <div style={{ position: "absolute", left: 930, top: 270, display: "flex", flexDirection: "column", gap: 28, alignItems: "flex-start" }}>
          <Chip start={local(C.chip1)} label={copy.chip1} />
          <Chip start={local(C.chip2)} label={copy.chip2} />
        </div>
        <div
          style={{
            position: "absolute",
            left: 930,
            top: 590,
            padding: "22px 40px",
            borderRadius: 32,
            background: theme.accent,
            transformOrigin: "left bottom",
            ...box,
          }}
        >
          <Text size={68} color={theme.accentInk}>
            {copy.statement}
          </Text>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Bubble: React.FC<{ start: number; fill: string; flip?: boolean; children?: React.ReactNode; w: number; h: number }> = ({
  start,
  fill,
  flip,
  children,
  w,
  h,
}) => {
  const sq = useSquash(start);
  return (
    <div style={{ position: "relative", width: w, height: h + 40, transformOrigin: flip ? "right bottom" : "left bottom", ...sq }}>
      <svg width={w} height={h + 40} viewBox={`0 0 ${w} ${h + 40}`} style={{ position: "absolute", overflow: "visible" }}>
        <rect x="3" y="3" width={w - 6} height={h - 6} rx="48" fill={fill} stroke={theme.structure} strokeWidth={theme.outline} />
        <polygon
          points={flip ? `${w - 110},${h - 4} ${w - 40},${h + 36} ${w - 60},${h - 4}` : `60,${h - 4} 40,${h + 36} 110,${h - 4}`}
          fill={fill}
          stroke={theme.structure}
          strokeWidth={theme.outline}
          strokeLinejoin="round"
        />
        <rect x={flip ? w - 112 : 56} y={h - 14} width="60" height="14" fill={fill} />
      </svg>
      <div style={{ position: "absolute", inset: 0, height: h, display: "flex", alignItems: "center", justifyContent: "center", gap: 22 }}>
        {children}
      </div>
    </div>
  );
};

const Dots: React.FC<{ start: number; color: string }> = ({ start, color }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {[0, 1, 2].map((i) => {
        const y = Math.sin((frame - start) / 4 - i * 0.9) * 7;
        return <div key={i} style={{ width: 30, height: 30, borderRadius: 15, background: color, transform: `translateY(${y}px)` }} />;
      })}
    </>
  );
};

const Takeaway: React.FC = () => {
  const cam = useCamera(S.takeaway.from, S.takeaway.to, false);
  const local = (abs: number) => abs - S.takeaway.from;
  const human = usePop(local(C.humanLine));
  const cta = usePop(local(C.cta));
  return (
    <AbsoluteFill style={cam}>
      <div style={{ position: "absolute", left: 170, top: 250, display: "flex", flexDirection: "column", gap: 26 }}>
        <Bubble start={local(C.bubble1)} fill={theme.surface} w={460} h={210}>
          <Dots start={local(C.bubble1)} color={theme.text} />
        </Bubble>
        <div style={{ marginLeft: 220 }}>
          <Bubble start={local(C.bubble2)} fill={theme.accent} flip w={420} h={190}>
            <Dots start={local(C.bubble2) + 6} color={theme.accentInk} />
          </Bubble>
        </div>
      </div>
      <div style={{ position: "absolute", left: 930, top: 290, width: 880 }}>
        <div style={{ transformOrigin: "left center", ...human }}>
          <Text size={56} weight={700} color={theme.mutedText}>
            {copy.human}
          </Text>
        </div>
        <div style={{ marginTop: 30, transformOrigin: "left center", ...cta }}>
          <Text size={80}>
            {copy.cta.map((line, i) => (
              <div key={i}>{line}</div>
            ))}
          </Text>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Sequence from={S.hook.from} durationInFrames={S.hook.to - S.hook.from}>
      <Hook />
    </Sequence>
    <Sequence from={S.explain.from} durationInFrames={S.explain.to - S.explain.from}>
      <Explain />
    </Sequence>
    <Sequence from={S.takeaway.from} durationInFrames={S.takeaway.to - S.takeaway.from}>
      <Takeaway />
    </Sequence>
  </AbsoluteFill>
);
