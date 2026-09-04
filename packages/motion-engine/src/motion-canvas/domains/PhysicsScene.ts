/**
 * Shikshak AI — Motion Canvas Physics Domain Scene.
 *
 * Specializes in:
 * - Deterministic IEC 60617 circuit schematic rendering
 * - Animated switch closure (open -> closed)
 * - Directional electron / charge particle drift flow along circuit wire paths
 * - Resistor potential drop visualization (Ohm's law: V = I * R)
 * - Semantic focus and causal trigger realization
 */

import { ObjectRegistry, ResolvedObjectVisual } from "../core/ObjectRegistry";

export class PhysicsScene {
  private registry: ObjectRegistry;

  constructor(registry: ObjectRegistry) {
    this.registry = registry;
    this.layoutObjects();
  }

  private layoutObjects(): void {
    this.registry.registerBounds("battery", { minX: 180, minY: 300, maxX: 280, maxY: 420 });
    this.registry.registerBounds("switch", { minX: 580, minY: 150, maxX: 700, maxY: 230 });
    this.registry.registerBounds("resistor", { minX: 980, minY: 300, maxX: 1100, maxY: 420 });
    this.registry.registerBounds("circuit_loop", { minX: 180, minY: 180, maxX: 1080, maxY: 540 });
  }

  public render(ctx: any, t: number, visuals: Map<string, ResolvedObjectVisual>): void {
    ctx.save();

    // Dark technical schematic canvas
    ctx.fillStyle = "#070d1e";
    ctx.fillRect(0, 0, 1280, 720);

    // Subtle electrical schematic grid
    ctx.fillStyle = "rgba(56, 189, 248, 0.05)";
    for (let x = 40; x < 1280; x += 40) {
      for (let y = 40; y < 720; y += 40) {
        ctx.beginPath();
        ctx.arc(x, y, 1.0, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Top Badge
    ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 24, 270, 32, 16);
    } else {
      ctx.rect(50, 24, 270, 32);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText("⚡ PHYSICS: CIRCUIT DYNAMICS", 68, 40);

    // Circuit parameters
    const voltage = 12.0; // Volts
    const resistance = 6.0; // Ohms
    const switchClosed = t >= 2.5; // Switch closes at t = 2.5s
    const current = switchClosed ? voltage / resistance : 0.0; // 2.0 Amperes

    // Formula Banner at top
    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 75, 1180, 75, 14);
    } else {
      ctx.rect(50, 75, 1180, 75);
    }
    ctx.fill();
    ctx.stroke();

    ctx.font = "bold 26px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillStyle = switchClosed ? "#38bdf8" : "#94a3b8";
    ctx.fillText("OHM'S LAW: V = I × R", 640, 112);

    // ── Circuit Wire Path (1280x720 coordinates) ──
    const leftX = 240;
    const rightX = 1040;
    const topY = 200;
    const bottomY = 520;

    // Main circuit wire
    ctx.strokeStyle = switchClosed ? "#0284c7" : "#475569";
    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    ctx.beginPath();
    // Bottom wire: rightX -> leftX
    ctx.moveTo(rightX, bottomY);
    ctx.lineTo(leftX, bottomY);
    // Left vertical wire through battery
    ctx.lineTo(leftX, 420);
    ctx.moveTo(leftX, 300);
    ctx.lineTo(leftX, topY);
    // Top wire to switch
    ctx.lineTo(600, topY);
    ctx.moveTo(680, topY);
    ctx.lineTo(rightX, topY);
    // Right vertical wire through resistor
    ctx.lineTo(rightX, 300);
    ctx.moveTo(rightX, 420);
    ctx.lineTo(rightX, bottomY);
    ctx.stroke();

    // ── Battery (IEC Symbol at Left) ──
    // Long line (+), short thick line (-)
    const batY = 360;
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 3;
    // Long plate (+)
    ctx.beginPath();
    ctx.moveTo(leftX - 35, batY - 20);
    ctx.lineTo(leftX + 35, batY - 20);
    ctx.stroke();
    // Short thick plate (-)
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(leftX - 18, batY + 20);
    ctx.lineTo(leftX + 18, batY + 20);
    ctx.stroke();

    // Battery labels
    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 16px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("+", leftX - 45, batY - 20);
    ctx.fillText("–", leftX - 45, batY + 20);
    ctx.fillText("Battery 12V", leftX - 70, batY);

    // ── Switch (Top Wire, Center: 600 -> 680) ──
    ctx.fillStyle = "#ffffff";
    // Terminal contact dots
    ctx.beginPath();
    ctx.arc(600, topY, 6, 0, Math.PI * 2);
    ctx.arc(680, topY, 6, 0, Math.PI * 2);
    ctx.fill();

    // Switch arm: rotates from 35 degrees open to 0 degrees closed
    const switchAngle = switchClosed ? 0.0 : -Math.PI / 5;
    const armLen = 80;
    const armEndX = 600 + Math.cos(switchAngle) * armLen;
    const armEndY = topY + Math.sin(switchAngle) * armLen;

    ctx.strokeStyle = switchClosed ? "#10b981" : "#f59e0b";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(600, topY);
    ctx.lineTo(armEndX, armEndY);
    ctx.stroke();

    ctx.fillStyle = switchClosed ? "#10b981" : "#f59e0b";
    ctx.font = "bold 14px system-ui, sans-serif";
    ctx.fillText(switchClosed ? "Switch: CLOSED" : "Switch: OPEN", 640, topY - 30);

    // ── Resistor (IEC Zigzag or Box Symbol at Right) ──
    ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(rightX - 30, 300, 60, 120, 8);
    } else {
      ctx.rect(rightX - 30, 300, 60, 120);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 16px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("R", rightX, 350);
    ctx.font = "bold 14px system-ui, sans-serif";
    ctx.fillText("6.0 Ω", rightX, 375);

    // ── Current Flow Particle Animation (When Closed) ──
    if (switchClosed) {
      const particleCount = 20;
      const speed = 240; // pixels per second
      const perimeter = 2 * (rightX - leftX) + 2 * (bottomY - topY);

      ctx.fillStyle = "#fef08a"; // Yellow glowing electrons
      ctx.shadowColor = "#facc15";
      ctx.shadowBlur = 10;

      for (let i = 0; i < particleCount; i++) {
        // Continuous loop offset
        const dist = ((t - 2.5) * speed + (i * perimeter) / particleCount) % perimeter;
        let px = leftX;
        let py = topY;

        // Trace clockwise loop: Top (left -> right), Right (top -> bottom), Bottom (right -> left), Left (bottom -> top)
        const topLen = rightX - leftX;
        const rightLen = bottomY - topY;
        const bottomLen = topLen;

        if (dist < topLen) {
          px = leftX + dist;
          py = topY;
        } else if (dist < topLen + rightLen) {
          px = rightX;
          py = topY + (dist - topLen);
        } else if (dist < topLen + rightLen + bottomLen) {
          px = rightX - (dist - topLen - rightLen);
          py = bottomY;
        } else {
          px = leftX;
          py = bottomY - (dist - topLen - rightLen - bottomLen);
        }

        ctx.beginPath();
        ctx.arc(px, py, 4.5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    }

    // ── Active Telemetry Meters at Bottom ──
    const meterY = 590;
    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(80, meterY, 1120, 95, 14);
    } else {
      ctx.rect(80, meterY, 1120, 95);
    }
    ctx.fill();
    ctx.stroke();

    ctx.textAlign = "left";
    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.fillText("CIRCUIT TELEMETRY & MEASUREMENTS", 110, meterY + 26);

    const stats = [
      { label: "Applied Voltage (V)", val: "12.0 V", status: "Active" },
      { label: "Circuit Resistance (R)", val: "6.0 Ω", status: "Fixed" },
      { label: "Measured Current (I)", val: `${current.toFixed(1)} A`, status: switchClosed ? "Flowing" : "Zero" },
    ];

    stats.forEach((st, idx) => {
      const colX = 110 + idx * 370;
      const rowY = meterY + 62;
      ctx.fillStyle = "#94a3b8";
      ctx.font = "bold 14px system-ui, sans-serif";
      ctx.fillText(st.label, colX, rowY);

      ctx.fillStyle = switchClosed ? "#10b981" : "#f8fafc";
      ctx.font = "bold 20px monospace";
      ctx.fillText(st.val, colX + 220, rowY);
    });

    ctx.restore();
  }
}
