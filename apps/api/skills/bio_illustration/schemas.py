from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from skills.diagram_engine.schemas import DiagramNode


class BioIllustrationRequest(BaseModel):
    structure: Literal["heart", "neuron", "flower", "plant_cell", "animal_cell", "eye", "nephron", "dna"]
    callouts: list[DiagramNode] = Field(default_factory=list)
    theme: Literal["light_textbook", "dark_focus"] = "light_textbook"
