from __future__ import annotations

from .models import PromptRecord
from .modules import (
    BBoxLayoutAssigner,
    ColorPaletteAssigner,
    IdeogramJSONBuilder,
    PromptTextBuilder,
    ShotlistPlanner,
    Validator,
)
from .variations import PromptVariationAssigner
from .styles import get_style_profile, style_with_profile


CHARACTER_LORA_PACK_PRESETS = (
    "character_lora_core",
    "character_lora_turnaround",
    "character_lora_expressions",
    "character_lora_costume_details",
    "character_lora_action",
    "character_lora_environment",
)

PACK_LABELS = {
    "character_lora_core": "core",
    "character_lora_turnaround": "turnaround",
    "character_lora_expressions": "expressions",
    "character_lora_costume_details": "costume_details",
    "character_lora_action": "action",
    "character_lora_environment": "environment",
}


def build_records(
    subject: str,
    style: str,
    mode: str,
    count: int,
    palette_name: str | None = None,
    character_bible: dict[str, str] | None = None,
    style_profile_name: str | None = None,
    style_intensity: str = "standard",
) -> list[PromptRecord]:
    style_profile = get_style_profile(style_profile_name, style_intensity)
    style = style_with_profile(style, style_profile)
    records = ShotlistPlanner().plan(
        subject=subject,
        style=style,
        mode=mode,
        count=count,
        style_profile=style_profile,
        character_bible=character_bible,
    )
    records = BBoxLayoutAssigner().apply(records)
    records = ColorPaletteAssigner(palette_name=palette_name).apply(records)
    records = PromptVariationAssigner().apply(records)
    records = PromptTextBuilder().apply(records)
    records = IdeogramJSONBuilder().apply(records)
    Validator().validate(records)
    return records


def build_character_lora_records(
    subject: str,
    character_bible: dict[str, str] | None = None,
    palette_name: str | None = None,
    pack_counts: dict[str, int] | None = None,
    style_profile_name: str | None = None,
    pack_style_profiles: dict[str, str] | None = None,
    style_intensity: str = "standard",
    pack_style_intensity: dict[str, str] | None = None,
) -> list[PromptRecord]:
    from .presets import get_preset

    combined: list[PromptRecord] = []
    pack_counts = pack_counts or {}
    pack_style_profiles = pack_style_profiles or {}
    pack_style_intensity = pack_style_intensity or {}
    for preset_name in CHARACTER_LORA_PACK_PRESETS:
        preset = get_preset(preset_name)
        pack = PACK_LABELS[preset_name]
        count = pack_counts.get(pack, preset.count)
        if count < 1:
            continue
        pack_style_profile_name = pack_style_profiles.get(pack, style_profile_name)
        pack_style_intensity_name = pack_style_intensity.get(pack, style_intensity)
        pack_records = build_records(
            subject=subject,
            style=preset.style,
            mode=preset.mode,
            count=count,
            palette_name=palette_name,
            character_bible=character_bible,
            style_profile_name=pack_style_profile_name,
            style_intensity=pack_style_intensity_name,
        )
        for record in pack_records:
            original_id = record.id
            record.id = f"{pack}-{original_id}"
            record.metadata["pack"] = pack
            record.metadata["pack_preset"] = preset_name
            record.metadata["pack_record_id"] = original_id
            if pack_style_profile_name:
                record.metadata["style_profile"] = pack_style_profile_name
                record.metadata["style_intensity"] = pack_style_intensity_name
            record.ideogram_json["metadata"]["id"] = record.id
            record.ideogram_json["metadata"]["pack"] = pack
            record.ideogram_json["metadata"]["pack_preset"] = preset_name
            if pack_style_profile_name:
                record.ideogram_json["metadata"]["style_profile"] = pack_style_profile_name
                record.ideogram_json["metadata"]["style_intensity"] = pack_style_intensity_name
        combined.extend(pack_records)
    Validator().validate(combined)
    return combined
