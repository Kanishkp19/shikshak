"""
Shikshak AI — Image Cache for Educational Asset Generation.

Caches synthesized AI illustrations and diagram visuals to prevent redundant
API calls, ensure deterministic rendering across retries, and speed up video rendering.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional


CACHE_DIR = Path("/tmp/shikshak_image_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def compute_cache_key(
    prompt: str,
    seed: int = 0,
    width: int = 1280,
    height: int = 720,
    style: str = "educational_illustration",
) -> str:
    """Derive a deterministic SHA-256 hash for the image generation parameters."""
    payload = f"{prompt.strip().lower()}|{seed}|{width}|{height}|{style.strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ImageCache:
    """Local filesystem cache for synthesized visual assets."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, cache_key: str) -> Optional[Path]:
        """Return the path to the cached image if it exists and is non-empty."""
        target = self.cache_dir / f"{cache_key}.png"
        if target.is_file() and target.stat().st_size > 500:
            return target
        return None

    def store(self, cache_key: str, data: bytes) -> Path:
        """Store image bytes into cache and return path."""
        target = self.cache_dir / f"{cache_key}.png"
        target.write_bytes(data)
        return target

    def store_file(self, cache_key: str, source_path: Path) -> Path:
        """Copy an existing image file into the cache."""
        target = self.cache_dir / f"{cache_key}.png"
        if source_path.resolve() != target.resolve():
            import shutil
            shutil.copyfile(str(source_path), str(target))
        return target


default_image_cache = ImageCache()
