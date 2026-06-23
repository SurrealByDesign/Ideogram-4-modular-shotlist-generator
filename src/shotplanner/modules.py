from __future__ import annotations

from collections import Counter
from typing import Iterable

from .bbox import validate_layout
from .character import character_bible_text
from .models import PromptRecord
from .palettes import default_palette_for_mode, get_palette
from .shotlists import get_mode_specs
from .templates import get_template


class ShotlistPlanner:
    def plan(
        self,
        subject: str,
        mode: str,
        count: int,
        style: str = "",
        style_profile: dict[str, object] | None = None,
        character_bible: dict[str, str] | None = None,
    ) -> list[PromptRecord]:
        if count < 1:
            raise ValueError("count must be at least 1")
        specs = get_mode_specs(mode)
        records: list[PromptRecord] = []
        for index in range(count):
            spec = specs[index % len(specs)]
            records.append(
                PromptRecord(
                    id=f"{mode}-{index + 1:04d}",
                    subject=subject,
                    mode=mode,
                    shot_type=spec.shot_type,
                    angle=spec.angle,
                    character_bible=dict(character_bible or {}),
                    style_description=self._style_description(style, style_profile),
                    metadata={
                        "sequence_index": index,
                        "bbox_template": spec.template,
                        "planner": "ShotlistPlanner",
                    },
                )
            )
        return records

    def _style_description(self, style: str, style_profile: dict[str, object] | None) -> dict[str, object]:
        description: dict[str, object] = {"name": style, "source": "cli"} if style else {}
        if style_profile:
            description["profile"] = style_profile
        return description


class BBoxLayoutAssigner:
    def apply(self, records: Iterable[PromptRecord]) -> list[PromptRecord]:
        updated = list(records)
        for record in updated:
            template_name = record.metadata.get("bbox_template", "centered_full_body")
            layout = get_template(template_name)
            validate_layout(layout)
            record.bbox_layout = layout
            record.aspect_ratio = layout["aspect_ratio"]
        return updated


class ColorPaletteAssigner:
    def __init__(self, palette_name: str | None = None):
        self.palette_name = palette_name

    def apply(self, records: Iterable[PromptRecord]) -> list[PromptRecord]:
        updated = list(records)
        for record in updated:
            palette_name = self.palette_name or default_palette_for_mode(record.mode)
            record.color_palette = get_palette(palette_name)
            record.metadata["color_palette_source"] = "ColorPaletteAssigner"
        return updated


class PromptTextBuilder:
    def apply(self, records: Iterable[PromptRecord]) -> list[PromptRecord]:
        updated = list(records)
        for record in updated:
            style = record.style_description.get("name", "").strip()
            layout_desc = "; ".join(element["desc"] for element in record.bbox_layout.get("elements", []))
            variation = record.metadata.get("prompt_variation", {})
            identity_text = character_bible_text(record.character_bible)
            variation_text = self._variation_text(variation)
            palette_text = self._palette_text(record.color_palette)
            guidance_parts = [part for part in [identity_text, variation_text, palette_text] if part]
            record.prompt_text = (
                f"{self._lead_text(record, style)}. "
                f"{' '.join(guidance_parts)} "
                f"Layout: {layout_desc}."
            )
            record.negative_prompt = (
                "low quality, blurry, cropped subject, broken anatomy, unreadable text, "
                "extra limbs, distorted layout, inconsistent identity, cluttered background"
            )
            avoid = str(record.character_bible.get("avoid", "")).strip()
            if avoid:
                record.negative_prompt = f"{record.negative_prompt}, {avoid}"
            profile = record.style_description.get("profile", {})
            if isinstance(profile, dict):
                negative_terms = profile.get("negative_terms", [])
                if isinstance(negative_terms, list) and negative_terms:
                    record.negative_prompt = f"{record.negative_prompt}, {', '.join(str(term) for term in negative_terms)}"
        return updated

    def _lead_text(self, record: PromptRecord, style: str) -> str:
        shot = record.shot_type.replace("_", " ").strip()
        angle = record.angle.replace("_", " ").strip()
        parts = [record.subject]
        for part in [shot, angle, style]:
            if part and part not in parts:
                parts.append(part)
        return ", ".join(parts)

    def _variation_text(self, variation: dict[str, str]) -> str:
        if not variation:
            return ""
        parts = [
            variation.get("pose", ""),
            variation.get("framing", ""),
            variation.get("lighting", ""),
            variation.get("background", ""),
            variation.get("detail", ""),
            variation.get("shot_hint", ""),
        ]
        clean_parts = [part for part in parts if part]
        if not clean_parts:
            return ""
        return "Guidance: " + "; ".join(clean_parts) + "."

    def _palette_text(self, palette: dict[str, object]) -> str:
        if not palette:
            return ""
        name = str(palette.get("name", "")).replace("_", " ")
        mood = str(palette.get("mood", ""))
        usage = str(palette.get("usage", ""))
        parts = [part.strip().rstrip(".") for part in [name, mood, usage] if part.strip()]
        if not parts:
            return ""
        return "Palette guidance: " + "; ".join(parts) + "."


class IdeogramJSONBuilder:
    def apply(self, records: Iterable[PromptRecord]) -> list[PromptRecord]:
        updated = list(records)
        for record in updated:
            record.ideogram_json = {
                "prompt": record.prompt_text,
                "negative_prompt": record.negative_prompt,
                "aspect_ratio": record.aspect_ratio,
                "layout": record.bbox_layout,
                "color_palette": record.color_palette,
                "character_bible": record.character_bible,
                "style": record.style_description,
                "metadata": {
                    "id": record.id,
                    "mode": record.mode,
                    "shot_type": record.shot_type,
                    "angle": record.angle,
                },
            }
        return updated


class Validator:
    def validate(self, records: Iterable[PromptRecord]) -> None:
        ids: set[str] = set()
        for record in records:
            if not record.id:
                raise ValueError("record id is required")
            if record.id in ids:
                raise ValueError(f"duplicate record id: {record.id}")
            ids.add(record.id)
            if not record.subject:
                raise ValueError(f"record {record.id} has no subject")
            if record.bbox_layout:
                validate_layout(record.bbox_layout)


def summarize_records(records: Iterable[PromptRecord]) -> dict[str, Counter[str]]:
    record_list = list(records)
    return {
        "shot_type_counts": Counter(record.shot_type for record in record_list),
        "angle_counts": Counter(record.angle for record in record_list),
        "aspect_ratio_counts": Counter(record.aspect_ratio for record in record_list),
        "template_counts": Counter(record.metadata.get("bbox_template", "") for record in record_list),
        "palette_counts": Counter(record.color_palette.get("name", "") for record in record_list),
    }
