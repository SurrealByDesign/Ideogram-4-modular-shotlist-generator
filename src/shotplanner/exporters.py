from __future__ import annotations

import csv
from collections import Counter
import html
import json
from pathlib import Path

from .character import lora_coverage_report
from .models import PromptRecord
from .modules import summarize_records


class Exporter:
    def export(self, records: list[PromptRecord], out_dir: str | Path) -> dict[str, Path]:
        output_path = Path(out_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        files = {
            "records_json": output_path / "records.json",
            "downstream_handoff_json": output_path / "downstream_handoff.json",
            "batch_csv": output_path / "batch.csv",
            "review_csv": output_path / "review.csv",
            "report_md": output_path / "report.md",
            "preview_html": output_path / "preview.html",
        }

        self._write_records_json(records, files["records_json"])
        self._write_downstream_handoff(records, files["downstream_handoff_json"])
        self._write_batch_csv(records, files["batch_csv"])
        self._write_review_csv(records, files["review_csv"])
        self._write_report(records, files["report_md"])
        self._write_preview_html(records, files["preview_html"])
        return files

    def _write_records_json(self, records: list[PromptRecord], path: Path) -> None:
        path.write_text(
            json.dumps([record.to_dict() for record in records], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _write_downstream_handoff(self, records: list[PromptRecord], path: Path) -> None:
        handoff = {
            "schema_version": "shotplanner.downstream_handoff.v1",
            "source": "shotplanner",
            "intended_consumer": "generic_downstream_prompt_workflow",
            "notes": [
                "records.json remains the canonical editable shotplanner output.",
                "base_prompt_json is a ready structured prompt object for downstream tooling.",
                "style_json_fragment and compositional_json are split out for optional workflow wiring.",
                "element_json_strings preserve per-element bbox data for downstream wrappers.",
            ],
            "records": [self._downstream_record(record, index) for index, record in enumerate(records)],
        }
        path.write_text(json.dumps(handoff, indent=2, ensure_ascii=False), encoding="utf-8")

    def _downstream_record(self, record: PromptRecord, index: int) -> dict[str, object]:
        base_prompt_json = self._downstream_base_prompt(record)
        style_json_fragment = {"style_description": base_prompt_json["style_description"]}
        compositional_json = base_prompt_json["compositional_deconstruction"]
        element_json_strings = [
            json.dumps(element, ensure_ascii=False, separators=(",", ":"))
            for element in compositional_json["elements"]
        ]
        palette_json = json.dumps(record.color_palette.get("colors", []), ensure_ascii=False, separators=(",", ":"))
        return {
            "index": index,
            "id": record.id,
            "label": f"{record.shot_type} / {record.angle}",
            "subject": record.subject,
            "mode": record.mode,
            "shot_type": record.shot_type,
            "angle": record.angle,
            "aspect_ratio": record.aspect_ratio,
            "prompt_text": record.prompt_text,
            "negative_prompt": record.negative_prompt,
            "character_bible": record.character_bible,
            "palette_json": palette_json,
            "style_json_fragment": style_json_fragment,
            "style_json_fragment_text": json.dumps(style_json_fragment, ensure_ascii=False, separators=(",", ":")),
            "compositional_json": compositional_json,
            "compositional_json_text": json.dumps(compositional_json, ensure_ascii=False, separators=(",", ":")),
            "element_json_strings": element_json_strings,
            "base_prompt_json": base_prompt_json,
            "base_prompt_json_text": json.dumps(base_prompt_json, ensure_ascii=False, separators=(",", ":")),
            "metadata": {
                "bbox_template": record.metadata.get("bbox_template", ""),
                "sequence_index": record.metadata.get("sequence_index", index),
                "prompt_variation": record.metadata.get("prompt_variation", {}),
                "shotplanner_record_id": record.id,
                "character_bible": record.character_bible,
            },
        }

    def _downstream_base_prompt(self, record: PromptRecord) -> dict[str, object]:
        variation = record.metadata.get("prompt_variation", {})
        colors = list(record.color_palette.get("colors", []))
        style_name = record.style_description.get("name", "")
        return {
            "prompt": record.prompt_text,
            "negative_prompt": record.negative_prompt,
            "aspect_ratio": record.aspect_ratio,
            "style_description": {
                "aesthetics": style_name,
                "lighting": variation.get("lighting", ""),
                "color_palette": colors,
            },
            "compositional_deconstruction": {
                "background": variation.get("background", ""),
                "elements": [
                    self._downstream_element(record, element, colors)
                    for element in record.bbox_layout.get("elements", [])
                ],
            },
            "metadata": {
                "source": "shotplanner",
                "id": record.id,
                "mode": record.mode,
                "shot_type": record.shot_type,
                "angle": record.angle,
                "bbox_template": record.metadata.get("bbox_template", ""),
                "character_bible": record.character_bible,
            },
        }

    def _downstream_element(self, record: PromptRecord, element: dict[str, object], colors: list[str]) -> dict[str, object]:
        element_type = str(element.get("type", "obj"))
        result = {
            "type": element_type,
            "description": str(element.get("desc", "")),
            "bbox": element.get("bbox", []),
        }
        if element_type == "text":
            result["text_content"] = record.subject if record.mode == "poster" else ""
        if colors:
            result["color_palette"] = colors[:5]
        return result

    def _write_batch_csv(self, records: list[PromptRecord], path: Path) -> None:
        fieldnames = [
            "id",
            "subject",
            "mode",
            "shot_type",
            "angle",
            "aspect_ratio",
            "prompt_text",
            "negative_prompt",
            "bbox_template",
            "color_palette_name",
            "metadata",
            "ideogram_json",
        ]
        with path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {
                        "id": record.id,
                        "subject": record.subject,
                        "mode": record.mode,
                        "shot_type": record.shot_type,
                        "angle": record.angle,
                        "aspect_ratio": record.aspect_ratio,
                        "prompt_text": record.prompt_text,
                        "negative_prompt": record.negative_prompt,
                        "bbox_template": record.metadata.get("bbox_template", ""),
                        "color_palette_name": record.color_palette.get("name", ""),
                        "metadata": json.dumps(record.metadata, ensure_ascii=False, separators=(",", ":")),
                        "ideogram_json": json.dumps(record.ideogram_json, ensure_ascii=False, separators=(",", ":")),
                    }
                )

    def _write_review_csv(self, records: list[PromptRecord], path: Path) -> None:
        fieldnames = [
            "index",
            "id",
            "pack",
            "mode",
            "shot_type",
            "angle",
            "aspect_ratio",
            "bbox_template",
            "palette",
            "coverage_category",
            "prompt_short",
        ]
        with path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for index, record in enumerate(records):
                writer.writerow(
                    {
                        "index": index,
                        "id": record.id,
                        "pack": record.metadata.get("pack", ""),
                        "mode": record.mode,
                        "shot_type": record.shot_type,
                        "angle": record.angle,
                        "aspect_ratio": record.aspect_ratio,
                        "bbox_template": record.metadata.get("bbox_template", ""),
                        "palette": record.color_palette.get("name", ""),
                        "coverage_category": self._coverage_category(record),
                        "prompt_short": self._short_text(record.prompt_text),
                    }
                )

    def _coverage_category(self, record: PromptRecord) -> str:
        shot_type = record.shot_type
        if "expression" in shot_type or shot_type == "portrait":
            return "expression_or_portrait"
        if shot_type in {"front_view", "left_side_view", "right_side_view", "side_view", "back_view", "three_quarter", "three_quarter_front", "three_quarter_back", "turnaround_sheet", "head_turnaround"}:
            return "turnaround"
        if "detail" in shot_type or shot_type in {"hands_or_gloves", "footwear_detail", "prop_detail", "accessory_detail", "material_detail"}:
            return "detail"
        if "pose" in shot_type or shot_type in {"action_pose", "walking_pose", "turning_pose", "reaching_pose", "crouching_pose", "hero_pose"}:
            return "action"
        if "context" in shot_type or shot_type == "environment":
            return "environment"
        if shot_type in {"full_body", "neutral_reference"}:
            return "core_reference"
        return "other"

    def _short_text(self, text: str, limit: int = 180) -> str:
        clean = " ".join(text.split())
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    def _write_report(self, records: list[PromptRecord], path: Path) -> None:
        if records:
            subject = records[0].subject
            mode = self._report_mode(records)
        else:
            subject = ""
            mode = ""
        summary = summarize_records(records)
        coverage = lora_coverage_report(records)
        lines = [
            "# shotplanner build report",
            "",
            f"- Subject: {subject}",
            f"- Mode: {mode}",
            f"- Count: {len(records)}",
            "",
            "## Templates used",
            *self._counter_lines(summary["template_counts"]),
            "",
            "## Color palettes",
            *self._counter_lines(summary["palette_counts"]),
            "",
            "## Style profiles",
            *self._counter_lines(self._style_profile_counts(records)),
            "",
            "## Review summary",
            *self._counter_lines(self._review_status_counts(records)),
            "",
            "## Review flags",
            *self._counter_lines(self._review_flag_counts(records)),
            "",
            "## Shot type counts",
            *self._counter_lines(summary["shot_type_counts"]),
            "",
            "## Angle counts",
            *self._counter_lines(summary["angle_counts"]),
            "",
            "## Aspect ratio counts",
            *self._counter_lines(summary["aspect_ratio_counts"]),
            "",
            "## Character LoRA coverage",
            *self._coverage_lines(coverage),
            "",
            "## Files written",
            "- records.json",
            "- downstream_handoff.json",
            "- batch.csv",
            "- review.csv",
            "- report.md",
            "- preview.html",
            "",
            "## Known limitations",
            "- This tool does not generate images.",
            "- It does not call the Ideogram API.",
            "- Color palette data uses static planning palettes, not image analysis or extraction.",
            "- Downstream handoff is file-based; it does not install or run external wrappers.",
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _counter_lines(self, counter: dict[str, int]) -> list[str]:
        if not counter:
            return ["- None"]
        return [f"- {name}: {count}" for name, count in sorted(counter.items())]

    def _style_profile_counts(self, records: list[PromptRecord]) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for record in records:
            profile = record.style_description.get("profile", {})
            if not isinstance(profile, dict) or not profile.get("name"):
                continue
            intensity = str(profile.get("intensity", "standard"))
            counts[f"{profile['name']} / {intensity}"] += 1
        return dict(counts)

    def _review_status_counts(self, records: list[PromptRecord]) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for record in records:
            status = str(record.review.get("review_status", "")).strip() or "unreviewed"
            counts[status] += 1
        return dict(counts)

    def _review_flag_counts(self, records: list[PromptRecord]) -> dict[str, int]:
        counts: Counter[str] = Counter()
        selected = sum(1 for record in records if record.review.get("selected") is True)
        needs_regen = sum(1 for record in records if record.review.get("needs_regen") is True)
        if selected:
            counts["selected=true"] = selected
        if needs_regen:
            counts["needs_regen=true"] = needs_regen
        return dict(counts)

    def _report_mode(self, records: list[PromptRecord]) -> str:
        modes = {record.mode for record in records}
        packs = {record.metadata.get("pack", "") for record in records if record.metadata.get("pack")}
        if len(modes) > 1 and packs:
            return "character_lora_multipack"
        if len(modes) == 1:
            return next(iter(modes))
        return "mixed"

    def _coverage_lines(self, coverage: dict[str, object]) -> list[str]:
        if not coverage["applies"]:
            return ["- Not applicable for this mode."]
        decision = coverage["decision"]
        required = coverage["required"]
        required_text = ", ".join(item.replace("_", " ") for item in required)
        lines = [
            f"- Status: {coverage['status']}",
            f"- Decision: {decision['summary']}",
            f"- Recommended next action: {decision['recommendation']}",
            f"- Required coverage for this plan: {required_text}",
            f"- Coverage profile: {coverage['description']}",
            "",
            "### Coverage counts",
        ]
        for category, count in coverage["coverage"].items():
            lines.append(f"- {category.replace('_', ' ')}: {count}")
        missing = coverage["missing"]
        thin = coverage["thin"]
        missing_text = ", ".join(item.replace("_", " ") for item in missing) if missing else "none"
        thin_text = ", ".join(item.replace("_", " ") for item in thin) if thin else "none"
        lines.append(f"- Missing: {missing_text}")
        lines.append(f"- Thin coverage: {thin_text}")
        recommendations = coverage.get("recommendations", [])
        if recommendations:
            lines.extend(["", "### Add-count recommendations"])
            for item in recommendations:
                if isinstance(item, dict):
                    lines.append(f"- {item['summary']} Example shot types: {item['examples']}.")
        else:
            lines.extend(["", "### Add-count recommendations", "- none"])
        return lines

    def _write_preview_html(self, records: list[PromptRecord], path: Path) -> None:
        subject = records[0].subject if records else ""
        mode = records[0].mode if records else ""
        summary = summarize_records(records)
        coverage = lora_coverage_report(records)
        cards = "\n".join(self._record_card(record) for record in records)
        pack_filters = "\n".join(
            f'<option value="{html.escape(name)}">{html.escape(name)} ({count})</option>'
            for name, count in sorted(self._pack_counts(records).items())
            if name
        )
        template_filters = "\n".join(
            f'<option value="{html.escape(name)}">{html.escape(name)} ({count})</option>'
            for name, count in sorted(summary["template_counts"].items())
            if name
        )
        shot_filters = "\n".join(
            f'<option value="{html.escape(name)}">{html.escape(name)} ({count})</option>'
            for name, count in sorted(summary["shot_type_counts"].items())
            if name
        )
        page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>shotplanner preview - {html.escape(subject)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1b1f24;
      --muted: #5b6472;
      --line: #d6dbe3;
      --panel: #f7f8fa;
      --accent: #235789;
      --accent-soft: #e8f1f8;
      --text-zone: #c84630;
      --obj-zone: #235789;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #ffffff;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    header {{
      padding: 24px 28px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 24px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      color: var(--muted);
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(180px, 1fr) minmax(140px, 190px) minmax(150px, 220px) minmax(150px, 220px);
      gap: 12px;
      padding: 16px 28px;
      border-bottom: 1px solid var(--line);
      background: #fff;
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    .summary-band {{
      display: grid;
      grid-template-columns: minmax(220px, 1fr) minmax(220px, 1fr);
      gap: 16px;
      padding: 16px 28px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    .summary-block {{
      min-width: 0;
    }}
    .summary-block h2 {{
      margin: 0 0 8px;
      font-size: 15px;
    }}
    .summary-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    input, select {{
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }}
    main {{
      padding: 20px 28px 32px;
    }}
    .records {{
      display: grid;
      gap: 14px;
    }}
    article {{
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: #fff;
    }}
    .card-head {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: start;
      padding: 14px 16px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    .id {{
      font-family: Consolas, Menlo, monospace;
      font-size: 13px;
      color: var(--accent);
      overflow-wrap: anywhere;
    }}
    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: flex-end;
    }}
    .tag {{
      border: 1px solid #b8c8d8;
      border-radius: 999px;
      padding: 3px 8px;
      color: #153b5c;
      background: var(--accent-soft);
      font-size: 12px;
      white-space: nowrap;
    }}
    .card-body {{
      display: grid;
      grid-template-columns: minmax(260px, 380px) minmax(0, 1fr);
      gap: 16px;
      padding: 16px;
    }}
    .layout-box {{
      position: relative;
      width: 100%;
      aspect-ratio: 1 / 1;
      border: 1px solid var(--line);
      border-radius: 6px;
      background:
        linear-gradient(to right, rgba(35, 87, 137, .08) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(35, 87, 137, .08) 1px, transparent 1px);
      background-size: 10% 10%;
    }}
    .bbox {{
      position: absolute;
      border: 2px solid var(--obj-zone);
      background: rgba(35, 87, 137, .10);
      overflow: hidden;
    }}
    .bbox.text {{
      border-color: var(--text-zone);
      background: rgba(200, 70, 48, .10);
    }}
    .bbox-label {{
      display: block;
      padding: 4px 5px;
      color: var(--ink);
      font-size: 11px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }}
    .prompt {{
      margin: 0 0 12px;
      font-size: 15px;
    }}
    details {{
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }}
    summary {{
      cursor: pointer;
      color: var(--accent);
      font-weight: 700;
    }}
    pre {{
      max-height: 320px;
      overflow: auto;
      margin: 10px 0 0;
      padding: 12px;
      border-radius: 6px;
      background: #101418;
      color: #eef4f8;
      font-size: 12px;
      line-height: 1.4;
    }}
    .empty {{
      padding: 24px;
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 8px;
    }}
    @media (max-width: 820px) {{
      .toolbar, .card-body {{
        grid-template-columns: 1fr;
      }}
      .tags {{
        justify-content: flex-start;
      }}
      header, .toolbar, main, .summary-band {{
        padding-left: 16px;
        padding-right: 16px;
      }}
      .summary-band {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(subject) if subject else "shotplanner preview"}</h1>
    <div class="meta">
      <span>Mode: {html.escape(mode)}</span>
      <span>Records: {len(records)}</span>
      <span>Generated preview: preview.html</span>
    </div>
  </header>
  {self._preview_summary_html(records, coverage)}
  <section class="toolbar" aria-label="Preview filters">
    <input id="search" type="search" placeholder="Search prompts, ids, angles, templates">
    <select id="packFilter">
      <option value="">All packs</option>
      {pack_filters}
    </select>
    <select id="shotFilter">
      <option value="">All shot types</option>
      {shot_filters}
    </select>
    <select id="templateFilter">
      <option value="">All templates</option>
      {template_filters}
    </select>
  </section>
  <main>
    <section class="records" id="records">
      {cards if cards else '<div class="empty">No records to preview.</div>'}
    </section>
  </main>
  <script>
    const search = document.querySelector("#search");
    const packFilter = document.querySelector("#packFilter");
    const shotFilter = document.querySelector("#shotFilter");
    const templateFilter = document.querySelector("#templateFilter");
    const cards = Array.from(document.querySelectorAll("article[data-search]"));

    function applyFilters() {{
      const query = search.value.trim().toLowerCase();
      const pack = packFilter.value;
      const shot = shotFilter.value;
      const template = templateFilter.value;
      for (const card of cards) {{
        const matchesQuery = !query || card.dataset.search.includes(query);
        const matchesPack = !pack || card.dataset.pack === pack;
        const matchesShot = !shot || card.dataset.shot === shot;
        const matchesTemplate = !template || card.dataset.template === template;
        card.hidden = !(matchesQuery && matchesPack && matchesShot && matchesTemplate);
      }}
    }}

    search.addEventListener("input", applyFilters);
    packFilter.addEventListener("change", applyFilters);
    shotFilter.addEventListener("change", applyFilters);
    templateFilter.addEventListener("change", applyFilters);
  </script>
</body>
</html>
"""
        path.write_text(page, encoding="utf-8")

    def _record_card(self, record: PromptRecord) -> str:
        template_name = str(record.metadata.get("bbox_template", ""))
        pack_name = str(record.metadata.get("pack", ""))
        searchable = " ".join(
            [
                record.id,
                record.subject,
                record.mode,
                record.shot_type,
                record.angle,
                record.aspect_ratio,
                template_name,
                pack_name,
                record.prompt_text,
            ]
        ).lower()
        tags = [
            f"pack:{pack_name}" if pack_name else "",
            record.shot_type,
            record.angle,
            record.aspect_ratio,
            f"template:{template_name}" if template_name else "",
        ]
        if record.character_bible:
            tags.append("identity_anchor")
        tag_html = "\n".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in tags if tag)
        json_text = json.dumps(record.to_dict(), indent=2, ensure_ascii=False)
        return f"""<article data-search="{html.escape(searchable, quote=True)}" data-pack="{html.escape(pack_name, quote=True)}" data-shot="{html.escape(record.shot_type, quote=True)}" data-template="{html.escape(template_name, quote=True)}">
  <div class="card-head">
    <div>
      <div class="id">{html.escape(record.id)}</div>
      <strong>{html.escape(record.shot_type.replace("_", " "))}</strong>
    </div>
    <div class="tags">{tag_html}</div>
  </div>
  <div class="card-body">
    <div>
      <div class="layout-box" aria-label="Normalized bbox preview for {html.escape(record.id, quote=True)}">
        {self._bbox_html(record)}
      </div>
    </div>
    <div>
      <p class="prompt">{html.escape(record.prompt_text)}</p>
      {self._character_bible_html(record)}
      <p><strong>Negative:</strong> {html.escape(record.negative_prompt)}</p>
      <details>
        <summary>Structured record JSON</summary>
        <pre>{html.escape(json_text)}</pre>
      </details>
    </div>
  </div>
</article>"""

    def _preview_summary_html(self, records: list[PromptRecord], coverage: dict[str, object]) -> str:
        bible = next((record.character_bible for record in records if record.character_bible), {})
        bible_items = "".join(
            f'<li class="tag">{html.escape(key.replace("_", " "))}: {html.escape(str(value))}</li>'
            for key, value in bible.items()
            if value
        )
        if not bible_items:
            bible_items = '<li class="tag">No character bible fields provided</li>'
        if coverage["applies"]:
            coverage_items = "".join(
                f'<li class="tag">{html.escape(key.replace("_", " "))}: {count}</li>'
                for key, count in coverage["coverage"].items()
            )
        else:
            coverage_items = '<li class="tag">Coverage applies to character_lora mode</li>'
        pack_items = self._summary_tags(self._pack_counts(records), "No pack metadata")
        template_items = self._summary_tags(self._template_counts(records), "No templates")
        return f"""<section class="summary-band" aria-label="LoRA planning summary">
    <div class="summary-block">
      <h2>Character Bible</h2>
      <ul class="summary-list">{bible_items}</ul>
    </div>
    <div class="summary-block">
      <h2>LoRA Coverage</h2>
      <ul class="summary-list">{coverage_items}</ul>
    </div>
    <div class="summary-block">
      <h2>Packs</h2>
      <ul class="summary-list">{pack_items}</ul>
    </div>
    <div class="summary-block">
      <h2>Templates</h2>
      <ul class="summary-list">{template_items}</ul>
    </div>
  </section>"""

    def _summary_tags(self, counts: dict[str, int], empty_label: str) -> str:
        if not counts:
            return f'<li class="tag">{html.escape(empty_label)}</li>'
        return "".join(
            f'<li class="tag">{html.escape(name)}: {count}</li>'
            for name, count in sorted(counts.items())
            if name
        )

    def _pack_counts(self, records: list[PromptRecord]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            pack = str(record.metadata.get("pack", ""))
            if pack:
                counts[pack] = counts.get(pack, 0) + 1
        return counts

    def _template_counts(self, records: list[PromptRecord]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            template = str(record.metadata.get("bbox_template", ""))
            if template:
                counts[template] = counts.get(template, 0) + 1
        return counts

    def _character_bible_html(self, record: PromptRecord) -> str:
        if not record.character_bible:
            return ""
        items = "".join(
            f"<li><strong>{html.escape(key.replace('_', ' '))}:</strong> {html.escape(str(value))}</li>"
            for key, value in record.character_bible.items()
            if value
        )
        if not items:
            return ""
        return f"<details><summary>Character bible</summary><ul>{items}</ul></details>"

    def _bbox_html(self, record: PromptRecord) -> str:
        elements = record.bbox_layout.get("elements", [])
        boxes = []
        for element in elements:
            y_min, x_min, y_max, x_max = element["bbox"]
            left = x_min / 10
            top = y_min / 10
            width = (x_max - x_min) / 10
            height = (y_max - y_min) / 10
            element_type = str(element.get("type", "obj"))
            css_class = "bbox text" if element_type == "text" else "bbox"
            label = f"{element_type}: {element.get('desc', '')}"
            boxes.append(
                f'<div class="{css_class}" style="left:{left:.1f}%;top:{top:.1f}%;width:{width:.1f}%;height:{height:.1f}%;">'
                f'<span class="bbox-label">{html.escape(label)}</span></div>'
            )
        return "\n".join(boxes)
