from __future__ import annotations

from collections import Counter
from typing import Any

from .bbox import validate_bbox, validate_layout
from .character import lora_coverage_report
from .models import PromptRecord
from .modules import Validator


def validate_records_for_handoff(records: list[PromptRecord]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not records:
        errors.append("records.json contains no records")
        return {"status": "invalid", "errors": errors, "warnings": warnings, "record_count": 0}

    ids = Counter(record.id for record in records)
    for record_id, count in sorted(ids.items()):
        if not record_id:
            errors.append("one or more records are missing an id")
        elif count > 1:
            errors.append(f"duplicate record id: {record_id} appears {count} times")

    for index, record in enumerate(records):
        label = record.id or f"index {index}"
        if not record.subject.strip():
            errors.append(f"{label}: missing subject")
        if not record.mode.strip():
            errors.append(f"{label}: missing mode")
        if not record.prompt_text.strip():
            errors.append(f"{label}: missing prompt_text")
        if not record.negative_prompt.strip():
            warnings.append(f"{label}: missing negative_prompt")
        if not record.aspect_ratio.strip():
            errors.append(f"{label}: missing aspect_ratio")
        if not record.bbox_layout:
            errors.append(f"{label}: missing bbox_layout")
        else:
            try:
                validate_layout(record.bbox_layout)
            except ValueError as exc:
                errors.append(f"{label}: invalid bbox_layout: {exc}")
        if not record.ideogram_json:
            warnings.append(f"{label}: missing ideogram_json")
        elif record.ideogram_json.get("prompt") != record.prompt_text:
            warnings.append(f"{label}: ideogram_json prompt does not match prompt_text")

    character_records = [record for record in records if record.mode.startswith("character_lora")]
    if character_records:
        coverage = lora_coverage_report(records)
        if coverage["status"] != "ready":
            warnings.append(str(coverage["decision"]["summary"]))
            warnings.append(str(coverage["decision"]["recommendation"]))
        if not any(record.character_bible for record in character_records):
            warnings.append("character LoRA records do not include a character_bible identity anchor")

    status = "invalid" if errors else "valid"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "record_count": len(records),
    }


def format_validation_report(report: dict[str, Any], path: str) -> str:
    lines = [
        f"Records file: {path}",
        f"Status: {str(report['status']).upper()}",
        f"Total records: {report['record_count']}",
        "",
        "Errors:",
    ]
    errors = list(report.get("errors", []))
    warnings = list(report.get("warnings", []))
    lines.extend(f"- {error}" for error in errors) if errors else lines.append("- none")
    lines.extend(["", "Warnings:"])
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- none")
    return "\n".join(lines)

__all__ = [
    "Validator",
    "format_validation_report",
    "validate_bbox",
    "validate_layout",
    "validate_records_for_handoff",
]
