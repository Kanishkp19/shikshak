"""
Shikshak AI — AI Educational Illustration Scene Renderer.

Renders high-fidelity educational illustrations with dynamic Ken Burns
camera motion (continuous zoom + sinusoidal lateral tracking) and pedagogical
title/label overlays.
"""
from __future__ import annotations

import logging
from pathlib import Path
import subprocess
from typing import Any, Optional
import uuid

from PIL import Image, ImageDraw, ImageFont

from skills.image_generation.generator import generate_educational_image
from skills.video_generation.media import require_playable_video

logger = logging.getLogger(__name__)


def render_ai_illustration(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Optional[Path] = None,
) -> Path:
    """Render an AI illustration scene with smooth kinetic camera push-in and clean captioning."""
    duration_s = max(2.0, min(90.0, float(duration_seconds)))
    if out_path is None:
        target_path = Path("/tmp/shikshak_scenes") / f"ai_illus_{uuid.uuid4().hex}.mp4"
    else:
        target_path = Path(out_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Obtain or generate base educational image
    image_path_str = payload_dict.get("image_path")
    img_path = Path(image_path_str) if image_path_str else None

    title = payload_dict.get("title") or "Educational Concept"
    caption = payload_dict.get("caption") or narration_text[:80]
    entities = payload_dict.get("entities") or []
    prompt = payload_dict.get("prompt") or f"Educational illustration of {title}"
    style = payload_dict.get("style", "educational_illustration")

    if img_path is None or not img_path.is_file() or img_path.stat().st_size < 1000:
        logger.info("[AiIllustrationRenderer] Synthesizing image asset for %r", title)
        img_temp = Path("/tmp/shikshak_concept_images") / f"illus_{uuid.uuid4().hex}.png"
        img_path = generate_educational_image(
            concept=title,
            visual_objective=caption,
            entities=entities,
            narration_span=narration_text,
            out_path=img_temp,
            style=style,
        )

    # 2. Add lower-third pedagogical title strip
    prepared_img = Path("/tmp/shikshak_concept_images") / f"prepared_{uuid.uuid4().hex}.png"
    prepared_img.parent.mkdir(parents=True, exist_ok=True)

    try:
        base_img = Image.open(img_path).convert("RGB")
        base_img = base_img.resize((1280, 720), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(base_img)

        # Elegant semi-transparent bottom strip
        draw.rectangle([(0, 660), (1280, 720)], fill=(15, 23, 42))

        # Fonts
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFProText.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        font = None
        sub_font = None
        for fp in font_paths:
            if Path(fp).exists():
                try:
                    font = ImageFont.truetype(fp, 20)
                    sub_font = ImageFont.truetype(fp, 13)
                    break
                except Exception:
                    continue
        if font is None:
            font = ImageFont.load_default()
            sub_font = ImageFont.load_default()

        # Render clean title & entity tags
        clean_title = title.replace("\n", " ")[:65]
        draw.text((36, 676), clean_title, fill=(248, 250, 252), font=font)

        if entities:
            ent_text = " • ".join(entities[:3])[:60]
            draw.text((1240 - len(ent_text) * 8, 680), ent_text, fill=(56, 189, 248), font=sub_font)

        base_img.save(prepared_img, format="PNG", quality=95)
        source_img_path = prepared_img
    except Exception as exc:
        logger.warning("[AiIllustrationRenderer] Failed to overlay title strip: %s; using raw image", exc)
        source_img_path = img_path

    # 3. Dynamic Ken Burns Camera Pan/Zoom via FFmpeg
    fps = 25
    total_frames = max(25, int(round(duration_s * fps)))
    target_max_zoom = 1.18
    zoom_step = (target_max_zoom - 1.0) / total_frames
    zoom_step_str = f"{zoom_step:.7f}"

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
        "-i", str(source_img_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-crf", "18",
        "-t", f"{duration_s:.2f}",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(target_path),
    ]

    try:
        subprocess.run(cmd, check=True, timeout=120, capture_output=True)
    except subprocess.CalledProcessError as err:
        stderr = err.stderr.decode("utf-8", errors="replace") if err.stderr else ""
        logger.error("[AiIllustrationRenderer] FFmpeg failed: %s", stderr[-300:])
        raise RuntimeError(f"Ken Burns rendering failed: {stderr[-300:]}") from err
    finally:
        if prepared_img.exists() and prepared_img != img_path:
            prepared_img.unlink(missing_ok=True)

    require_playable_video(str(target_path), min_width=640, min_height=360, min_duration_seconds=1.0)
    return target_path
