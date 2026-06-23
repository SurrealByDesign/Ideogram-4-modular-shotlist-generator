from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
from typing import Any

from .character import build_character_bible
from .character import lora_coverage_report
from .exporters import Exporter
from .generator import build_character_lora_records, build_records
from .models import PromptRecord
from .palettes import COLOR_PALETTES
from .presets import BUILD_PRESETS, default_output_dir, get_preset
from .shotlists import MODES
from .styles import STYLE_INTENSITIES, STYLE_PROFILES
from .templates import LAYOUT_TEMPLATES
from .validation import format_validation_report, validate_records_for_handoff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shotplanner", description="Generate modular Ideogram-style shotlist records.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build a shotlist record batch.")
    build.add_argument("--config", help="Load build settings from a JSON config file.")
    build.add_argument("--subject", default=None, help="Subject to plan shots for.")
    build.add_argument("--preset", choices=sorted(BUILD_PRESETS), help="Use a build preset for mode, count, style, and output defaults.")
    build.add_argument("--style", default=None, help="Visual style description.")
    build.add_argument("--style-profile", choices=sorted(STYLE_PROFILES), help="Apply a named reusable style profile.")
    build.add_argument("--style-intensity", choices=STYLE_INTENSITIES, default=None, help="Control style profile strength.")
    build.add_argument("--mode", choices=MODES, help="Shotlist mode.")
    build.add_argument("--count", type=int, default=None, help="Number of records to generate.")
    build.add_argument("--palette", choices=sorted(COLOR_PALETTES), help="Use a named static color palette.")
    build.add_argument("--identity", default="", help="Stable character identity anchor.")
    build.add_argument("--face", default="", help="Face details that should stay consistent.")
    build.add_argument("--hair", default="", help="Hair details that should stay consistent.")
    build.add_argument("--body", default="", help="Body/proportion details that should stay consistent.")
    build.add_argument("--outfit", default="", help="Outfit details that should stay consistent.")
    build.add_argument("--accessories", default="", help="Accessory or prop details that should stay consistent.")
    build.add_argument("--must-keep", default="", help="Traits that every generated shot should preserve.")
    build.add_argument("--avoid", default="", help="Traits or mistakes to avoid.")
    build.add_argument("--out", default=None, help="Output directory.")

    character_lora = subparsers.add_parser("build-character-lora", help="Build a complete multi-pack character LoRA shot plan.")
    character_lora.add_argument("--config", help="Load character LoRA settings from a JSON config file.")
    character_lora.add_argument("--subject", default=None, help="Subject to plan shots for.")
    character_lora.add_argument("--palette", choices=sorted(COLOR_PALETTES), help="Use a named static color palette.")
    character_lora.add_argument("--style-profile", choices=sorted(STYLE_PROFILES), help="Apply a named reusable style profile.")
    character_lora.add_argument("--style-intensity", choices=STYLE_INTENSITIES, default=None, help="Control style profile strength.")
    add_character_bible_args(character_lora)
    character_lora.add_argument("--core-count", type=int, default=None, help="Override core pack count.")
    character_lora.add_argument("--turnaround-count", type=int, default=None, help="Override turnaround pack count.")
    character_lora.add_argument("--expressions-count", type=int, default=None, help="Override expressions pack count.")
    character_lora.add_argument("--costume-details-count", type=int, default=None, help="Override costume details pack count.")
    character_lora.add_argument("--action-count", type=int, default=None, help="Override action pack count.")
    character_lora.add_argument("--environment-count", type=int, default=None, help="Override environment pack count.")
    character_lora.add_argument("--out", default=None, help="Output directory.")

    list_parser = subparsers.add_parser("list", help="List available shotplanner resources.")
    list_parser.add_argument("resource", choices=["modes", "presets", "palettes", "styles", "templates", "packs"], help="Resource type to list.")

    inspect_parser = subparsers.add_parser("inspect", help="Summarize a generated records.json file.")
    inspect_parser.add_argument("records_path", help="Path to records.json.")

    stats_parser = subparsers.add_parser("stats", help="Print compact count tables for a generated records.json file.")
    stats_parser.add_argument("records_path", help="Path to records.json.")

    validate_parser = subparsers.add_parser("validate", help="Validate a generated records.json file for handoff.")
    validate_parser.add_argument("records_path", help="Path to records.json.")

    qa_parser = subparsers.add_parser("qa", help="Run rule-based prompt and metadata quality checks on records.json.")
    qa_parser.add_argument("records_path", help="Path to records.json.")
    qa_parser.add_argument("--pack", help="Check only records from this pack.")
    qa_parser.add_argument("--mode", help="Check only records from this mode.")
    qa_parser.add_argument("--shot-type", help="Check only records with this shot type.")
    qa_parser.add_argument("--template", help="Check only records using this bbox template.")
    qa_parser.add_argument("--code", choices=["missing_identity_anchor", "empty_negative_prompt", "long_prompt", "duplicate_prompt", "repeated_prompt_words"], help="Show only findings with this QA code.")
    qa_parser.add_argument("--severity", choices=["warning", "info"], help="Show only findings with this severity.")
    qa_parser.add_argument("--field", choices=["summary", "json"], default="summary", help="QA output format.")

    export_qa = subparsers.add_parser("export-qa", help="Export QA findings as JSON and CSV files.")
    export_qa.add_argument("records_path", help="Path to records.json.")
    export_qa.add_argument("--out", required=True, help="Output directory for QA findings.")
    export_qa.add_argument("--pack", help="Check only records from this pack.")
    export_qa.add_argument("--mode", help="Check only records from this mode.")
    export_qa.add_argument("--shot-type", help="Check only records with this shot type.")
    export_qa.add_argument("--template", help="Check only records using this bbox template.")
    export_qa.add_argument("--code", choices=["missing_identity_anchor", "empty_negative_prompt", "long_prompt", "duplicate_prompt", "repeated_prompt_words"], help="Export only findings with this QA code.")
    export_qa.add_argument("--severity", choices=["warning", "info"], help="Export only findings with this severity.")

    export_revisions = subparsers.add_parser("export-revisions", help="Export a revision worklist from review state and QA findings.")
    export_revisions.add_argument("records_path", help="Path to records.json.")
    export_revisions.add_argument("--out", required=True, help="Output directory for revision worklist files.")
    export_revisions.add_argument("--pack", help="Export only records from this pack.")
    export_revisions.add_argument("--mode", help="Export only records from this mode.")
    export_revisions.add_argument("--shot-type", help="Export only records with this shot type.")
    export_revisions.add_argument("--template", help="Export only records using this bbox template.")
    export_revisions.add_argument("--review-status", choices=["unreviewed", "selected", "rejected", "needs_regen"], help="Include records with this review status.")
    export_revisions.add_argument("--selected", choices=["true", "false"], help="Include records with this selected flag.")
    export_revisions.add_argument("--needs-regen", choices=["true", "false"], help="Include records with this regeneration flag.")
    export_revisions.add_argument("--qa-code", choices=["missing_identity_anchor", "empty_negative_prompt", "long_prompt", "duplicate_prompt", "repeated_prompt_words"], help="Include records with this QA finding code.")
    export_revisions.add_argument("--qa-severity", choices=["warning", "info"], help="Include records with this QA finding severity.")

    revision_summary = subparsers.add_parser("revision-summary", help="Summarize records needing revision from review state and QA findings.")
    revision_summary.add_argument("records_path", help="Path to records.json.")
    revision_summary.add_argument("--pack", help="Summarize only records from this pack.")
    revision_summary.add_argument("--mode", help="Summarize only records from this mode.")
    revision_summary.add_argument("--shot-type", help="Summarize only records with this shot type.")
    revision_summary.add_argument("--template", help="Summarize only records using this bbox template.")
    revision_summary.add_argument("--review-status", choices=["unreviewed", "selected", "rejected", "needs_regen"], help="Include records with this review status.")
    revision_summary.add_argument("--selected", choices=["true", "false"], help="Include records with this selected flag.")
    revision_summary.add_argument("--needs-regen", choices=["true", "false"], help="Include records with this regeneration flag.")
    revision_summary.add_argument("--qa-code", choices=["missing_identity_anchor", "empty_negative_prompt", "long_prompt", "duplicate_prompt", "repeated_prompt_words"], help="Include records with this QA finding code.")
    revision_summary.add_argument("--qa-severity", choices=["warning", "info"], help="Include records with this QA finding severity.")
    revision_summary.add_argument("--field", choices=["summary", "json"], default="summary", help="Revision summary output format.")

    copy_records = subparsers.add_parser("copy-records", help="Copy a filtered record subset into a new planning folder.")
    copy_records.add_argument("records_path", help="Path to records.json.")
    copy_records.add_argument("--out", required=True, help="Output directory for the copied records.json and subset manifest.")
    copy_records.add_argument("--pack", help="Copy only records from this pack.")
    copy_records.add_argument("--mode", help="Copy only records from this mode.")
    copy_records.add_argument("--shot-type", help="Copy only records with this shot type.")
    copy_records.add_argument("--template", help="Copy only records using this bbox template.")
    copy_records.add_argument("--review-status", choices=["unreviewed", "selected", "rejected", "needs_regen"], help="Copy only records with this review status.")
    copy_records.add_argument("--selected", choices=["true", "false"], help="Copy only records with this selected flag.")
    copy_records.add_argument("--needs-regen", choices=["true", "false"], help="Copy only records with this regeneration flag.")
    copy_records.add_argument("--qa-code", choices=["missing_identity_anchor", "empty_negative_prompt", "long_prompt", "duplicate_prompt", "repeated_prompt_words"], help="Copy only records with this QA finding code.")
    copy_records.add_argument("--qa-severity", choices=["warning", "info"], help="Copy only records with this QA finding severity.")

    audit_results = subparsers.add_parser("audit-results", help="Summarize generated result references in a records.json file.")
    audit_results.add_argument("records_path", help="Path to records.json.")
    audit_results.add_argument("--pack", help="Audit only records from this pack.")
    audit_results.add_argument("--mode", help="Audit only records from this mode.")
    audit_results.add_argument("--shot-type", help="Audit only records with this shot type.")
    audit_results.add_argument("--template", help="Audit only records using this bbox template.")
    audit_results.add_argument("--has-results", choices=["true", "false"], help="Audit only records with or without attached result references.")
    audit_results.add_argument("--result-status", choices=["unreviewed", "accepted", "rejected", "needs_regen"], help="Audit only records with at least one result reference in this status.")
    audit_results.add_argument("--field", choices=["summary", "missing", "json"], default="summary", help="Result audit output format.")

    recommend_parser = subparsers.add_parser("recommend", help="Print LoRA coverage additions for a generated records.json file.")
    recommend_parser.add_argument("records_path", help="Path to records.json.")

    review_parser = subparsers.add_parser("review", help="List records by review state and planning filters.")
    review_parser.add_argument("records_path", help="Path to records.json.")
    review_parser.add_argument("--pack", help="Show only records from this pack.")
    review_parser.add_argument("--mode", help="Show only records from this mode.")
    review_parser.add_argument("--shot-type", help="Show only records with this shot type.")
    review_parser.add_argument("--template", help="Show only records using this bbox template.")
    review_parser.add_argument("--status", choices=["unreviewed", "selected", "rejected", "needs_regen"], help="Show only records with this review status.")
    review_parser.add_argument("--selected", choices=["true", "false"], help="Show only records with this selected flag.")
    review_parser.add_argument("--needs-regen", choices=["true", "false"], help="Show only records with this regeneration flag.")
    review_parser.add_argument("--field", choices=["summary", "ids", "prompts", "json"], default="summary", help="Review output format.")

    select_parser = subparsers.add_parser("select", help="Print one record from a generated records.json file.")
    select_parser.add_argument("records_path", help="Path to records.json.")
    selector = select_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--index", type=int, help="Zero-based record index.")
    selector.add_argument("--id", help="Record id.")
    select_parser.add_argument("--field", choices=["record", "prompt", "negative", "bbox", "character_bible", "ideogram_json", "metadata", "review", "result_refs"], default="record", help="Field to print.")

    mark_parser = subparsers.add_parser("mark", help="Add review status fields to one record in records.json.")
    mark_parser.add_argument("records_path", help="Path to records.json.")
    mark_selector = mark_parser.add_mutually_exclusive_group(required=True)
    mark_selector.add_argument("--index", type=int, help="Zero-based record index.")
    mark_selector.add_argument("--id", help="Record id.")
    mark_parser.add_argument("--status", choices=["unreviewed", "selected", "rejected", "needs_regen"], help="Review status.")
    mark_parser.add_argument("--notes", help="Review notes.")
    mark_parser.add_argument("--selected", choices=["true", "false"], help="Whether this record is selected.")
    mark_parser.add_argument("--needs-regen", choices=["true", "false"], help="Whether this record needs regeneration.")

    attach_result = subparsers.add_parser("attach-result", help="Attach a generated result reference to one record in records.json.")
    attach_result.add_argument("records_path", help="Path to records.json.")
    attach_selector = attach_result.add_mutually_exclusive_group(required=True)
    attach_selector.add_argument("--index", type=int, help="Zero-based record index.")
    attach_selector.add_argument("--id", help="Record id.")
    attach_result.add_argument("--path", required=True, help="Local result file path or relative project path.")
    attach_result.add_argument("--status", choices=["unreviewed", "accepted", "rejected", "needs_regen"], help="Result review status.")
    attach_result.add_argument("--notes", help="Result notes.")

    export_missing = subparsers.add_parser("export-missing-results", help="Export a worklist of records without attached result references.")
    export_missing.add_argument("records_path", help="Path to records.json.")
    export_missing.add_argument("--out", required=True, help="Output directory for the missing-result worklist.")
    export_missing.add_argument("--pack", help="Export only records from this pack.")
    export_missing.add_argument("--mode", help="Export only records from this mode.")
    export_missing.add_argument("--shot-type", help="Export only records with this shot type.")
    export_missing.add_argument("--template", help="Export only records using this bbox template.")

    export_prompts = subparsers.add_parser("export-prompts", help="Export prompt text files from a generated records.json file.")
    export_prompts.add_argument("records_path", help="Path to records.json.")
    export_prompts.add_argument("--out", required=True, help="Output directory for prompt text files.")
    export_prompts.add_argument("--include-negative", action="store_true", help="Also write negative prompt text files.")
    export_prompts.add_argument("--pack", help="Export only records from this pack.")
    export_prompts.add_argument("--mode", help="Export only records from this mode.")
    export_prompts.add_argument("--shot-type", help="Export only records with this shot type.")
    export_prompts.add_argument("--template", help="Export only records using this bbox template.")
    export_prompts.add_argument("--review-status", choices=["unreviewed", "selected", "rejected", "needs_regen"], help="Export only records with this review status.")
    export_prompts.add_argument("--selected", choices=["true", "false"], help="Export only records with this selected flag.")
    export_prompts.add_argument("--needs-regen", choices=["true", "false"], help="Export only records with this regeneration flag.")
    return parser


def add_character_bible_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--identity", default="", help="Stable character identity anchor.")
    parser.add_argument("--face", default="", help="Face details that should stay consistent.")
    parser.add_argument("--hair", default="", help="Hair details that should stay consistent.")
    parser.add_argument("--body", default="", help="Body/proportion details that should stay consistent.")
    parser.add_argument("--outfit", default="", help="Outfit details that should stay consistent.")
    parser.add_argument("--accessories", default="", help="Accessory or prop details that should stay consistent.")
    parser.add_argument("--must-keep", default="", help="Traits that every generated shot should preserve.")
    parser.add_argument("--avoid", default="", help="Traits or mistakes to avoid.")


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"error: config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: config file is not valid JSON: {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("error: config file must contain a JSON object")
    return data


def config_value(config: dict[str, Any], key: str, current: Any = None) -> Any:
    if current not in (None, ""):
        return current
    if key in config:
        return config[key]
    return current


def apply_common_config(args: argparse.Namespace, config: dict[str, Any]) -> argparse.Namespace:
    args.subject = config_value(config, "subject", args.subject)
    args.palette = config_value(config, "palette", getattr(args, "palette", None))
    args.style_profile = config_value(config, "style_profile", getattr(args, "style_profile", None))
    args.style_intensity = config_value(config, "style_intensity", getattr(args, "style_intensity", None)) or "standard"
    args.out = config_value(config, "out", getattr(args, "out", None))
    character_bible = config.get("character_bible", {})
    if character_bible is not None and not isinstance(character_bible, dict):
        raise SystemExit("error: character_bible must be a JSON object")
    for key in ("identity", "face", "hair", "body", "outfit", "accessories", "must_keep", "avoid"):
        setattr(args, key, config_value(character_bible, key, getattr(args, key, "")))
    if not args.subject:
        raise SystemExit("error: --subject is required unless provided by --config")
    return args


def character_bible_from_args(args: argparse.Namespace) -> dict[str, str]:
    return build_character_bible(
        identity=args.identity,
        face=args.face,
        hair=args.hair,
        body=args.body,
        outfit=args.outfit,
        accessories=args.accessories,
        must_keep=args.must_keep,
        avoid=args.avoid,
    )


def resolve_build_args(args: argparse.Namespace) -> argparse.Namespace:
    config = load_config(getattr(args, "config", None))
    args = apply_common_config(args, config)
    args.preset = config_value(config, "preset", args.preset)
    args.mode = config_value(config, "mode", args.mode)
    args.style = config_value(config, "style", args.style)
    args.count = config_value(config, "count", args.count)
    preset = get_preset(args.preset) if args.preset else None

    mode = args.mode or (preset.mode if preset else None)
    if not mode:
        raise SystemExit("error: --mode is required when --preset is not provided")

    count = args.count if args.count is not None else (preset.count if preset else 10)
    style = args.style if args.style is not None else (preset.style if preset else "")
    output = args.out or default_output_dir(args.subject, args.preset or mode)

    args.mode = mode
    args.count = count
    args.style = style
    args.out = output
    return args


def resolve_character_lora_args(args: argparse.Namespace) -> argparse.Namespace:
    config = load_config(getattr(args, "config", None))
    args = apply_common_config(args, config)
    packs = config.get("packs", {})
    if packs is not None and not isinstance(packs, dict):
        raise SystemExit("error: packs must be a JSON object")
    pack_style_profiles = config.get("pack_style_profiles", {})
    if pack_style_profiles is not None and not isinstance(pack_style_profiles, dict):
        raise SystemExit("error: pack_style_profiles must be a JSON object")
    args.pack_style_profiles = {str(key): str(value) for key, value in pack_style_profiles.items()} if pack_style_profiles else {}
    pack_style_intensity = config.get("pack_style_intensity", {})
    if pack_style_intensity is not None and not isinstance(pack_style_intensity, dict):
        raise SystemExit("error: pack_style_intensity must be a JSON object")
    args.pack_style_intensity = {str(key): str(value) for key, value in pack_style_intensity.items()} if pack_style_intensity else {}
    pack_arg_names = {
        "core": "core_count",
        "turnaround": "turnaround_count",
        "expressions": "expressions_count",
        "costume_details": "costume_details_count",
        "action": "action_count",
        "environment": "environment_count",
    }
    for pack_name, arg_name in pack_arg_names.items():
        current = getattr(args, arg_name)
        configured = packs.get(pack_name)
        setattr(args, arg_name, current if current is not None else configured)
    args.out = args.out or default_output_dir(args.subject, "character_lora_multipack")
    return args


def format_list(resource: str) -> str:
    if resource == "modes":
        return "\n".join(MODES)
    if resource == "presets":
        lines = []
        for name, preset in sorted(BUILD_PRESETS.items()):
            lines.append(f"{name}\tmode={preset.mode}\tcount={preset.count}\tstyle={preset.style}")
        return "\n".join(lines)
    if resource == "palettes":
        lines = []
        for name, palette in sorted(COLOR_PALETTES.items()):
            lines.append(f"{name}\tcolors={len(palette.colors)}\tmood={palette.mood}")
        return "\n".join(lines)
    if resource == "styles":
        lines = []
        for name, profile in sorted(STYLE_PROFILES.items()):
            lines.append(f"{name}\tprompt={profile.prompt}\tnotes={profile.notes}")
        return "\n".join(lines)
    if resource == "templates":
        lines = []
        for name, template in sorted(LAYOUT_TEMPLATES.items()):
            lines.append(f"{name}\taspect_ratio={template['aspect_ratio']}\telements={len(template['elements'])}")
        return "\n".join(lines)
    if resource == "packs":
        from .generator import PACK_LABELS

        lines = []
        for preset_name, pack in PACK_LABELS.items():
            preset = BUILD_PRESETS[preset_name]
            lines.append(f"{pack}\tpreset={preset_name}\tcount={preset.count}")
        return "\n".join(lines)
    raise SystemExit(f"error: unknown list resource: {resource}")


def load_records(path: str | Path) -> list[PromptRecord]:
    records_path = Path(path)
    try:
        data = json.loads(records_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"error: records file not found: {records_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: records file is not valid JSON: {records_path}: {exc}") from exc
    if not isinstance(data, list):
        raise SystemExit("error: records file must contain a JSON array")
    return [PromptRecord.from_dict(item) for item in data if isinstance(item, dict)]


def save_records(records: list[PromptRecord], path: str | Path) -> None:
    records_path = Path(path)
    records_path.write_text(json.dumps([record.to_dict() for record in records], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_records_inspection(records: list[PromptRecord], path: str | Path) -> str:
    if not records:
        return f"Records file: {path}\nTotal records: 0"
    modes = Counter(record.mode for record in records)
    packs = Counter(str(record.metadata.get("pack", "")) for record in records if record.metadata.get("pack"))
    shot_types = Counter(record.shot_type for record in records)
    templates = Counter(str(record.metadata.get("bbox_template", "")) for record in records if record.metadata.get("bbox_template"))
    aspect_ratios = Counter(record.aspect_ratio for record in records)
    lines = [
        f"Records file: {path}",
        f"Total records: {len(records)}",
        f"Subject: {records[0].subject}",
        "",
        "Modes:",
        *counter_lines(modes),
    ]
    if packs:
        lines.extend(["", "Packs:", *counter_lines(packs)])
    lines.extend(
        [
            "",
            "Shot types:",
            *counter_lines(shot_types),
            "",
            "Templates:",
            *counter_lines(templates),
            "",
            "Aspect ratios:",
            *counter_lines(aspect_ratios),
            "",
            "First record:",
            f"- index: 0",
            f"- id: {records[0].id}",
            f"- shot_type: {records[0].shot_type}",
            f"- angle: {records[0].angle}",
        ]
    )
    return "\n".join(lines)


def format_records_stats(records: list[PromptRecord], path: str | Path) -> str:
    if not records:
        return f"Records file: {path}\nTotal records: 0"
    counters = {
        "Packs": Counter(str(record.metadata.get("pack", "")) for record in records if record.metadata.get("pack")),
        "Modes": Counter(record.mode for record in records),
        "Shot types": Counter(record.shot_type for record in records),
        "Templates": Counter(str(record.metadata.get("bbox_template", "")) for record in records if record.metadata.get("bbox_template")),
        "Aspect ratios": Counter(record.aspect_ratio for record in records),
        "Palettes": Counter(str(record.color_palette.get("name", "")) for record in records if record.color_palette.get("name")),
        "Style profiles": style_profile_counts(records),
        "Review status": review_status_counts(records),
        "Review flags": review_flag_counts(records),
    }
    lines = [
        f"Records file: {path}",
        f"Total records: {len(records)}",
    ]
    for title, counter in counters.items():
        lines.extend(["", f"{title}:", *counter_lines(counter)])
    return "\n".join(lines)


def counter_lines(counter: Counter[str]) -> list[str]:
    if not counter:
        return ["- none"]
    return [f"- {name}: {count}" for name, count in sorted(counter.items())]


def style_profile_counts(records: list[PromptRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        profile = record.style_description.get("profile", {})
        if not isinstance(profile, dict) or not profile.get("name"):
            continue
        intensity = str(profile.get("intensity", "standard"))
        counts[f"{profile['name']} / {intensity}"] += 1
    return counts


def review_status_counts(records: list[PromptRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        status = str(record.review.get("review_status", "")).strip() or "unreviewed"
        counts[status] += 1
    return counts


def review_flag_counts(records: list[PromptRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    selected = sum(1 for record in records if record.review.get("selected") is True)
    needs_regen = sum(1 for record in records if record.review.get("needs_regen") is True)
    if selected:
        counts["selected=true"] = selected
    if needs_regen:
        counts["needs_regen=true"] = needs_regen
    return counts


def normalize_words(text: str) -> list[str]:
    return ["".join(char for char in word.lower() if char.isalnum()) for word in text.split()]


def record_has_identity_anchor(record: PromptRecord) -> bool:
    identity = str(record.character_bible.get("identity", "")).strip()
    if not identity:
        return False
    return identity.lower() in record.prompt_text.lower()


def repeated_prompt_words(prompt: str, minimum_count: int = 6) -> dict[str, int]:
    ignored = {
        "and",
        "the",
        "with",
        "for",
        "from",
        "into",
        "that",
        "this",
        "shot",
        "view",
        "style",
        "guidance",
        "identity",
        "anchor",
        "character",
        "reference",
        "readable",
        "silhouette",
        "clean",
    }
    counts = Counter(word for word in normalize_words(prompt) if len(word) > 3 and word not in ignored)
    return {word: count for word, count in sorted(counts.items()) if count >= minimum_count}


def filter_qa_findings(findings: list[dict[str, Any]], code: str | None = None, severity: str | None = None) -> list[dict[str, Any]]:
    filtered = []
    for finding in findings:
        if code and finding.get("code") != code:
            continue
        if severity and finding.get("severity") != severity:
            continue
        filtered.append(finding)
    return filtered


def plan_qa_payload(
    records: list[PromptRecord],
    prompt_length_limit: int = 1200,
    source_records: list[PromptRecord] | None = None,
    code: str | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    source_indexes = {id(record): index for index, record in enumerate(source_records or records)}
    checks = []
    duplicate_prompt_counts = Counter(record.prompt_text.strip() for record in records if record.prompt_text.strip())
    for index, record in enumerate(records):
        label = {
            "index": source_indexes.get(id(record), index),
            "id": record.id,
            "pack": record.metadata.get("pack", ""),
            "mode": record.mode,
            "shot_type": record.shot_type,
        }
        if record.mode.startswith("character_lora") and not record_has_identity_anchor(record):
            checks.append({**label, "severity": "warning", "code": "missing_identity_anchor", "message": "Character LoRA record is missing a prompt identity anchor."})
        if not record.negative_prompt.strip():
            checks.append({**label, "severity": "warning", "code": "empty_negative_prompt", "message": "Negative prompt is empty."})
        if len(record.prompt_text) > prompt_length_limit:
            checks.append({**label, "severity": "warning", "code": "long_prompt", "message": f"Prompt is longer than {prompt_length_limit} characters."})
        if record.prompt_text.strip() and duplicate_prompt_counts[record.prompt_text.strip()] > 1:
            checks.append({**label, "severity": "warning", "code": "duplicate_prompt", "message": "Prompt text is duplicated in this plan."})
        repeated_words = repeated_prompt_words(record.prompt_text)
        if repeated_words:
            top_words = ", ".join(f"{word}={count}" for word, count in list(repeated_words.items())[:5])
            checks.append({**label, "severity": "info", "code": "repeated_prompt_words", "message": f"Prompt repeats words often: {top_words}."})

    checks = filter_qa_findings(checks, code=code, severity=severity)
    severity_counts = Counter(str(item["severity"]) for item in checks)
    code_counts = Counter(str(item["code"]) for item in checks)
    return {
        "total_records": len(records),
        "total_findings": len(checks),
        "status": "clean" if not checks else "review",
        "severity_counts": dict(sorted(severity_counts.items())),
        "code_counts": dict(sorted(code_counts.items())),
        "findings": checks,
    }


def format_plan_qa(
    records: list[PromptRecord],
    path: str | Path,
    field: str = "summary",
    source_records: list[PromptRecord] | None = None,
    code: str | None = None,
    severity: str | None = None,
) -> str:
    payload = plan_qa_payload(records, source_records=source_records, code=code, severity=severity)
    if field == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    lines = [
        f"Records file: {path}",
        f"Status: {payload['status'].upper()}",
        f"Total records: {payload['total_records']}",
        f"Findings: {payload['total_findings']}",
        "",
        "Severity:",
        *counter_lines(Counter(payload["severity_counts"])),
        "",
        "Finding types:",
        *counter_lines(Counter(payload["code_counts"])),
        "",
        "Findings:",
    ]
    if not payload["findings"]:
        lines.append("- none")
    else:
        for item in payload["findings"][:20]:
            pack = str(item.get("pack", "")).strip() or "-"
            lines.append(f"- index={item['index']} id={item['id']} pack={pack} code={item['code']} severity={item['severity']} - {item['message']}")
        remaining = payload["total_findings"] - 20
        if remaining > 0:
            lines.append(f"- ... {remaining} more")
    return "\n".join(lines)


def result_status_counts(records: list[PromptRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        for result_ref in record.result_refs:
            status = "unreviewed"
            if isinstance(result_ref, dict):
                status = str(result_ref.get("status", "")).strip() or "unreviewed"
            counts[status] += 1
    return counts


def select_record(records: list[PromptRecord], index: int | None = None, record_id: str | None = None) -> PromptRecord:
    if index is not None:
        if index < 0 or index >= len(records):
            raise SystemExit(f"error: index out of range: {index} (records: {len(records)})")
        return records[index]
    for record in records:
        if record.id == record_id:
            return record
    raise SystemExit(f"error: record id not found: {record_id}")


def format_selected_record(record: PromptRecord, field: str) -> str:
    if field == "prompt":
        return record.prompt_text
    if field == "negative":
        return record.negative_prompt
    data = record.to_dict()
    field_map = {
        "record": data,
        "bbox": record.bbox_layout,
        "character_bible": record.character_bible,
        "ideogram_json": record.ideogram_json,
        "metadata": record.metadata,
        "review": record.review,
        "result_refs": record.result_refs,
    }
    return json.dumps(field_map[field], indent=2, ensure_ascii=False)


def parse_bool(value: str) -> bool:
    return value.lower() == "true"


def mark_record(
    records: list[PromptRecord],
    index: int | None = None,
    record_id: str | None = None,
    status: str | None = None,
    notes: str | None = None,
    selected: bool | None = None,
    needs_regen: bool | None = None,
) -> PromptRecord:
    record = select_record(records, index=index, record_id=record_id)
    review = dict(record.review)
    if status is not None:
        review["review_status"] = status
    if notes is not None:
        review["review_notes"] = notes
    if selected is not None:
        review["selected"] = selected
    if needs_regen is not None:
        review["needs_regen"] = needs_regen
    record.review = review
    return record


def attach_result_ref(
    records: list[PromptRecord],
    index: int | None = None,
    record_id: str | None = None,
    path: str = "",
    status: str | None = None,
    notes: str | None = None,
) -> PromptRecord:
    record = select_record(records, index=index, record_id=record_id)
    result_ref = {"path": path}
    if status is not None:
        result_ref["status"] = status
    if notes is not None:
        result_ref["notes"] = notes
    record.result_refs = [*record.result_refs, result_ref]
    return record


def format_recommendations(records: list[PromptRecord], path: str | Path) -> str:
    coverage = lora_coverage_report(records)
    if not coverage["applies"]:
        return f"Records file: {path}\nRecommended additions:\n- not applicable for this mode"

    lines = [
        f"Records file: {path}",
        f"Coverage status: {coverage['status']}",
        "",
        "Recommended additions:",
    ]
    recommendations = coverage.get("recommendations", [])
    if not recommendations:
        lines.append("- none")
    else:
        for item in recommendations:
            if isinstance(item, dict):
                lines.append(f"- {item['summary']} Example shot types: {item['examples']}.")
    return "\n".join(lines)


def record_has_result_status(record: PromptRecord, result_status: str) -> bool:
    for result_ref in record.result_refs:
        status = "unreviewed"
        if isinstance(result_ref, dict):
            status = str(result_ref.get("status", "")).strip() or "unreviewed"
        if status == result_status:
            return True
    return False


def filter_result_records(
    records: list[PromptRecord],
    has_results: bool | None = None,
    result_status: str | None = None,
) -> list[PromptRecord]:
    filtered = []
    for record in records:
        if has_results is not None and bool(record.result_refs) is not has_results:
            continue
        if result_status and not record_has_result_status(record, result_status):
            continue
        filtered.append(record)
    return filtered


def result_audit_payload(records: list[PromptRecord], source_records: list[PromptRecord] | None = None) -> dict[str, Any]:
    source_indexes = {id(record): index for index, record in enumerate(source_records or records)}
    missing = []
    records_with_results = 0
    total_result_refs = 0
    for index, record in enumerate(records):
        total_result_refs += len(record.result_refs)
        if record.result_refs:
            records_with_results += 1
        else:
            missing.append(
                {
                    "index": source_indexes.get(id(record), index),
                    "id": record.id,
                    "pack": record.metadata.get("pack", ""),
                    "shot_type": record.shot_type,
                    "angle": record.angle,
                }
            )
    return {
        "total_records": len(records),
        "records_with_results": records_with_results,
        "records_without_results": len(missing),
        "total_result_refs": total_result_refs,
        "result_status": dict(sorted(result_status_counts(records).items())),
        "missing_records": missing,
    }


def format_result_audit(
    records: list[PromptRecord],
    path: str | Path,
    field: str = "summary",
    source_records: list[PromptRecord] | None = None,
) -> str:
    payload = result_audit_payload(records, source_records=source_records)
    if field == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    if field == "missing":
        lines = [
            f"Records file: {path}",
            f"Records without results: {payload['records_without_results']}",
            "",
            "Missing result records:",
        ]
        if not payload["missing_records"]:
            lines.append("- none")
        else:
            for item in payload["missing_records"]:
                lines.append(f"- index={item['index']} id={item['id']} pack={item['pack'] or '-'} shot={item['shot_type']} angle={item['angle']}")
        return "\n".join(lines)
    lines = [
        f"Records file: {path}",
        f"Total records: {payload['total_records']}",
        f"Records with results: {payload['records_with_results']}",
        f"Records without results: {payload['records_without_results']}",
        f"Total result refs: {payload['total_result_refs']}",
        "",
        "Result status:",
        *counter_lines(Counter(payload["result_status"])),
        "",
        "Next missing records:",
    ]
    next_missing = payload["missing_records"][:10]
    if not next_missing:
        lines.append("- none")
    else:
        for item in next_missing:
            lines.append(f"- index={item['index']} id={item['id']} pack={item['pack'] or '-'} shot={item['shot_type']} angle={item['angle']}")
        remaining = payload["records_without_results"] - len(next_missing)
        if remaining > 0:
            lines.append(f"- ... {remaining} more")
    return "\n".join(lines)


def format_review_records(
    records: list[PromptRecord],
    path: str | Path,
    source_records: list[PromptRecord] | None = None,
    field: str = "summary",
) -> str:
    source_indexes = {id(record): index for index, record in enumerate(source_records or records)}
    if field == "ids":
        return "\n".join(record.id for record in records)
    if field == "prompts":
        chunks = []
        for fallback_index, record in enumerate(records):
            index = source_indexes.get(id(record), fallback_index)
            chunks.append(f"{index} {record.id}\n{record.prompt_text}")
        return "\n\n".join(chunks)
    if field == "json":
        payload = [
            {
                "index": source_indexes.get(id(record), fallback_index),
                "id": record.id,
                "pack": record.metadata.get("pack", ""),
                "mode": record.mode,
                "shot_type": record.shot_type,
                "angle": record.angle,
                "review": record.review,
            }
            for fallback_index, record in enumerate(records)
        ]
        return json.dumps(payload, indent=2, ensure_ascii=False)
    lines = [
        f"Records file: {path}",
        f"Matched records: {len(records)}",
        "",
        "Review records:",
    ]
    if not records:
        lines.append("- none")
        return "\n".join(lines)
    for fallback_index, record in enumerate(records):
        index = source_indexes.get(id(record), fallback_index)
        pack = str(record.metadata.get("pack", "")).strip() or "-"
        status = str(record.review.get("review_status", "")).strip() or "unreviewed"
        selected = record.review.get("selected")
        needs_regen = record.review.get("needs_regen")
        flags = []
        if selected is True:
            flags.append("selected")
        if needs_regen is True:
            flags.append("needs_regen")
        flag_text = f" [{' '.join(flags)}]" if flags else ""
        notes = str(record.review.get("review_notes", "")).strip()
        note_text = f" - {notes}" if notes else ""
        lines.append(f"- index={index} id={record.id} pack={pack} shot={record.shot_type} angle={record.angle} status={status}{flag_text}{note_text}")
    return "\n".join(lines)


def safe_filename(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value.strip())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned[:120] or "record"


def filter_records(
    records: list[PromptRecord],
    pack: str | None = None,
    mode: str | None = None,
    shot_type: str | None = None,
    template: str | None = None,
    review_status: str | None = None,
    selected: bool | None = None,
    needs_regen: bool | None = None,
) -> list[PromptRecord]:
    filtered = []
    for record in records:
        if pack and record.metadata.get("pack") != pack:
            continue
        if mode and record.mode != mode:
            continue
        if shot_type and record.shot_type != shot_type:
            continue
        if template and record.metadata.get("bbox_template") != template:
            continue
        if review_status and record.review.get("review_status") != review_status:
            continue
        if selected is not None and record.review.get("selected") is not selected:
            continue
        if needs_regen is not None and record.review.get("needs_regen") is not needs_regen:
            continue
        filtered.append(record)
    return filtered


def export_qa_findings(
    records: list[PromptRecord],
    output_dir: str | Path,
    source_records: list[PromptRecord] | None = None,
    filters: dict[str, str] | None = None,
    code: str | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    payload = plan_qa_payload(records, source_records=source_records, code=code, severity=severity)
    payload["filters"] = filters or {}

    json_path = base_path / "qa_findings.json"
    csv_path = base_path / "qa_findings.csv"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["index", "id", "pack", "mode", "shot_type", "severity", "code", "message"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload["findings"])

    return {
        "finding_count": payload["total_findings"],
        "json": json_path,
        "csv": csv_path,
    }


def review_revision_reasons(
    record: PromptRecord,
    review_status: str | None = None,
    selected: bool | None = None,
    needs_regen: bool | None = None,
) -> list[str]:
    review = record.review
    status = str(review.get("review_status", "")).strip() or "unreviewed"
    reasons = []
    if review_status is not None and status == review_status:
        reasons.append(f"review_status={status}")
    elif review_status is None and status in {"selected", "rejected", "needs_regen"}:
        reasons.append(f"review_status={status}")
    if selected is not None and review.get("selected") is selected:
        reasons.append(f"selected={str(selected).lower()}")
    elif selected is None and review.get("selected") is True:
        reasons.append("selected=true")
    if needs_regen is not None and review.get("needs_regen") is needs_regen:
        reasons.append(f"needs_regen={str(needs_regen).lower()}")
    elif needs_regen is None and review.get("needs_regen") is True:
        reasons.append("needs_regen=true")
    return reasons


def revision_worklist_payload(
    records: list[PromptRecord],
    source_records: list[PromptRecord] | None = None,
    filters: dict[str, str] | None = None,
    review_status: str | None = None,
    selected: bool | None = None,
    needs_regen: bool | None = None,
    qa_code: str | None = None,
    qa_severity: str | None = None,
) -> dict[str, Any]:
    source_indexes = {id(record): index for index, record in enumerate(source_records or records)}
    qa_payload = plan_qa_payload(records, source_records=source_records, code=qa_code, severity=qa_severity)
    qa_by_id: dict[str, list[dict[str, Any]]] = {}
    for finding in qa_payload["findings"]:
        qa_by_id.setdefault(str(finding["id"]), []).append(finding)

    entries = []
    for fallback_index, record in enumerate(records):
        review_reasons = review_revision_reasons(record, review_status=review_status, selected=selected, needs_regen=needs_regen)
        qa_findings = qa_by_id.get(record.id, [])
        reasons = [*review_reasons]
        if qa_findings:
            reasons.extend(f"qa:{finding['code']}" for finding in qa_findings)
        if not reasons:
            continue
        entries.append(
            {
                "index": source_indexes.get(id(record), fallback_index),
                "id": record.id,
                "pack": record.metadata.get("pack", ""),
                "mode": record.mode,
                "shot_type": record.shot_type,
                "angle": record.angle,
                "review_status": str(record.review.get("review_status", "")).strip() or "unreviewed",
                "selected": record.review.get("selected") is True,
                "needs_regen": record.review.get("needs_regen") is True,
                "review_notes": str(record.review.get("review_notes", "")).strip(),
                "qa_count": len(qa_findings),
                "qa_codes": sorted({str(finding["code"]) for finding in qa_findings}),
                "qa_findings": qa_findings,
                "reasons": reasons,
                "prompt_text": record.prompt_text,
                "negative_prompt": record.negative_prompt,
            }
        )

    return {
        "source_count": len(source_records or records),
        "filtered_count": len(records),
        "revision_count": len(entries),
        "filters": filters or {},
        "records": entries,
    }


def export_revision_worklist(
    records: list[PromptRecord],
    output_dir: str | Path,
    source_records: list[PromptRecord] | None = None,
    filters: dict[str, str] | None = None,
    review_status: str | None = None,
    selected: bool | None = None,
    needs_regen: bool | None = None,
    qa_code: str | None = None,
    qa_severity: str | None = None,
) -> dict[str, Any]:
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    payload = revision_worklist_payload(
        records,
        source_records=source_records,
        filters=filters,
        review_status=review_status,
        selected=selected,
        needs_regen=needs_regen,
        qa_code=qa_code,
        qa_severity=qa_severity,
    )
    json_path = base_path / "revision_worklist.json"
    csv_path = base_path / "revision_worklist.csv"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "index",
            "id",
            "pack",
            "mode",
            "shot_type",
            "angle",
            "review_status",
            "selected",
            "needs_regen",
            "review_notes",
            "qa_count",
            "qa_codes",
            "reasons",
            "prompt_text",
            "negative_prompt",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in payload["records"]:
            row = dict(entry)
            row["qa_codes"] = ", ".join(entry["qa_codes"])
            row["reasons"] = ", ".join(entry["reasons"])
            row.pop("qa_findings", None)
            writer.writerow(row)
    return {
        "revision_count": payload["revision_count"],
        "json": json_path,
        "csv": csv_path,
    }


def revision_summary_payload(revision_payload: dict[str, Any]) -> dict[str, Any]:
    records = revision_payload["records"]
    review_status = Counter(str(record["review_status"]) for record in records)
    packs = Counter(str(record["pack"]) for record in records if record.get("pack"))
    qa_codes: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    review_records = 0
    qa_records = 0
    for record in records:
        if record["review_status"] != "unreviewed" or record["selected"] or record["needs_regen"]:
            review_records += 1
        if record["qa_count"]:
            qa_records += 1
        qa_codes.update(str(code) for code in record["qa_codes"])
        reasons.update(str(reason) for reason in record["reasons"])
    return {
        "source_count": revision_payload["source_count"],
        "filtered_count": revision_payload["filtered_count"],
        "revision_count": revision_payload["revision_count"],
        "review_records": review_records,
        "qa_records": qa_records,
        "both_review_and_qa": sum(1 for record in records if (record["review_status"] != "unreviewed" or record["selected"] or record["needs_regen"]) and record["qa_count"]),
        "filters": revision_payload["filters"],
        "review_status": dict(sorted(review_status.items())),
        "packs": dict(sorted(packs.items())),
        "qa_codes": dict(sorted(qa_codes.items())),
        "reasons": dict(sorted(reasons.items())),
        "records": [
            {
                "index": record["index"],
                "id": record["id"],
                "pack": record["pack"],
                "shot_type": record["shot_type"],
                "review_status": record["review_status"],
                "qa_count": record["qa_count"],
                "reasons": record["reasons"],
            }
            for record in records
        ],
    }


def format_revision_summary(
    records: list[PromptRecord],
    path: str | Path,
    field: str = "summary",
    source_records: list[PromptRecord] | None = None,
    filters: dict[str, str] | None = None,
    review_status: str | None = None,
    selected: bool | None = None,
    needs_regen: bool | None = None,
    qa_code: str | None = None,
    qa_severity: str | None = None,
) -> str:
    revision_payload = revision_worklist_payload(
        records,
        source_records=source_records,
        filters=filters,
        review_status=review_status,
        selected=selected,
        needs_regen=needs_regen,
        qa_code=qa_code,
        qa_severity=qa_severity,
    )
    payload = revision_summary_payload(revision_payload)
    if field == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    lines = [
        f"Records file: {path}",
        f"Filtered records: {payload['filtered_count']}",
        f"Revision records: {payload['revision_count']}",
        f"Review records: {payload['review_records']}",
        f"QA records: {payload['qa_records']}",
        f"Both review and QA: {payload['both_review_and_qa']}",
        "",
        "Review status:",
        *counter_lines(Counter(payload["review_status"])),
        "",
        "QA codes:",
        *counter_lines(Counter(payload["qa_codes"])),
        "",
        "Packs:",
        *counter_lines(Counter(payload["packs"])),
        "",
        "Top revision records:",
    ]
    if not payload["records"]:
        lines.append("- none")
    else:
        for record in payload["records"][:20]:
            pack = str(record["pack"]).strip() or "-"
            reasons = ", ".join(record["reasons"])
            lines.append(f"- index={record['index']} id={record['id']} pack={pack} shot={record['shot_type']} reasons={reasons}")
        remaining = payload["revision_count"] - 20
        if remaining > 0:
            lines.append(f"- ... {remaining} more")
    return "\n".join(lines)


def filter_records_by_qa(
    records: list[PromptRecord],
    source_records: list[PromptRecord] | None = None,
    qa_code: str | None = None,
    qa_severity: str | None = None,
) -> list[PromptRecord]:
    if qa_code is None and qa_severity is None:
        return records
    payload = plan_qa_payload(records, source_records=source_records, code=qa_code, severity=qa_severity)
    ids_with_findings = {str(finding["id"]) for finding in payload["findings"]}
    return [record for record in records if record.id in ids_with_findings]


def copy_record_subset(
    records: list[PromptRecord],
    output_dir: str | Path,
    source_records: list[PromptRecord] | None = None,
    filters: dict[str, str] | None = None,
) -> dict[str, Any]:
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    source_indexes = {id(record): index for index, record in enumerate(source_records or records)}
    records_path = base_path / "records.json"
    manifest_path = base_path / "subset_manifest.json"
    save_records(records, records_path)
    manifest = {
        "source_count": len(source_records or records),
        "copied_count": len(records),
        "filters": filters or {},
        "records": [
            {
                "source_index": source_indexes.get(id(record), fallback_index),
                "id": record.id,
                "pack": record.metadata.get("pack", ""),
                "mode": record.mode,
                "shot_type": record.shot_type,
                "angle": record.angle,
            }
            for fallback_index, record in enumerate(records)
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "copied_count": len(records),
        "records_json": records_path,
        "manifest": manifest_path,
    }


def export_missing_result_worklist(
    records: list[PromptRecord],
    output_dir: str | Path,
    source_records: list[PromptRecord] | None = None,
    filters: dict[str, str] | None = None,
) -> dict[str, Any]:
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    source_indexes = {id(record): index for index, record in enumerate(source_records or records)}
    missing_records = [record for record in records if not record.result_refs]
    entries = []
    for fallback_index, record in enumerate(missing_records):
        entries.append(
            {
                "index": source_indexes.get(id(record), fallback_index),
                "id": record.id,
                "pack": record.metadata.get("pack", ""),
                "mode": record.mode,
                "shot_type": record.shot_type,
                "angle": record.angle,
                "aspect_ratio": record.aspect_ratio,
                "bbox_template": record.metadata.get("bbox_template", ""),
                "prompt_text": record.prompt_text,
                "negative_prompt": record.negative_prompt,
            }
        )

    json_path = base_path / "missing_results.json"
    csv_path = base_path / "missing_results.csv"
    payload = {
        "source_count": len(source_records or records),
        "filtered_count": len(records),
        "missing_count": len(entries),
        "filters": filters or {},
        "records": entries,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["index", "id", "pack", "mode", "shot_type", "angle", "aspect_ratio", "bbox_template", "prompt_text", "negative_prompt"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    return {
        "missing_count": len(entries),
        "json": json_path,
        "csv": csv_path,
    }


def export_prompt_files(
    records: list[PromptRecord],
    output_dir: str | Path,
    include_negative: bool = False,
    source_count: int | None = None,
    filters: dict[str, str] | None = None,
) -> dict[str, Any]:
    base_path = Path(output_dir)
    prompts_path = base_path / "prompts"
    negatives_path = base_path / "negative_prompts"
    prompts_path.mkdir(parents=True, exist_ok=True)
    if include_negative:
        negatives_path.mkdir(parents=True, exist_ok=True)

    manifest_records = []
    for index, record in enumerate(records):
        filename_stem = f"{index:04d}_{safe_filename(record.id)}"
        prompt_path = prompts_path / f"{filename_stem}.txt"
        prompt_path.write_text(record.prompt_text.strip() + "\n", encoding="utf-8")
        manifest_entry = {
            "index": index,
            "id": record.id,
            "prompt_file": str(prompt_path),
            "shot_type": record.shot_type,
            "angle": record.angle,
            "pack": record.metadata.get("pack", ""),
            "mode": record.mode,
            "template": record.metadata.get("bbox_template", ""),
        }
        if include_negative:
            negative_path = negatives_path / f"{filename_stem}.txt"
            negative_path.write_text(record.negative_prompt.strip() + "\n", encoding="utf-8")
            manifest_entry["negative_file"] = str(negative_path)
        manifest_records.append(manifest_entry)

    manifest = {
        "source_count": source_count if source_count is not None else len(records),
        "exported_count": len(records),
        "include_negative": include_negative,
        "filters": filters or {},
        "records": manifest_records,
    }
    manifest_path = base_path / "prompt_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "prompt_count": len(records),
        "prompts_dir": prompts_path,
        "negative_prompts_dir": negatives_path if include_negative else None,
        "manifest": manifest_path,
    }


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        args = resolve_build_args(args)
        records = build_records(
            subject=args.subject,
            style=args.style,
            mode=args.mode,
            count=args.count,
            palette_name=args.palette,
            character_bible=character_bible_from_args(args),
            style_profile_name=args.style_profile,
            style_intensity=args.style_intensity,
        )
        files = Exporter().export(records, args.out)
        print(f"Wrote {len(records)} records")
        for path in files.values():
            print(path)
    elif args.command == "build-character-lora":
        args = resolve_character_lora_args(args)
        pack_counts = {
            "core": args.core_count,
            "turnaround": args.turnaround_count,
            "expressions": args.expressions_count,
            "costume_details": args.costume_details_count,
            "action": args.action_count,
            "environment": args.environment_count,
        }
        pack_counts = {key: value for key, value in pack_counts.items() if value is not None}
        records = build_character_lora_records(
            subject=args.subject,
            character_bible=character_bible_from_args(args),
            palette_name=args.palette,
            pack_counts=pack_counts,
            style_profile_name=args.style_profile,
            pack_style_profiles=args.pack_style_profiles,
            style_intensity=args.style_intensity,
            pack_style_intensity=args.pack_style_intensity,
        )
        files = Exporter().export(records, args.out)
        print(f"Wrote {len(records)} records")
        for path in files.values():
            print(path)
    elif args.command == "list":
        print(format_list(args.resource))
    elif args.command == "inspect":
        records = load_records(args.records_path)
        print(format_records_inspection(records, args.records_path))
    elif args.command == "stats":
        records = load_records(args.records_path)
        print(format_records_stats(records, args.records_path))
    elif args.command == "validate":
        records = load_records(args.records_path)
        report = validate_records_for_handoff(records)
        print(format_validation_report(report, args.records_path))
        if report["status"] != "valid":
            raise SystemExit(1)
    elif args.command == "qa":
        records = load_records(args.records_path)
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
        )
        print(format_plan_qa(filtered_records, args.records_path, field=args.field, source_records=records, code=args.code, severity=args.severity))
    elif args.command == "export-qa":
        records = load_records(args.records_path)
        filters = {
            key: value
            for key, value in {
                "pack": args.pack,
                "mode": args.mode,
                "shot_type": args.shot_type,
                "template": args.template,
                "code": args.code,
                "severity": args.severity,
            }.items()
            if value
        }
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
        )
        files = export_qa_findings(
            filtered_records,
            args.out,
            source_records=records,
            filters=filters,
            code=args.code,
            severity=args.severity,
        )
        print(f"Wrote {files['finding_count']} QA findings")
        print(files["json"])
        print(files["csv"])
    elif args.command == "export-revisions":
        records = load_records(args.records_path)
        filters = {
            key: value
            for key, value in {
                "pack": args.pack,
                "mode": args.mode,
                "shot_type": args.shot_type,
                "template": args.template,
                "review_status": args.review_status,
                "selected": args.selected,
                "needs_regen": args.needs_regen,
                "qa_code": args.qa_code,
                "qa_severity": args.qa_severity,
            }.items()
            if value
        }
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
        )
        files = export_revision_worklist(
            filtered_records,
            args.out,
            source_records=records,
            filters=filters,
            review_status=args.review_status,
            selected=parse_bool(args.selected) if args.selected is not None else None,
            needs_regen=parse_bool(args.needs_regen) if args.needs_regen is not None else None,
            qa_code=args.qa_code,
            qa_severity=args.qa_severity,
        )
        print(f"Wrote {files['revision_count']} revision records")
        print(files["json"])
        print(files["csv"])
    elif args.command == "revision-summary":
        records = load_records(args.records_path)
        filters = {
            key: value
            for key, value in {
                "pack": args.pack,
                "mode": args.mode,
                "shot_type": args.shot_type,
                "template": args.template,
                "review_status": args.review_status,
                "selected": args.selected,
                "needs_regen": args.needs_regen,
                "qa_code": args.qa_code,
                "qa_severity": args.qa_severity,
            }.items()
            if value
        }
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
        )
        print(
            format_revision_summary(
                filtered_records,
                args.records_path,
                field=args.field,
                source_records=records,
                filters=filters,
                review_status=args.review_status,
                selected=parse_bool(args.selected) if args.selected is not None else None,
                needs_regen=parse_bool(args.needs_regen) if args.needs_regen is not None else None,
                qa_code=args.qa_code,
                qa_severity=args.qa_severity,
            )
        )
    elif args.command == "copy-records":
        records = load_records(args.records_path)
        filters = {
            key: value
            for key, value in {
                "pack": args.pack,
                "mode": args.mode,
                "shot_type": args.shot_type,
                "template": args.template,
                "review_status": args.review_status,
                "selected": args.selected,
                "needs_regen": args.needs_regen,
                "qa_code": args.qa_code,
                "qa_severity": args.qa_severity,
            }.items()
            if value
        }
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
            review_status=args.review_status,
            selected=parse_bool(args.selected) if args.selected is not None else None,
            needs_regen=parse_bool(args.needs_regen) if args.needs_regen is not None else None,
        )
        filtered_records = filter_records_by_qa(
            filtered_records,
            source_records=records,
            qa_code=args.qa_code,
            qa_severity=args.qa_severity,
        )
        files = copy_record_subset(filtered_records, args.out, source_records=records, filters=filters)
        print(f"Copied {files['copied_count']} records")
        print(files["records_json"])
        print(files["manifest"])
    elif args.command == "audit-results":
        records = load_records(args.records_path)
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
        )
        filtered_records = filter_result_records(
            filtered_records,
            has_results=parse_bool(args.has_results) if args.has_results is not None else None,
            result_status=args.result_status,
        )
        print(format_result_audit(filtered_records, args.records_path, field=args.field, source_records=records))
    elif args.command == "recommend":
        records = load_records(args.records_path)
        print(format_recommendations(records, args.records_path))
    elif args.command == "review":
        records = load_records(args.records_path)
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
            review_status=args.status,
            selected=parse_bool(args.selected) if args.selected is not None else None,
            needs_regen=parse_bool(args.needs_regen) if args.needs_regen is not None else None,
        )
        print(format_review_records(filtered_records, args.records_path, source_records=records, field=args.field))
    elif args.command == "select":
        records = load_records(args.records_path)
        record = select_record(records, index=args.index, record_id=args.id)
        print(format_selected_record(record, args.field))
    elif args.command == "mark":
        records = load_records(args.records_path)
        record = mark_record(
            records,
            index=args.index,
            record_id=args.id,
            status=args.status,
            notes=args.notes,
            selected=parse_bool(args.selected) if args.selected is not None else None,
            needs_regen=parse_bool(args.needs_regen) if args.needs_regen is not None else None,
        )
        save_records(records, args.records_path)
        print(f"Marked {record.id}")
        print(format_selected_record(record, "review"))
    elif args.command == "attach-result":
        records = load_records(args.records_path)
        record = attach_result_ref(
            records,
            index=args.index,
            record_id=args.id,
            path=args.path,
            status=args.status,
            notes=args.notes,
        )
        save_records(records, args.records_path)
        print(f"Attached result to {record.id}")
        print(json.dumps(record.result_refs[-1], indent=2, ensure_ascii=False))
    elif args.command == "export-missing-results":
        records = load_records(args.records_path)
        filters = {
            key: value
            for key, value in {
                "pack": args.pack,
                "mode": args.mode,
                "shot_type": args.shot_type,
                "template": args.template,
            }.items()
            if value
        }
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
        )
        files = export_missing_result_worklist(filtered_records, args.out, source_records=records, filters=filters)
        print(f"Wrote {files['missing_count']} missing-result records")
        print(files["json"])
        print(files["csv"])
    elif args.command == "export-prompts":
        records = load_records(args.records_path)
        filters = {
            key: value
            for key, value in {
                "pack": args.pack,
                "mode": args.mode,
                "shot_type": args.shot_type,
                "template": args.template,
                "review_status": args.review_status,
                "selected": args.selected,
                "needs_regen": args.needs_regen,
            }.items()
            if value
        }
        filtered_records = filter_records(
            records,
            pack=args.pack,
            mode=args.mode,
            shot_type=args.shot_type,
            template=args.template,
            review_status=args.review_status,
            selected=parse_bool(args.selected) if args.selected is not None else None,
            needs_regen=parse_bool(args.needs_regen) if args.needs_regen is not None else None,
        )
        files = export_prompt_files(
            filtered_records,
            args.out,
            include_negative=args.include_negative,
            source_count=len(records),
            filters=filters,
        )
        print(f"Wrote {files['prompt_count']} prompt files")
        print(files["prompts_dir"])
        if files["negative_prompts_dir"]:
            print(files["negative_prompts_dir"])
        print(files["manifest"])
