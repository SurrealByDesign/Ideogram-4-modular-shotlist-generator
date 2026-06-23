# Changelog

## 1.0.0 - Stable CLI Workflow

Changed:

- Reorganized README command examples into stable workflow groups.
- Added a command-family guide for build, inspect, review, QA, results, revision, and prompt handoff commands.
- Added a compact README CLI reference covering each public command's purpose, inputs, outputs, and notes.
- Added `CONTRIBUTING.md` with test, scope, output artifact, and documentation guidance.
- Added `RELEASE_CHECKLIST.md` for pre-tag verification and GitHub release steps.
- Added `RELEASE_NOTES_1.0.0.md` as a GitHub release note draft.
- Added GitHub issue and pull request templates.
- Added `SECURITY.md` with local-data reporting guidance.
- Added GitHub Actions test workflow for Python 3.10, 3.11, and 3.12.
- Added `.gitattributes` to keep text file line endings predictable.
- Changed package maturity classifier from Production/Stable to Beta for the first public release.
- Added `examples/stable_cli_workflow/` as an end-to-end command workflow from build through QA, revision, subset copying, and prompt export.
- Trimmed checked-in example artifacts to keep release fixtures compact and reproducible.
- Renamed optional structured handoff output to `downstream_handoff.json`.
- Documented the `downstream_handoff.json` helper schema.
- Added package metadata classifiers and keywords.
- Added a README quickstart and made workflow handoff examples use the checked-in stable workflow fixture.
- Updated quickstart and workflow handoff examples to write generated files under ignored `outputs/` folders.
- Documented v1.0 output stability: `records.json` remains canonical and current helper outputs remain supported derived files.

## 0.9.0 - Revision Workflow

Added:

- `export-revisions` command for JSON and CSV revision worklists from review state and QA findings.
- `revision-summary` command for summarizing records needing revision from review state and QA findings.
- `copy-records` command for copying filtered record subsets into new planning folders.

## 0.8.0 - Plan QA / Prompt Quality Checks

Added:

- `qa` command for local rule-based prompt and metadata quality checks.
- `export-qa` command for writing JSON and CSV QA finding handoff files.
- QA summary and JSON output modes.
- QA filters for pack, mode, shot type, bbox template, finding code, and severity.
- Checks for weak character identity anchors, empty negative prompts, long prompts, duplicate prompts, and repeated prompt words.

## 0.7.0 - Result Audit Prep

Added:

- `result_refs` field on `PromptRecord` for local generated-result references.
- `attach-result` command for linking generated result files back to planned records.
- `audit-results` command for summarizing result reference coverage and missing records.
- Result audit filters for pack, mode, shot type, bbox template, attached-result presence, and result status.
- `export-missing-results` command for writing JSON and CSV worklists of planned records that still need result files.
- `select --field result_refs` support.

## 0.6.0 - Review Workflow Polish

Added:

- `review` command for listing records by review state and planning filters.
- `review --field` output modes for summary, ids, prompts, and JSON.
- `examples/review_workflow/` with mark, review, and review-filtered export sample outputs.

## 0.5.0 - Review Workflow

Added:

- `review` field on `PromptRecord` for human review state.
- `mark` command for setting review status, notes, selected state, and regeneration flags in `records.json`.
- `select --field review` support.
- review filters for `export-prompts`.
- review status and flag summaries in `stats` and `report.md`.

## 0.4.0 - Style Modules

Added:

- Named style profiles for reusable prompt and negative guidance.
- `--style-profile` support for `build` and `build-character-lora`.
- `--style-intensity` support for light, standard, and strong style profile phrasing.
- `style_profile` config field.
- `style_intensity` config field.
- `pack_style_profiles` config field for multi-pack style overrides.
- `pack_style_intensity` config field for multi-pack intensity overrides.
- `list styles` command.
- Style profile/intensity summaries in `stats` and `report.md`.
- `examples/style_profiles/` with global and per-pack style profile/intensity sample config and outputs.

## 0.3.0 - Workflow Handoff

Added:

- `stats` command for compact count tables from a finished `records.json`.
- `validate` command for checking finished `records.json` files before handoff.
- `recommend` command for printing only LoRA coverage additions from a finished `records.json`.
- Add-count recommendations in LoRA coverage reports for missing or thin shot categories.
- `export-prompts` command for writing one prompt `.txt` file per record from a finished `records.json`.
- `export-prompts` filters for pack, mode, shot type, and bbox template.
- Optional `--include-negative` export for matching negative prompt text files.
- `prompt_manifest.json` to map exported prompt files back to record ids, indexes, packs, shot types, and angles.
- `examples/workflow_handoff/` usage notes.

## 0.2.0 - Better Shot Planning

This release turns the original foundation into a stronger standalone LoRA/reference shot planner.

Added:

- Project naming standardized on `shotplanner`.
- Focused character LoRA pack modes and presets:
  - `character_lora_core`
  - `character_lora_turnaround`
  - `character_lora_expressions`
  - `character_lora_costume_details`
  - `character_lora_action`
  - `character_lora_environment`
- `build-character-lora` command for complete multi-pack character LoRA plans.
- JSON `--config` input for repeatable single-pack and multi-pack builds.
- Character bible fields for identity consistency.
- LoRA coverage reporting with plain-language decisions and recommended next actions.
- Specialized bbox templates for expression strips, turnarounds, hands, props, materials, costume layers, and accessory callouts.
- Static planning palettes.
- Deterministic prompt variation.
- `preview.html` with pack/template summaries and filters.
- `review.csv` compact planning export.
- Optional `downstream_handoff.json` derived output.
- `list` command for presets, modes, palettes, templates, and packs.
- `examples/` folder with small sample builds.
- `docs/records_schema.md` and `docs/config_schema.md`.
- Schema stability tests.

Still out of scope:

- image generation
- Ideogram API calls
- External wrapper implementation
- LoRA training
- dataset cleanup
- ML image analysis
- GUI or web app

## 0.1.0 - Foundation

Initial command-line foundation:

- `PromptRecord` model with forward-compatible `extra`.
- modular shot planning pipeline
- core modes: `character_lora`, `three_d_reference`, `product_sheet`, `poster`
- normalized bbox templates and validation
- JSON, CSV, report, and preview exports
- initial tests and README
