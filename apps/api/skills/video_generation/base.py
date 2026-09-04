"""
Shikshak AI — video generation provider base.

Every video provider (FlowCache, Manim, Diagram, Cinematic, WanZeroGPU, etc.)
implements this interface so the Concept Animation agent doesn't need to know
which provider is active — it always calls `factory.generate_with_fallback(...)`.

The factory falls back to the next provider on failure per the TRD error handling
strategy; agents never call a provider directly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any, Optional


@dataclass
class VideoGenerationRequest:
    """Request contract for video generation providers."""

    segment_id: str = ""
    concept: str = ""
    narration_script: str = ""
    visual_type: str = ""
    depth: str = "beginner"
    language: str = "en"
    extra_params: Optional[dict[str, Any]] = None

    # Optional compatibility fields for diagram/animation renderers
    duration_seconds: float = 30.0
    diagram_spec: Optional[dict[str, Any]] = None
    scenes: Optional[list[dict[str, Any]]] = None
    out_path: Optional[Path] = None


@dataclass
class VideoGenerationResult(os.PathLike):
    """Result returned by video generation providers."""

    video_url: str
    provider: str
    cache_hit: bool = False
    video_cache_id: Optional[str] = None

    def __fspath__(self) -> str:
        return self.video_url

    def __str__(self) -> str:
        return self.video_url

    def __iter__(self):
        yield self.video_url
        yield self.provider



class VideoGenerationError(Exception):
    """Typed error raised when a video generation provider fails."""

    def __init__(self, provider: str, reason: str):
        self.provider = provider
        self.reason = reason
        super().__init__(f"[{provider}] {reason}")


@dataclass
class VisualBrief:
    """Legacy visual brief contract maintained for backwards compatibility."""

    concept: str
    visual_type: str
    narration_script: str
    language: str = "en"
    duration_seconds: int = 30
    diagram_spec: dict[str, Any] | None = None
    scenes: list[dict[str, Any]] | None = None
    depth: str = "beginner"
    segment_id: str = ""

    def to_request(self) -> VideoGenerationRequest:
        return VideoGenerationRequest(
            segment_id=self.segment_id,
            concept=self.concept,
            narration_script=self.narration_script,
            visual_type=self.visual_type,
            depth=self.depth,
            language=self.language,
            duration_seconds=float(self.duration_seconds),
            diagram_spec=self.diagram_spec,
            scenes=self.scenes,
            extra_params={
                "duration_seconds": self.duration_seconds,
                "diagram_spec": self.diagram_spec,
                "scenes": self.scenes,
            },
        )


class VideoGenerationProvider(ABC):
    """Every video provider implements this interface."""

    name: str = "base"

    @abstractmethod
    def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Render or retrieve a video for the request and return a VideoGenerationResult."""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Return False if the provider can't be used right now."""
        return True
