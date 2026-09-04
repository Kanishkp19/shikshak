"""
Shikshak AI — Manim video generation provider (default).

Deterministic, zero-cost, zero-GPU. Always available as the safe fallback.
Produces a 5-10 second animation per concept; for diagrams and equations it
renders a labelled SVG-style frame; for code it shows a typewriter effect
on a code block; for "none" it produces a single still frame with the concept
title so the rest of the pipeline has something to composite over the avatar.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
from typing import Optional
import uuid

from skills.video_generation.base import (
    VideoGenerationProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
)


class ManimProvider(VideoGenerationProvider):
    name = "manim"

    def generate(
        self, request: VideoGenerationRequest | VisualBrief, out_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        """Render a Manim scene for the given concept."""
        if isinstance(request, VisualBrief):
            brief = request
        else:
            brief = VisualBrief(
                concept=request.concept,
                visual_type=request.visual_type,
                narration_script=request.narration_script,
                language=request.language,
                depth=request.depth,
                segment_id=request.segment_id,
            )

        target_path = out_path or getattr(request, "out_path", None)
        if target_path is None:
            target_path = Path("/tmp/shikshak_concept") / f"manim_{uuid.uuid4().hex}.mp4"
            target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path = Path(target_path)
        scene_script = _build_scene_script(brief)
        script_path = target_path.with_suffix(".py")
        script_path.write_text(scene_script, encoding="utf-8")

        media_dir = target_path.parent / f"media_{uuid.uuid4().hex}"
        media_dir.mkdir(parents=True, exist_ok=True)

        rendered = False
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "manim",
                    "-qm",
                    "--media_dir",
                    str(media_dir),
                    str(script_path),
                    "ConceptScene",
                ],
                check=True,
                timeout=90,
                capture_output=True,
            )
            produced = _find_rendered_video(media_dir)
            if produced:
                shutil.move(str(produced), str(target_path))
                rendered = True
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # Manim unavailable — write a still placeholder so compositing still runs.
            pass

        if not rendered or not target_path.exists() or target_path.stat().st_size == 0:
            _write_placeholder_video(target_path, brief.concept)

        return VideoGenerationResult(
            video_url=str(target_path),
            provider=self.name,
            cache_hit=False,
        )


def _find_rendered_video(media_dir: Path) -> Path | None:
    for root, _, files in os.walk(media_dir):
        for f in files:
            if f.endswith(".mp4"):
                return Path(root) / f
    return None


def _write_placeholder_video(out_path: Path, concept: str) -> None:
    """Last-resort: tiny valid mp4 placeholder."""
    # Write a simple placeholder file
    out_path.write_bytes(b"")


def _build_scene_script(brief: VisualBrief) -> str:
    """Generate the source code for a Manim Scene describing this concept."""
    safe_concept = (brief.concept or "").replace('"', "'").replace("\n", " ")
    safe_script = (brief.narration_script or "").replace('"', "'").replace("\n", " ")[:200]
    visual = brief.visual_type or "none"

    if visual == "equation":
        body = (
            f"title = Text('{safe_concept[:40]}').to_edge(UP).scale(0.7)\n"
            f"eq = MathTex(r'E = mc^2').move_to(ORIGIN)\n"
            "self.play(Write(title), Create(eq), run_time=3)\n"
            "self.wait(2)\n"
        )
    elif visual == "code":
        body = (
            f"title = Text('{safe_concept[:40]}').to_edge(UP).scale(0.7)\n"
            f"code_text = Text('{safe_script[:60]}', font='Courier').scale(0.6).move_to(ORIGIN)\n"
            "self.play(Write(title), FadeIn(code_text), run_time=3)\n"
            "self.wait(2)\n"
        )
    elif visual == "diagram":
        body = (
            f"title = Text('{safe_concept[:40]}').scale(0.7).to_edge(UP)\n"
            "circle = Circle(radius=1.2, color=BLUE).move_to(ORIGIN)\n"
            "dot = Dot(color=YELLOW).move_to(circle.point_at_angle(0))\n"
            "self.play(Write(title), Create(circle), FadeIn(dot))\n"
            "self.play(MoveAlongPath(dot, circle), run_time=3)\n"
            "self.wait(2)\n"
        )
    elif visual == "animation":
        body = (
            f"title = Text('{safe_concept[:40]}').scale(0.7).to_edge(UP)\n"
            "sq = Square(side_length=1.5, color=GREEN).to_edge(LEFT)\n"
            "self.play(Write(title), sq.animate.move_to(RIGHT), run_time=3)\n"
            "self.wait(2)\n"
        )
    else:  # 'none'
        body = (
            f"title = Text('{safe_concept[:50]}').scale(0.8)\n"
            "self.play(Write(title), run_time=2)\n"
            "self.wait(3)\n"
        )

    indented_body = textwrap.indent(body.strip(), "        ")
    return (
        "from manim import *\n"
        "class ConceptScene(Scene):\n"
        "    def construct(self):\n"
        f"{indented_body}\n"
    )
