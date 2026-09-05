"""
Shikshak AI — Educational Image Generation Package.
"""
from skills.image_generation.cache import (
    ImageCache,
    compute_cache_key,
    default_image_cache,
)
from skills.image_generation.prompt_engineer import (
    EducationalPrompt,
    ImageStyle,
    build_educational_prompt,
)
from skills.image_generation.generator import (
    generate_educational_image,
    create_fallback_chalkboard_canvas,
)

__all__ = [
    "ImageCache",
    "compute_cache_key",
    "default_image_cache",
    "EducationalPrompt",
    "ImageStyle",
    "build_educational_prompt",
    "generate_educational_image",
    "create_fallback_chalkboard_canvas",
]
