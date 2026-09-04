import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const DiagramBuild: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  steps = [],
  elements = [],
  keyTakeaway,
  badge = "DIAGRAM BUILD",
  accentColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const items =
    steps.length > 0
      ? steps
      : elements
          .filter((e) => e.type === "text" || e.type === "card")
          .map((e) => e.content);

  const displayItems = items.length > 0 ? items : ["Input Component", "Processing Stage", "Output Result"];

  const headerProgress = spring({
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
          "radial-gradient(ellipse at 50% 50%, rgba(56, 189, 248, 0.08) 0%, transparent 65%)",
        color: "#f8fafc",
        fontFamily: "system-ui, -apple-system, sans-serif",
        padding: "48px 64px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          opacity: interpolate(headerProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(headerProgress, [0, 1], [-20, 0])}px)`,
        }}
      >
        <span
          style={{
            fontSize: "13px",
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            padding: "4px 12px",
            borderRadius: "9999px",
            backgroundColor: "rgba(56, 189, 248, 0.15)",
            color: accentColor,
          }}
        >
          {badge}
        </span>
        <h1 style={{ margin: "10px 0 4px 0", fontSize: "36px", fontWeight: 800 }}>
          {title}
        </h1>
        {subtitle && <p style={{ margin: 0, color: "#94a3b8", fontSize: "16px" }}>{subtitle}</p>}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "28px",
          width: "100%",
          padding: "24px 0",
        }}
      >
        {displayItems.map((item, idx) => {
          const itemDelay = Math.floor(10 + (idx * (durationInFrames * 0.45)) / displayItems.length);
          const iProgress = spring({
            frame: Math.max(0, frame - itemDelay),
            fps,
            config: { damping: 13, stiffness: 100 },
          });

          return (
            <div
              key={idx}
              style={{
                opacity: interpolate(iProgress, [0, 1], [0, 1]),
                transform: `scale(${interpolate(iProgress, [0, 1], [0.8, 1])}) translateY(${interpolate(
                  iProgress,
                  [0, 1],
                  [20, 0]
                )}px)`,
                backgroundColor: "rgba(15, 23, 42, 0.85)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "18px",
                padding: "28px 24px",
                minWidth: "200px",
                maxWidth: "280px",
                flex: 1,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: "12px",
                  fontWeight: 800,
                  color: accentColor,
                  letterSpacing: "0.1em",
                  marginBottom: "10px",
                  textTransform: "uppercase",
                }}
              >
                MODULE {idx + 1}
              </div>
              <div style={{ fontSize: "19px", fontWeight: 700, color: "#ffffff", lineHeight: 1.35 }}>
                {item}
              </div>
            </div>
          );
        })}
      </div>

      {keyTakeaway && (
        <div
          style={{
            backgroundColor: "rgba(30, 41, 59, 0.5)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: "12px",
            padding: "14px 20px",
            fontSize: "15px",
            color: "#cbd5e1",
          }}
        >
          <strong style={{ color: "#ffffff" }}>Key Assembly: </strong>
          {keyTakeaway}
        </div>
      )}
    </div>
  );
};
