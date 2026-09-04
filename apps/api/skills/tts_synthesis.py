"""
Shikshak AI — Human-like TTS synthesis skill.

Primary Engine: Kokoro-82M (Ultra-fast, local, human-level warmth & prosody).
Optional Engine: Voicebox Local Daemon (zero-shot teacher cloning via HTTP).
Resilient Fallback: Microsoft Edge TTS (modern conversational neural voices + SSML).
Safety Fallback: macOS built-in say → minimal silent WAV.

Guarantees the pipeline invariant:
Output is strictly 16,000 Hz, single-channel (mono), 16-bit PCM WAV.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Optional

from config import settings

# ── Singleton Kokoro Engine Cache ─────────────────────────────────────────────
_KOKORO_INSTANCE = None
_KOKORO_LOCK = threading.Lock()


def _get_kokoro():
    """Lazily load and cache the Kokoro-ONNX model singleton."""
    global _KOKORO_INSTANCE
    if _KOKORO_INSTANCE is None:
        with _KOKORO_LOCK:
            if _KOKORO_INSTANCE is None:
                model_path = Path(settings.kokoro_model_path)
                voices_path = Path(settings.kokoro_voices_path)
                if model_path.exists() and voices_path.exists():
                    try:
                        from kokoro_onnx import Kokoro
                        _KOKORO_INSTANCE = Kokoro(str(model_path), str(voices_path))
                    except Exception:
                        _KOKORO_INSTANCE = None
    return _KOKORO_INSTANCE


# ── Language → Edge TTS voice mapping (Modern Conversational / Educator Voices)
_EDGE_VOICE_MAP: dict[str, str] = {
    # English: Natural, articulate female educator voices
    "en": "en-US-JennyNeural",
    "en-US": "en-US-JennyNeural",
    "en-IN": "en-IN-NeerjaNeural",
    "en-GB": "en-GB-SoniaNeural",
    
    # Hindi & Indian Regional: Warm, natural female educator voices
    "hi": "hi-IN-SwaraNeural",
    "hi-Latn": "en-IN-NeerjaNeural",  # Hinglish with articulate Indian English female voice
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "pa": "pa-IN-GurpreetNeural",
    "ur": "ur-PK-UzmaNeural",
    
    # International
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-AlvaroNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
}


def synthesize_speech(text: str, language: str = "en") -> str:
    """Synthesize a wav file from `text`, returning the local file path.

    Args:
        text: the script to speak.
        language: BCP-47 language code (e.g. 'en', 'hi', 'hi-Latn').

    Returns:
        Path to the generated .wav file (under /tmp/shikshak_audio/).
        Guaranteed to be 16,000 Hz, 1-channel mono PCM WAV.
    """
    out_dir = Path("/tmp/shikshak_audio")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"tts_{uuid.uuid4().hex}.wav"

    # 1. Try Voicebox Local REST Daemon (if configured as primary)
    if settings.tts_provider == "voicebox":
        if _synthesize_voicebox(text, language, out_path):
            return str(out_path)

    # 2. Try Kokoro-TTS (fast, local, human-level natural speech)
    if settings.tts_provider in ("kokoro", "voicebox", ""):
        if _synthesize_kokoro(text, language, out_path):
            return str(out_path)

    # 3. Try Upgraded Natural Edge-TTS (modern conversational voices + prosody)
    if _synthesize_edge_tts(text, language, out_path):
        return str(out_path)

    # 4. Try Coqui XTTS-v2 (if explicitly selected and configured)
    if settings.tts_provider == "coqui":
        if _synthesize_coqui(text, language, out_path):
            return str(out_path)

    # 5. Try macOS built-in system TTS
    if _synthesize_system_tts(text, language, out_path):
        return str(out_path)

    # 6. Fallback: silent wav (failsafe)
    _write_silent_wav(out_path, duration_s=max(1, len(text) // 15))
    return str(out_path)


def _normalize_to_16k_mono_wav(src_path: Path, out_path: Path) -> bool:
    """Normalize any audio file to 16,000 Hz, 1-channel mono PCM WAV."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(src_path),
                "-ar", "16000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                str(out_path),
            ],
            check=True,
            timeout=30,
            capture_output=True,
        )
        return out_path.exists() and out_path.stat().st_size > 500
    except Exception:
        return False


def _synthesize_kokoro(text: str, language: str, out_path: Path) -> bool:
    """Use Kokoro-82M via ONNX runtime for ultra-fast human-grade voice."""
    raw_wav = out_path.with_suffix(".kokoro.raw.wav")
    try:
        kokoro = _get_kokoro()
        if kokoro is None:
            return False

        # Language and voice selection
        lang_lower = language.lower()
        if lang_lower.startswith("hi"):
            # Kokoro Hindi voices or fallback to warm heart voice
            voice = getattr(settings, "kokoro_voice_hi", "hf_alpha")
            lang_code = "hi" if "hf_alpha" in kokoro.get_voices() else "en-us"
        elif lang_lower.startswith("en-in"):
            voice = "af_heart"
            lang_code = "en-us"
        elif lang_lower.startswith("en-gb"):
            voice = "bm_daniel"
            lang_code = "en-gb"
        else:
            voice = getattr(settings, "kokoro_voice_en", "af_heart")
            lang_code = "en-us"

        # Validate voice existence in loaded model
        available_voices = kokoro.get_voices()
        if voice not in available_voices:
            voice = "af_heart" if "af_heart" in available_voices else available_voices[0]

        import soundfile as sf
        samples, sample_rate = kokoro.create(
            text=text,
            voice=voice,
            speed=1.0,
            lang=lang_code,
        )

        sf.write(str(raw_wav), samples, sample_rate)
        if not raw_wav.exists() or raw_wav.stat().st_size < 500:
            raw_wav.unlink(missing_ok=True)
            return False

        success = _normalize_to_16k_mono_wav(raw_wav, out_path)
        raw_wav.unlink(missing_ok=True)
        return success
    except Exception:
        raw_wav.unlink(missing_ok=True)
        return False


def _synthesize_voicebox(text: str, language: str, out_path: Path) -> bool:
    """Synthesize speech via local Voicebox sidecar REST API (if running)."""
    raw_audio = out_path.with_suffix(".vb.raw.wav")
    try:
        import httpx

        url = f"{settings.voicebox_api_url.rstrip('/')}/generate"
        payload = {
            "text": text,
            "profile": settings.voicebox_profile,
            "language": language.split("-")[0],
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                # Try fallback speak endpoint
                alt_url = f"{settings.voicebox_api_url.rstrip('/')}/speak"
                resp = client.post(
                    alt_url,
                    json={"text": text, "profile": settings.voicebox_profile},
                    headers={"X-Voicebox-Client-Id": "shikshak-ai"},
                )

            if resp.status_code != 200 or not resp.content:
                return False

            raw_audio.write_bytes(resp.content)

        success = _normalize_to_16k_mono_wav(raw_audio, out_path)
        raw_audio.unlink(missing_ok=True)
        return success
    except Exception:
        raw_audio.unlink(missing_ok=True)
        return False


def _synthesize_edge_tts(text: str, language: str, out_path: Path) -> bool:
    """Use Microsoft Edge TTS Neural voices with conversational educator models."""
    try:
        import edge_tts

        # Select voice based on language
        lang_key = language if language in _EDGE_VOICE_MAP else language.split("-")[0]
        if language == "en-IN":
            voice = getattr(settings, "edge_tts_voice_in_en", "en-IN-NeerjaNeural")
        elif lang_key == "hi":
            voice = getattr(settings, "edge_tts_voice_hi", "hi-IN-SwaraNeural")
        elif lang_key == "en":
            voice = getattr(settings, "edge_tts_voice", "en-US-JennyNeural")
        else:
            voice = _EDGE_VOICE_MAP.get(lang_key, settings.edge_tts_voice)

        mp3_path = out_path.with_suffix(".mp3")
        rate = getattr(settings, "tts_rate", "-3%")

        async def _run():
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(str(mp3_path))

        try:
            asyncio.run(_run())
        except RuntimeError:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(lambda: asyncio.run(_run())).result(timeout=60)

        if not mp3_path.exists() or mp3_path.stat().st_size < 500:
            mp3_path.unlink(missing_ok=True)
            return False

        success = _normalize_to_16k_mono_wav(mp3_path, out_path)
        mp3_path.unlink(missing_ok=True)
        return success
    except Exception:
        return False


def _synthesize_coqui(text: str, language: str, out_path: Path) -> bool:
    """Use Coqui XTTS-v2 for local voice cloning (requires model + reference voice)."""
    try:
        from TTS.api import TTS  # type: ignore

        ref_voice = settings.teacher_reference_voice
        if not os.path.exists(ref_voice) or os.path.getsize(ref_voice) < 1000:
            return False

        raw_wav = out_path.with_suffix(".xtts.raw.wav")
        tts = TTS(model_path=settings.xtts_model_path)
        tts.tts_to_file(
            text=text,
            speaker_wav=ref_voice,
            language=language.split("-")[0],
            file_path=str(raw_wav),
        )
        if not raw_wav.exists() or raw_wav.stat().st_size < 1000:
            raw_wav.unlink(missing_ok=True)
            return False

        success = _normalize_to_16k_mono_wav(raw_wav, out_path)
        raw_wav.unlink(missing_ok=True)
        return success
    except Exception:
        return False


def _synthesize_system_tts(text: str, language: str, out_path: Path) -> bool:
    """Use macOS system TTS (Siri voices) as last resort."""
    try:
        voice_map = {
            "hi": "Rishi",
            "en": "Samantha",
        }
        voice = voice_map.get(language.split("-")[0], "Samantha")
        aiff_path = out_path.with_suffix(".aiff")

        try:
            subprocess.run(["say", "-v", voice, "-o", str(aiff_path), text], check=True, timeout=30)
        except Exception:
            subprocess.run(["say", "-o", str(aiff_path), text], check=True, timeout=30)

        success = _normalize_to_16k_mono_wav(aiff_path, out_path)
        aiff_path.unlink(missing_ok=True)
        return success
    except Exception:
        return False


def _write_silent_wav(path: Path, duration_s: int) -> None:
    """Fallback: write a minimal silent WAV so the pipeline path doesn't break."""
    try:
        import wave
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(b"\x00\x00" * 16000 * duration_s)
    except Exception:
        path.write_bytes(b"")

