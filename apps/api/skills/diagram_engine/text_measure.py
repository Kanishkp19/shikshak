"""Measured text geometry used by every deterministic diagram layout."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from PIL import ImageFont

from .schemas import DiagramNode

HORIZONTAL_PADDING = 24
VERTICAL_PADDING = 18
MIN_NODE_WIDTH = 132
MAX_NODE_WIDTH = 238


@dataclass(frozen=True)
class MeasuredText:
    lines: tuple[str, ...]
    width: float
    height: float


@dataclass(frozen=True)
class NodeBoxSize:
    width: float
    height: float
    label: MeasuredText
    sublabel: MeasuredText | None


@lru_cache(maxsize=16)
def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Use a stable system font when Inter is not installed on the renderer."""
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, font: ImageFont.ImageFont, max_width: float) -> tuple[str, ...]:
    words = text.split() or [""]
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and font.getlength(candidate) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return tuple(lines)


def measure_text(text: str, *, font_size: int, max_width: float = MAX_NODE_WIDTH - 2 * HORIZONTAL_PADDING) -> MeasuredText:
    font = get_font(font_size)
    lines = _wrap(text, font, max_width)
    line_height = max(font_size + 4, int(font.getbbox("Ag")[3] - font.getbbox("Ag")[1]) + 3)
    return MeasuredText(
        lines=lines,
        width=max((font.getlength(line) for line in lines), default=0),
        height=line_height * len(lines),
    )


def measure_node(node: DiagramNode, theme: dict[str, object]) -> NodeBoxSize:
    label = measure_text(node.label, font_size=int(theme["font_size_label"]))
    sublabel = (
        measure_text(node.sublabel, font_size=int(theme["font_size_sublabel"]))
        if node.sublabel
        else None
    )
    text_width = max(label.width, sublabel.width if sublabel else 0)
    width = min(MAX_NODE_WIDTH, max(MIN_NODE_WIDTH, text_width + 2 * HORIZONTAL_PADDING))
    height = label.height + (sublabel.height + 7 if sublabel else 0) + 2 * VERTICAL_PADDING
    return NodeBoxSize(width=width, height=height, label=label, sublabel=sublabel)
