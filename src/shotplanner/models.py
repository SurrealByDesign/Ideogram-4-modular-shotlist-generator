from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptRecord:
    id: str
    subject: str
    mode: str
    shot_type: str = ""
    angle: str = ""
    aspect_ratio: str = ""
    prompt_text: str = ""
    negative_prompt: str = ""
    character_bible: dict[str, Any] = field(default_factory=dict)
    style_description: dict[str, Any] = field(default_factory=dict)
    bbox_layout: dict[str, Any] = field(default_factory=dict)
    color_palette: dict[str, Any] = field(default_factory=dict)
    ideogram_json: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    review: dict[str, Any] = field(default_factory=dict)
    result_refs: list[dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "mode": self.mode,
            "shot_type": self.shot_type,
            "angle": self.angle,
            "aspect_ratio": self.aspect_ratio,
            "prompt_text": self.prompt_text,
            "negative_prompt": self.negative_prompt,
            "character_bible": self.character_bible,
            "style_description": self.style_description,
            "bbox_layout": self.bbox_layout,
            "color_palette": self.color_palette,
            "ideogram_json": self.ideogram_json,
            "metadata": self.metadata,
            "review": self.review,
            "result_refs": self.result_refs,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptRecord":
        known = {
            "id",
            "subject",
            "mode",
            "shot_type",
            "angle",
            "aspect_ratio",
            "prompt_text",
            "negative_prompt",
            "character_bible",
            "style_description",
            "bbox_layout",
            "color_palette",
            "ideogram_json",
            "metadata",
            "review",
            "result_refs",
            "extra",
        }
        init_data = {key: data[key] for key in known if key in data}
        record = cls(**init_data)
        unknown = {key: value for key, value in data.items() if key not in known}
        if unknown:
            record.extra.update(unknown)
        return record
