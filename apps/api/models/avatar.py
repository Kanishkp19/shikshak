"""
Shikshak AI — Avatar Profiles & Presenter Modes Models.

Defines:
  1. AvatarPresenterMode: Pedagogically controlled teacher presence modes
     (Intro, Explain/PIP, Emphasize, Question, Recap, Off-Screen).
  2. AvatarProfile: Model-agnostic avatar metadata supporting MuseTalk v1.5
     on Apple Silicon and future talking-head engines.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class AvatarPresenterMode(str, Enum):
    """Pedagogical teacher visibility and layout modes."""
    TEACHER_INTRO = "TEACHER_INTRO"         # Full-frame or prominent introduction
    TEACHER_EXPLAIN = "TEACHER_EXPLAIN"     # Picture-in-picture (PIP) corner overlay during explanation
    TEACHER_EMPHASIZE = "TEACHER_EMPHASIZE" # Prominent framing highlighting key principle
    TEACHER_QUESTION = "TEACHER_QUESTION"   # Checkpoint interaction / pedagogical pause
    TEACHER_RECAP = "TEACHER_RECAP"         # Summary stage recap
    TEACHER_OFF_SCREEN = "TEACHER_OFF_SCREEN" # Completely hidden during dense visual reasoning


class AvatarProfile(BaseModel):
    """Metadata and asset references for an educator avatar."""
    model_config = {"protected_namespaces": ()}

    avatar_id: str = Field(default="female_teacher_v1", description="Unique identifier for the avatar")
    display_name: str = Field(default="Prof. Priya Sharma", description="Human educator display name")
    portrait_path: str = Field(
        default="assets/female_teacher_ref.jpg",
        description="Path to high-resolution reference portrait (front-facing, closed lips)",
    )
    source_video_path: Optional[str] = Field(
        default=None,
        description="Optional idle/talking video reference for head movement continuity",
    )
    idle_clips: list[str] = Field(default_factory=list, description="Optional idle loops")
    prepared_avatar_key: Optional[str] = Field(
        default="female_teacher_v1",
        description="Cached avatar identifier in MuseTalk service",
    )
    voice_id: str = Field(default="af_heart", description="TTS voice identifier")
    language: str = Field(default="en", description="Primary spoken language")
    resolution: tuple[int, int] = Field(default=(512, 512), description="Avatar render dimensions")
    fps: int = Field(default=25, description="Target lip-sync frame rate")
    model_version: str = Field(default="v1.5", description="Target lip sync model version")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_absolute_portrait_path(self) -> Path:
        """Resolve absolute path on disk to the portrait asset."""
        p = Path(self.portrait_path)
        if p.is_absolute() and p.exists():
            return p
        # Relative to apps/api
        base_dir = Path(__file__).resolve().parent.parent
        resolved = (base_dir / self.portrait_path).resolve()
        if resolved.exists():
            return resolved
        return p


# Default female teacher profile for production Shikshak AI
DEFAULT_FEMALE_TEACHER = AvatarProfile(
    avatar_id="female_teacher_v1",
    display_name="Prof. Priya Sharma",
    portrait_path="assets/female_teacher_ref.jpg",
    prepared_avatar_key="female_teacher_v1",
    voice_id="af_heart",
    model_version="v1.5",
)
