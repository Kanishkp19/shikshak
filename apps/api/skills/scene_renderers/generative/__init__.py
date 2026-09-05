"""
Shikshak AI — Generative Scene Renderers Package.

Includes:
  - ai_illustration: Synthesized pedagogical artwork + Ken Burns cinematic pan/zoom
  - kinetic_text: Dynamic typography, core definitions & sequential takeaways
  - split_screen: Dual-pane layout (illustration/diagram + structured takeaway card)
"""
from skills.scene_renderers.generative.ai_illustration_renderer import render_ai_illustration
from skills.scene_renderers.generative.kinetic_text_renderer import render_kinetic_text
from skills.scene_renderers.generative.split_screen_renderer import render_split_screen

__all__ = [
    "render_ai_illustration",
    "render_kinetic_text",
    "render_split_screen",
]
