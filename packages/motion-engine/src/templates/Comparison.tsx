import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const Comparison: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  steps = [],
  elements = [],
  keyTakeaway,
  badge = "COMPARATIVE ANALYSIS",
  accentColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Split into left and right comparison sides
  const items = steps.length > 0 ? steps : elements.map((e) => e.content);
  const leftItem = items[0] || "State A / Concept 1";
  const rightItem = items[1] || "State B / Concept 2";

  const headerProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const leftProgress = spring({
    frame: Math.max(0, frame - 10),
    fps,
    config: { damping: 13, stiffness: 90 },
  });

  const rightProgress = spring({
    frame: Math.max(0, frame - 20),
    fps,
    config: { damping: 13, stiffness: 90 },
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070c18",
        backgroundImage:
          "radial-gradient(circle at 50% 10%, rgba(56, 189, 248, 0.08) 0%, transparent 60%)",
        color: "#f8fafc",
        fontFamily: "system-ui, -apple-system, sans-serif",
        padding: "48px 64px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
      }}
    >
      {/* Header */}
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

      {/* Comparison Cards */}
      <div style={{ display: "flex", gap: "32px", alignItems: "stretch", flex: 1, margin: "24px 0" }}>
        {/* Left Column */}
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            border: "1px solid rgba(56, 189, 248, 0.3)",
            borderRadius: "20px",
            padding: "32px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            opacity: interpolate(leftProgress, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(leftProgress, [0, 1], [-30, 0])}px)`,
          }}
        >
          <div style={{ color: accentColor, fontSize: "13px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "8px" }}>
            SIDE A
          </div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", lineHeight: 1.4 }}>
            {leftItem}
          </div>
        </div>

        {/* VS Divider */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "50%",
              backgroundColor: "rgba(30, 41, 59, 0.9)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              color: "#94a3b8",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 800,
              fontSize: "14px",
            }}
          >
            VS
          </div>
        </div>

        {/* Right Column */}
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "20px",
            padding: "32px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            opacity: interpolate(rightProgress, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(rightProgress, [0, 1], [30, 0])}px)`,
          }}
        >
          <div style={{ color: "#10b981", fontSize: "13px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "8px" }}>
            SIDE B
          </div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", lineHeight: 1.4 }}>
            {rightItem}
          </div>
        </div>
      </div>

      {/* Bottom Takeaway */}
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
          <strong style={{ color: "#ffffff" }}>Key Distinction: </strong>
          {keyTakeaway}
        </div>
      )}
    </div>
  );
};
