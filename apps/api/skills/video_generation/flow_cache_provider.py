"""
Shikshak AI — Flow Cache Video Provider.

Serves pre-generated clips manually created in Google Flow and registered via
CLI into the `video_cache` table and Supabase Storage `videos` bucket.
Lookup-only: no browser automation or runtime video generation.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from skills.caching import hash_prompt
from skills.video_generation.base import (
    VideoGenerationError,
    VideoGenerationProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
)

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = Any


class FlowCacheProvider(VideoGenerationProvider):
    """Lookup-only provider that retrieves pre-cached Google Flow clips from Supabase."""

    name = "flow_cache"

    def __init__(self, client: Optional[Any] = None):
        if client is not None:
            self.client = client
        else:
            supabase_url = os.environ.get("SUPABASE_URL")
            service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            if not supabase_url or not service_role_key:
                raise RuntimeError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment"
                )
            if create_client is None:
                raise RuntimeError("supabase package is not installed — pip install supabase")
            self.client = create_client(supabase_url, service_role_key)

    def is_available(self) -> bool:
        return True

    def generate(
        self, request: VideoGenerationRequest | VisualBrief, out_path: Optional[Any] = None
    ) -> VideoGenerationResult:
        if isinstance(request, VisualBrief):
            req = request.to_request()
        else:
            req = request

        concept = req.concept or ""
        visual_type = req.visual_type or ""
        depth = req.depth or "beginner"
        language = req.language or "en"

        prompt_hash = hash_prompt(
            concept=concept,
            visual_type=visual_type,
            depth=depth,
            language=language,
        )

        res = (
            self.client.table("video_cache")
            .select("id, storage_path, provider")
            .eq("prompt_hash", prompt_hash)
            .limit(1)
            .execute()
        )

        if not res.data:
            raise VideoGenerationError(
                provider="flow_cache",
                reason=(
                    f"No cached clip found for concept '{concept}' (visual_type='{visual_type}', "
                    f"depth='{depth}', language='{language}', hash='{prompt_hash}'). "
                    f"Generate it in Google Flow UI, download .mp4, and run: "
                    f"python scripts/populate_video_cache.py --file <path> --concept \"{concept}\" "
                    f"--visual-type {visual_type} --depth {depth} --language {language}"
                ),
            )

        row = res.data[0]
        storage_path = row["storage_path"]
        public_url = self.client.storage.from_("videos").get_public_url(storage_path)

        return VideoGenerationResult(
            video_url=public_url,
            provider=row.get("provider", self.name),
            cache_hit=True,
            video_cache_id=row.get("id"),
        )
