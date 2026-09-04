"""
Tests for MuseTalk v1.5 Integration and Avatar Subsystem.

Validates:
1. MuseTalkMacRenderer health check & error resilience.
2. AvatarProfile and female educator defaults (female_teacher_v1).
3. Graceful fallback producing playable H.264 MP4 with synchronized audio.
"""
import subprocess
from pathlib import Path
import pytest

from models.avatar import AvatarProfile, AvatarPresenterMode, DEFAULT_FEMALE_TEACHER
from skills.avatar.musetalk_client import MuseTalkMacRenderer
from skills.video_generation.media import require_playable_video


def test_avatar_profile_defaults():
    profile = DEFAULT_FEMALE_TEACHER
    assert profile.avatar_id == "female_teacher_v1"
    assert profile.display_name == "Prof. Priya Sharma"
    assert profile.model_version == "v1.5"
    assert profile.get_absolute_portrait_path().exists()


def test_musetalk_health_check_offline_resilience():
    # Points to a non-existent port to test offline handling
    renderer = MuseTalkMacRenderer(endpoint="http://127.0.0.1:59999")
    status = renderer.health_check()
    assert status["ok"] is False
    assert "error" in status


def test_musetalk_render_speech_fallback(tmp_path):
    # Create a 2-second silent AAC/WAV audio file
    audio_path = tmp_path / "test_narration.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", "2.0", str(audio_path)
    ], check=True, capture_output=True)

    out_video = tmp_path / "rendered_avatar.mp4"
    renderer = MuseTalkMacRenderer(endpoint="http://127.0.0.1:59999")

    result = renderer.render_speech(
        audio_path=audio_path,
        profile=DEFAULT_FEMALE_TEACHER,
        out_path=out_video,
    )

    assert result.exists()
    assert result.stat().st_size > 1000
    require_playable_video(str(result), min_duration_seconds=1.5)


def test_avatar_presenter_modes():
    modes = [
        AvatarPresenterMode.TEACHER_INTRO,
        AvatarPresenterMode.TEACHER_EXPLAIN,
        AvatarPresenterMode.TEACHER_EMPHASIZE,
        AvatarPresenterMode.TEACHER_QUESTION,
        AvatarPresenterMode.TEACHER_RECAP,
        AvatarPresenterMode.TEACHER_OFF_SCREEN,
    ]
    assert len(modes) == 6
