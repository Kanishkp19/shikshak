"""
Shikshak AI — Cinematic AI Video Generation Provider (v3).

Generates high-definition, transcript-grounded educational illustrations via Pollinations AI
and renders them with continuous, full-duration kinetic camera movement (no slideshow freezes).

Key guarantees:
  1. Transcript-Timed Scene Contract: matches exact narration duration (no arbitrary 10s caps).
  2. Transcript-Grounded Prompts: synthesized from visual_objective, entities, and narration span,
     filtering against negative visual vocabulary.
  3. Continuous Kinetic Motion: dynamic zoom velocity calibrated to duration so motion persists
     smoothly throughout 100% of the clip (eliminates the 8-second freeze bug).
  4. Pedagogical Fallback Canvas: renders a structured chalkboard schema when network is unreachable.
  5. Visual Quality Gate: validates motion variance, timing coverage, and non-blank content.
"""
from __future__ import annotations

import io
import logging
import math
import os
from pathlib import Path
import ssl
import subprocess
from typing import Any, Optional
import urllib.parse
import urllib.request
import uuid

from PIL import Image, ImageDraw, ImageFont

from skills.video_generation.base import (
    VideoGenerationProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
)
from skills.quality_gate import NEGATIVE_VISUAL_VOCABULARY, audit_cinematic_video

logger = logging.getLogger(__name__)


class CinematicProvider(VideoGenerationProvider):
    name = "cinematic"

    def generate(
        self, request: VideoGenerationRequest | VisualBrief | dict[str, Any], out_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        """Generate a transcript-timed cinematic concept animation video."""
        # 1. Unpack transcript-timed contract fields
        concept = getattr(request, "concept", "") or ""
        visual_type = getattr(request, "visual_type", "animation")
        narration_script = getattr(request, "narration_script", "") or ""
        language = getattr(request, "language", "en")
        depth = getattr(request, "depth", "intermediate")
        segment_id = getattr(request, "segment_id", "")

        # Extract transcript-timed attributes from request or extra_params
        extra = getattr(request, "extra_params", {}) or {}
        if isinstance(request, dict):
            concept = request.get("concept", concept)
            narration_script = request.get("narration_script", narration_script)
            extra = request

        narration_span = extra.get("narration_span") or narration_script
        visual_objective = extra.get("visual_objective") or f"Illustrate {concept}"
        entities = extra.get("entities") or []
        motion_beats = extra.get("motion_beats") or []
        forbidden_terms = extra.get("forbidden_terms") or []

        # 2. Calculate precise duration from narration span if not given
        raw_dur = getattr(request, "duration_seconds", None) or extra.get("duration_seconds")
        if raw_dur and float(raw_dur) > 1.0:
            duration = float(raw_dur)
        else:
            word_count = len((narration_span or narration_script or "").split())
            duration = max(4.0, round(word_count / 2.3, 1))

        target_path = out_path or getattr(request, "out_path", None)
        if target_path is None:
            target_path = Path("/tmp/shikshak_concept") / f"cinematic_{uuid.uuid4().hex}.mp4"
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        img_path = target_path.with_suffix(".jpg")

        # 3. Generate transcript-grounded illustration
        self._generate_cinematic_image(
            concept=concept,
            visual_objective=visual_objective,
            entities=entities,
            narration_span=narration_span,
            forbidden_terms=forbidden_terms,
            img_path=img_path,
        )

        # 4. Render continuous kinetic video matching exact scene duration
        self._render_cinematic_video(
            img_path=img_path,
            concept=concept,
            entities=entities,
            duration=duration,
            out_path=target_path,
        )

        # 5. Audit output against visual quality gate
        quality_res = audit_cinematic_video(
            target_path,
            expected_duration=duration,
            concept=concept,
            entities=entities,
        )
        if not quality_res.passed:
            logger.warning(
                "[CinematicProvider] Quality gate flagged issues for %s: %s",
                concept,
                [i.message for i in quality_res.issues],
            )

        return VideoGenerationResult(
            video_url=str(target_path),
            provider=self.name,
            cache_hit=False,
        )

    def _generate_cinematic_image(
        self,
        *,
        concept: str,
        visual_objective: str,
        entities: list[str],
        narration_span: str,
        forbidden_terms: list[str],
        img_path: Path,
    ) -> None:
        """Synthesize a transcript-grounded educational illustration via Pollinations AI."""
        clean_concept = (concept or "Scientific Concept").replace("\n", " ").strip()
        clean_obj = (visual_objective or f"Explain {clean_concept}").replace("\n", " ").strip()
        clean_span = (narration_span or "")[:140].replace("\n", " ").strip()

        # Filter forbidden anti-patterns
        combined_forbidden = set(forbidden_terms)
        for rule in NEGATIVE_VISUAL_VOCABULARY.values():
            combined_forbidden.update(rule.get("forbidden_terms", []))

        clean_entities = [
            e for e in entities
            if not any(f in e.lower() for f in combined_forbidden)
        ]
        entity_str = ", ".join(clean_entities[:5]) if clean_entities else clean_concept

        # Construct high-density academic vector prompt
        prompt = (
            f"Detailed educational textbook scientific illustration of {clean_concept}. "
            f"Visual focus: {clean_obj}. "
            f"Key components clearly labeled: {entity_str}. "
            f"Context: {clean_span}. "
            "Clean labeled schematic diagram, sharp pedagogical vectors, dark slate chalkboard background (#0f172a), "
            "crisp vibrant accents (#38bdf8, #818cf8, #34d399), scientific accuracy, "
            "16:9 widescreen composition, no watermarks, no decorative balance scales, no photorealistic portraits, 8k render"
        )
        encoded_prompt = urllib.parse.quote(prompt[:320])

        # Deterministic seed based on concept + entities
        seed = abs(hash(f"{clean_concept}_{entity_str}")) % 10000
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1280&height=720&nologo=true&seed={seed}"
        )

        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                data = resp.read()
                if len(data) > 1000:
                    img_path.write_bytes(data)
                    return
        except Exception as e:
            logger.info("[CinematicProvider] Pollinations API unavailable: %s; rendering local canvas", e)

        self._create_fallback_canvas(img_path, clean_concept, clean_entities, clean_obj)

    def _create_fallback_canvas(
        self,
        img_path: Path,
        concept: str,
        entities: list[str],
        objective: str,
    ) -> None:
        """Create a high-contrast pedagogical chalkboard canvas as a local fallback."""
        width, height = 1280, 720
        img = Image.new("RGB", (width, height), color=(15, 23, 42))  # #0f172a slate
        draw = ImageDraw.Draw(img)

        # Subtle academic grid lines
        grid_color = (25, 36, 60)
        for x in range(0, width, 80):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, 80):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)

        # Hairline frame border
        draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(56, 189, 248), width=2)

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except Exception:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Concept Title & Eyebrow
        draw.text((60, 50), "SHIKSHAK ACADEMIC STUDIO · CONCEPT SCHEMA", fill=(148, 163, 184), font=small_font)
        draw.text((60, 80), concept[:60], fill=(248, 250, 252), font=title_font)

        # Objective Box
        draw.rectangle([(60, 150), (width - 60, 210)], fill=(30, 41, 59), outline=(56, 189, 248, 80), width=1)
        draw.text((80, 168), f"Instructional Focus: {objective[:80]}", fill=(186, 230, 253), font=body_font)

        # Key Entity Chips
        display_entities = entities[:4] if entities else ["Core Principle", "Governing Law", "Apparatus"]
        chip_x = 60
        chip_y = 250
        for idx, ent in enumerate(display_entities):
            chip_text = f"• {ent[:30]}"
            draw.rectangle([(chip_x, chip_y), (chip_x + 260, chip_y + 60)], fill=(30, 41, 59), outline=(129, 140, 248), width=1)
            draw.text((chip_x + 15, chip_y + 18), chip_text, fill=(224, 231, 255), font=body_font)
            chip_x += 280
            if chip_x + 260 > width - 60:
                chip_x = 60
                chip_y += 80

        # Bottom Takeaway Ribbon
        draw.rectangle([(60, height - 90), (width - 60, height - 40)], fill=(12, 74, 110), outline=(56, 189, 248), width=1)
        draw.text((80, height - 75), f"Key Concept: Physical properties and relationships governing {concept[:40]}", fill=(224, 242, 254), font=small_font)

        img.save(img_path, quality=95)

    def _render_cinematic_video(
        self,
        img_path: Path,
        concept: str,
        entities: list[str],
        duration: float,
        out_path: Path,
    ) -> None:
        """Render continuous kinetic video with dynamic zoom velocity matching exact duration."""
        fps = 25
        duration_s = max(3.0, float(duration))
        total_frames = max(25, int(round(duration_s * fps)))

        # Clean bottom title strip
        try:
            img = Image.open(img_path).convert("RGB")
            img = img.resize((1280, 720))
            draw = ImageDraw.Draw(img)

            # Elegant semi-transparent bottom strip
            draw.rectangle([(0, 665), (1280, 720)], fill=(15, 23, 42))
            clean_title = (concept or "Educational Lesson").replace("\n", " ")[:60]

            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
                sub_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
            except Exception:
                font = ImageFont.load_default()
                sub_font = ImageFont.load_default()

            draw.text((40, 680), clean_title, fill=(248, 250, 252), font=font)
            if entities:
                ent_text = " | ".join(entities[:3])
                draw.text((1240 - len(ent_text) * 8, 684), ent_text, fill=(56, 189, 248), font=sub_font)

            img.save(img_path, quality=95)
        except Exception:
            pass

        # FIX FOR THE 8-SECOND FREEZE BUG:
        # Dynamically calculate zoom velocity so the camera moves smoothly from start to finish.
        # Max zoom target: 1.18 (a gentle, cinematic 18% push-in)
        target_max_zoom = 1.18
        zoom_step = (target_max_zoom - 1.0) / total_frames
        zoom_step_str = f"{zoom_step:.7f}"

        # Kinetic trajectory: slow continuous zoom + gentle sinusoidal lateral tracking pan
        # d=total_frames enables FFmpeg to continuously increment zoom across all frames without resetting
        vf = (
            "scale=1920:1080,"
            "zoompan="
            f"z='min(zoom+{zoom_step_str},{target_max_zoom})':"
            f"d={total_frames}:fps=25:"
            f"x='iw/2-(iw/zoom/2)+sin(on/{total_frames}*3.14159)*30':"
            f"y='ih/2-(ih/zoom/2)+cos(on/{total_frames}*3.14159)*10':"
            "s=1280x720"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(img_path),
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "18",
            "-t", f"{duration_s:.2f}",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(out_path),
        ]
        subprocess.run(cmd, check=True, timeout=120, capture_output=True)
