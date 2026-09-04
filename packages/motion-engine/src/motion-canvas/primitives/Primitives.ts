/**
 * Shikshak AI — Educational Motion Primitives.
 *
 * Core kinetic realization functions for scientific entities:
 * - Atom clusters & molecules with atom counters
 * - Chemical equation terms with animated coefficient insertion
 * - IEC circuit components, switches, and electron flow particles
 * - Biological membranes, organelles, photon absorption, and ATP synthase
 * - Mathematical equation transformation and term continuity
 */

import { ResolvedObjectVisual } from "../core/ObjectRegistry";

export interface PrimitiveStyle {
  textColor: string;
  accentColor: string;
  borderColor: string;
  surfaceColor: string;
  highlightGlow: string;
}

export const DARK_STUDIO_STYLE: PrimitiveStyle = {
  textColor: "#f8fafc",
  accentColor: "#38bdf8",
  borderColor: "#334155",
  surfaceColor: "#1e293b",
  highlightGlow: "rgba(56, 189, 248, 0.45)",
};

/**
 * Draw pedagogical highlight aura around an object's bounding box
 */
export function drawHighlightAura(
  ctx: any,
  visual: ResolvedObjectVisual,
  style = DARK_STUDIO_STYLE
): void {
  if (visual.highlightIntensity <= 0) return;

  const { minX, minY, maxX, maxY } = visual.bounds;
  const padding = 12 + visual.highlightIntensity * 8;
  const w = maxX - minX + padding * 2;
  const h = maxY - minY + padding * 2;
  const x = minX - padding;
  const y = minY - padding;

  ctx.save();
  ctx.strokeStyle = style.accentColor;
  ctx.lineWidth = 2.5;
  ctx.fillStyle = style.highlightGlow;
  ctx.beginPath();
  if (ctx.roundRect) {
    ctx.roundRect(x, y, w, h, 14);
  } else {
    ctx.rect(x, y, w, h);
  }
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

/**
 * Draw comparison brackets between two or more visual objects
 */
export function drawComparisonFrame(
  ctx: any,
  visualA: ResolvedObjectVisual,
  visualB: ResolvedObjectVisual,
  label = "COMPARE COUNTS",
  style = DARK_STUDIO_STYLE
): void {
  ctx.save();
  const bA = visualA.bounds;
  const bB = visualB.bounds;

  ctx.strokeStyle = "#f59e0b";
  ctx.lineWidth = 2.0;
  ctx.setLineDash([6, 4]);

  // Connect centers with comparison indicator
  const cAx = (bA.minX + bA.maxX) / 2;
  const cAy = (bA.minY + bA.maxY) / 2;
  const cBx = (bB.minX + bB.maxX) / 2;
  const cBy = (bB.minY + bB.maxY) / 2;

  ctx.beginPath();
  ctx.moveTo(cAx, cAy);
  ctx.lineTo(cBx, cBy);
  ctx.stroke();
  ctx.setLineDash([]);

  // Comparison pill badge at midpoint
  const midX = (cAx + cBx) / 2;
  const midY = (cAy + cBy) / 2;
  ctx.fillStyle = "#fffbeb";
  ctx.strokeStyle = "#d97706";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(midX, midY, 16, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = "#b45309";
  ctx.font = "bold 13px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("vs", midX, midY);

  ctx.restore();
}

/**
 * Draw an atom circle with symbol and count badge
 */
export function drawAtomNode(
  ctx: any,
  x: number,
  y: number,
  element: string,
  count = 1,
  color = "#38bdf8",
  radius = 28,
  highlight = 0.0
): void {
  ctx.save();
  if (highlight > 0) {
    ctx.shadowColor = color;
    ctx.shadowBlur = 15 * highlight;
  }

  // Atom circle
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();

  ctx.lineWidth = 2.5;
  ctx.strokeStyle = "#ffffff";
  ctx.stroke();

  // Element symbol text
  ctx.fillStyle = "#0f172a";
  ctx.font = `800 ${Math.round(radius * 0.85)}px system-ui, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(element, x, y);

  // Count badge (if count > 1 or highlighted)
  if (count > 0) {
    const badgeX = x + radius * 0.75;
    const badgeY = y - radius * 0.75;
    ctx.fillStyle = "#2563eb";
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 12px monospace";
    ctx.fillText(`${count}`, badgeX, badgeY);
  }

  ctx.restore();
}

/**
 * Draw coefficient animated into formula
 */
export function drawCoefficient(
  ctx: any,
  x: number,
  y: number,
  value: number,
  scale = 1.0,
  color = "#38bdf8"
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(scale, scale);

  ctx.fillStyle = color;
  ctx.font = "bold 38px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(`${value}`, 0, 0);

  ctx.restore();
}
