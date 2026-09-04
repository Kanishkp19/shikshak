"""
Shikshak AI — video generation factory.

THE single entry point every agent uses for concept animation.
Never call a provider's SDK directly — always go through `generate_with_fallback()`.

Implements the automatic fallback chain:
  FlowCacheProvider (if ENABLE_FLOW_CACHE=true) -> configured VIDEO_PROVIDER -> ManimProvider
so a student never sees a raw provider error (per TRD error strategy).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from config import settings
from skills.video_generation.base import (
    VideoGenerationError,
    VideoGenerationProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
)
from skills.video_generation.flow_cache_provider import FlowCacheProvider
from skills.video_generation.manim_provider import ManimProvider
from skills.video_generation.media import require_playable_video

logger = logging.getLogger(__name__)


def _build_chain(primary: Optional[str] = None) -> list[VideoGenerationProvider]:
    """Return ordered list of providers to try, starting with FlowCache if enabled."""
    chain: list[VideoGenerationProvider] = []

    enable_flow_cache = os.environ.get(
        "ENABLE_FLOW_CACHE", str(getattr(settings, "enable_flow_cache", "false"))
    ).strip().lower()
    if enable_flow_cache in ("true", "1", "yes"):

        try:
            chain.append(FlowCacheProvider())
        except Exception as e:
            logger.warning("Could not initialize FlowCacheProvider: %s", e)

    video_provider = (
        primary
        or os.environ.get("VIDEO_PROVIDER", getattr(settings, "video_provider", "manim"))
    ).strip().lower()

    if video_provider == "manim":
        chain.append(ManimProvider())
    elif video_provider == "wan_zerogpu":
        try:
            from skills.video_generation.wan_zerogpu_provider import WanZeroGPUProvider

            chain.append(WanZeroGPUProvider())
        except Exception as e:
            logger.warning("Could not load WanZeroGPUProvider: %s", e)
        chain.append(ManimProvider())
    elif video_provider == "diagram":
        try:
            from skills.video_generation.diagram_provider import DiagramProvider

            chain.append(DiagramProvider())
        except Exception as e:
            logger.warning("Could not load DiagramProvider: %s", e)
        chain.append(ManimProvider())
    elif video_provider == "cinematic":
        try:
            from skills.video_generation.cinematic_provider import CinematicProvider

            chain.append(CinematicProvider())
        except Exception as e:
            logger.warning("Could not load CinematicProvider: %s", e)
        chain.append(ManimProvider())
    else:
        # Default / unrecognized value
        chain.append(ManimProvider())

    return chain


def _fallback_chain(primary: Optional[str] = None) -> list[VideoGenerationProvider]:
    """Dynamically delegate to _build_chain for backwards compatibility and test monkeypatching."""
    try:
        return _build_chain(primary)
    except TypeError:
        return _build_chain()




def get_provider(name: Optional[str] = None) -> VideoGenerationProvider:
    """Return a single provider instance by name (defaulting to configured provider)."""
    name = (name or os.environ.get("VIDEO_PROVIDER", getattr(settings, "video_provider", "manim"))).strip().lower()
    if name == "flow_cache":
        return FlowCacheProvider()
    if name == "diagram":
        from skills.video_generation.diagram_provider import DiagramProvider

        return DiagramProvider()
    if name == "cinematic":
        from skills.video_generation.cinematic_provider import CinematicProvider

        return CinematicProvider()
    if name == "wan_zerogpu":
        from skills.video_generation.wan_zerogpu_provider import WanZeroGPUProvider

        return WanZeroGPUProvider()
    return ManimProvider()


def generate_with_fallback(
    request: VideoGenerationRequest | VisualBrief, out_path: Optional[Path] = None
) -> VideoGenerationResult:
    """Run the video generation fallback chain end-to-end.

    Iterates through the chain in order:
      1. FlowCacheProvider (if enabled)
      2. Configured provider (e.g. WanZeroGPU, Diagram, Cinematic, Manim)
      3. ManimProvider (final safety net)

    Returns:
        VideoGenerationResult with video_url, provider, cache_hit, and video_cache_id.
    """
    if isinstance(request, VisualBrief):
        req = request.to_request()
    else:
        req = request

    if out_path is not None:
        req.out_path = Path(out_path)

    # Use _fallback_chain to support test monkeypatching
    try:
        chain = _fallback_chain(settings.video_provider)
    except TypeError:
        chain = _fallback_chain()

    last_err: Exception | None = None

    for provider in chain:
        if not provider.is_available():
            continue
        try:
            if req.out_path:
                req.out_path.unlink(missing_ok=True)

            # Providers support generate(req) or legacy generate(brief, out_path)
            try:
                result = provider.generate(req)
            except TypeError:
                if req.out_path:
                    raw_res = provider.generate(req, req.out_path)
                    result = VideoGenerationResult(
                        video_url=str(raw_res),
                        provider=provider.name,
                        cache_hit=False,
                    )
                else:
                    raise

            # If result is not already VideoGenerationResult, wrap it
            if not isinstance(result, VideoGenerationResult):
                if isinstance(result, tuple):
                    result = VideoGenerationResult(video_url=str(result[0]), provider=str(result[1]))
                else:
                    result = VideoGenerationResult(video_url=str(result), provider=provider.name)

            # Validate video if it's a local file path
            if result.video_url and not result.video_url.startswith(("http://", "https://")):
                video_file = Path(result.video_url)
                if video_file.exists():
                    require_playable_video(
                        str(video_file),
                        min_width=640,
                        min_height=360,
                        min_duration_seconds=1.0,
                    )

            logger.info(
                "Video generation successful [segment_id=%s, provider=%s, cache_hit=%s]",
                req.segment_id,
                result.provider,
                result.cache_hit,
            )
            return result
        except VideoGenerationError as e:
            logger.info("Video provider [%s] missed or raised expected error: %s", provider.name, e)
            last_err = e
            if req.out_path:
                req.out_path.unlink(missing_ok=True)
            continue
        except Exception as e:
            logger.info("Video provider [%s] failed, trying fallback: %s", provider.name, e)
            last_err = e
            if req.out_path:
                req.out_path.unlink(missing_ok=True)
            continue

    if last_err is not None:
        raise last_err

    raise RuntimeError(f"All video providers failed for concept {req.concept!r}")
