"""
Shikshak AI — Motion Canvas Primary Educational Scene Renderer.

Executes deterministic, camera-choreographed educational animation scenes
using Motion Canvas on Apple Silicon / Node.js:
  - Chemistry: Reaction kinetics, atom conservation & balancing (No seesaw)
  - Physics: IEC circuit schematics, switch closure, and electron drift
  - Biology: Photosynthesis thylakoid reactions, proton gradient & ATP synthase
  - Mathematics: Step-by-step quadratic equation derivations with term continuity
  - Motion Graphics: Multi-step process flows, kinetic principles & spotlight cards

Guarantees:
  1. Coordinate Invariant: LLM provides structured semantic intent only.
  2. Deterministic SHA-256 caching for instant replay & remediation reuse.
  3. Graceful Fallback: Auto-falls back to Flick / Remotion or CairoSVG on error.
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

from models.animation_spec import AnimationSceneSpec
from skills.video_generation.media import require_playable_video

logger = logging.getLogger(__name__)

# Root workspace path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
MOTION_ENGINE_DIR = WORKSPACE_ROOT / "packages" / "motion-engine"
MOTION_CANVAS_SCRIPT = MOTION_ENGINE_DIR / "src" / "motion-canvas" / "render.ts"
CACHE_DIR = Path("/tmp/shikshak_cache/motion_canvas")


def compute_motion_canvas_cache_key(
    spec_data: dict[str, Any],
    duration_seconds: float,
    engine_version: str = "v1.5_mc",
) -> str:
    """Compute a deterministic SHA-256 hash for Motion Canvas scene caching."""
    hasher = hashlib.sha256()
    payload_str = json.dumps(spec_data, sort_keys=True, default=str)
    hasher.update(payload_str.encode("utf-8"))
    hasher.update(f"{duration_seconds:.2f}".encode("utf-8"))
    hasher.update(engine_version.encode("utf-8"))
    return hasher.hexdigest()


def render_motion_canvas_spec(
    spec: AnimationSceneSpec | dict[str, Any],
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render an AnimationSceneSpec using the headless Motion Canvas engine to 1280x720 H.264 MP4."""
    duration_seconds = max(2.0, min(90.0, float(duration_seconds)))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if isinstance(spec, AnimationSceneSpec):
        spec_dict = spec.model_dump(by_alias=True)
    else:
        spec_dict = dict(spec)

    spec_dict["duration"] = duration_seconds

    if out_path is None:
        target_path = Path("/tmp/shikshak_scenes") / f"mc_{uuid.uuid4().hex}.mp4"
    else:
        target_path = Path(out_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Check Scene Cache ───────────────────────────────────────────────────
    cache_key = compute_motion_canvas_cache_key(spec_dict, duration_seconds)
    cached_file = CACHE_DIR / f"{cache_key}.mp4"
    if cached_file.exists():
        try:
            require_playable_video(str(cached_file), min_width=640, min_height=360, min_duration_seconds=1.0)
            shutil.copy(str(cached_file), str(target_path))
            logger.info("[MotionCanvas] Cache HIT for scene hash: %s", cache_key)
            return target_path
        except Exception:
            cached_file.unlink(missing_ok=True)

    # ── Write Spec to Scratch File ──────────────────────────────────────────
    scratch_dir = WORKSPACE_ROOT / "packages" / "motion-engine" / ".cache"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    spec_file = scratch_dir / f"spec_{uuid.uuid4().hex}.json"
    spec_file.write_text(json.dumps(spec_dict, indent=2), encoding="utf-8")

    # ── Execute Motion Canvas CLI ────────────────────────────────────────────
    try:
        cmd = [
            "npx",
            "tsx",
            str(MOTION_CANVAS_SCRIPT),
            "--spec", str(spec_file),
            "--out", str(target_path),
            "--fps", "30",
        ]

        logger.info("[MotionCanvas] Running: %s", " ".join(cmd))
        proc = subprocess.run(
            cmd,
            cwd=str(MOTION_ENGINE_DIR),
            capture_output=True,
            text=True,
            timeout=180,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Motion Canvas render failed (code {proc.returncode}): {proc.stderr or proc.stdout}")

        require_playable_video(str(target_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

        # Store in cache
        shutil.copy(str(target_path), str(cached_file))
        logger.info("[MotionCanvas] Rendered and cached scene to: %s", target_path)
        return target_path

    except Exception as exc:
        logger.warning(
            "[MotionCanvas] Render failed: %s. Initiating graceful fallback.",
            exc,
        )
        # Graceful fallback to generic explainer
        from skills.scene_renderers.chemistry import render_generic_explainer
        fallback_payload = {
            "title": spec_dict.get("sceneId") or "Lesson Concept",
            "key_points": [obj.get("pedagogicalPurpose") or obj.get("id") for obj in spec_dict.get("objects", [])[:4]] or ["Concept Overview"],
            "equation": f"Domain: {spec_dict.get('domain', 'general')}",
        }
        return render_generic_explainer(
            payload_dict=fallback_payload,
            narration_text="",
            duration_seconds=duration_seconds,
            out_path=out_path,
        )
    finally:
        spec_file.unlink(missing_ok=True)
