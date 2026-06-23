from __future__ import annotations

from collections import Counter
from typing import Any

from .models import PromptRecord


CHARACTER_BIBLE_FIELDS = (
    "identity",
    "face",
    "hair",
    "body",
    "outfit",
    "accessories",
    "must_keep",
    "avoid",
)


CHARACTER_LORA_COVERAGE: dict[str, set[str]] = {
    "portrait": {"portrait"},
    "full_body": {"full_body"},
    "front_view": {"portrait", "full_body", "front_view"},
    "three_quarter": {"three_quarter", "three_quarter_front", "three_quarter_back", "expression_profile", "head_turnaround"},
    "side_view": {"side_view", "left_side_view", "right_side_view"},
    "back_view": {"back_view"},
    "action_pose": {
        "action_pose",
        "walking_pose",
        "turning_pose",
        "reaching_pose",
        "crouching_pose",
        "hero_pose",
    },
    "expression": {
        "expression",
        "expression_smile",
        "expression_serious",
        "expression_surprised",
        "expression_angry",
        "expression_profile",
    },
    "costume_detail": {
        "costume_detail",
        "accessory_detail",
        "material_detail",
        "hands_or_gloves",
        "footwear_detail",
        "prop_detail",
    },
    "environment": {"environment", "workshop_context", "street_context", "interior_context"},
    "neutral_reference": {"neutral_reference", "turnaround_sheet", "head_turnaround"},
}


CHARACTER_LORA_MODE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "character_lora": tuple(CHARACTER_LORA_COVERAGE),
    "character_lora_multipack": tuple(CHARACTER_LORA_COVERAGE),
    "character_lora_core": (
        "portrait",
        "full_body",
        "front_view",
        "three_quarter",
        "side_view",
        "back_view",
        "neutral_reference",
    ),
    "character_lora_turnaround": (
        "front_view",
        "three_quarter",
        "side_view",
        "back_view",
        "neutral_reference",
    ),
    "character_lora_expressions": ("portrait", "three_quarter", "expression"),
    "character_lora_costume_details": ("full_body", "costume_detail"),
    "character_lora_action": ("full_body", "action_pose", "neutral_reference"),
    "character_lora_environment": ("portrait", "full_body", "environment", "neutral_reference"),
}


CHARACTER_LORA_MODE_DESCRIPTIONS = {
    "character_lora": "Balanced all-in-one character LoRA plan.",
    "character_lora_multipack": "Complete multi-pack character LoRA plan.",
    "character_lora_core": "Core identity pack for clean reusable character views.",
    "character_lora_turnaround": "Turnaround pack for front, side, back, and three-quarter reference.",
    "character_lora_expressions": "Expression pack for face consistency and expression variation.",
    "character_lora_costume_details": "Costume detail pack for outfit, material, accessory, and prop references.",
    "character_lora_action": "Action pack for pose variety while preserving identity.",
    "character_lora_environment": "Environment pack for light context scenes while keeping identity primary.",
}


CHARACTER_LORA_RECOMMENDATION_LABELS = {
    "portrait": "portrait records",
    "full_body": "full-body records",
    "front_view": "front-view reference records",
    "three_quarter": "three-quarter reference records",
    "side_view": "side-view reference records",
    "back_view": "back-view reference records",
    "action_pose": "action pose records",
    "expression": "expression records",
    "costume_detail": "costume or accessory detail records",
    "environment": "environment context records",
    "neutral_reference": "neutral reference records",
}


CHARACTER_LORA_RECOMMENDATION_EXAMPLES = {
    "portrait": "portrait",
    "full_body": "full_body",
    "front_view": "front_view or full_body",
    "three_quarter": "three_quarter_front or three_quarter_back",
    "side_view": "left_side_view or right_side_view",
    "back_view": "back_view",
    "action_pose": "walking_pose, reaching_pose, or hero_pose",
    "expression": "expression_smile, expression_serious, or expression_surprised",
    "costume_detail": "costume_detail, hands_or_gloves, or prop_detail",
    "environment": "workshop_context, street_context, or interior_context",
    "neutral_reference": "neutral_reference, turnaround_sheet, or head_turnaround",
}


def build_character_bible(**values: str | None) -> dict[str, str]:
    return {
        field: str(values.get(field, "")).strip()
        for field in CHARACTER_BIBLE_FIELDS
        if values.get(field) is not None and str(values.get(field, "")).strip()
    }


def character_bible_text(character_bible: dict[str, Any]) -> str:
    if not character_bible:
        return ""
    labels = {
        "face": "face",
        "hair": "hair",
        "body": "body",
        "outfit": "outfit",
        "accessories": "accessories",
        "must_keep": "must keep",
        "avoid": "avoid",
    }
    parts = []
    identity = str(character_bible.get("identity", "")).strip().rstrip(".")
    if identity:
        parts.append(identity)
    for field in CHARACTER_BIBLE_FIELDS:
        if field == "identity":
            continue
        value = str(character_bible.get(field, "")).strip().rstrip(".")
        if value:
            parts.append(f"{labels[field]}: {value}")
    if not parts:
        return ""
    return "Identity anchor: " + "; ".join(parts) + "."


def lora_coverage_report(records: list[PromptRecord]) -> dict[str, Any]:
    character_records = [record for record in records if record.mode.startswith("character_lora")]
    modes = {record.mode for record in character_records}
    packs = {record.metadata.get("pack", "") for record in character_records if record.metadata.get("pack")}
    if len(modes) > 1 and packs:
        mode = "character_lora_multipack"
    else:
        mode = character_records[0].mode if character_records else "character_lora"
    required = list(CHARACTER_LORA_MODE_REQUIREMENTS.get(mode, tuple(CHARACTER_LORA_COVERAGE)))
    counts = Counter(record.shot_type for record in character_records)
    coverage = {
        category: sum(counts[shot_type] for shot_type in shot_types)
        for category, shot_types in CHARACTER_LORA_COVERAGE.items()
    }
    missing = [category for category in required if coverage[category] == 0]
    thin = [category for category in required if coverage[category] == 1]
    if character_records and not missing and thin:
        status = "ready_with_thin_coverage"
    elif character_records and not missing:
        status = "ready"
    else:
        status = "needs_review"
    recommendations = lora_coverage_recommendations(required=required, coverage=coverage)
    return {
        "mode": mode,
        "description": CHARACTER_LORA_MODE_DESCRIPTIONS.get(mode, "Character LoRA planning coverage."),
        "required": required,
        "applies": bool(character_records),
        "total_records": len(character_records),
        "coverage": coverage,
        "missing": missing,
        "thin": thin,
        "status": status,
        "decision": lora_coverage_decision(status=status, mode=mode, missing=missing, thin=thin),
        "recommendations": recommendations,
    }


def lora_coverage_recommendations(required: list[str], coverage: dict[str, int]) -> list[dict[str, Any]]:
    recommendations = []
    for category in required:
        current = coverage.get(category, 0)
        if current >= 2:
            continue
        add_count = 2 - current
        label = CHARACTER_LORA_RECOMMENDATION_LABELS.get(category, category.replace("_", " ") + " records")
        examples = CHARACTER_LORA_RECOMMENDATION_EXAMPLES.get(category, category)
        record_word = "record" if add_count == 1 else "records"
        summary = f"Add at least {add_count} {label}."
        if label.endswith(" records"):
            summary = f"Add at least {add_count} {label.removesuffix(' records')} {record_word}."
        recommendations.append(
            {
                "category": category,
                "current": current,
                "target": 2,
                "add_count": add_count,
                "summary": summary,
                "examples": examples,
            }
        )
    return recommendations


def lora_coverage_decision(status: str, mode: str, missing: list[str], thin: list[str]) -> dict[str, str]:
    mode_label = mode.replace("_", " ")
    missing_text = ", ".join(item.replace("_", " ") for item in missing)
    thin_text = ", ".join(item.replace("_", " ") for item in thin)
    if status == "needs_review":
        summary = f"This {mode_label} plan is missing required coverage: {missing_text}."
        recommendation = "Add records or increase pack counts before using this as a real LoRA planning set."
    elif status == "ready_with_thin_coverage":
        summary = f"This {mode_label} plan includes required coverage, but thin categories need review: {thin_text}."
        recommendation = "Use it for a smoke test, or increase thin categories/default pack counts for a stronger dataset plan."
    else:
        summary = f"This {mode_label} plan includes the required coverage categories."
        recommendation = "Proceed with review of prompts and bbox layouts before generation."
    return {"summary": summary, "recommendation": recommendation}
