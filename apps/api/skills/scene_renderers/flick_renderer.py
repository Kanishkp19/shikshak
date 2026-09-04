"""
Shikshak AI — Flick / Remotion Motion Graphics Scene Renderer.

Executes deterministic Remotion motion templates across all subjects:
  - StepByStepFlow (Photosynthesis, biochemical pathways, multi-step reactions)
  - AnimatedTitle (Kinetic typography title cards)
  - ConceptHighlight (Core laws, definitions, spotlight cards)
  - Comparison (Side-by-side comparative analysis)
  - Timeline (Milestones and sequential chronologies)
  - DiagramBuild (Progressive module assembly)
  - TextReveal (Staggered educational definition reveals)

Guarantees:
  1. Coordinate Invariant: LLM provides structured semantic data only.
  2. Deterministic SHA-256 caching for instant replay & remediation reuse.
  3. Graceful Fallback: Auto-falls back to CairoSVG generic_explainer on error.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from skills.video_generation.media import require_playable_video
from skills.scene_renderers.chemistry import render_generic_explainer

logger = logging.getLogger(__name__)

# Root workspace path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
MOTION_ENGINE_DIR = WORKSPACE_ROOT / "packages" / "motion-engine"
MOTION_RENDER_SCRIPT = MOTION_ENGINE_DIR / "dist" / "render.js"
CACHE_DIR = Path("/tmp/shikshak_cache/flick")


def _compute_cache_key(
    payload: dict[str, Any],
    narration_text: str,
    duration_seconds: float,
    template_version: str = "v1.0",
) -> str:
    """Compute a deterministic SHA-256 hash for scene caching."""
    hasher = hashlib.sha256()
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    hasher.update(payload_str.encode("utf-8"))
    hasher.update(narration_text.strip().encode("utf-8"))
    hasher.update(f"{duration_seconds:.2f}".encode("utf-8"))
    hasher.update(template_version.encode("utf-8"))
    return hasher.hexdigest()


def render_flick_motion(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render a structured motion scene to 1280x720 H.264 MP4 using Remotion."""
    duration_seconds = max(2.0, min(90.0, float(duration_seconds)))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if out_path is None:
        target_path = Path("/tmp/shikshak_scenes") / f"flick_{uuid.uuid4().hex}.mp4"
    else:
        target_path = Path(out_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Check Scene Cache ───────────────────────────────────────────────────
    cache_key = _compute_cache_key(payload_dict, narration_text, duration_seconds)
    cached_file = CACHE_DIR / f"{cache_key}.mp4"
    if cached_file.exists():
        try:
            require_playable_video(str(cached_file), min_width=640, min_height=360, min_duration_seconds=1.0)
            shutil.copy(str(cached_file), str(target_path))
            logger.info("[FlickRenderer] Cache HIT for scene hash: %s", cache_key)
            return target_path
        except Exception:
            cached_file.unlink(missing_ok=True)

    # ── Prepare Remotion Input Props ────────────────────────────────────────
    template = payload_dict.get("template") or "step_by_step_flow"
    title = payload_dict.get("title") or "Core Mechanism"
    subtitle = payload_dict.get("subtitle") or narration_text[:100]
    steps = payload_dict.get("steps") or []
    elements = payload_dict.get("elements") or []
    key_takeaway = payload_dict.get("key_takeaway") or ""
    accent_color = payload_dict.get("accent_color") or "#38bdf8"
    badge = payload_dict.get("badge") or "PROCESS FLOW"

    props = {
        "template": template,
        "title": title,
        "subtitle": subtitle,
        "steps": steps,
        "elements": elements,
        "keyTakeaway": key_takeaway,
        "accentColor": accent_color,
        "badge": badge,
        "narrationText": narration_text,
        "durationSeconds": duration_seconds,
    }

    props_file = Path("/tmp/shikshak_scenes") / f"props_{uuid.uuid4().hex}.json"
    props_file.write_text(json.dumps(props, indent=2), encoding="utf-8")

    # ── Execute Remotion Engine ──────────────────────────────────────────────
    try:
        # Check if compiled dist/render.js exists
        if not MOTION_RENDER_SCRIPT.exists():
            logger.info("[FlickRenderer] Building motion-engine dist/render.js...")
            build_res = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(MOTION_ENGINE_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if build_res.returncode != 0:
                raise RuntimeError(f"Failed to build motion-engine: {build_res.stderr}")

        cmd = [
            "node",
            str(MOTION_RENDER_SCRIPT),
            "--props", str(props_file),
            "--out", str(target_path),
            "--duration", f"{duration_seconds:.2f}",
        ]

        logger.info("[FlickRenderer] Running: %s", " ".join(cmd))
        proc = subprocess.run(
            cmd,
            cwd=str(MOTION_ENGINE_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Remotion render failed (code {proc.returncode}): {proc.stderr or proc.stdout}")

        require_playable_video(str(target_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

        # Store in cache
        shutil.copy(str(target_path), str(cached_file))
        logger.info("[FlickRenderer] Rendered and cached scene to: %s", target_path)
        return target_path

    except Exception as exc:
        logger.warning(
            "[FlickRenderer] Remotion rendering failed: %s. Initiating graceful fallback to generic_explainer.",
            exc,
        )
        target_path.unlink(missing_ok=True)
        # Graceful fallback to deterministic CairoSVG generic explainer
        fallback_payload = {
            "title": title,
            "key_points": steps[:4] if steps else [key_takeaway or "Core process mechanism."],
            "icons": ["sparkles", "atom"],
            "equation": "",
        }
        return render_generic_explainer(
            payload_dict=fallback_payload,
            narration_text=narration_text,
            duration_seconds=duration_seconds,
            out_path=target_path,
        )
    finally:
        props_file.unlink(missing_ok=True)
