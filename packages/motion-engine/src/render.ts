import path from "path";
import fs from "fs";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { MotionSceneProps } from "./types";

// Ensure Chrome on macOS is detected
const CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

async function main() {
  const args = process.argv.slice(2);
  let propsArg = "{}";
  let outPath = "/tmp/shikshak_scenes/remotion_output.mp4";
  let durationSeconds = 6;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--props" && args[i + 1]) {
      propsArg = args[i + 1];
      i++;
    } else if (args[i] === "--out" && args[i + 1]) {
      outPath = args[i + 1];
      i++;
    } else if (args[i] === "--duration" && args[i + 1]) {
      durationSeconds = parseFloat(args[i + 1]);
      i++;
    }
  }

  let inputProps: MotionSceneProps = {
    template: "step_by_step_flow",
    title: "Lesson Scene",
    steps: ["Step 1", "Step 2", "Step 3"],
    durationSeconds,
  };

  try {
    if (fs.existsSync(propsArg)) {
      const fileContent = fs.readFileSync(propsArg, "utf-8");
      inputProps = { ...inputProps, ...JSON.parse(fileContent) };
    } else {
      inputProps = { ...inputProps, ...JSON.parse(propsArg) };
    }
  } catch (err) {
    console.error("Failed to parse props JSON:", err);
  }

  inputProps.durationSeconds = durationSeconds;

  // Ensure output directory exists
  const outDir = path.dirname(outPath);
  fs.mkdirSync(outDir, { recursive: true });

  const srcEntry = path.resolve(import.meta.dirname, "../src/index.ts");
  const distEntry = path.resolve(import.meta.dirname, "index.js");
  const entryPoint = fs.existsSync(srcEntry) ? srcEntry : distEntry;

  console.log(`[MotionEngine] Bundling Remotion composition from ${entryPoint}...`);
  const bundleLocation = await bundle({
    entryPoint,
    // Webpack caching for speed
    webpackOverride: (config) => config,
  });

  const browserExecutable = fs.existsSync(CHROME_PATH) ? CHROME_PATH : undefined;

  console.log(`[MotionEngine] Selecting composition 'MotionScene'...`);
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: "MotionScene",
    inputProps: inputProps as unknown as Record<string, unknown>,
    browserExecutable,
  });

  console.log(`[MotionEngine] Rendering video to ${outPath} (${composition.durationInFrames} frames)...`);
  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: outPath,
    inputProps: inputProps as unknown as Record<string, unknown>,
    browserExecutable,
    concurrency: 1,
    scale: 1,
    imageFormat: "png",
    logLevel: "warn",
  });

  console.log(`[MotionEngine] Successfully rendered: ${outPath}`);
}

main().catch((err) => {
  console.error("[MotionEngine] Render error:", err);
  process.exit(1);
});
