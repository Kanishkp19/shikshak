"""
Shikshak AI — Wan2.1-ZeroGPU video generation provider (alternate).

Routes through a Hugging Face ZeroGPU Space via gradio_client. Requires
HF_TOKEN; subject to shared queue/quota limits. Falls back automatically
to the Manim provider on quota exhaustion or Space-down (per TRD).
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import time
from typing import Optional
import uuid

from config import settings
from skills.video_generation.base import (
    VideoGenerationProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
)


class WanZeroGPUProvider(VideoGenerationProvider):
    name = "wan_zerogpu"

    # The HF Space id we submit to — can be overridden via env in production.
    space_id = "Wan-AI/Wan2.1-T2V-14B-480P"

    def is_available(self) -> bool:
        return bool(settings.hf_token)

    def generate(
        self, request: VideoGenerationRequest | VisualBrief, out_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        if isinstance(request, VisualBrief):
            brief = request
        else:
            brief = VisualBrief(
                concept=request.concept,
                visual_type=request.visual_type,
                narration_script=request.narration_script,
                language=request.language,
                depth=request.depth,
                segment_id=request.segment_id,
            )

        target_path = out_path or getattr(request, "out_path", None)
        if target_path is None:
            target_path = Path("/tmp/shikshak_concept") / f"wan_{uuid.uuid4().hex}.mp4"
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            from gradio_client import Client, handle_file  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "gradio-client not installed — pip install gradio-client"
            ) from e

        client = Client(self.space_id, hf_token=settings.hf_token)
        prompt = f"{brief.concept}: {brief.narration_script[:200]}"
        job = client.submit(
            prompt=prompt,
            negative_prompt="low quality, blurry, distorted",
            size="480*832",
            steps=20,
            frames=81,
        )
        # Hard 4-minute timeout per TRD before the factory falls back.
        deadline = time.time() + 240
        while not job.done():
            if time.time() > deadline:
                raise TimeoutError("Wan2.1 ZeroGPU generation timed out")
            time.sleep(5)
        result = job.result()
        # result is a filepath on the Space's filesystem; download it
        video_path = result[0] if isinstance(result, list) else result
        local = client.download(video_path) if hasattr(client, "download") else video_path
        shutil.move(str(local), str(target_path))

        return VideoGenerationResult(
            video_url=str(target_path),
            provider=self.name,
            cache_hit=False,
        )


# Alias for backward compatibility
WanZerogpuProvider = WanZeroGPUProvider
