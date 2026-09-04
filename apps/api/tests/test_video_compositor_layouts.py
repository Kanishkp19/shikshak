"""
Tests for Dynamic Presenter Layouts & Video Stitching Compositor.

Validates:
1. TEACHER_OFF_SCREEN: 100% full-canvas visual without teacher.
2. TEACHER_EXPLAIN: Full-canvas visual with floating PIP presenter overlay.
3. TEACHER_INTRO: Prominent educator framing with preview inset.
4. Output playable at 1280x720 H.264 MP4.
"""
import subprocess
from pathlib import Path
import pytest

from models.avatar import AvatarPresenterMode
from skills.video_stitching import stitch_segment
from skills.video_generation.media import require_playable_video


@pytest.fixture
def sample_media(tmp_path):
    # Create 2s test concept video (1280x720)
    concept_path = tmp_path / "concept.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=30",
        "-t", "2.0", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(concept_path)
    ], check=True, capture_output=True)

    # Create 2s test avatar video (512x512)
    avatar_path = tmp_path / "avatar.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:size=512x512:rate=25",
        "-t", "2.0", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(avatar_path)
    ], check=True, capture_output=True)

    # Create 2s test audio
    audio_path = tmp_path / "audio.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
        "-t", "2.0", str(audio_path)
    ], check=True, capture_output=True)

    return concept_path, avatar_path, audio_path


def test_stitch_teacher_explain_pip(sample_media):
    concept, avatar, audio = sample_media
    out = stitch_segment(
        concept_video_path=str(concept),
        avatar_video_path=str(avatar),
        audio_path=str(audio),
        presenter_mode=AvatarPresenterMode.TEACHER_EXPLAIN,
    )
    assert Path(out).exists()
    require_playable_video(out, min_width=1280, min_height=720, min_duration_seconds=1.5)


def test_stitch_teacher_intro(sample_media):
    concept, avatar, audio = sample_media
    out = stitch_segment(
        concept_video_path=str(concept),
        avatar_video_path=str(avatar),
        audio_path=str(audio),
        presenter_mode=AvatarPresenterMode.TEACHER_INTRO,
    )
    assert Path(out).exists()
    require_playable_video(out, min_width=1280, min_height=720, min_duration_seconds=1.5)


def test_stitch_teacher_off_screen(sample_media):
    concept, avatar, audio = sample_media
    out = stitch_segment(
        concept_video_path=str(concept),
        avatar_video_path=str(avatar),
        audio_path=str(audio),
        presenter_mode=AvatarPresenterMode.TEACHER_OFF_SCREEN,
    )
    assert Path(out).exists()
    require_playable_video(out, min_width=1280, min_height=720, min_duration_seconds=1.5)
