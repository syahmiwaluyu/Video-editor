import React from "react";
import { Composition } from "remotion";
import { Main, Seg, segFrames } from "./Main";
import { LECTURE_IN, PREVIEW_OUT, TEASER, TEASER_ON, TITLE_CARD_SEC } from "./edl";
import { FPS, H, W } from "./theme";

const lecture = (out: number): Seg[] => [
  ...(TEASER_ON
    ? ([
        { kind: "video", srcIn: TEASER.in, srcOut: TEASER.out, fadeOut: true },
        { kind: "title", sec: TITLE_CARD_SEC },
      ] as Seg[])
    : []),
  { kind: "video", srcIn: LECTURE_IN, srcOut: out, fadeIn: TEASER_ON, fadeOut: true },
];

const previewSegs = lecture(PREVIEW_OUT);

export const Root: React.FC = () => (
  <Composition
    id="BLS-Preview"
    component={Main}
    durationInFrames={previewSegs.reduce((a, s) => a + segFrames(s), 0)}
    fps={FPS}
    width={W}
    height={H}
    defaultProps={{ segs: previewSegs, video: "proxy_preview.mp4" }}
  />
);
