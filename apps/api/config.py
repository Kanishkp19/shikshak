"""
Shikshak AI — Backend configuration.

Loads environment variables and exposes them as a typed Settings instance.
All agent and skill modules import from here; never read os.environ directly
outside this file.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field


VideoProvider = Literal["diagram", "cinematic", "manim", "wan_zerogpu", "flow_cache"]
TTSProvider = Literal["kokoro", "voicebox", "edge_tts", "coqui", "system"]
AvatarProvider = Literal["sadtalker", "wav2lip", "still_image"]


class Settings(BaseModel):
    # ── Supabase ──────────────────────────────────────────────────────────────
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    # ── LLM providers ─────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.5-flash-lite", alias="GEMINI_MODEL")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-120b", alias="GROQ_MODEL")

    # ── LLM routing (which provider handles what) ──────────────────────────────
    # "groq" for all content/orchestration (fast, high RPM via Groq Cloud)
    # "gemini" for animation diagram planning
    content_llm_provider: str = Field(default="groq", alias="CONTENT_LLM_PROVIDER")
    animation_llm_provider: str = Field(default="gemini", alias="ANIMATION_LLM_PROVIDER")

    # ── Hugging Face ZeroGPU (optional video provider) ─────────────────────────
    hf_token: str = Field(default="", alias="HF_TOKEN")

    # ── Redis / Celery ─────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # ── Video provider factory ─────────────────────────────────────────────────
    video_provider: VideoProvider = Field(default="diagram", alias="VIDEO_PROVIDER")
    enable_flow_cache: bool = Field(default=False, alias="ENABLE_FLOW_CACHE")
    diagram_plan_timeout_seconds: int = Field(default=10, alias="DIAGRAM_PLAN_TIMEOUT_SECONDS")


    # ── TTS provider ───────────────────────────────────────────────────────────
    tts_provider: TTSProvider = Field(default="kokoro", alias="TTS_PROVIDER")
    
    # Kokoro-TTS (fast, local, human-quality 82M model)
    kokoro_model_path: str = Field(default="./models/kokoro/kokoro-v1.0.onnx", alias="KOKORO_MODEL_PATH")
    kokoro_voices_path: str = Field(default="./models/kokoro/voices-v1.0.bin", alias="KOKORO_VOICES_PATH")
    kokoro_voice_en: str = Field(default="af_heart", alias="KOKORO_VOICE_EN")
    kokoro_voice_hi: str = Field(default="af_heart", alias="KOKORO_VOICE_HI")

    # Voicebox local daemon (optional sidecar at http://127.0.0.1:17493)
    voicebox_api_url: str = Field(default="http://127.0.0.1:17493", alias="VOICEBOX_API_URL")
    voicebox_profile: str = Field(default="shikshak_teacher", alias="VOICEBOX_PROFILE")

    # Natural Edge-TTS settings (conversational, expressive voices + SSML)
    edge_tts_voice: str = Field(default="en-US-JennyNeural", alias="EDGE_TTS_VOICE")
    edge_tts_voice_in_en: str = Field(default="en-IN-NeerjaNeural", alias="EDGE_TTS_VOICE_IN_EN")
    edge_tts_voice_hi: str = Field(default="hi-IN-SwaraNeural", alias="EDGE_TTS_VOICE_HI")
    tts_rate: str = Field(default="-3%", alias="TTS_RATE")

    # ── TTS / avatar assets ────────────────────────────────────────────────────
    xtts_model_path: str = Field(default="./models/xtts_v2", alias="XTTS_MODEL_PATH")
    teacher_reference_image: str = Field(
        default="./assets/female_teacher_ref.jpg", alias="TEACHER_REFERENCE_IMAGE"
    )
    teacher_reference_voice: str = Field(
        default="./assets/teacher_voice.wav", alias="TEACHER_REFERENCE_VOICE"
    )

    # ── Avatar rendering ───────────────────────────────────────────────────────
    avatar_provider: AvatarProvider = Field(default="wav2lip", alias="AVATAR_PROVIDER")
    sadtalker_checkpoint_dir: str = Field(
        default="./models/sadtalker", alias="SADTALKER_CHECKPOINT_DIR"
    )

    # ── File upload limits ─────────────────────────────────────────────────────
    max_upload_mb: int = 25
    allowed_upload_ext: tuple[str, ...] = (".pdf", ".docx", ".pptx")

    # ── Rate limits (per-IP, per-minute) ───────────────────────────────────────
    session_create_rate: int = 10
    render_rate: int = 30

    @property
    def supabase_client_kwargs(self) -> dict:
        return {
            "url": self.supabase_url,
            "key": self.supabase_service_role_key or self.supabase_anon_key,
        }


@lru_cache
def get_settings() -> Settings:
    """Cached Settings singleton."""
    load_dotenv()
    env_kwargs = {}
    for name, field in Settings.model_fields.items():
        alias = field.alias or name.upper()
        if alias in os.environ:
            env_kwargs[alias] = os.environ[alias]
        elif name.upper() in os.environ:
            env_kwargs[name] = os.environ[name.upper()]
        elif name in os.environ:
            env_kwargs[name] = os.environ[name]
    return Settings(**env_kwargs)


# Eager singleton import for convenience
settings = get_settings()
