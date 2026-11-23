import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import timing from "../timing.json";

export const Root: React.FC = () => (
  <Composition
    id="Launch-Preview"
    component={Main}
    durationInFrames={timing.durationInFrames}
    fps={timing.fps}
    width={timing.width}
    height={timing.height}
  />
);
