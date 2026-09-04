"""
Unit and integration tests for Shikshak AI human-like voice synthesis.
Tests the Kokoro-82M engine, Edge-TTS educator fallback, and 16kHz mono audio invariants.
"""
import wave
from pathlib import Path

import pytest
from skills.tts_synthesis import (
    synthesize_speech,
    _synthesize_kokoro,
    _synthesize_edge_tts,
    _normalize_to_16k_mono_wav,
)
from agents.voice_synthesis import synthesize as agent_synthesize


def _verify_wav_properties(wav_path_str: str, min_duration: float = 0.5):
    """Verify strictly the pipeline invariant: 16,000 Hz, 1-channel mono PCM WAV."""
    path = Path(wav_path_str)
    assert path.exists(), f"File does not exist: {path}"
    assert path.stat().st_size > 1000, f"File too small: {path.stat().st_size} bytes"

    with wave.open(str(path), "rb") as w:
        channels = w.getnchannels()
        sample_rate = w.getframerate()
        sample_width = w.getsampwidth()
        frames = w.getnframes()
        duration = frames / float(sample_rate)

        assert channels == 1, f"Expected 1 channel (mono), got {channels}"
        assert sample_rate == 16000, f"Expected 16000 Hz, got {sample_rate}"
        assert sample_width == 2, f"Expected 16-bit PCM (2 bytes), got {sample_width}"
        assert duration >= min_duration, f"Duration {duration:.2f}s is less than {min_duration}s"


def test_synthesize_speech_english_default():
    """Test primary speech synthesis for English narration."""
    text = "Photosynthesis is the biological process by which plants use sunlight to synthesize nutrients."
    wav_path = synthesize_speech(text, language="en")
    _verify_wav_properties(wav_path, min_duration=1.0)


def test_synthesize_speech_hindi_conversational():
    """Test speech synthesis for Hindi narration (MadhurNeural educator voice)."""
    text = "आज की इस कक्षा में हम न्यूटन के गति के नियमों को गहराई से समझेंगे।"
    wav_path = synthesize_speech(text, language="hi")
    _verify_wav_properties(wav_path, min_duration=1.0)


def test_voice_synthesis_agent_delegation():
    """Verify that the Voice Synthesis Agent produces valid 16kHz mono audio."""
    text = "The mitochondria is often called the powerhouse of the cell."
    wav_path = agent_synthesize(narration_script=text, language="en")
    _verify_wav_properties(wav_path, min_duration=1.0)


def test_edge_tts_educator_voices():
    """Verify Edge-TTS synthesis explicitly with modern educator voices."""
    out_path = Path("/tmp/shikshak_audio/test_edge_direct.wav")
    success = _synthesize_edge_tts("Energy can neither be created nor destroyed.", "en", out_path)
    assert success is True
    _verify_wav_properties(str(out_path), min_duration=1.0)
    out_path.unlink(missing_ok=True)
