import React from "react";
import { Composition } from "remotion";
import { MotionScene } from "./compositions/MotionScene";
import { MotionSceneProps } from "./types";

const defaultProps: MotionSceneProps = {
  template: "step_by_step_flow",
  title: "Photosynthesis Light Reactions",
  subtitle: "Inside the thylakoid membrane",
  steps: ["Sunlight", "Chlorophyll", "Water Splitting", "ATP Synthase"],
  keyTakeaway: "Light energy is converted into chemical bond energy (ATP).",
  accentColor: "#38bdf8",
  badge: "BIOLOGY FLOW",
  durationSeconds: 6,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition<any, any>
        id="MotionScene"
        component={MotionScene}
        durationInFrames={144}
        fps={24}
        width={1280}
        height={720}
        defaultProps={defaultProps}
        calculateMetadata={({ props }) => {
          const dur = typeof props?.durationSeconds === "number" ? props.durationSeconds : 6;
          return {
            durationInFrames: Math.max(48, Math.round(dur * 24)),
          };
        }}
      />
    </>
  );
};
