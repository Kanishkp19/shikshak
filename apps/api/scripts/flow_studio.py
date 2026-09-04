#!/usr/bin/env python3
"""
Shikshak AI — Flow Studio Companion CLI.

Speeds up Google Flow creation:
1. Auto-fills prompt, model, and 16:9 ratio in Google Flow (Option C).
2. You click Generate in Chrome.
3. Automatically ingests downloaded .mp4 into Supabase Storage & video_cache table.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

# Ensure apps/api is in sys.path
current_dir = Path(__file__).resolve().parent
api_root = current_dir.parent
workspace_root = api_root.parent.parent
if str(api_root) not in sys.path:
    sys.path.insert(0, str(api_root))

from scripts.populate_video_cache import populate_video_cache
from skills.caching import hash_prompt

MCP_DIR = workspace_root / "tools" / "google-flow-browser-mcp"


def formulate_flow_prompt(concept: str, visual_type: str, depth: str, narration: str = "") -> str:
    """Generate an optimized visual prompt tailored for Google Veo / Imagen in Google Flow."""
    clean_concept = (concept or "").strip()
    clean_narration = (narration or "")[:150].strip()

    style_guide = {
        "diagram": "Clear educational 3D infographic illustration, labelled elements, crisp motion",
        "equation": "Cinematic visual math animation with glowing formulas and graphical representation",
        "code": "Modern dynamic code visualization with illuminated syntax tree and execution flow",
        "animation": "High definition 3D scientific concept animation, smooth motion, realistic physics",
        "none": "Stunning textbook quality educational graphic illustration",
    }.get(visual_type, "3D educational science animation")

    depth_guide = {
        "beginner": "Intuitive, friendly, high-level visual overview with vivid clear shapes",
        "intermediate": "Detailed structural mechanisms with clear step-by-step interaction",
        "advanced": "Comprehensive deep-dive molecular and technical dynamics",
    }.get(depth, "Clear educational visual")

    prompt = (
        f"{style_guide} of {clean_concept}. "
        f"{depth_guide}. "
        f"{clean_narration} "
        f"Dark navy blue background (#0b1329), vibrant cyan and gold accents, cinematic lighting, 8k quality, no watermarks."
    )
    return prompt.strip()


def ensure_browser_running():
    """Ensure Chrome is running with remote debugging on port 9222."""
    check_cmd = ["curl", "-s", "http://localhost:9222/json/version"]
    res = subprocess.run(check_cmd, capture_output=True, text=True)
    if res.returncode == 0 and "Browser" in res.stdout:
        return True

    start_script = MCP_DIR / "scripts" / "start-browser.sh"
    if start_script.exists():
        print("🌐 Starting Chrome with remote debugging on port 9222...")
        subprocess.run(["bash", str(start_script)], check=False)
        time.sleep(2)
        return True
    return False


def setup_flow_ui(prompt: str, model: str = "Veo 3.1 - Fast", ratio: str = "16:9", duration: str = "6s"):
    """Call the MCP helper to auto-fill the Flow UI."""
    setup_script = MCP_DIR / "scripts" / "flow-setup.js"
    cmd = [
        "node",
        str(setup_script),
        "--prompt",
        prompt,
        "--model",
        model,
        "--ratio",
        ratio,
        "--duration",
        duration,
    ]
    subprocess.run(cmd, cwd=str(MCP_DIR), check=True)



def watch_and_ingest(concept: str, visual_type: str, depth: str, language: str = "en", timeout_seconds: int = 300):
    """Watch the user's Downloads folder for newly downloaded Flow video and auto-register it."""
    downloads_dir = Path.home() / "Downloads"
    print(f"👀 Watching {downloads_dir} for new .mp4 download (timeout: {timeout_seconds}s)...")
    start_time = time.time()
    initial_files = {p: p.stat().st_mtime for p in downloads_dir.glob("*.mp4")}

    while time.time() - start_time < timeout_seconds:
        current_files = list(downloads_dir.glob("*.mp4"))
        for f in current_files:
            mtime = f.stat().st_mtime
            if f not in initial_files or mtime > initial_files.get(f, 0):
                # File was created or updated after start
                # Wait for download to finish (size stops changing)
                time.sleep(1)
                print(f"\n🎉 Detected new downloaded clip: {f.name}")
                res = populate_video_cache(
                    file_path=f,
                    concept=concept,
                    visual_type=visual_type,
                    depth=depth,
                    language=language,
                )
                print(f"✅ Successfully ingested clip to Supabase with hash: {res['prompt_hash']}")
                return res
        time.sleep(2)

    print("⚠️ Timeout waiting for download. You can register manually with:")
    print(f"  python scripts/populate_video_cache.py --file <path> --concept \"{concept}\" --visual-type {visual_type} --depth {depth}")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Shikshak AI Flow Studio: Auto-fill Google Flow form and auto-ingest generated clips."
    )
    parser.add_argument(
        "--concept",
        required=True,
        type=str,
        help="Educational concept (e.g. 'Photosynthesis').",
    )
    parser.add_argument(
        "--visual-type",
        default="animation",
        choices=["diagram", "equation", "code", "animation", "none"],
        help="Visual style (default: 'animation').",
    )
    parser.add_argument(
        "--depth",
        default="beginner",
        choices=["beginner", "intermediate", "advanced"],
        help="Learning depth level.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language code (default: 'en').",
    )
    parser.add_argument(
        "--narration",
        default="",
        help="Optional narration text to guide prompt generation.",
    )
    parser.add_argument(
        "--model",
        default="Veo 3.1 - Fast",
        help="Google Flow model to select (default: 'Veo 3.1 - Fast').",
    )
    parser.add_argument(
        "--duration",
        default="6s",
        help="Duration in seconds (default: '6s').",
    )
    parser.add_argument(
        "--no-watch",
        action="store_true",
        help="Do not auto-watch Downloads folder for finished clip.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Directly ingest an already-downloaded file instead of opening Flow.",
    )

    args = parser.parse_args()

    if args.file:
        res = populate_video_cache(
            file_path=args.file,
            concept=args.concept,
            visual_type=args.visual_type,
            depth=args.depth,
            language=args.language,
        )
        print(f"✅ Ingested {args.file} into video_cache: {res['prompt_hash']}")
        return

    prompt = formulate_flow_prompt(args.concept, args.visual_type, args.depth, args.narration)
    prompt_hash = hash_prompt(args.concept, args.visual_type, args.depth, args.language)

    print("\n" + "=" * 65)
    print(" 🎬 Shikshak AI — Google Flow Studio Assistant")
    print("=" * 65)
    print(f" Concept     : {args.concept}")
    print(f" Visual Type : {args.visual_type}")
    print(f" Depth       : {args.depth}")
    print(f" Target Hash : {prompt_hash}")
    print("=" * 65)

    setup_flow_ui(prompt=prompt, model=args.model, ratio="16:9", duration=args.duration)

    if not args.no_watch:
        watch_and_ingest(
            concept=args.concept,
            visual_type=args.visual_type,
            depth=args.depth,
            language=args.language,
        )


if __name__ == "__main__":
    main()
