from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CircuitComponent(BaseModel):
    id: str
    component_type: Literal["battery", "resistor", "bulb", "switch", "ammeter", "voltmeter"]
    label: str | None = None
    state: Literal["open", "closed"] | None = None


class CircuitConnection(BaseModel):
    source_id: str
    target_id: str


class CircuitDiagramSpec(BaseModel):
    circuit_type: Literal["series", "parallel"]
    components: list[CircuitComponent] = Field(min_length=1)
    connections: list[CircuitConnection] = Field(default_factory=list)
    highlight_current_path: bool = False
