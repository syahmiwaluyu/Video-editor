import React from "react";
import "@fontsource/cormorant-garamond/500.css";
import "@fontsource/cormorant-garamond/500-italic.css";
import "@fontsource/cormorant-garamond/600.css";
import "@fontsource/montserrat/300.css";
import "@fontsource/montserrat/400.css";
import {
  AbsoluteFill,
  Easing,
  Img,
  Sequence,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
} from "remotion";
import timing from "../timing.json";
import { copy, theme } from "./theme";

const C = timing.cues;
const S = timing.scenes;
const OV = timing.overlap;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.33, 0, 0.2, 1);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// ---------- atmosphere ----------

// Soft floating particles: small glints + large out-of-focus bokeh. Deterministic (seeded).
const Particles: React.FC<{ count?: number; warmth?: number; opacity?: number }> = ({
  count = 46,
  warmth = 0,
  opacity = 1,
}) => {
  const frame = useCurrentFrame();
  const items = new Array(count).fill(0).map((_, i) => {
    const big = random(`big${i}`) < 0.22;
    const size = big ? 40 + random(`s${i}`) * 90 : 3 + random(`s${i}`) * 6;
    const speed = big ? 0.12 + random(`v${i}`) * 0.18 : 0.25 + random(`v${i}`) * 0.5;
    const x0 = random(`x${i}`) * 1920;
    const y0 = random(`y${i}`) * 1300;
    const y = ((y0 - frame * speed) % 1300 + 1300) % 1300 - 110;
    const x = x0 + Math.sin(frame / (70 + random(`p${i}`) * 60) + i) * (big ? 30 : 14);
    const tw = 0.55 + 0.45 * Math.sin(frame / (18 + random(`t${i}`) * 30) + i * 1.7);
    const col = random(`c${i}`) < 0.25 + warmth * 0.25 ? theme.champagne : random(`c2${i}`) < 0.5 ? theme.lavenderPale : theme.lilac;
    const a = (big ? 0.10 : 0.55) * tw * opacity;
    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: size,
          height: size,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${col} 0%, ${col}00 70%)`,
          opacity: a,
          filter: big ? "blur(6px)" : "blur(0.6px)",
          boxShadow: big ? "none" : `0 0 ${size * 2.5}px ${col}`,
        }}
      />
    );
  });
  return <AbsoluteFill style={{ pointerEvents: "none" }}>{items}</AbsoluteFill>;
};

// Slow-moving lavender gradient with gentle light pools.
const GradientBG: React.FC<{ deep?: number }> = ({ deep = 1 }) => {
  const frame = useCurrentFrame();
  const a = 30 + Math.sin(frame / 90) * 8;
  const b = 70 + Math.cos(frame / 110) * 8;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 60% 55% at ${a}% 35%, ${theme.lavender}${deep ? "55" : "88"} 0%, transparent 70%),
          radial-gradient(ellipse 55% 60% at ${b}% 75%, ${theme.plum}cc 0%, transparent 70%),
          linear-gradient(160deg, ${theme.plumDeep} 0%, #1d0f26 55%, ${theme.plumDeep} 100%)`,
      }}
    />
  );
};

const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.75 }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse 75% 70% at 50% 50%, transparent 45%, rgba(30,12,40,${strength}) 100%)`,
    }}
  />
);

// Soft lavender light sweep used on transitions.
const LightWash: React.FC<{ at: number; peak?: number }> = ({ at, peak = 0.32 }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [at - 16, at, at + 20], [0, peak, 0], clamp);
  const x = interpolate(frame, [at - 16, at + 20], [-20, 120], clamp);
  if (o <= 0) return null;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 45% 90% at ${x}% 50%, ${theme.lavenderPale} 0%, ${theme.lilac}66 35%, transparent 70%)`,
        opacity: o,
        mixBlendMode: "screen",
      }}
    />
  );
};

// ---------- typography ----------

const Reveal: React.FC<{
  start: number;
  end?: number;
  rise?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ start, end, rise = 18, children, style }) => {
  const frame = useCurrentFrame();
  const inT = interpolate(frame, [start, start + 28], [0, 1], { ...clamp, easing: ease });
  const outT = end === undefined ? 1 : interpolate(frame, [end - 20, end], [1, 0], { ...clamp, easing: ease });
  const blur = interpolate(inT, [0, 1], [8, 0]);
  return (
    <div
      style={{
        opacity: inT * outT,
        transform: `translateY(${(1 - inT) * rise}px)`,
        filter: `blur(${blur}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const serifLine = (size: number, color = theme.lavenderPale): React.CSSProperties => ({
  fontFamily: theme.serif,
  fontWeight: 500,
  fontSize: size,
  color,
  lineHeight: 1.15,
  textAlign: "center",
  textShadow: `0 0 28px ${theme.lavender}88, 0 2px 12px rgba(20,8,30,0.6)`,
});

const capsLine = (size: number, color = theme.silver): React.CSSProperties => ({
  fontFamily: theme.sans,
  fontWeight: 400,
  fontSize: size,
  letterSpacing: "0.32em",
  textTransform: "uppercase",
  color,
  textAlign: "center",
  textShadow: "0 2px 10px rgba(20,8,30,0.7)",
});

const silverFill: React.CSSProperties = {
  backgroundImage: `linear-gradient(180deg, #ffffff 0%, ${theme.silver} 45%, ${theme.silverDark} 70%, #f2f2f7 100%)`,
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
};

const Center: React.FC<{ children: React.ReactNode; y?: number }> = ({ children, y = 0 }) => (
  <AbsoluteFill
    style={{
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
      padding: `${theme.safeY}px ${theme.safeX}px`,
      transform: `translateY(${y}px)`,
    }}
  >
    {children}
  </AbsoluteFill>
);

const LowerText: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      justifyContent: "flex-end",
      alignItems: "center",
      flexDirection: "column",
      paddingBottom: theme.safeY + 30,
    }}
  >
    {children}
  </AbsoluteFill>
);

const Hairline: React.FC<{ start: number; width?: number }> = ({ start, width = 360 }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [start, start + 40], [0, 1], { ...clamp, easing: ease });
  return (
    <div
      style={{
        width: width * t,
        height: 1.5,
        margin: "26px auto",
        background: `linear-gradient(90deg, transparent, ${theme.champagne}, transparent)`,
        boxShadow: `0 0 12px ${theme.champagne}aa`,
      }}
    />
  );
};

// ---------- photo shots ----------

type Shot = (typeof timing.shots)[number] & { band?: boolean; portrait?: boolean };

// Lavender grade. warmth 0 = muted reflective, 1 = warmer lavender with soft natural light.
const Graded: React.FC<{ src: string; warmth: number; fx: number; fy: number; scale: number; fit?: "cover" | "contain" }> = ({
  src,
  warmth,
  fx,
  fy,
  scale,
  fit = "cover",
}) => (
  <AbsoluteFill style={{ overflow: "hidden" }}>
    <Img
      src={src}
      style={{
        width: "100%",
        height: "100%",
        objectFit: fit,
        objectPosition: `${fx}% ${fy}%`,
        transform: `scale(${scale})`,
        transformOrigin: `${fx}% ${fy}%`,
        filter: `saturate(${lerp(0.32, 0.82, warmth)}) brightness(${lerp(0.72, 0.98, warmth)}) contrast(${lerp(0.9, 0.96, warmth)})`,
      }}
    />
    {/* hue pull toward lavender: strong when muted, lighter when warm so skin stays natural */}
    <AbsoluteFill style={{ background: theme.lavender, mixBlendMode: "color", opacity: lerp(0.42, 0.16, warmth) }} />
    <AbsoluteFill
      style={{
        background: `linear-gradient(170deg, ${theme.lilac} 0%, ${theme.plum} 100%)`,
        mixBlendMode: "soft-light",
        opacity: lerp(0.65, 0.35, warmth),
      }}
    />
    {/* warm natural light from upper left, grows with warmth */}
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 70% 60% at 22% 18%, ${theme.champagne} 0%, transparent 65%)`,
        mixBlendMode: "soft-light",
        opacity: warmth * 0.75,
      }}
    />
  </AbsoluteFill>
);

const PhotoShot: React.FC<{ shot: Shot }> = ({ shot }) => {
  const frame = useCurrentFrame(); // local to the Sequence
  const len = shot.to - shot.from;
  const opacity = interpolate(frame, [0, OV, len - OV, len], [0, 1, 1, 0], { ...clamp, easing: ease });
  const scale = interpolate(frame, [0, len], [1.0, 1.07], clamp);
  const src = staticFile(`photos/${shot.id}.jpg`);

  if (shot.band) {
    // cinematic 2.29:1 band for the low-resolution role-play still, soft-focus on the edges
    return (
      <AbsoluteFill style={{ opacity }}>
        <GradientBG />
        <AbsoluteFill style={{ filter: "blur(28px)", opacity: 0.5 }}>
          <Graded src={src} warmth={shot.warmth} fx={shot.fx} fy={shot.fy} scale={1.2} />
        </AbsoluteFill>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <div style={{ width: 1920, height: 838, position: "relative", overflow: "hidden", boxShadow: "0 30px 80px rgba(15,5,25,0.7)" }}>
            <Graded src={src} warmth={shot.warmth} fx={shot.fx} fy={shot.fy} scale={scale * 1.01} />
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }

  if (shot.portrait) {
    return (
      <AbsoluteFill style={{ opacity }}>
        <AbsoluteFill style={{ filter: "blur(36px)" }}>
          <Graded src={src} warmth={shot.warmth} fx={50} fy={50} scale={1.3} />
        </AbsoluteFill>
        <AbsoluteFill style={{ background: `${theme.plumDeep}55` }} />
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <div
            style={{
              width: 600,
              height: 802,
              marginRight: 620,
              position: "relative",
              overflow: "hidden",
              border: `1.5px solid ${theme.champagne}aa`,
              boxShadow: `0 30px 90px rgba(15,5,25,0.6), 0 0 40px ${theme.lilac}44`,
              transform: `scale(${interpolate(frame, [0, len], [0.97, 1.02], clamp)})`,
            }}
          >
            <Graded src={src} warmth={shot.warmth} fx={50} fy={50} scale={1.0} />
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ opacity }}>
      <Graded src={src} warmth={shot.warmth} fx={shot.fx} fy={shot.fy} scale={scale} />
    </AbsoluteFill>
  );
};

// ---------- scenes ----------

const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [S.opening[1] - 10, S.opening[1] + OV], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <GradientBG />
      <Particles count={40} opacity={interpolate(frame, [0, 40], [0, 1], clamp)} />
      <Center>
        <Reveal start={C.open_line1}>
          <div style={{ ...serifLine(74), fontStyle: "italic" }}>{copy.open1}</div>
        </Reveal>
        <Reveal start={C.open_line2}>
          <div style={{ ...serifLine(60, theme.lilac), marginTop: 18 }}>{copy.open2}</div>
        </Reveal>
      </Center>
    </AbsoluteFill>
  );
};

const TitleReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const local = frame - S.title[0];
  const bgIn = interpolate(frame, [S.title[0] - OV, S.title[0] + 6], [0, 1], clamp);
  const fade = interpolate(frame, [C.fade_out, timing.durationInFrames], [1, 0], clamp);
  const spacing = interpolate(frame, [C.title_main, C.title_main + 70], [0.22, 0.06], { ...clamp, easing: ease });
  const glow = 0.5 + 0.2 * Math.sin(local / 24);
  return (
    <AbsoluteFill style={{ opacity: bgIn * fade }}>
      <GradientBG deep={1} />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 45% 30% at 50% 47%, ${theme.lavender}${Math.round(glow * 120)
            .toString(16)
            .padStart(2, "0")} 0%, transparent 70%)`,
        }}
      />
      <Particles count={60} warmth={0.4} />
      <Center y={-10}>
        <Reveal start={C.title_main} rise={10}>
          {copy.titleMain.map((l) => (
            <div
              key={l}
              style={{
                fontFamily: theme.serif,
                fontWeight: 600,
                fontSize: 88,
                lineHeight: 1.08,
                textAlign: "center",
                textTransform: "uppercase",
                letterSpacing: `${spacing}em`,
                ...silverFill,
                filter: `drop-shadow(0 0 18px ${theme.lilac}66)`,
              }}
            >
              {l}
            </div>
          ))}
        </Reveal>
        <Hairline start={C.title_sub - 10} width={520} />
        <Reveal start={C.title_sub}>
          <div style={{ ...serifLine(58, theme.lavenderPale), fontStyle: "italic" }}>{copy.titleSub}</div>
        </Reveal>
        <Reveal start={C.title_meta}>
          <div style={{ ...capsLine(22, theme.champagne), marginTop: 40, letterSpacing: "0.28em" }}>{copy.titleMeta}</div>
        </Reveal>
      </Center>
      <Vignette strength={0.55} />
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const shots = timing.shots as Shot[];
  // warmth of whatever shot is on screen, used to tint particles
  const cur = shots.filter((s) => frame >= s.from && frame < s.to).pop();
  const w = cur ? cur.warmth : 0;
  const photoParticles = interpolate(frame, [S.emotional[0], S.emotional[0] + 30, S.title[0], S.title[0] + 10], [0, 0.55, 0.85, 0], clamp);

  return (
    <AbsoluteFill style={{ backgroundColor: theme.plumDeep }}>
      {shots.map((s) => (
        <Sequence key={s.id} from={s.from} durationInFrames={s.to - s.from}>
          <PhotoShot shot={s} />
        </Sequence>
      ))}

      {/* overall vignette over photos, softer as we warm up */}
      <Sequence from={S.emotional[0]} durationInFrames={S.title[0] - S.emotional[0] + OV}>
        <Vignette strength={lerp(0.8, 0.5, w)} />
        {/* soft plum scrim so lower text stays legible on busy photos */}
        <AbsoluteFill style={{ background: `linear-gradient(0deg, ${theme.plumDeep}cc 0%, ${theme.plumDeep}55 22%, transparent 42%)` }} />
        <AbsoluteFill style={{ opacity: photoParticles }}>
          <Particles count={34} warmth={w} />
        </AbsoluteFill>
      </Sequence>

      {/* text over the photo scenes */}
      <Sequence from={S.emotional[0]} durationInFrames={S.title[0] - S.emotional[0]}>
        <AbsoluteFill style={{ transform: `translateY(${0}px)` }}>
          <FrameText />
        </AbsoluteFill>
      </Sequence>

      {timing.shots.slice(1).map((s) => (
        <LightWash key={s.id} at={s.from + OV / 2} peak={0.12 + s.warmth * 0.18} />
      ))}
      <LightWash at={S.title[0]} peak={0.3} />

      <Sequence from={0} durationInFrames={S.opening[1] + OV}>
        <Opening />
      </Sequence>
      <Sequence from={S.title[0] - OV} durationInFrames={timing.durationInFrames - S.title[0] + OV}>
        <TitleRevealWrap />
      </Sequence>
    </AbsoluteFill>
  );
};

const FrameText: React.FC = () => {
  const local = useCurrentFrame();
  const f = local + S.emotional[0];
  const emoEnd = 384;
  return (
    <AbsoluteFill>
      <AtFrame f={f}>
        <LowerText>
          <Reveal start={C.emo_line1} end={emoEnd}>
            <div style={{ ...serifLine(66), fontStyle: "italic" }}>{copy.emo1}</div>
          </Reveal>
          <Reveal start={C.emo_line2} end={emoEnd}>
            <div style={{ ...capsLine(22, theme.lavenderPale), marginTop: 14 }}>{copy.emo2}</div>
          </Reveal>
        </LowerText>
        <LowerText>
          <Reveal start={C.distress_caption} end={S.emotional[1]}>
            <div style={capsLine(26, theme.lavenderPale)}>{copy.distress}</div>
          </Reveal>
        </LowerText>
        <LowerText>
          <Reveal start={C.event_caption} end={C.event_caption + 120}>
            <div style={capsLine(24, theme.champagne)}>{copy.eventCaption}</div>
          </Reveal>
        </LowerText>
        <LowerText>
          <Reveal start={C.peer_line1} end={C.peer_line1 + 150}>
            <div style={{ ...serifLine(72), fontStyle: "italic" }}>{copy.peer1}</div>
          </Reveal>
        </LowerText>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingLeft: 640 }}>
          <Reveal start={C.peer_line2} end={1330}>
            <div style={{ ...serifLine(84, "#fbf6ff"), textAlign: "left", lineHeight: 1.2 }}>
              {copy.peer2.split(". ").map((l, i, a) => (
                <div key={l}>{i < a.length - 1 ? l + "." : l}</div>
              ))}
            </div>
          </Reveal>
        </AbsoluteFill>
      </AtFrame>
    </AbsoluteFill>
  );
};

// Provides an absolute-frame context to Reveal/Hairline by re-offsetting a nested Sequence.
const AtFrame: React.FC<{ f: number; children: React.ReactNode }> = ({ f, children }) => {
  const local = useCurrentFrame();
  const offset = f - local; // absolute start of the parent sequence
  return (
    <Sequence from={-offset} layout="none">
      {children}
    </Sequence>
  );
};

const TitleRevealWrap: React.FC = () => (
  <Sequence from={-(S.title[0] - OV)} layout="none">
    <TitleReveal />
  </Sequence>
);
