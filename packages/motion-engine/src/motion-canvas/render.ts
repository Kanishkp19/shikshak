/**
 * Shikshak AI — Headless Motion Canvas Render Engine.
 *
 * Runs deterministic frame-by-frame rendering of AnimationSceneSpec directly to H.264 MP4:
 * 1. Reads AnimationSceneSpec JSON.
 * 2. Initializes CameraSystem and ObjectRegistry.
 * 3. Resolves domain-specific scenes (Chemistry, Physics, Biology, Math, General).
 * 4. Renders 1280x720 frames at 30 fps using accelerated canvas.
 * 5. Streams PNG buffers directly to FFmpeg stdin for zero-temp-file, high-throughput rendering.
 */

import fs from "fs";
import path from "path";
import { spawn } from "child_process";
import { createCanvas } from "@napi-rs/canvas";

import { AnimationSceneSpec } from "../types/animation-spec";
import { CameraSystem } from "./core/CameraSystem";
import { ObjectRegistry } from "./core/ObjectRegistry";
import { ChemistryScene } from "./domains/ChemistryScene";
import { PhysicsScene } from "./domains/PhysicsScene";
import { BiologyScene } from "./domains/BiologyScene";
import { MathematicsScene } from "./domains/MathematicsScene";

interface RenderOptions {
  specPath: string;
  outPath: string;
  fps?: number;
}

export async function renderMotionCanvasScene(options: RenderOptions): Promise<string> {
  const { specPath, outPath, fps = 30 } = options;

  if (!fs.existsSync(specPath)) {
    throw new Error(`Spec file not found: ${specPath}`);
  }

  const raw = fs.readFileSync(specPath, "utf-8");
  const spec: AnimationSceneSpec = JSON.parse(raw);

  const width = spec.width ?? 1280;
  const height = spec.height ?? 720;
  const duration = spec.duration ?? 6.0;
  const totalFrames = Math.max(1, Math.round(duration * fps));

  const outDir = path.dirname(outPath);
  fs.mkdirSync(outDir, { recursive: true });

  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");

  // Initialize Core Subsystems
  const registry = new ObjectRegistry(spec.objects ?? [], spec.beats ?? []);
  const camera = new CameraSystem(width, height, (targetIds) => registry.getBounds(targetIds));
  if (spec.camera) {
    camera.setKeyframes(spec.camera);
  }

  // Initialize Domain Scene
  let sceneRenderer: { render: (ctx: any, t: number, visuals: any) => void };
  const domain = (spec.domain || "general").toLowerCase();

  if (domain === "chemistry") {
    sceneRenderer = new ChemistryScene(registry);
  } else if (domain === "physics") {
    sceneRenderer = new PhysicsScene(registry);
  } else if (domain === "biology") {
    sceneRenderer = new BiologyScene(registry);
  } else if (domain === "mathematics") {
    sceneRenderer = new MathematicsScene(registry);
  } else {
    // Default to Chemistry or general fallback
    sceneRenderer = new ChemistryScene(registry);
  }

  console.log(`[MotionCanvas] Rendering ${spec.sceneId} (${domain}): ${totalFrames} frames (${duration}s @ ${fps}fps) -> ${outPath}`);

  const ffmpegCmd = "ffmpeg";
  const ffmpegArgs = [
    "-y",
    "-f", "image2pipe",
    "-vcodec", "png",
    "-r", `${fps}`,
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    "-t", `${duration}`,
    outPath,
  ];

  const ffmpegProc = spawn(ffmpegCmd, ffmpegArgs, { stdio: ["pipe", "ignore", "pipe"] });

  let stderrOutput = "";
  ffmpegProc.stderr.on("data", (chunk) => {
    stderrOutput += chunk.toString();
  });

  const writeFrame = (buf: Buffer): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!ffmpegProc.stdin.write(buf)) {
        ffmpegProc.stdin.once("drain", resolve);
      } else {
        process.nextTick(resolve);
      }
    });
  };

  const startTime = Date.now();

  for (let frame = 0; frame < totalFrames; frame++) {
    const t = frame / fps;
    const visuals = registry.resolveVisualsAt(t);
    const camState = camera.getStateAt(t);

    ctx.save();
    // Render the domain scene
    sceneRenderer.render(ctx, t, visuals);
    ctx.restore();

    // Export frame as PNG buffer
    const buf = canvas.toBuffer("image/png");
    await writeFrame(buf);
  }

  ffmpegProc.stdin.end();

  await new Promise<void>((resolve, reject) => {
    ffmpegProc.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`FFmpeg exited with code ${code}: ${stderrOutput}`));
      }
    });
    ffmpegProc.on("error", reject);
  });

  const elapsedMs = Date.now() - startTime;
  console.log(`[MotionCanvas] Successfully rendered ${outPath} in ${(elapsedMs / 1000).toFixed(2)}s`);

  return outPath;
}

// ── CLI Invocation ──
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  let specPath = "";
  let outPath = "/tmp/shikshak_scenes/motion_canvas_output.mp4";
  let fps = 30;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--spec" && args[i + 1]) {
      specPath = args[i + 1];
      i++;
    } else if (args[i] === "--out" && args[i + 1]) {
      outPath = args[i + 1];
      i++;
    } else if (args[i] === "--fps" && args[i + 1]) {
      fps = parseInt(args[i + 1], 10);
      i++;
    }
  }

  if (!specPath) {
    console.error("Usage: tsx render.ts --spec <spec.json> --out <output.mp4>");
    process.exit(1);
  }

  renderMotionCanvasScene({ specPath, outPath, fps })
    .then((p) => {
      console.log(`[MotionCanvas] Output ready: ${p}`);
      process.exit(0);
    })
    .catch((err) => {
      console.error("[MotionCanvas] Render failed:", err);
      process.exit(1);
    });
}
