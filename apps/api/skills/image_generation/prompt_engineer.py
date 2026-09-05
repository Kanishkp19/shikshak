"""
Shikshak AI — Prompt Engineer for Educational Image Synthesis.

Constructs high-density, pedagogically grounded prompts for text-to-image models,
enforcing domain accuracy, clean compositions, and negative visual vocabulary filters.
"""
from __future__ import annotations

import re
from typing import Literal, Optional
from pydantic import BaseModel, Field

from skills.quality_gate import NEGATIVE_VISUAL_VOCABULARY

ImageStyle = Literal[
    "educational_illustration",
    "realistic_photo",
    "infographic",
    "schematic_diagram",
]


class EducationalPrompt(BaseModel):
    prompt: str
    negative_prompt: str
    style: ImageStyle
    seed: int
    concept: str
    visual_objective: str
    entities: list[str] = Field(default_factory=list)


def build_educational_prompt(
    *,
    concept: str,
    visual_objective: str = "",
    entities: Optional[list[str]] = None,
    narration_span: str = "",
    forbidden_terms: Optional[list[str]] = None,
    style: ImageStyle = "educational_illustration",
    seed: Optional[int] = None,
) -> EducationalPrompt:
    """Construct an optimized, quality-gated prompt for educational image synthesis."""
    clean_concept = (concept or "Educational Concept").replace("\n", " ").strip()
    clean_obj = (visual_objective or f"Detailed visualization of {clean_concept}").replace("\n", " ").strip()
    clean_span = (narration_span or "")[:150].replace("\n", " ").strip()

    # Collect and combine all forbidden anti-patterns
    combined_forbidden: set[str] = set()
    for term in (forbidden_terms or []):
        t_clean = term.strip().lower()
        combined_forbidden.add(t_clean)
        combined_forbidden.add(t_clean.replace("_", " "))
        combined_forbidden.add(t_clean.replace(" ", "_"))

    for rule in NEGATIVE_VISUAL_VOCABULARY.values():
        for term in rule.get("forbidden_terms", []):
            t_clean = term.strip().lower()
            combined_forbidden.add(t_clean)
            combined_forbidden.add(t_clean.replace("_", " "))
        for kw in rule.get("metaphor_keywords", []):
            kw_clean = kw.strip().lower()
            combined_forbidden.add(kw_clean)
            combined_forbidden.add(kw_clean.replace(" ", "_"))

    # Sanitize entities
    input_entities = entities or []
    clean_entities: list[str] = []
    for ent in input_entities:
        ent_clean = str(ent).strip()
        if not ent_clean:
            continue
        ent_lower = ent_clean.lower()
        ent_spaced = ent_lower.replace("_", " ")
        if any(f in ent_lower or f in ent_spaced for f in combined_forbidden):
            continue
        clean_entities.append(ent_clean)

    entity_str = ", ".join(clean_entities[:5]) if clean_entities else clean_concept

    # Calculate deterministic seed if not provided
    if seed is None:
        seed = abs(hash(f"{clean_concept}_{entity_str}_{style}")) % 100000

    # If concept is abstract (e.g. "Natural Chemical Changes"), extract concrete physical items from narration
    concrete_cue = ""
    lower_span = (clean_span + " " + clean_concept).lower()
    physical_items = []
    if "curd" in lower_span or "milk" in lower_span:
        physical_items.append("fresh milk converting to thick curd in a ceramic bowl")
    if "rust" in lower_span or "iron" in lower_span:
        physical_items.append("oxidized iron nail with reddish-brown rust texture")
    if "ferment" in lower_span or "sugarcane" in lower_span or "juice" in lower_span:
        physical_items.append("fermenting sugarcane juice with gentle foam bubbles in a glass vessel")
    if "burn" in lower_span or "magnesium" in lower_span or "ribbon" in lower_span:
        physical_items.append("burning magnesium ribbon emitting bright white flame held by laboratory tongs")
    if "precipitate" in lower_span or "beaker" in lower_span:
        physical_items.append("transparent laboratory beaker showing white precipitate settling at the bottom")
    if any(k in lower_span for k in ("optic", "light", "refract", "reflect", "lens", "mirror", "ray", "focal", "prism")):
        physical_items.append("laboratory optical bench with mounted glass lens and crisp collimated light rays on a dark measurement grid")

    if physical_items:
        concrete_cue = " Real-world physical subjects: " + ", ".join(physical_items) + "."

    # Build prompt based on style
    if style == "realistic_photo":
        prompt = (
            f"National Geographic documentary photography of {clean_concept}.{concrete_cue} "
            f"Subject focus: {clean_obj}. "
            f"Key elements visible: {entity_str}. "
            f"Pedagogical context: {clean_span}. "
            "High resolution 8k photograph, authentic scientific visual, crisp natural depth of field, "
            "cinematic studio lighting, 16:9 aspect ratio, professional camera lens, hyper-realistic, no text overlay"
        )
    elif style == "schematic_diagram":
        prompt = (
            f"Technical schematic blueprint diagram of {clean_concept}.{concrete_cue} "
            f"Cross-section and internal mechanisms: {clean_obj}. "
            f"Labeled structures: {entity_str}. "
            "Dark slate chalkboard background (#0f172a), crisp blueprint lineart in cyan (#38bdf8) and indigo (#818cf8), "
            "pedagogical callout arrows, millimeter precision, scientific textbook vector illustration, 16:9 widescreen"
        )
    elif style == "infographic":
        prompt = (
            f"Modern educational visual infographic explaining {clean_concept}.{concrete_cue} "
            f"Core principle: {clean_obj}. "
            f"Key elements: {entity_str}. "
            "Clean flat vector graphics, high visual clarity, dark academic background, glowing neon pedagogical accents, "
            "structured layout, 16:9 widescreen composition, no clutter"
        )
    else:  # "educational_illustration" (default)
        prompt = (
            f"Detailed educational textbook scientific illustration of {clean_concept}.{concrete_cue} "
            f"Visual focus: {clean_obj}. "
            f"Key pedagogical components: {entity_str}. "
            f"Context: {clean_span}. "
            "Clean labeled schematic illustration, sharp pedagogical vectors, dark slate chalkboard background (#0f172a), "
            "crisp vibrant accents (#38bdf8, #818cf8, #34d399), scientific accuracy, "
            "16:9 widescreen composition, 8k render, no decorative balance scales, no photorealistic human portraits"
        )

    negative_prompt = (
        "cosmic flare, space nebula, underwater ripples, starburst, glowing orb, fantasy energy beam, mystical lighting, "
        "ethereal halo, sci-fi portal, circular ripples, deep ocean glow, fantasy magic, circular dial, gauge, stovetop, "
        "burner plate, compass, clock, speedometer, abstract circular diagram, sci-fi hud circle, low quality, blurry, "
        "distorted, watermarks, signature, meme, caricature, cartoonish face, distorted text, weighing scales, balance scale, "
        "lightning bolts, clutter, oversaturated noise"
    )


    return EducationalPrompt(
        prompt=prompt,
        negative_prompt=negative_prompt,
        style=style,
        seed=seed,
        concept=clean_concept,
        visual_objective=clean_obj,
        entities=clean_entities,
    )
