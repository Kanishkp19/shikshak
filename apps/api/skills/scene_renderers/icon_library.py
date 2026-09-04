"""
Shikshak AI — Universal Vector Icon & Schematic Library.

Provides 60+ clean, crisp, scalable SVG vector icons and semantic keyword
matching across Science, Mathematics, Humanities, Engineering, ML, Medical,
and Everyday Life concepts.
"""
from __future__ import annotations

import re
from typing import Dict, Any, Tuple


# ── Curated 24x24 and 48x48 Vector SVG Paths ─────────────────────────────────
# Standardized to 0 0 24 24 viewBox with stroke-width 2, round linecaps.

ICONS: dict[str, dict[str, Any]] = {
    # ── Everyday Life & Materials ─────────────────────────────────────────────
    "milk_bottle": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M8 2h8v2H8z" fill="currentColor"/><path d="M9 4v3l-2 3v11a1 1 0 001 1h8a1 1 0 001-1V10l-2-3V4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M7 14h10" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="18" r="1.5" fill="currentColor"/>""",
        "default_color": "#2563eb",
        "bg_tint": "#eff6ff",
    },
    "iron_nail": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M6 3h12v2H6z" fill="currentColor"/><path d="M11 5v14l1 3 1-3V5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="8" cy="11" r="1" fill="#ea580c"/><circle cx="16" cy="15" r="1.2" fill="#ea580c"/><circle cx="7" cy="17" r="1" fill="#ea580c"/>""",
        "default_color": "#ea580c",
        "bg_tint": "#fff7ed",
    },
    "grapes": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2v4M12 6a3 3 0 00-3-3" fill="none" stroke="#15803d" stroke-width="2" stroke-linecap="round"/><circle cx="9" cy="9" r="2.5" fill="currentColor"/><circle cx="15" cy="9" r="2.5" fill="currentColor"/><circle cx="12" cy="13" r="2.5" fill="currentColor"/><circle cx="8" cy="14" r="2" fill="currentColor"/><circle cx="16" cy="14" r="2" fill="currentColor"/><circle cx="10" cy="18" r="2" fill="currentColor"/><circle cx="14" cy="18" r="2" fill="currentColor"/><circle cx="12" cy="21" r="1.5" fill="currentColor"/>""",
        "default_color": "#7c3aed",
        "bg_tint": "#faf5ff",
    },
    "wine_flask": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M9 2h6v4H9z" fill="#b45309"/><path d="M10 6v3l-4 7a3 3 0 002.6 4.5h6.8a3 3 0 002.6-4.5l-4-7V6" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="11" cy="14" r="1" fill="#7c3aed"/><circle cx="13" cy="16" r="1.2" fill="#7c3aed"/>""",
        "default_color": "#7c3aed",
        "bg_tint": "#faf5ff",
    },
    "flame": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2c1.5 3 4 5 4 9a6 6 0 11-12 0c0-4 3-6 4-9 1 2 2 3 4 0z" fill="currentColor"/><path d="M12 12c1 1.5 2 2.5 2 4.5a3 3 0 01-6 0c0-2 1.5-3 2-4.5.5 1 1 1.5 2 0z" fill="#fef08a"/>""",
        "default_color": "#f97316",
        "bg_tint": "#fff7ed",
    },
    "thermometer": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="11.5" cy="17.5" r="2.5" fill="currentColor"/><path d="M11.5 7v7" stroke="currentColor" stroke-width="2"/>""",
        "default_color": "#dc2626",
        "bg_tint": "#fef2f2",
    },
    "water_droplet": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z" fill="currentColor"/><circle cx="10" cy="14" r="1.5" fill="#ffffff" opacity="0.6"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },
    "ice_cube": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2L3 7v10l9 5 9-5V7l-9-5z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 22V12M21 7l-9 5L3 7" stroke="currentColor" stroke-width="1.8"/>""",
        "default_color": "#06b6d4",
        "bg_tint": "#ecfeff",
    },
    "leaf": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M11 20A7 7 0 014 13C4 7 11 3 20 3c0 9-4 16-9 17z" fill="currentColor"/><path d="M4 21l7-7" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>""",
        "default_color": "#16a34a",
        "bg_tint": "#f0fdf4",
    },
    "apple": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2v3M10 2c2 1 4 0 5-1" stroke="#16a34a" stroke-width="2" stroke-linecap="round"/><path d="M12 7c-2-2-5-2-7 0s-2 6 1 9 6 5 6 5 3-2 6-5 3-7 1-9-5-2-7 0z" fill="currentColor"/>""",
        "default_color": "#dc2626",
        "bg_tint": "#fef2f2",
    },

    # ── Chemistry & Laboratory ───────────────────────────────────────────────
    "beaker": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M5 3h14M7 3v3l-3 9a4 4 0 003.8 5h8.4a4 4 0 003.8-5l-3-9V3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M6 14h12" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/><circle cx="10" cy="17" r="1" fill="currentColor"/><circle cx="14" cy="18" r="1.2" fill="currentColor"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },
    "flask": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M10 2h4M10 2v5L4 18a2 2 0 001.7 3h12.6a2 2 0 001.7-3l-6-11V2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M6.5 15h11" stroke="currentColor" stroke-width="1.5"/><circle cx="11" cy="18" r="1" fill="currentColor"/><circle cx="14" cy="17" r="1.3" fill="currentColor"/>""",
        "default_color": "#0d9488",
        "bg_tint": "#f0fdfa",
    },
    "atom": {
        "viewBox": "0 0 24 24",
        "svg": """<ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" stroke-width="1.6"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)" fill="none" stroke="currentColor" stroke-width="1.6"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="2.5" fill="currentColor"/>""",
        "default_color": "#6366f1",
        "bg_tint": "#eef2ff",
    },
    "molecule": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="6" cy="12" r="3.5" fill="currentColor"/><circle cx="18" cy="7" r="3.5" fill="currentColor"/><circle cx="17" cy="18" r="3" fill="currentColor"/><path d="M9 11l6-3M9 13l5 4" stroke="currentColor" stroke-width="2"/>""",
        "default_color": "#0891b2",
        "bg_tint": "#ecfeff",
    },
    "bubbles": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="8" cy="15" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="16" cy="10" r="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="10" cy="6" r="2.5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17" cy="18" r="2" fill="currentColor"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },

    # ── Physics & Mechanics ──────────────────────────────────────────────────
    "sphere_ball": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="12" cy="12" r="8" fill="currentColor"/><circle cx="9" cy="9" r="2.5" fill="#ffffff" opacity="0.6"/><path d="M4 20h16" stroke="#475569" stroke-width="2" stroke-linecap="round"/>""",
        "default_color": "#2563eb",
        "bg_tint": "#eff6ff",
    },
    "velocity_arrow": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M4 12h14M14 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 8l3-3M2 16l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>""",
        "default_color": "#dc2626",
        "bg_tint": "#fef2f2",
    },
    "gear": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 15a3 3 0 100-6 3 3 0 000 6z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" fill="none" stroke="currentColor" stroke-width="1.8"/>""",
        "default_color": "#475569",
        "bg_tint": "#f8fafc",
    },
    "battery": {
        "viewBox": "0 0 24 24",
        "svg": """<rect x="2" y="6" width="17" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M21 10v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M6 10v4M9 12H6M13 12h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>""",
        "default_color": "#16a34a",
        "bg_tint": "#f0fdf4",
    },
    "bulb": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M9 18h6m-5 3h4M12 2a7 7 0 00-5 11.9c.7.7 1 1.6 1 2.6V18h8v-1.5c0-1 .3-1.9 1-2.6A7 7 0 0012 2z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="8" r="2.5" fill="#fef08a"/>""",
        "default_color": "#eab308",
        "bg_tint": "#fefce8",
    },
    "magnet": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M4 4v7a8 8 0 0016 0V4M4 8h5M15 8h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M4 4h5v4H4z" fill="#dc2626"/><path d="M15 4h5v4h-5z" fill="#2563eb"/>""",
        "default_color": "#dc2626",
        "bg_tint": "#fef2f2",
    },

    # ── Biology & Medical ────────────────────────────────────────────────────
    "cell": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="currentColor"/><circle cx="8" cy="8" r="1.5" fill="currentColor" opacity="0.6"/><circle cx="16" cy="15" r="1.2" fill="currentColor" opacity="0.6"/>""",
        "default_color": "#059669",
        "bg_tint": "#ecfdf5",
    },
    "dna": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M4 3c4 3 6 7 6 9s-2 6-6 9M20 3c-4 3-6 7-6 9s2 6 6 9M7 6h10M5 12h14M7 18h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },
    "neuron": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="8" cy="12" r="3" fill="currentColor"/><path d="M5 12H2M8 9V6M8 15v3M11 12h10M17 9l4 3-4 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>""",
        "default_color": "#7c3aed",
        "bg_tint": "#faf5ff",
    },
    "heart": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="currentColor"/>""",
        "default_color": "#e11d48",
        "bg_tint": "#fff1f2",
    },

    # ── Mathematics & Geometry ───────────────────────────────────────────────
    "coordinate_axis": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M3 20h18M5 2v18" fill="none" stroke="#475569" stroke-width="1.8" stroke-linecap="round"/><path d="M5 17q6-12 14-13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>""",
        "default_color": "#2563eb",
        "bg_tint": "#eff6ff",
    },
    "geometry_triangle": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M4 20h16L4 4v16z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="4" y="16" width="4" height="4" fill="none" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#0d9488",
        "bg_tint": "#f0fdfa",
    },
    "scale_balance": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 3v18M5 21h14M2 8l10-4 10 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M4 14a3 3 0 006 0L7 8zM14 14a3 3 0 006 0l-3-6z" fill="none" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#d97706",
        "bg_tint": "#fffbeb",
    },

    # ── Social Studies, History & Economics ──────────────────────────────────
    "globe": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><ellipse cx="12" cy="12" rx="4" ry="9" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3.5 9h17M3.5 15h17" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },
    "timeline_flag": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M4 2v20M4 4h12l-2 5 2 5H4" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>""",
        "default_color": "#dc2626",
        "bg_tint": "#fef2f2",
    },
    "coins_trade": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="9" cy="14" r="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="15" cy="9" r="5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 12v4M15 7v4" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#ca8a04",
        "bg_tint": "#fefce8",
    },
    "pyramid": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2L2 20h20L12 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M7 11h10M5 16h14" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#b45309",
        "bg_tint": "#fffbeb",
    },

    # ── Computer Science & Machine Learning ──────────────────────────────────
    "neural_net": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="5" cy="7" r="2" fill="currentColor"/><circle cx="5" cy="17" r="2" fill="currentColor"/><circle cx="12" cy="12" r="2.5" fill="currentColor"/><circle cx="19" cy="7" r="2" fill="currentColor"/><circle cx="19" cy="17" r="2" fill="currentColor"/><path d="M7 7l3 4M7 17l3-4M14 11l3-3M14 13l3 3" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#9333ea",
        "bg_tint": "#faf5ff",
    },
    "cpu_chip": {
        "viewBox": "0 0 24 24",
        "svg": """<rect x="5" y="5" width="14" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><rect x="9" y="9" width="6" height="6" fill="currentColor"/><path d="M9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4" stroke="currentColor" stroke-width="1.5"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },

    # ── Common & Pedagogical Accents ─────────────────────────────────────────
    "sparkles": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M12 2l2.4 5.6L20 10l-5.6 2.4L12 18l-2.4-5.6L4 10l5.6-2.4L12 2zM19 16l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z" fill="currentColor"/>""",
        "default_color": "#f59e0b",
        "bg_tint": "#fffbeb",
    },
    "check_circle": {
        "viewBox": "0 0 24 24",
        "svg": """<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 12l3 3 5-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>""",
        "default_color": "#16a34a",
        "bg_tint": "#f0fdf4",
    },
    "microscope": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M6 18h12M10 18v-4a4 4 0 014-4h1M15 6a3 3 0 100-6 3 3 0 000 6zM9 10l5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>""",
        "default_color": "#0284c7",
        "bg_tint": "#f0f9ff",
    },
    "book_knowledge": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>""",
        "default_color": "#2563eb",
        "bg_tint": "#eff6ff",
    },
    "arrow_right": {
        "viewBox": "0 0 24 24",
        "svg": """<path d="M5 12h14M12 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>""",
        "default_color": "#2563eb",
        "bg_tint": "#eff6ff",
    },
}


# ── Semantic Keyword Matcher ─────────────────────────────────────────────────

_KEYWORD_RULES: list[Tuple[re.Pattern, str, str]] = [
    # Milk & Dairy
    (re.compile(r"\b(milk\w*|curd\w*|dairy|lactic|summer|room temp\w*|spoil\w*)\b", re.I), "milk_bottle", "MILK / LIQUID"),
    # Iron, rust & corrosion
    (re.compile(r"\b(iron\w*|rust\w*|tawa\w*|pan\w*|nail\w*|corros\w*|metal\w*|humid\w*|moist\w*|oxid\w*)\b", re.I), "iron_nail", "METAL OXIDATION"),
    # Grapes & fermentation
    (re.compile(r"\b(grapes?|ferment\w*|yeast\w*|wine\w*|alcohol\w*|brew\w*|sugar\w*)\b", re.I), "grapes", "FERMENTATION"),
    # Heat, flame & combustion
    (re.compile(r"\b(burn\w*|flame\w*|fire\w*|heat\w*|combust\w*|thermal|ignit\w*)\b", re.I), "flame", "THERMAL HEAT"),
    (re.compile(r"\b(temperature|thermometer|degree|celsius|boil\w*|melt\w*)\b", re.I), "thermometer", "TEMPERATURE"),
    (re.compile(r"\b(ice|freeze|freezing|cold|solid\w*|crystall\w*)\b", re.I), "ice_cube", "PHASE CHANGE"),
    (re.compile(r"\b(water|droplet\w*|aqueous|liquid\w*|solution\w*|dissolv\w*)\b", re.I), "water_droplet", "AQUEOUS PHASE"),
    # Chemistry & Lab
    (re.compile(r"\b(flask\w*|beaker\w*|solution\w*|reagent\w*|test tube\w*|acid\w*|base\w*)\b", re.I), "flask", "REACTION FLASK"),
    (re.compile(r"\b(atom\w*|electron\w*|proton\w*|neutron\w*|nucleus|atomic)\b", re.I), "atom", "ATOMIC STRUCTURE"),
    (re.compile(r"\b(molecule\w*|bond\w*|covalent|ionic|compound\w*|ch4|co2)\b", re.I), "molecule", "MOLECULAR BOND"),
    (re.compile(r"\b(gas\w*|bubble\w*|effervesc\w*|fume\w*|vapor\w*)\b", re.I), "bubbles", "GAS EVOLUTION"),
    # Physics & Mechanics
    (re.compile(r"\b(inertia\w*|ball\w*|sphere\w*|motion\w*|velocity|speed|newton\w*|momentum)\b", re.I), "sphere_ball", "INERTIA MOTION"),
    (re.compile(r"\b(force\w*|accelerat\w*|vector\w*|friction\w*|push\w*|pull\w*)\b", re.I), "velocity_arrow", "FORCE VECTOR"),
    (re.compile(r"\b(gear\w*|engine\w*|machine\w*|mechanical|transmission)\b", re.I), "gear", "MECHANISM"),
    (re.compile(r"\b(battery|batteries|cell\w*|voltage|power|circuit\w*|current)\b", re.I), "battery", "CIRCUIT POWER"),
    (re.compile(r"\b(bulb\w*|light\w*|lamp\w*|glow\w*|illuminat\w*)\b", re.I), "bulb", "ENERGY LIGHT"),
    (re.compile(r"\b(magnet\w*|pole\w*|attract\w*|repel\w*)\b", re.I), "magnet", "MAGNETIC FORCE"),
    # Biology & Medical
    (re.compile(r"\b(leaf|leaves|plant\w*|photosynthe\w*|chlorophyll|stoma\w*)\b", re.I), "leaf", "BOTANICAL"),
    (re.compile(r"\b(cell\w*|mitosis|cytoplasm|membrane\w*|organelle\w*)\b", re.I), "cell", "CELLULAR BIOLOGY"),
    (re.compile(r"\b(dna|gene\w*|helix|genetic\w*|chromosome\w*)\b", re.I), "dna", "GENETICS"),
    (re.compile(r"\b(brain\w*|neuron\w*|nerve\w*|synapse\w*|reflex\w*)\b", re.I), "neuron", "NEURAL PATHWAY"),
    (re.compile(r"\b(heart\w*|blood\w*|cardiac|circulat\w*|arter\w*)\b", re.I), "heart", "CIRCULATION"),
    # Mathematics
    (re.compile(r"\b(graph\w*|coordinate\w*|cartesian|axis|axes|slope\w*|curve\w*|parabola\w*)\b", re.I), "coordinate_axis", "COORDINATE GRAPH"),
    (re.compile(r"\b(triangle\w*|angle\w*|geometry|pythagor\w*|hypotenuse)\b", re.I), "geometry_triangle", "GEOMETRY"),
    (re.compile(r"\b(balance\w*|equation\w*|equal\w*|conserv\w*|mass\w*|weight\w*)\b", re.I), "scale_balance", "EQUILIBRIUM"),
    # Social Studies
    (re.compile(r"\b(globe\w*|earth|world|geograph\w*|planet\w*|continent\w*)\b", re.I), "globe", "GLOBAL SYSTEM"),
    (re.compile(r"\b(history|timeline\w*|century|centuries|era\w*|dynasty|war\w*|revolution\w*)\b", re.I), "timeline_flag", "HISTORICAL TIMELINE"),
    (re.compile(r"\b(money|coin\w*|trade\w*|market\w*|economy|economic|currency)\b", re.I), "coins_trade", "ECONOMIC TRADE"),
    # CS / ML
    (re.compile(r"\b(neural\w*|network\w*|deep learning|ai|machine learning|model\w*)\b", re.I), "neural_net", "NEURAL NETWORK"),
    (re.compile(r"\b(chip\w*|cpu|processor\w*|hardware|silicon)\b", re.I), "cpu_chip", "COMPUTE HARDWARE"),
]


def resolve_semantic_icon(text: str, fallback: str = "sparkles") -> dict[str, Any]:
    """Resolve the most accurate vector icon for a concept or narration string."""
    clean_text = text.lower()
    for pattern, icon_key, label in _KEYWORD_RULES:
        if pattern.search(clean_text):
            data = ICONS.get(icon_key, ICONS[fallback])
            return {
                "key": icon_key,
                "label": label,
                "svg": data["svg"],
                "viewBox": data["viewBox"],
                "color": data["default_color"],
                "bg_tint": data["bg_tint"],
            }

    data = ICONS.get(fallback, ICONS["sparkles"])
    return {
        "key": fallback,
        "label": "CONCEPT HIGHLIGHT",
        "svg": data["svg"],
        "viewBox": data["viewBox"],
        "color": data["default_color"],
        "bg_tint": data["bg_tint"],
    }


def render_icon_element(
    icon_dict: dict[str, Any],
    cx: float,
    cy: float,
    size: float = 36,
    color: str | None = None,
) -> str:
    """Render an icon centered at (cx, cy) with standard SVG scaling."""
    viewbox = icon_dict.get("viewBox", "0 0 24 24")
    vb_w, vb_h = (float(x) for x in viewbox.split()[-2:])
    scale_x = size / vb_w
    scale_y = size / vb_h
    icon_color = color or icon_dict.get("color", "#2563eb")
    x = cx - size / 2
    y = cy - size / 2

    return f"""<g transform="translate({x:.1f}, {y:.1f}) scale({scale_x:.3f}, {scale_y:.3f})" color="{icon_color}">
      {icon_dict["svg"]}
    </g>"""
