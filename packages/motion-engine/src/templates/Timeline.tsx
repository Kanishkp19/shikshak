import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const Timeline: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  steps = [],
  elements = [],
  keyTakeaway,
  badge = "SEQUENCE TIMELINE",
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

  const displayItems = items.length > 0 ? items : ["Phase 1", "Phase 2", "Phase 3"];

  const headerProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  // Track progress line length
  const lineProgress = interpolate(
    frame,
    [10, durationInFrames * 0.75],
    [0, 100],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070c18",
        backgroundImage:
          "radial-gradient(ellipse at 50% 30%, rgba(56, 189, 248, 0.08) 0%, transparent 60%)",
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

      {/* Horizontal Timeline Container */}
      <div style={{ position: "relative", width: "100%", padding: "40px 0" }}>
        {/* Base Track Line */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "5%",
            right: "5%",
            height: "4px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            transform: "translateY(-50%)",
          }}
        />

        {/* Animated Active Progress Line */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "5%",
            width: `${lineProgress * 0.9}%`,
            height: "4px",
            backgroundColor: accentColor,
            boxShadow: `0 0 12px ${accentColor}`,
            transform: "translateY(-50%)",
          }}
        />

        {/* Timeline Milestones */}
        <div
          style={{
            position: "relative",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "0 5%",
          }}
        >
          {displayItems.map((item, idx) => {
            const milestoneDelay = Math.floor(10 + (idx * (durationInFrames * 0.5)) / displayItems.length);
            const mProgress = spring({
              frame: Math.max(0, frame - milestoneDelay),
              fps,
              config: { damping: 13, stiffness: 100 },
            });

            const isActive = frame >= milestoneDelay;

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  opacity: interpolate(mProgress, [0, 1], [0, 1]),
                  transform: `scale(${interpolate(mProgress, [0, 1], [0.7, 1])})`,
                }}
              >
                {/* Milestone Node */}
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    backgroundColor: isActive ? accentColor : "#0f172a",
                    border: `3px solid ${isActive ? "#ffffff" : "rgba(255, 255, 255, 0.2)"}`,
                    boxShadow: isActive ? `0 0 16px ${accentColor}` : "none",
                    marginBottom: "16px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "13px",
                    fontWeight: 800,
                    color: isActive ? "#070c18" : "#94a3b8",
                  }}
                >
                  {idx + 1}
                </div>

                {/* Milestone Text Box */}
                <div
                  style={{
                    backgroundColor: "rgba(15, 23, 42, 0.85)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: "12px",
                    padding: "12px 18px",
                    maxWidth: "200px",
                    textAlign: "center",
                    fontSize: "15px",
                    fontWeight: 600,
                    color: "#f8fafc",
                  }}
                >
                  {item}
                </div>
              </div>
            );
          })}
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
          <strong style={{ color: "#ffffff" }}>Timeline Progression: </strong>
          {keyTakeaway}
        </div>
      )}
    </div>
  );
};
