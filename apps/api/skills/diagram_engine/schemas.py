"""Coordinate-free content contracts for the Diagram Animation Engine."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DiagramNode(BaseModel):
    id: str
    label: str = Field(max_length=28)
    sublabel: str | None = None
    node_type: Literal["concept", "input", "output", "process"]
    highlight_at_ms: int | None = Field(default=None, ge=0)


class DiagramEdge(BaseModel):
    source_id: str
    target_id: str
    label: str | None = None


class DiagramSpec(BaseModel):
    layout: Literal["flowchart", "cross_section", "comparison", "hierarchy", "cycle"]
    nodes: list[DiagramNode] = Field(min_length=1)
    edges: list[DiagramEdge] = Field(default_factory=list)
    theme: Literal["light_textbook", "dark_focus"] = "light_textbook"


class ContentBlueprint(BaseModel):
    segment_id: str
    narration_script: str
    narration_duration_estimate_ms: int = Field(gt=0)
    diagram_spec: DiagramSpec
