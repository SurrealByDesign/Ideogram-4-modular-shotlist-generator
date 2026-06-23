from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class ColorPalette:
    name: str
    colors: tuple[str, ...]
    mood: str
    usage: str


COLOR_PALETTES: dict[str, ColorPalette] = {
    "character_reference": ColorPalette(
        name="character_reference",
        colors=("#f2efe8", "#4b5563", "#8a5a44", "#c9b37e", "#2f3a45"),
        mood="neutral reference colors with a few material accents",
        usage="Keep identity, materials, and silhouette readable across the set.",
    ),
    "technical_neutral": ColorPalette(
        name="technical_neutral",
        colors=("#f7f7f5", "#d8dadd", "#8f959e", "#4f5661", "#20242a"),
        mood="flat technical neutrals",
        usage="Prioritize form, contour, and material breaks over atmosphere.",
    ),
    "product_studio": ColorPalette(
        name="product_studio",
        colors=("#ffffff", "#eef1f4", "#c7ccd3", "#4a5565", "#111827"),
        mood="clean commercial studio palette",
        usage="Use bright grounds, crisp edges, and controlled reflections.",
    ),
    "cinematic_poster": ColorPalette(
        name="cinematic_poster",
        colors=("#111827", "#394150", "#b84a3a", "#f2c15b", "#f7efe1"),
        mood="cinematic contrast with warm key-art accents",
        usage="Separate hero subject, background depth, and text-safe zones clearly.",
    ),
    "watercolor_fantasy": ColorPalette(
        name="watercolor_fantasy",
        colors=("#f4ead7", "#88a6a3", "#586f5c", "#b87952", "#513b56"),
        mood="soft illustrated fantasy color",
        usage="Keep washes gentle while preserving costume and prop details.",
    ),
    "monochrome_ink": ColorPalette(
        name="monochrome_ink",
        colors=("#fafafa", "#d7d7d7", "#8b8b8b", "#3d3d3d", "#111111"),
        mood="restrained monochrome drawing palette",
        usage="Emphasize linework, shape clarity, and value separation.",
    ),
}


MODE_DEFAULT_PALETTES: dict[str, str] = {
    "character_lora": "character_reference",
    "character_lora_core": "character_reference",
    "character_lora_turnaround": "technical_neutral",
    "character_lora_expressions": "character_reference",
    "character_lora_costume_details": "character_reference",
    "character_lora_action": "character_reference",
    "character_lora_environment": "character_reference",
    "three_d_reference": "technical_neutral",
    "product_sheet": "product_studio",
    "poster": "cinematic_poster",
}


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def validate_palette(palette: ColorPalette) -> None:
    if not palette.name:
        raise ValueError("palette must include a name")
    if not palette.colors:
        raise ValueError(f"palette {palette.name} must include colors")
    for color in palette.colors:
        if not HEX_COLOR_RE.match(color):
            raise ValueError(f"palette {palette.name} has invalid color: {color}")
    if not palette.mood:
        raise ValueError(f"palette {palette.name} must include a mood")
    if not palette.usage:
        raise ValueError(f"palette {palette.name} must include usage guidance")


def validate_palettes() -> None:
    for palette in COLOR_PALETTES.values():
        validate_palette(palette)
    for mode, palette_name in MODE_DEFAULT_PALETTES.items():
        if palette_name not in COLOR_PALETTES:
            raise ValueError(f"mode {mode} references unknown palette: {palette_name}")


def get_palette(name: str) -> dict[str, Any]:
    if name not in COLOR_PALETTES:
        valid = ", ".join(sorted(COLOR_PALETTES))
        raise KeyError(f"unknown color palette: {name}. Choose one of: {valid}")
    palette = COLOR_PALETTES[name]
    return deepcopy(
        {
            "name": palette.name,
            "colors": list(palette.colors),
            "mood": palette.mood,
            "usage": palette.usage,
            "source": "static_palette_catalog",
        }
    )


def default_palette_for_mode(mode: str) -> str:
    return MODE_DEFAULT_PALETTES.get(mode, "character_reference")
