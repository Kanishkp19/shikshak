import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const AnimatedTitle: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  keyTakeaway,
  badge = "CONCEPT ESSENTIALS",
  accentColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 90 },
  });

  const subProgress = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  const barProgress = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 16, stiffness: 100 },
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070c18",
        backgroundImage:
          "radial-gradient(ellipse at 50% 50%, rgba(56, 189, 248, 0.12) 0%, transparent 75%)",
        color: "#f8fafc",
        fontFamily: "system-ui, -apple-system, sans-serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "64px",
        boxSizing: "border-box",
        textAlign: "center",
      }}
    >
      {/* Category Pill */}
      <div
        style={{
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          transform: `scale(${interpolate(titleProgress, [0, 1], [0.8, 1])})`,
          fontSize: "14px",
          fontWeight: 800,
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          padding: "6px 18px",
          borderRadius: "9999px",
          backgroundColor: "rgba(56, 189, 248, 0.15)",
          color: accentColor,
          border: `1px solid ${accentColor}50`,
          marginBottom: "24px",
        }}
      >
        {badge}
      </div>

      {/* Main Kinetic Title */}
      <h1
        style={{
          opacity: interpolate(titleProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
          fontSize: "58px",
          fontWeight: 900,
          letterSpacing: "-0.03em",
          lineHeight: 1.15,
          margin: "0 0 16px 0",
          maxWidth: "960px",
          background: "linear-gradient(135deg, #ffffff 0%, #e2e8f0 70%, #94a3b8 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
      >
        {title}
      </h1>

      {/* Animated Accent Bar */}
      <div
        style={{
          width: `${interpolate(barProgress, [0, 1], [0, 160])}px`,
          height: "4px",
          borderRadius: "2px",
          backgroundColor: accentColor,
          boxShadow: `0 0 16px ${accentColor}`,
          marginBottom: "24px",
        }}
      />

      {/* Subtitle / Narration Beat */}
      {subtitle && (
        <p
          style={{
            opacity: interpolate(subProgress, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(subProgress, [0, 1], [20, 0])}px)`,
            fontSize: "24px",
            color: "#94a3b8",
            fontWeight: 500,
            maxWidth: "760px",
            margin: "0 0 24px 0",
            lineHeight: 1.45,
          }}
        >
          {subtitle}
        </p>
      )}

      {/* Key Takeaway Note */}
      {keyTakeaway && (
        <div
          style={{
            opacity: interpolate(subProgress, [0, 1], [0, 1]),
            fontSize: "17px",
            color: "#cbd5e1",
            backgroundColor: "rgba(15, 23, 42, 0.7)",
            padding: "10px 24px",
            borderRadius: "12px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          {keyTakeaway}
        </div>
      )}
    </div>
  );
};
