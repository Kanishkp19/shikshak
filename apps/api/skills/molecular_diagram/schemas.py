from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MolecularDiagramRequest(BaseModel):
    compound_name: str
    smiles: str | None = None
    highlight_bonds: list[str] = Field(default_factory=list)
    theme: Literal["light_textbook", "dark_focus"] = "light_textbook"
