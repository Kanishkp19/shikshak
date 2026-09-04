"""Manifest of curated biological illustration vector assets."""
from __future__ import annotations

from pathlib import Path

# Sourced from BioIcons (CC-BY 4.0 & CC0), versioned in assets/bio_icons/
ASSET_ROOT = Path(__file__).resolve().parents[4] / "assets" / "bio_icons"

BIO_ASSET_PATHS: dict[str, Path] = {
    "heart": ASSET_ROOT / "heart_cross_section.svg",
    "neuron": ASSET_ROOT / "neuron_structure.svg",
    "flower": ASSET_ROOT / "flower_cross_section.svg",
    "plant_cell": ASSET_ROOT / "plant_cell.svg",
    "animal_cell": ASSET_ROOT / "animal_cell.svg",
    "eye": ASSET_ROOT / "eye_cross_section.svg",
    "nephron": ASSET_ROOT / "nephron.svg",
    "dna": ASSET_ROOT / "dna_double_helix.svg",
}
