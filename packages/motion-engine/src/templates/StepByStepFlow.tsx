import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MotionSceneProps } from "../types";

export const StepByStepFlow: React.FC<MotionSceneProps> = ({
  title,
  subtitle,
  steps = [],
  elements = [],
  keyTakeaway,
  accentColor = "#38bdf8",
  badge = "PROCESS FLOW",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Consolidate steps from either `steps` or `elements`
  const flowItems =
    steps.length > 0
      ? steps
      : elements
          .filter((el) => el.type === "text" || el.type === "card")
          .map((el) => el.content);

  const displayItems = flowItems.length > 0 ? flowItems : ["Initiation", "Reaction", "Completion"];

  // Header animation
  const headerProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const headerOpacity = interpolate(headerProgress, [0, 1], [0, 1]);
  const headerY = interpolate(headerProgress, [0, 1], [-20, 0]);

  // Bottom banner animation
  const bannerDelay = Math.max(10, Math.floor(durationInFrames * 0.55));
  const bannerProgress = spring({
    frame: Math.max(0, frame - bannerDelay),
    fps,
    config: { damping: 15, stiffness: 90 },
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070c18",
        backgroundImage:
          "radial-gradient(circle at 50% 20%, rgba(56, 189, 248, 0.08) 0%, transparent 70%)",
        color: "#f8fafc",
        fontFamily: "system-ui, -apple-system, sans-serif",
        padding: "48px 64px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      {/* Top Header */}
      <div
        style={{
          opacity: headerOpacity,
          transform: `translateY(${headerY}px)`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
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
              border: `1px solid ${accentColor}40`,
            }}
          >
            {badge}
          </span>
          {subtitle && (
            <span style={{ fontSize: "16px", color: "#94a3b8", fontWeight: 500 }}>
              {subtitle}
            </span>
          )}
        </div>
        <h1
          style={{
            margin: 0,
            fontSize: "38px",
            fontWeight: 800,
            letterSpacing: "-0.02em",
            background: "linear-gradient(to right, #ffffff, #cbd5e1)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          {title}
        </h1>
      </div>

      {/* Process Flow Cards Container */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "24px",
          width: "100%",
          padding: "20px 0",
        }}
      >
        {displayItems.map((item, idx) => {
          // Staggered entrance timing
          const itemDelay = Math.floor(10 + (idx * (durationInFrames * 0.45)) / displayItems.length);
          const itemProgress = spring({
            frame: Math.max(0, frame - itemDelay),
            fps,
            config: { damping: 13, stiffness: 110 },
          });

          const scale = interpolate(itemProgress, [0, 1], [0.75, 1]);
          const opacity = interpolate(itemProgress, [0, 1], [0, 1]);
          const y = interpolate(itemProgress, [0, 1], [30, 0]);

          // Glow active state based on video timeline progression
          const activeStart = itemDelay;
          const activeEnd = itemDelay + 30;
          const isGlowActive = frame >= activeStart && frame <= activeEnd;
          const glowPulse = isGlowActive ? "0 0 28px rgba(56, 189, 248, 0.4)" : "none";

          return (
            <React.Fragment key={idx}>
              {/* Step Card */}
              <div
                style={{
                  opacity,
                  transform: `translateY(${y}px) scale(${scale})`,
                  backgroundColor: "rgba(15, 23, 42, 0.85)",
                  border: `1px solid ${isGlowActive ? accentColor : "rgba(255, 255, 255, 0.12)"}`,
                  boxShadow: glowPulse,
                  borderRadius: "20px",
                  padding: "28px 24px",
                  minWidth: "200px",
                  maxWidth: "280px",
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  textAlign: "center",
                  backdropFilter: "blur(12px)",
                  transition: "border 0.2s ease",
                }}
              >
                {/* Step Number Tag */}
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    backgroundColor: isGlowActive ? accentColor : "rgba(255, 255, 255, 0.08)",
                    color: isGlowActive ? "#090d16" : "#94a3b8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "14px",
                    fontWeight: 800,
                    marginBottom: "16px",
                  }}
                >
                  {String(idx + 1).padStart(2, "0")}
                </div>

                {/* Step Content */}
                <div
                  style={{
                    fontSize: "20px",
                    fontWeight: 700,
                    color: "#f8fafc",
                    lineHeight: 1.35,
                  }}
                >
                  {item}
                </div>
              </div>

              {/* Animated Connector Arrow between cards */}
              {idx < displayItems.length - 1 && (
                <div
                  style={{
                    opacity: interpolate(
                      spring({
                        frame: Math.max(0, frame - (itemDelay + 8)),
                        fps,
                        config: { damping: 14, stiffness: 120 },
                      }),
                      [0, 1],
                      [0, 1]
                    ),
                    transform: `scale(${interpolate(
                      spring({
                        frame: Math.max(0, frame - (itemDelay + 8)),
                        fps,
                        config: { damping: 14, stiffness: 120 },
                      }),
                      [0, 1],
                      [0.5, 1]
                    )})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M5 12H19M19 12L13 6M19 12L13 18"
                      stroke={accentColor}
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Bottom Takeaway Card */}
      <div
        style={{
          opacity: interpolate(bannerProgress, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(bannerProgress, [0, 1], [20, 0])}px)`,
          backgroundColor: "rgba(30, 41, 59, 0.6)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: "14px",
          padding: "16px 24px",
          display: "flex",
          alignItems: "center",
          gap: "16px",
        }}
      >
        <div
          style={{
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            backgroundColor: accentColor,
            boxShadow: `0 0 10px ${accentColor}`,
          }}
        />
        <div style={{ fontSize: "16px", color: "#cbd5e1", fontWeight: 500 }}>
          <strong style={{ color: "#ffffff", fontWeight: 700 }}>Key Mechanism: </strong>
          {keyTakeaway || "Sequential transformation driven by cellular and biochemical energy."}
        </div>
      </div>
    </div>
  );
};
