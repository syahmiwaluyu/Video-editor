import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import { FPS, H, W } from "./theme";
import timing from "../timing.json";

export const Root: React.FC = () => (
  <Composition
    id="Footage-Preview"
    component={Main}
    durationInFrames={Math.round((timing as { durationSec: number }).durationSec * FPS)}
    fps={FPS}
    width={W}
    height={H}
  />
);
