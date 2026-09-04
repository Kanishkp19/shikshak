import { Config } from "@remotion/cli/config";
import fs from "fs";

Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
if (fs.existsSync(chromePath)) {
  Config.setBrowserExecutable(chromePath);
}
