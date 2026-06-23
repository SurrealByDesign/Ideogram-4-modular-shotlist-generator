from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class BuildPreset:
    name: str
    mode: str
    count: int
    style: str


BUILD_PRESETS: dict[str, BuildPreset] = {
    "character_lora": BuildPreset(
        name="character_lora",
        mode="character_lora",
        count=50,
        style="clean character reference sheet, consistent identity, dataset-friendly concept art",
    ),
    "character_lora_core": BuildPreset(
        name="character_lora_core",
        mode="character_lora_core",
        count=30,
        style="clean core character LoRA reference, consistent identity, neutral readable views",
    ),
    "character_lora_turnaround": BuildPreset(
        name="character_lora_turnaround",
        mode="character_lora_turnaround",
        count=24,
        style="technical character turnaround sheet, consistent proportions, neutral lighting",
    ),
    "character_lora_expressions": BuildPreset(
        name="character_lora_expressions",
        mode="character_lora_expressions",
        count=20,
        style="consistent character facial expression study, clean portrait reference",
    ),
    "character_lora_costume_details": BuildPreset(
        name="character_lora_costume_details",
        mode="character_lora_costume_details",
        count=20,
        style="character costume and accessory detail reference, material clarity",
    ),
    "character_lora_action": BuildPreset(
        name="character_lora_action",
        mode="character_lora_action",
        count=24,
        style="character pose variety for LoRA training, identity preserved, clear silhouette",
    ),
    "character_lora_environment": BuildPreset(
        name="character_lora_environment",
        mode="character_lora_environment",
        count=18,
        style="character in simple context scenes, identity prioritized over environment",
    ),
    "three_d_reference": BuildPreset(
        name="three_d_reference",
        mode="three_d_reference",
        count=30,
        style="technical 3D model reference, orthographic clarity, neutral lighting",
    ),
    "product_sheet": BuildPreset(
        name="product_sheet",
        mode="product_sheet",
        count=24,
        style="commercial product concept sheet, clean studio presentation",
    ),
    "poster": BuildPreset(
        name="poster",
        mode="poster",
        count=12,
        style="cinematic poster key art, designed layout, readable typography zones",
    ),
}


def slugify_subject(subject: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", subject.lower()).strip("_")
    return slug[:48].strip("_") or "subject"


def default_output_dir(subject: str, preset_or_mode: str) -> str:
    return str(Path("outputs") / f"{slugify_subject(subject)}_{preset_or_mode}")


def get_preset(name: str) -> BuildPreset:
    try:
        return BUILD_PRESETS[name]
    except KeyError as exc:
        valid = ", ".join(sorted(BUILD_PRESETS))
        raise ValueError(f"unknown preset '{name}'. Choose one of: {valid}") from exc
