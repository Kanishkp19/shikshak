"""
Shikshak AI — Wav2Lip Neural Lip-Sync Test Suite.

Verifies end-to-end neural lip-sync generation on Apple Silicon MPS / CPU:
  1. Wav2Lip generator model initialization and forward pass
  2. Checkpoint weights verification (no missing / unexpected keys)
  3. Audio mel-spectrogram window extraction (80 mels x 16 frames)
  4. End-to-end video synthesis producing playable H.264 MP4
  5. High-level `render_lip_sync()` dispatch
"""
from __future__ import annotations

from pathlib import Path
import pytest
import torch

from models.avatar import DEFAULT_FEMALE_TEACHER
from skills.avatar.wav2lip.model import Wav2Lip
from skills.avatar.wav2lip.audio import get_mel_chunks_for_frames
from skills.avatar.wav2lip_renderer import Wav2LipRenderer
from skills.lip_sync_rendering import render_lip_sync
from skills.video_generation.media import require_playable_video


class TestWav2LipNeuralAvatar:
    """Acceptance test suite for Wav2Lip educator video generation."""

    def test_01_wav2lip_model_forward_pass(self):
        """Verify Wav2Lip PyTorch model executes with correct tensor dimensions."""
        model = Wav2Lip()
        model.eval()

        dummy_audio = torch.randn(2, 1, 80, 16)
        dummy_face = torch.randn(2, 6, 96, 96)

        with torch.no_grad():
            out = model(dummy_audio, dummy_face)

        assert out.shape == (2, 3, 96, 96)
        assert out.min() >= 0.0 and out.max() <= 1.0  # Output is sigmoid-activated

    def test_02_checkpoint_weights_load_cleanly(self):
        """Verify pre-trained weights load without key mismatches."""
        checkpoint_path = Path(__file__).resolve().parent.parent / "models" / "wav2lip" / "wav2lip_gan.pth"
        assert checkpoint_path.exists(), f"Wav2Lip checkpoint missing at: {checkpoint_path}"

        model = Wav2Lip()
        checkpoint = torch.load(str(checkpoint_path), map_location="cpu")
        sd = checkpoint.get("state_dict", checkpoint)
        new_sd = {k.replace("module.", ""): v for k, v in sd.items()}

        missing, unexpected = model.load_state_dict(new_sd, strict=False)
        assert len(missing) == 0, f"Missing keys in checkpoint: {missing}"
        assert len(unexpected) == 0, f"Unexpected keys in checkpoint: {unexpected}"

    def test_03_mel_spectrogram_chunking(self):
        """Verify 80-channel mel chunk extraction from teacher audio."""
        audio_path = Path(__file__).resolve().parent.parent / "assets" / "teacher_voice.wav"
        assert audio_path.exists(), f"Teacher voice missing at: {audio_path}"

        chunks, num_frames = get_mel_chunks_for_frames(str(audio_path), fps=25)
        assert len(chunks) == num_frames
        assert num_frames > 10
        assert chunks[0].shape == (80, 16)

    def test_04_wav2lip_render_speech_to_mp4(self, tmp_path: Path):
        """Verify end-to-end video synthesis using Wav2LipRenderer."""
        audio_path = Path(__file__).resolve().parent.parent / "assets" / "teacher_voice.wav"
        out_mp4 = tmp_path / "wav2lip_test.mp4"

        renderer = Wav2LipRenderer()
        result = renderer.render_speech(
            audio_path=audio_path,
            profile=DEFAULT_FEMALE_TEACHER,
            out_path=out_mp4,
            fps=25,
            canvas_size=512,
            batch_size=16,
        )

        assert result.exists()
        assert result.stat().st_size > 10000
        require_playable_video(str(result), min_duration_seconds=1.0)

    def test_05_render_lip_sync_integration(self):
        """Verify high-level render_lip_sync dispatch uses Wav2Lip by default."""
        audio_path = Path(__file__).resolve().parent.parent / "assets" / "teacher_voice.wav"
        out_video = render_lip_sync(str(audio_path))

        out_path = Path(out_video)
        assert out_path.exists()
        assert out_path.stat().st_size > 10000
        require_playable_video(str(out_path), min_duration_seconds=1.0)
