from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StyleProfile:
    name: str
    prompt: str
    negative_terms: tuple[str, ...]
    notes: str


STYLE_PROFILES: dict[str, StyleProfile] = {
    "clean_reference": StyleProfile(
        name="clean_reference",
        prompt="clean reference lighting, readable silhouette, minimal stylization",
        negative_terms=("heavy atmosphere", "busy background", "extreme lens distortion"),
        notes="Best for reusable character, product, or 3D reference planning.",
    ),
    "cinematic_realism": StyleProfile(
        name="cinematic_realism",
        prompt="cinematic realistic concept art, controlled contrast, grounded materials",
        negative_terms=("cartoonish rendering", "overly glossy plastic", "flat lighting"),
        notes="Best for polished concept-art batches that still need consistent forms.",
    ),
    "storybook_illustration": StyleProfile(
        name="storybook_illustration",
        prompt="storybook illustration, hand-painted texture, clear charming shapes",
        negative_terms=("photorealism", "harsh neon lighting", "gritty horror mood"),
        notes="Best for softer illustrative plans and expressive character sets.",
    ),
    "technical_sheet": StyleProfile(
        name="technical_sheet",
        prompt="technical design sheet, orthographic clarity, measured proportions",
        negative_terms=("dramatic perspective", "motion blur", "decorative clutter"),
        notes="Best for turnarounds, model sheets, props, and construction references.",
    ),
}

STYLE_INTENSITIES = ("light", "standard", "strong")


def get_style_profile(name: str | None, intensity: str = "standard") -> dict[str, Any]:
    if not name:
        return {}
    if intensity not in STYLE_INTENSITIES:
        valid_intensities = ", ".join(STYLE_INTENSITIES)
        raise ValueError(f"unknown style intensity '{intensity}'. Choose one of: {valid_intensities}")
    try:
        profile = STYLE_PROFILES[name]
    except KeyError as exc:
        valid = ", ".join(sorted(STYLE_PROFILES))
        raise ValueError(f"unknown style profile '{name}'. Choose one of: {valid}") from exc
    return {
        "name": profile.name,
        "prompt": prompt_for_intensity(profile.prompt, intensity),
        "base_prompt": profile.prompt,
        "intensity": intensity,
        "negative_terms": list(profile.negative_terms),
        "notes": profile.notes,
    }


def prompt_for_intensity(prompt: str, intensity: str) -> str:
    if intensity == "light":
        return f"subtle {prompt}"
    if intensity == "strong":
        return f"strongly emphasize {prompt}"
    return prompt


def style_with_profile(style: str, style_profile: dict[str, Any]) -> str:
    profile_prompt = str(style_profile.get("prompt", "")).strip()
    style = style.strip()
    if profile_prompt and style:
        return f"{style}, {profile_prompt}"
    return profile_prompt or style
