"""Measured tree layout built from the same deterministic layered geometry."""
from __future__ import annotations

from ..schemas import DiagramSpec
from .common import LayoutResult
from .flowchart import _place_layered


def layout_hierarchy(spec: DiagramSpec) -> LayoutResult:
    return _place_layered(spec, hierarchy=True)
