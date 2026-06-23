# records.json Schema

`records.json` is the canonical `shotplanner` output. It is a JSON array of `PromptRecord` objects.

The format is intended to be editable and forward-compatible. Downstream tools should ignore unknown fields they do not use.

## PromptRecord

Required top-level fields:

- `id`: string. Unique record id within the file.
- `subject`: string. User-facing subject being planned.
- `mode`: string. Shotlist mode, such as `character_lora_core` or `product_sheet`.
- `shot_type`: string. Semantic shot role.
- `angle`: string. View or pose angle.
- `aspect_ratio`: string. Ideogram-style aspect ratio label.
- `prompt_text`: string. Final prompt text built late in the pipeline.
- `negative_prompt`: string. Negative prompt text.
- `character_bible`: object. Stable character identity anchors. Empty for non-character builds.
- `style_description`: object. Style data used while building prompts.
- `bbox_layout`: object. Normalized layout plan.
- `color_palette`: object. Static planning palette.
- `ideogram_json`: object. Structured prompt payload derived from the record.
- `metadata`: object. Planner/module metadata.
- `review`: object. Optional human review state.
- `result_refs`: array. Optional local references to generated result files.
- `extra`: object. Future or unknown fields preserved by `PromptRecord.from_dict`.

## BBox Layout

`bbox_layout` must include:

- `name`: string.
- `aspect_ratio`: string.
- `elements`: array of element objects.

Each element must include:

- `type`: string, usually `obj` or `text`.
- `bbox`: array of four integers in `[y_min, x_min, y_max, x_max]` order.
- `desc`: string.

Coordinate rules:

- normalized range is `0` to `1000`
- `0 <= y_min < y_max <= 1000`
- `0 <= x_min < x_max <= 1000`
- coordinates are not pixels

## Character Bible

`character_bible` may include:

- `identity`
- `face`
- `hair`
- `body`
- `outfit`
- `accessories`
- `must_keep`
- `avoid`

The same object is also copied into `ideogram_json.character_bible`.

## Metadata

Common metadata fields:

- `sequence_index`: zero-based index inside the generated mode or pack.
- `bbox_template`: layout template name.
- `planner`: usually `ShotlistPlanner`.
- `color_palette_source`: usually `ColorPaletteAssigner`.
- `prompt_variation`: deterministic prompt variation fields.

Multi-pack character LoRA records also include:

- `pack`: short pack name, such as `core`, `turnaround`, or `expressions`.
- `pack_preset`: preset that generated the pack.
- `pack_record_id`: original id before pack prefixing.

## Review

`review` is reserved for human review state added after generation.

Common fields:

- `review_status`: one of `unreviewed`, `selected`, `rejected`, or `needs_regen`.
- `review_notes`: freeform note string.
- `selected`: boolean.
- `needs_regen`: boolean.

Freshly generated records use an empty `review` object and are counted as `unreviewed` in reports and stats.

## Result References

`result_refs` is reserved for links from planned records to generated files or other result artifacts.

Freshly generated records use an empty array.

Use `attach-result` to append a generated file reference to one planned record without changing the prompt plan itself.
Use `audit-results` to summarize how many records have result references and which planned records still need a linked result.
The audit can be filtered by pack, mode, shot type, bbox template, result presence, or result status.
Use `export-missing-results` to write JSON and CSV worklists from planned records that do not yet have any result references.

Suggested fields for each result reference:

- `path`: local file path or relative project path.
- `status`: review status for that result, such as `accepted`, `rejected`, or `needs_regen`.
- `notes`: freeform note string.

## Compatibility Rules

- `records.json` should remain a JSON array.
- Existing top-level fields should not be removed without a major schema change.
- New top-level fields should be treated as optional by downstream tools.
- Unknown fields loaded through `PromptRecord.from_dict` are preserved in `extra`.
- `records.json` is authoritative; CSV, report, preview, and handoff files are derived outputs.
- Derived helper outputs are stable for v1.0 but should be regenerated from `records.json` when possible.

## downstream_handoff.json

`downstream_handoff.json` is an optional structured helper output for wrappers or manual workflows that want prompt data split into reusable JSON fragments. It is derived from `records.json`; downstream tools should use `records.json` as the source of truth when there is any conflict.

Top-level fields:

- `schema_version`: currently `shotplanner.downstream_handoff.v1`.
- `source`: currently `shotplanner`.
- `intended_consumer`: descriptive string for generic downstream prompt workflows.
- `notes`: compatibility and usage notes.
- `records`: array of handoff records in the same order as `records.json`.

Each handoff record includes:

- `index`, `id`, `label`, `subject`, `mode`, `shot_type`, `angle`, and `aspect_ratio`.
- `prompt_text` and `negative_prompt`.
- `character_bible`.
- `palette_json`.
- `style_json_fragment` and `style_json_fragment_text`.
- `compositional_json` and `compositional_json_text`.
- `element_json_strings`.
- `base_prompt_json` and `base_prompt_json_text`.
- `metadata`.

## review.csv

`review.csv` is a compact planning table for sorting and scanning larger shot plans.

Columns:

- `index`
- `id`
- `pack`
- `mode`
- `shot_type`
- `angle`
- `aspect_ratio`
- `bbox_template`
- `palette`
- `coverage_category`
- `prompt_short`

## export-prompts

`export-prompts` reads a finished `records.json` file and writes plain text prompt files for batch use.

Default output:

- `prompts/`: one `.txt` prompt file per record.
- `prompt_manifest.json`: maps exported files back to record indexes, ids, packs, shot types, and angles.

Optional output with `--include-negative`:

- `negative_prompts/`: one `.txt` negative prompt file per record.

Optional filters:

- `--pack`
- `--mode`
- `--shot-type`
- `--template`
- `--review-status`
- `--selected`
- `--needs-regen`

When filters are used, `prompt_manifest.json` includes both `source_count` and `exported_count`.

## Helper Outputs

Result audit helpers:

- `missing_results.json`
- `missing_results.csv`

QA helpers:

- `qa_findings.json`
- `qa_findings.csv`

Revision helpers:

- `revision_worklist.json`
- `revision_worklist.csv`
- `subset_manifest.json`

These files are derived from `records.json` plus the filters used for the command that wrote them. They are stable workflow helpers, not replacements for the canonical record file.
