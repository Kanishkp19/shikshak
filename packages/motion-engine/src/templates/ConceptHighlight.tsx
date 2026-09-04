import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const ConceptHighlight: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  steps = [],
  elements = [],
  keyTakeaway,
  badge = "KEY CONCEPT",
  accentColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const points =
    steps.length > 0
      ? steps
      : elements
          .filter((el) => el.type === "text" || el.type === "highlight")
          .map((el) => el.content);

  const cardProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 95 },
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070c18",
        backgroundImage:
          "radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.08) 0%, transparent 65%)",
        color: "#f8fafc",
        fontFamily: "system-ui, -apple-system, sans-serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "48px 64px",
        boxSizing: "border-box",
      }}
    >
      {/* Central Highlight Card */}
      <div
        style={{
          width: "100%",
          maxWidth: "880px",
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          border: `1.5px solid ${accentColor}50`,
          borderRadius: "28px",
          padding: "44px 52px",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px rgba(56, 189, 248, 0.15)",
          transform: `scale(${interpolate(cardProgress, [0, 1], [0.85, 1])}) translateY(${interpolate(
            cardProgress,
            [0, 1],
            [30, 0]
          )}px)`,
          opacity: interpolate(cardProgress, [0, 1], [0, 1]),
          boxSizing: "border-box",
        }}
      >
        {/* Badge & Category */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
          <span
            style={{
              fontSize: "13px",
              fontWeight: 800,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              padding: "4px 14px",
              borderRadius: "9999px",
              backgroundColor: "rgba(56, 189, 248, 0.18)",
              color: accentColor,
            }}
          >
            {badge}
          </span>
          {subtitle && (
            <span style={{ fontSize: "15px", color: "#94a3b8", fontWeight: 500 }}>
              {subtitle}
            </span>
          )}
        </div>

        {/* Title */}
        <h2
          style={{
            fontSize: "36px",
            fontWeight: 800,
            margin: "0 0 24px 0",
            color: "#ffffff",
            lineHeight: 1.25,
          }}
        >
          {title}
        </h2>

        {/* Staggered Bullet Points */}
        {points.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "28px" }}>
            {points.map((pt, i) => {
              const ptDelay = Math.floor(12 + (i * (durationInFrames * 0.4)) / points.length);
              const ptProgress = spring({
                frame: Math.max(0, frame - ptDelay),
                fps,
                config: { damping: 14, stiffness: 100 },
              });

              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "14px",
                    opacity: interpolate(ptProgress, [0, 1], [0, 1]),
                    transform: `translateX(${interpolate(ptProgress, [0, 1], [-20, 0])}px)`,
                  }}
                >
                  <div
                    style={{
                      width: "8px",
                      height: "8px",
                      borderRadius: "50%",
                      backgroundColor: accentColor,
                      marginTop: "9px",
                      flexShrink: 0,
                    }}
                  />
                  <div style={{ fontSize: "19px", color: "#e2e8f0", lineHeight: 1.45 }}>
                    {pt}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Bottom Takeaway */}
        {keyTakeaway && (
          <div
            style={{
              borderTop: "1px solid rgba(255, 255, 255, 0.1)",
              paddingTop: "20px",
              fontSize: "16px",
              color: "#94a3b8",
            }}
          >
            <strong style={{ color: accentColor }}>Core Insight: </strong>
            {keyTakeaway}
          </div>
        )}
      </div>
    </div>
  );
};
