/**
 * Shikshak AI — Motion Canvas Mathematics Domain Scene.
 *
 * Specializes in:
 * - Step-by-step algebraic equation transformations with term continuity
 * - Quadratic equation derivation:
 *     1. ax² + bx + c = 0
 *     2. Divide by a: x² + (b/a)x + c/a = 0
 *     3. Transpose constant: x² + (b/a)x = -c/a
 *     4. Complete the square: x² + (b/a)x + (b/2a)² = (b/2a)² - c/a
 *     5. Factor left side: (x + b/2a)² = (b² - 4ac)/(4a²)
 *     6. Square root both sides: x + b/2a = ±√(b² - 4ac)/(2a)
 *     7. Final Quadratic Formula: x = (-b ± √(b² - 4ac)) / 2a
 * - Focus and camera tracking on the active transformed term
 */

import { ObjectRegistry, ResolvedObjectVisual } from "../core/ObjectRegistry";

interface MathStep {
  title: string;
  expression: string;
  rule: string;
  targetTerms: string[];
}

export class MathematicsScene {
  private registry: ObjectRegistry;

  constructor(registry: ObjectRegistry) {
    this.registry = registry;
    this.layoutObjects();
  }

  private layoutObjects(): void {
    this.registry.registerBounds("step_1", { minX: 160, minY: 140, maxX: 1120, maxY: 210 });
    this.registry.registerBounds("step_2", { minX: 160, minY: 220, maxX: 1120, maxY: 290 });
    this.registry.registerBounds("step_3", { minX: 160, minY: 300, maxX: 1120, maxY: 370 });
    this.registry.registerBounds("step_4", { minX: 160, minY: 380, maxX: 1120, maxY: 450 });
    this.registry.registerBounds("step_5", { minX: 160, minY: 460, maxX: 1120, maxY: 530 });
    this.registry.registerBounds("step_final", { minX: 160, minY: 540, maxX: 1120, maxY: 660 });
  }

  public render(ctx: any, t: number, visuals: Map<string, ResolvedObjectVisual>): void {
    ctx.save();

    // Deep mathematical navy chalkboard / studio surface
    ctx.fillStyle = "#0c1524";
    ctx.fillRect(0, 0, 1280, 720);

    // Subtle coordinate graph lines
    ctx.strokeStyle = "rgba(56, 189, 248, 0.04)";
    ctx.lineWidth = 1;
    for (let x = 0; x < 1280; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 720);
      ctx.stroke();
    }
    for (let y = 0; y < 720; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(1280, y);
      ctx.stroke();
    }

    // Top Header Badge
    ctx.fillStyle = "rgba(168, 85, 247, 0.15)";
    ctx.strokeStyle = "#a855f7";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 24, 340, 32, 16);
    } else {
      ctx.rect(50, 24, 340, 32);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#c084fc";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText("📐 MATHEMATICS: QUADRATIC DERIVATION", 68, 40);

    const steps: MathStep[] = [
      {
        title: "1. Standard Quadratic Equation",
        expression: "a x²  +  b x  +  c  =  0",
        rule: "Standard Form (a ≠ 0)",
        targetTerms: ["a x²", "b x", "c"],
      },
      {
        title: "2. Divide by leading coefficient (a)",
        expression: "x²  +  (b / a) x  +  (c / a)  =  0",
        rule: "Division Property of Equality",
        targetTerms: ["x²", "(b/a)x"],
      },
      {
        title: "3. Transpose constant term to right side",
        expression: "x²  +  (b / a) x  =  - (c / a)",
        rule: "Subtract (c/a) from both sides",
        targetTerms: ["- (c/a)"],
      },
      {
        title: "4. Complete the square by adding (b / 2a)²",
        expression: "x²  +  (b / a) x  +  (b / 2a)²  =  (b / 2a)²  -  (c / a)",
        rule: "Add (b/2a)² = b² / (4a²) to both sides",
        targetTerms: ["(b / 2a)²"],
      },
      {
        title: "5. Factor left side as a perfect square",
        expression: "(x  +  b / 2a)²  =  (b² - 4 a c) / (4 a²)",
        rule: "Perfect Square Binomial",
        targetTerms: ["(x + b/2a)²"],
      },
      {
        title: "6. Take square root and solve for x",
        expression: "x  =  ( - b  ±  √(b² - 4 a c) )  /  (2 a)",
        rule: "The Quadratic Formula",
        targetTerms: ["x = (-b ± √(b² - 4ac)) / 2a"],
      },
    ];

    // Determine how many steps to display based on progress time t
    // Total scene ~10-12s, reveal step every ~1.8s
    const visibleStepsCount = Math.min(steps.length, Math.max(1, Math.floor(t / 1.7) + 1));
    const activeStepIdx = visibleStepsCount - 1;

    for (let i = 0; i < visibleStepsCount; i++) {
      const step = steps[i];
      const stepY = 85 + i * 85;
      const isActive = i === activeStepIdx;
      const isFinal = i === steps.length - 1;

      // Card container for step
      ctx.fillStyle = isActive
        ? isFinal
          ? "rgba(168, 85, 247, 0.22)"
          : "rgba(30, 41, 59, 0.9)"
        : "rgba(15, 23, 42, 0.6)";

      ctx.strokeStyle = isActive
        ? isFinal
          ? "#c084fc"
          : "#38bdf8"
        : "#1e293b";

      ctx.lineWidth = isActive ? 2.0 : 1.0;

      ctx.beginPath();
      if (ctx.roundRect) {
        ctx.roundRect(80, stepY, 1120, 74, 12);
      } else {
        ctx.rect(80, stepY, 1120, 74);
      }
      ctx.fill();
      ctx.stroke();

      // Step title & justification rule
      ctx.textAlign = "left";
      ctx.font = "bold 12px system-ui, sans-serif";
      ctx.fillStyle = isActive ? "#38bdf8" : "#94a3b8";
      ctx.fillText(step.title, 100, stepY + 20);

      ctx.textAlign = "right";
      ctx.font = "italic 12px system-ui, sans-serif";
      ctx.fillStyle = "#64748b";
      ctx.fillText(`[${step.rule}]`, 1170, stepY + 20);

      // Mathematical expression text
      ctx.textAlign = "center";
      ctx.font = isFinal ? "bold 26px monospace" : "bold 22px monospace";
      ctx.fillStyle = isFinal ? "#fef08a" : isActive ? "#ffffff" : "#cbd5e1";
      ctx.fillText(step.expression, 640, stepY + 52);
    }

    ctx.restore();
  }
}
