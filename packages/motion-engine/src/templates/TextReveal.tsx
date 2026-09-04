import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const TextReveal: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  keyTakeaway,
  badge = "KEY DEFINITION",
  accentColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = (subtitle || title).split(" ");

  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070c18",
        backgroundImage:
          "radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.1) 0%, transparent 65%)",
        color: "#f8fafc",
        fontFamily: "system-ui, -apple-system, sans-serif",
        padding: "64px 80px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "flex-start",
        boxSizing: "border-box",
      }}
    >
      <span
        style={{
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          fontSize: "14px",
          fontWeight: 800,
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          padding: "5px 16px",
          borderRadius: "9999px",
          backgroundColor: "rgba(56, 189, 248, 0.15)",
          color: accentColor,
          marginBottom: "20px",
        }}
      >
        {badge}
      </span>

      <h1
        style={{
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          fontSize: "42px",
          fontWeight: 800,
          margin: "0 0 28px 0",
          color: "#ffffff",
        }}
      >
        {title}
      </h1>

      {/* Kinetic Word-by-Word Staggered Reveal */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px",
          fontSize: "26px",
          fontWeight: 500,
          lineHeight: 1.5,
          color: "#cbd5e1",
          maxWidth: "1000px",
          marginBottom: "32px",
        }}
      >
        {words.map((w, idx) => {
          const wDelay = Math.floor(6 + idx * 3);
          const wProgress = spring({
            frame: Math.max(0, frame - wDelay),
            fps,
            config: { damping: 14, stiffness: 120 },
          });

          return (
            <span
              key={idx}
              style={{
                opacity: interpolate(wProgress, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(wProgress, [0, 1], [15, 0])}px)`,
                display: "inline-block",
              }}
            >
              {w}
            </span>
          );
        })}
      </div>

      {keyTakeaway && (
        <div
          style={{
            borderLeft: `4px solid ${accentColor}`,
            paddingLeft: "16px",
            fontSize: "17px",
            color: "#94a3b8",
            marginTop: "12px",
          }}
        >
          {keyTakeaway}
        </div>
      )}
    </div>
  );
};
