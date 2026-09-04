/**
 * Shikshak AI — Motion Canvas Chemistry Domain Scene.
 *
 * Specializes in:
 * - Chemical reaction representation with molecular continuity
 * - Atom counting across reactants and products
 * - Dynamic coefficient insertion (e.g. animating coefficient 3 into Fe, 4 into H2O)
 * - Atomic inventory comparison WITHOUT physical balance scales / seesaws
 * - Reaction arrows and state transformations
 */

import { ObjectRegistry, ResolvedObjectVisual } from "../core/ObjectRegistry";
import { drawAtomNode, drawCoefficient, drawHighlightAura, drawComparisonFrame } from "../primitives/Primitives";

export interface ChemistrySceneConfig {
  unbalancedEquation: string;
  balancedEquation: string;
  reactants: { name: string; formula: string; atoms: { element: string; count: number }[] }[];
  products: { name: string; formula: string; atoms: { element: string; count: number }[] }[];
  activeStepIndex?: number;
}

export class ChemistryScene {
  private registry: ObjectRegistry;

  constructor(registry: ObjectRegistry) {
    this.registry = registry;
    this.layoutObjects();
  }

  /**
   * Deterministically assign world coordinates to semantic objects
   * based on reaction topology (Reactants Left, Arrow Center, Products Right).
   */
  private layoutObjects(): void {
    // Reactants stage: x = 200 - 520
    // Reaction arrow: x = 640
    // Products stage: x = 760 - 1080
    // Top equation line: y = 140
    // Molecular visual stage: y = 380
    // Atom inventory status board: y = 600

    this.registry.registerBounds("reactant_zone", { minX: 120, minY: 80, maxX: 580, maxY: 520 });
    this.registry.registerBounds("product_zone", { minX: 700, minY: 80, maxX: 1160, maxY: 520 });
    this.registry.registerBounds("fe_reactant", { minX: 160, minY: 280, maxX: 300, maxY: 440 });
    this.registry.registerBounds("h2o_reactant", { minX: 340, minY: 280, maxX: 540, maxY: 440 });
    this.registry.registerBounds("fe3o4_product", { minX: 720, minY: 260, maxX: 940, maxY: 460 });
    this.registry.registerBounds("h2_product", { minX: 980, minY: 300, maxX: 1120, maxY: 440 });
    this.registry.registerBounds("equation_header", { minX: 200, minY: 80, maxX: 1080, maxY: 200 });
  }

  public render(ctx: any, t: number, visuals: Map<string, ResolvedObjectVisual>): void {
    ctx.save();

    // ── Background Studio Surface ──
    ctx.fillStyle = "#0b1329";
    ctx.fillRect(0, 0, 1280, 720);

    // Subtle coordinate grid dots
    ctx.fillStyle = "rgba(56, 189, 248, 0.08)";
    for (let x = 40; x < 1280; x += 40) {
      for (let y = 40; y < 720; y += 40) {
        ctx.beginPath();
        ctx.arc(x, y, 1.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // ── Top Domain Header Badge ──
    ctx.fillStyle = "rgba(37, 99, 235, 0.15)";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 24, 260, 32, 16);
    } else {
      ctx.rect(50, 24, 260, 32);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText("⚛️ CHEMISTRY: ATOM BALANCING", 68, 40);

    // ── Equation Stage (Dynamic Coefficient Realization) ──
    // Progressively transforms: Fe + H2O -> Fe3O4 + H2  =>  3Fe + 4H2O -> Fe3O4 + 4H2
    const feVis = visuals.get("fe_reactant");
    const h2oVis = visuals.get("h2o_reactant");
    const fe3o4Vis = visuals.get("fe3o4_product");
    const h2Vis = visuals.get("h2_product");

    const feCoeff = feVis?.activeCoefficient ?? (t >= 4.5 ? 3 : 1);
    const h2oCoeff = h2oVis?.activeCoefficient ?? (t >= 7.5 ? 4 : 1);
    const h2Coeff = h2Vis?.activeCoefficient ?? (t >= 9.5 ? 4 : 1);

    // Reaction equation bar
    ctx.fillStyle = "rgba(30, 41, 59, 0.75)";
    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 75, 1180, 80, 16);
    } else {
      ctx.rect(50, 75, 1180, 80);
    }
    ctx.fill();
    ctx.stroke();

    // Render Equation Elements
    ctx.font = "bold 32px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    // Fe Term: [Coeff] Fe
    const feX = 220;
    const feY = 115;
    if (feCoeff > 1) {
      drawCoefficient(ctx, feX - 34, feY, feCoeff, 1.0, "#38bdf8");
    }
    ctx.fillStyle = feVis?.highlightIntensity ? "#38bdf8" : "#f8fafc";
    ctx.fillText("Fe", feX, feY);

    // Plus sign
    ctx.fillStyle = "#64748b";
    ctx.fillText("+", 330, feY);

    // H2O Term: [Coeff] H₂O
    const h2oX = 440;
    if (h2oCoeff > 1) {
      drawCoefficient(ctx, h2oX - 44, feY, h2oCoeff, 1.0, "#38bdf8");
    }
    ctx.fillStyle = h2oVis?.highlightIntensity ? "#38bdf8" : "#f8fafc";
    ctx.fillText("H₂O", h2oX, feY);

    // Reaction Arrow
    ctx.fillStyle = "#38bdf8";
    ctx.fillText("⟶", 640, feY);

    // Fe3O4 Term
    const fe3o4X = 840;
    ctx.fillStyle = fe3o4Vis?.highlightIntensity ? "#38bdf8" : "#f8fafc";
    ctx.fillText("Fe₃O₄", fe3o4X, feY);

    // Plus sign
    ctx.fillStyle = "#64748b";
    ctx.fillText("+", 960, feY);

    // H2 Term: [Coeff] H₂
    const h2X = 1060;
    if (h2Coeff > 1) {
      drawCoefficient(ctx, h2X - 34, feY, h2Coeff, 1.0, "#38bdf8");
    }
    ctx.fillStyle = h2Vis?.highlightIntensity ? "#38bdf8" : "#f8fafc";
    ctx.fillText("H₂", h2X, feY);

    // ── Molecular Structural Visualization Stage (Middle 380y) ──

    // Left Reactants Stage Box
    ctx.fillStyle = "rgba(15, 23, 42, 0.6)";
    ctx.strokeStyle = "rgba(56, 189, 248, 0.3)";
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(80, 180, 500, 360, 18);
      ctx.roundRect(700, 180, 500, 360, 18);
    } else {
      ctx.rect(80, 180, 500, 360);
      ctx.rect(700, 180, 500, 360);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#94a3b8";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("REACTANTS (LEFT)", 100, 210);
    ctx.fillText("PRODUCTS (RIGHT)", 720, 210);

    // Draw Reactant Iron Atoms
    const feAtomCount = feCoeff === 3 ? 3 : 1;
    const feHighlight = feVis?.highlightIntensity ?? (t >= 2.0 && t < 4.5 ? 1.0 : 0.0);

    if (feAtomCount === 1) {
      drawAtomNode(ctx, 230, 340, "Fe", 1, "#f59e0b", 34, feHighlight);
    } else {
      drawAtomNode(ctx, 190, 320, "Fe", 1, "#f59e0b", 28, feHighlight);
      drawAtomNode(ctx, 250, 320, "Fe", 2, "#f59e0b", 28, feHighlight);
      drawAtomNode(ctx, 220, 380, "Fe", 3, "#f59e0b", 28, feHighlight);
    }

    // Draw Reactant Water Molecules (O in center, 2 H attached)
    const waterCount = h2oCoeff === 4 ? 4 : 1;
    const oHighlight = h2oVis?.highlightIntensity ?? (t >= 6.0 && t < 8.0 ? 1.0 : 0.0);
    for (let i = 0; i < Math.min(4, waterCount); i++) {
      const wy = 290 + i * 55;
      const wx = 440;
      // Oxygen
      drawAtomNode(ctx, wx, wy, "O", i + 1, "#ef4444", 20, oHighlight);
      // Hydrogen bonded
      drawAtomNode(ctx, wx - 26, wy + 14, "H", 0, "#e2e8f0", 13, 0);
      drawAtomNode(ctx, wx + 26, wy + 14, "H", 0, "#e2e8f0", 13, 0);
    }

    // Draw Product Fe3O4 (3 Fe + 4 O cluster)
    const fe3o4Highlight = fe3o4Vis?.highlightIntensity ?? (t >= 2.5 && t < 5.0 ? 0.8 : 0.0);
    drawAtomNode(ctx, 790, 320, "Fe", 1, "#f59e0b", 28, fe3o4Highlight);
    drawAtomNode(ctx, 860, 320, "Fe", 2, "#f59e0b", 28, fe3o4Highlight);
    drawAtomNode(ctx, 825, 380, "Fe", 3, "#f59e0b", 28, fe3o4Highlight);

    drawAtomNode(ctx, 770, 370, "O", 1, "#ef4444", 18, 0);
    drawAtomNode(ctx, 880, 370, "O", 2, "#ef4444", 18, 0);
    drawAtomNode(ctx, 825, 270, "O", 3, "#ef4444", 18, 0);
    drawAtomNode(ctx, 825, 430, "O", 4, "#ef4444", 18, 0);

    // Draw Product H2 Molecules
    const h2ProductCount = h2Coeff === 4 ? 4 : 1;
    for (let i = 0; i < Math.min(4, h2ProductCount); i++) {
      const hy = 290 + i * 55;
      const hx = 1040;
      drawAtomNode(ctx, hx - 14, hy, "H", 0, "#e2e8f0", 14, 0);
      drawAtomNode(ctx, hx + 14, hy, "H", 0, "#e2e8f0", 14, 0);
    }

    // ── Comparison Frame if Comparing Counts ──
    if (t >= 2.5 && t <= 4.5 && feVis && fe3o4Vis) {
      drawComparisonFrame(ctx, feVis, fe3o4Vis, "Fe Atom Mismatch: 1 vs 3");
    }

    // ── Bottom Atom Conservation Inventory Board ──
    // Guaranteed NO SEESAW: Displays clean verified stoichiometry
    const invY = 570;
    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(80, invY, 1120, 110, 14);
    } else {
      ctx.rect(80, invY, 1120, 110);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("ATOM INVENTORY (MASS CONSERVATION TRACKER)", 100, invY + 24);

    // Table of elements
    const elements = [
      { name: "Iron (Fe)", left: feAtomCount, right: 3 },
      { name: "Hydrogen (H)", left: waterCount * 2, right: h2ProductCount * 2 },
      { name: "Oxygen (O)", left: waterCount, right: 4 },
    ];

    elements.forEach((el, idx) => {
      const colX = 100 + idx * 370;
      const rowY = invY + 58;
      const isMatched = el.left === el.right;

      ctx.fillStyle = "#f8fafc";
      ctx.font = "bold 15px system-ui, sans-serif";
      ctx.fillText(el.name, colX, rowY);

      // Counts pill
      ctx.fillStyle = isMatched ? "rgba(5, 150, 105, 0.25)" : "rgba(245, 158, 11, 0.25)";
      ctx.strokeStyle = isMatched ? "#10b981" : "#f59e0b";
      ctx.lineWidth = 1.0;
      ctx.beginPath();
      if (ctx.roundRect) {
        ctx.roundRect(colX + 160, rowY - 16, 140, 28, 8);
      } else {
        ctx.rect(colX + 160, rowY - 16, 140, 28);
      }
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = isMatched ? "#10b981" : "#fbbf24";
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "center";
      ctx.fillText(`${el.left} Left = ${el.right} Right ${isMatched ? "✓" : "≠"}`, colX + 230, rowY);
      ctx.textAlign = "left";
    });

    ctx.restore();
  }
}
