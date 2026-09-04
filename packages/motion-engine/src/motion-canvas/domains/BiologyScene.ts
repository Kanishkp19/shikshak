/**
 * Shikshak AI — Motion Canvas Biology Domain Scene.
 *
 * Specializes in:
 * - Photosynthesis: Light-dependent reactions on the thylakoid membrane
 * - Chlorophyll light absorption (incoming photon stream)
 * - Water photolysis: 2H2O -> 4H+ + O2 + 4e-
 * - Proton gradient accumulation in the thylakoid lumen
 * - ATP Synthase molecular rotor producing ATP from ADP + Pi
 */

import { ObjectRegistry, ResolvedObjectVisual } from "../core/ObjectRegistry";

export class BiologyScene {
  private registry: ObjectRegistry;

  constructor(registry: ObjectRegistry) {
    this.registry = registry;
    this.layoutObjects();
  }

  private layoutObjects(): void {
    this.registry.registerBounds("chlorophyll_complex", { minX: 180, minY: 280, maxX: 380, maxY: 460 });
    this.registry.registerBounds("water_splitting_site", { minX: 180, minY: 440, maxX: 400, maxY: 560 });
    this.registry.registerBounds("electron_transport_chain", { minX: 420, minY: 320, maxX: 720, maxY: 440 });
    this.registry.registerBounds("atp_synthase", { minX: 840, minY: 260, maxX: 1060, maxY: 540 });
    this.registry.registerBounds("lumen_zone", { minX: 100, minY: 420, maxX: 1180, maxY: 620 });
    this.registry.registerBounds("stroma_zone", { minX: 100, minY: 160, maxX: 1180, maxY: 340 });
  }

  public render(ctx: any, t: number, visuals: Map<string, ResolvedObjectVisual>): void {
    ctx.save();

    // Deep biological studio backdrop
    ctx.fillStyle = "#07141b";
    ctx.fillRect(0, 0, 1280, 720);

    // Subtle cellular membrane background texture
    ctx.fillStyle = "rgba(16, 185, 129, 0.05)";
    for (let x = 30; x < 1280; x += 60) {
      for (let y = 30; y < 720; y += 60) {
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Top Header Badge
    ctx.fillStyle = "rgba(16, 185, 129, 0.15)";
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 24, 300, 32, 16);
    } else {
      ctx.rect(50, 24, 300, 32);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#34d399";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText("🌿 BIOLOGY: LIGHT REACTION (THYLAKOID)", 68, 40);

    // Chemical equation banner
    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = "#064e3b";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(50, 75, 1180, 75, 14);
    } else {
      ctx.rect(50, 75, 1180, 75);
    }
    ctx.fill();
    ctx.stroke();

    ctx.font = "bold 24px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillStyle = "#34d399";
    ctx.fillText("PHOTOLYSIS & CHEMIOSMOSIS: 2H₂O + Light ⟶ 4H⁺ + O₂ + 4e⁻  |  ADP + Pᵢ ⟶ ATP", 640, 112);

    // ── Thylakoid Membrane Bilayer (Horizontal span: y = 340 to 420) ──
    const memY1 = 340;
    const memY2 = 420;

    // Stroma label (top) vs Lumen label (bottom)
    ctx.fillStyle = "#94a3b8";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("CHLOROPLAST STROMA (LOW H⁺ CONCENTRATION, pH ~ 8)", 80, 180);
    ctx.fillText("THYLAKOID LUMEN (HIGH H⁺ ACCUMULATION, pH ~ 5)", 80, 650);

    // Membrane lipid background strip
    ctx.fillStyle = "rgba(6, 78, 59, 0.5)";
    ctx.fillRect(50, memY1, 1180, memY2 - memY1);

    // Draw phospholipid heads (top and bottom rows)
    ctx.fillStyle = "#10b981";
    for (let x = 60; x < 1220; x += 18) {
      // Don't draw over embedded proteins (PSII: 220-340, ETC: 460-680, ATP Synthase: 860-980)
      if ((x >= 220 && x <= 340) || (x >= 460 && x <= 680) || (x >= 860 && x <= 980)) {
        continue;
      }
      // Top layer
      ctx.beginPath();
      ctx.arc(x, memY1, 6, 0, Math.PI * 2);
      ctx.fill();
      // Bottom layer
      ctx.beginPath();
      ctx.arc(x, memY2, 6, 0, Math.PI * 2);
      ctx.fill();
    }

    // ── 1. Photosystem II / Chlorophyll Complex (x: 230 to 330) ──
    const ps2Highlight = t >= 1.0 && t <= 4.0 ? 1.0 : 0.0;
    ctx.fillStyle = ps2Highlight ? "#059669" : "#047857";
    ctx.strokeStyle = "#34d399";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(230, 290, 100, 170, 20);
    } else {
      ctx.rect(230, 290, 100, 170);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 15px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("PS II", 280, 360);
    ctx.font = "12px system-ui, sans-serif";
    ctx.fillText("P680 Chl", 280, 385);

    // Incoming Sunlight Photons (Yellow light rays bouncing into PSII)
    const photonY = (t * 260) % 200;
    ctx.strokeStyle = "#facc15";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(200, 180 + photonY);
    ctx.lineTo(260, 240 + photonY);
    ctx.stroke();

    ctx.fillStyle = "#facc15";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.fillText("Sunlight (hν)", 250, 210);

    // Water Splitting (H2O -> 2H+ + 1/2 O2 + 2e-) at bottom of PS II
    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 14px system-ui, sans-serif";
    ctx.fillText("H₂O ⟶ 2H⁺ + ½O₂ + 2e⁻", 280, 490);

    // ── 2. Electron Transport Chain Cytochrome (x: 480 to 660) ──
    ctx.fillStyle = "#1e293b";
    ctx.strokeStyle = "#0284c7";
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(490, 310, 140, 130, 16);
    } else {
      ctx.rect(490, 310, 140, 130);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 14px system-ui, sans-serif";
    ctx.fillText("Cytochrome b₆f", 560, 365);
    ctx.font = "12px system-ui, sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("Proton Pump", 560, 390);

    // Animated Electron Transfer line (PSII -> Cyt b6f)
    ctx.strokeStyle = "#fef08a";
    ctx.lineWidth = 2.5;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(330, 360);
    ctx.lineTo(490, 360);
    ctx.stroke();
    ctx.setLineDash([]);

    // ── 3. ATP Synthase Molecular Motor (x: 880 to 980) ──
    const atpHighlight = t >= 5.0 ? 1.0 : 0.0;
    // Rotor stalk crossing membrane
    ctx.fillStyle = atpHighlight ? "#d97706" : "#b45309";
    ctx.strokeStyle = "#fbbf24";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(900, 330, 60, 110, 10);
    } else {
      ctx.rect(900, 330, 60, 110);
    }
    ctx.fill();
    ctx.stroke();

    // Rotating Catalytic Head (F1 subunit in Stroma)
    const rotorAngle = t * 4.0;
    ctx.save();
    ctx.translate(930, 270);
    ctx.rotate(rotorAngle);
    ctx.fillStyle = "#f59e0b";
    ctx.beginPath();
    ctx.arc(0, 0, 42, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.stroke();

    // 3 Catalytic lobes
    for (let i = 0; i < 3; i++) {
      const ang = (i * Math.PI * 2) / 3;
      ctx.fillStyle = "#78350f";
      ctx.beginPath();
      ctx.arc(Math.cos(ang) * 22, Math.sin(ang) * 22, 10, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.fillText("ATP Synthase", 930, 205);

    // ATP Synthesis callout
    if (t >= 5.0) {
      ctx.fillStyle = "#fbbf24";
      ctx.font = "bold 15px system-ui, sans-serif";
      ctx.fillText("ADP + Pᵢ ⟶ ATP ⚡", 930, 160);
    }

    // ── 4. Proton (H+) Gradient Particles in Lumen ──
    const protonCount = 18;
    ctx.fillStyle = "#f43f5e";
    ctx.font = "bold 11px system-ui, sans-serif";
    for (let i = 0; i < protonCount; i++) {
      const hx = 120 + ((i * 65 + t * 40) % 1040);
      const hy = 470 + (Math.sin(i + t * 2) * 45);

      ctx.beginPath();
      ctx.arc(hx, hy, 12, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#ffffff";
      ctx.fillText("H⁺", hx, hy + 4);
      ctx.fillStyle = "#f43f5e";
    }

    // Protons flowing upward through ATP Synthase channel into Stroma
    if (t >= 4.0) {
      const upwardY = 460 - ((t * 120) % 180);
      ctx.fillStyle = "#fbbf24";
      ctx.beginPath();
      ctx.arc(930, upwardY, 11, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#0f172a";
      ctx.fillText("H⁺", 930, upwardY + 4);
    }

    ctx.restore();
  }
}
