"""
Shikshak AI — Avatar Renderer Interface.

Abstract base class decoupling talking-head generation from specific backends
(MuseTalk-Mac, local Wav2Lip, still-image breathing fallback, or cloud services).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from models.avatar import AvatarProfile


class AvatarRenderer(ABC):
    """Abstract interface for educational presenter lip-sync generation."""

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Verify service health and readiness."""
        pass

    @abstractmethod
    def prepare_avatar(self, profile: AvatarProfile) -> str:
        """Warm up or cache avatar features (face detection, landmarks, latent cache).
        
        Returns the prepared avatar key string.
        """
        pass

    @abstractmethod
    def render_speech(
        self,
        audio_path: Path,
        profile: AvatarProfile,
        out_path: Optional[Path] = None,
    ) -> Path:
        """Render synchronized talking-head MP4 video for the given audio."""
        pass

    def render_stream(
        self,
        audio_path: Path,
        profile: AvatarProfile,
    ) -> Any:
        """Stream lip-synced video chunks (optional streaming support)."""
        raise NotImplementedError("Streaming not supported by this avatar renderer.")
