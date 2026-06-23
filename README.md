# shotplanner

`shotplanner` is a small Python command-line tool for generating modular Ideogram 4-style shotlist records.

Current version: `1.0.0`.

It does not generate images. The tool creates editable `PromptRecord` objects that move through local planning modules such as bbox layout assignment, style changes, prompt mutation, Ideogram-style JSON export, and optional downstream handoff files.

Prompt wording includes deterministic variation for pose, framing, lighting, background, and detail emphasis. Re-running the same command produces stable records, which makes output easier to review and reuse.

For release history, see `CHANGELOG.md`.

Small sample builds and workflow examples are available in `examples/`.

Schema notes are available in `docs/records_schema.md` and `docs/config_schema.md`.

Contribution notes are available in `CONTRIBUTING.md`.

Release steps are available in `RELEASE_CHECKLIST.md`.

Security reporting notes are available in `SECURITY.md`.

## Install

```bash
python -m pip install -e .
```

## Quickstart

Run a small built-in workflow from the project root:

```powershell
python -m shotplanner build-character-lora --config examples/stable_cli_workflow/stable_cli_workflow_config.json --out outputs/quickstart_plan
python -m shotplanner inspect outputs/quickstart_plan/records.json
python -m shotplanner stats outputs/quickstart_plan/records.json
```

The build writes a compact example plan to `outputs/quickstart_plan/`, which is ignored by Git. For your own work, use another ignored output folder such as `outputs/my_character_plan`.

## Testing

Run the test suite from the project root:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Example

Preset-based:

```powershell
python -m shotplanner build `
  --preset character_lora `
  --subject "orc mechanic woman with red braid, brass goggles, patched leather coat"
```

Fully explicit:

```powershell
python -m shotplanner build `
  --subject "orc mechanic woman with red braid, brass goggles, patched leather coat" `
  --style "cinematic realistic concept art" `
  --mode character_lora `
  --identity "same orc mechanic woman in every shot" `
  --hair "single red braid" `
  --outfit "patched leather coat, oil-stained work gloves" `
  --accessories "brass goggles, tool belt" `
  --must-keep "green skin, tusks, red braid, brass goggles" `
  --avoid "different face, different age, missing goggles" `
  --palette watercolor_fantasy `
  --count 50 `
  --out outputs/orc_mechanic
```

For Command Prompt, replace the trailing backticks with `^`. On macOS or Linux, replace them with `\`.

Multi-pack character LoRA plan:

```powershell
python -m shotplanner build-character-lora `
  --subject "orc mechanic woman with red braid, brass goggles, patched leather coat" `
  --identity "same orc mechanic woman in every shot" `
  --hair "single red braid" `
  --outfit "patched leather coat, oil-stained work gloves" `
  --accessories "brass goggles, tool belt" `
  --must-keep "green skin, tusks, red braid, brass goggles" `
  --avoid "different face, different age, missing goggles" `
  --out outputs/orc_mechanic_lora_plan
```

The same multi-pack build can be driven by a JSON config:

```powershell
python -m shotplanner build-character-lora `
  --config examples/character_lora_multipack_config.json
```

Explicit CLI flags override config values.

Preset values can be overridden with explicit flags such as `--count`, `--style`, `--mode`, or `--out`.

Apply a reusable style profile:

```powershell
python -m shotplanner build --subject "Moon Temple Knight" --mode character_lora --count 12 --style-profile technical_sheet
python -m shotplanner build --subject "Moon Temple Knight" --mode character_lora --count 12 --style-profile technical_sheet --style-intensity light
```

List available resources:

```powershell
python -m shotplanner list presets
python -m shotplanner list modes
python -m shotplanner list palettes
python -m shotplanner list styles
python -m shotplanner list templates
python -m shotplanner list packs
```

Inspect and validate generated records:

```powershell
python -m shotplanner inspect outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner stats outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner validate outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner recommend outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner select outputs/orc_mechanic_lora_plan/records.json --index 12
python -m shotplanner select outputs/orc_mechanic_lora_plan/records.json --id core-character_lora_core-0001 --field prompt
```

Run plan QA:

```powershell
python -m shotplanner qa outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner qa outputs/orc_mechanic_lora_plan/records.json --field json
python -m shotplanner qa outputs/orc_mechanic_lora_plan/records.json --pack expressions --code repeated_prompt_words
python -m shotplanner qa outputs/orc_mechanic_lora_plan/records.json --severity warning
python -m shotplanner export-qa outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/qa_findings
python -m shotplanner export-qa outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/expression_qa_findings --pack expressions --code repeated_prompt_words
```

Build revision worklists and subset plans:

```powershell
python -m shotplanner export-revisions outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/revision_worklist
python -m shotplanner export-revisions outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/expression_revisions --pack expressions --qa-code repeated_prompt_words
python -m shotplanner revision-summary outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner revision-summary outputs/orc_mechanic_lora_plan/records.json --qa-code repeated_prompt_words --field json
python -m shotplanner copy-records outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/expression_revision_records --pack expressions --qa-code repeated_prompt_words
python -m shotplanner copy-records outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/selected_records --selected true
```

Track generated result files:

```powershell
python -m shotplanner audit-results outputs/orc_mechanic_lora_plan/records.json
python -m shotplanner audit-results outputs/orc_mechanic_lora_plan/records.json --field missing
python -m shotplanner audit-results outputs/orc_mechanic_lora_plan/records.json --pack expressions --has-results false
python -m shotplanner audit-results outputs/orc_mechanic_lora_plan/records.json --result-status needs_regen
python -m shotplanner export-missing-results outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/missing_result_worklist
python -m shotplanner export-missing-results outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/expression_missing_results --pack expressions
python -m shotplanner attach-result outputs/orc_mechanic_lora_plan/records.json --id core-character_lora_core-0001 --path outputs/images/core_0001.png --status accepted --notes "best face consistency"
python -m shotplanner select outputs/orc_mechanic_lora_plan/records.json --id core-character_lora_core-0001 --field result_refs
```

Mark and review records:

```powershell
python -m shotplanner mark outputs/orc_mechanic_lora_plan/records.json --id core-character_lora_core-0001 --status selected --selected true --notes "best identity shot"
python -m shotplanner review outputs/orc_mechanic_lora_plan/records.json --status selected
python -m shotplanner review outputs/orc_mechanic_lora_plan/records.json --status selected --field ids
```

Export prompt text files from a finished plan:

```powershell
python -m shotplanner export-prompts outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/prompt_export
python -m shotplanner export-prompts outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/prompt_export --include-negative
python -m shotplanner export-prompts outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/expression_prompt_export --pack expressions
python -m shotplanner export-prompts outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/side_view_prompt_export --shot-type left_side_view
python -m shotplanner export-prompts outputs/orc_mechanic_lora_plan/records.json --out outputs/orc_mechanic_lora_plan/selected_prompt_export --review-status selected --selected true
```

## Command families

- Build: `build`, `build-character-lora`
- Inspect: `inspect`, `stats`, `validate`, `recommend`, `select`, `list`
- Review: `mark`, `review`
- QA: `qa`, `export-qa`
- Results: `attach-result`, `audit-results`, `export-missing-results`
- Revision: `revision-summary`, `export-revisions`, `copy-records`
- Prompt handoff: `export-prompts`

## CLI reference

| Command | Purpose | Main inputs | Outputs | Notes |
| --- | --- | --- | --- | --- |
| `build` | Build a single shotlist batch. | `--subject`, `--mode` or `--preset`, optional `--config`, `--style-profile`, `--palette`, `--out`, and `--count`. | Standard build files in the output folder. | Config files are supported; explicit flags override matching config fields. |
| `build-character-lora` | Build a multi-pack character LoRA planning set. | `--subject`, character bible fields, pack counts, optional `--config`, `--style-profile`, `--palette`, and `--out`. | Standard build files in the output folder. | Pack defaults can be overridden from flags or config. |
| `list` | Show available built-in planning resources. | Resource name such as `modes`, `presets`, `palettes`, `styles`, `templates`, or `packs`. | Text list. | Read-only. |
| `inspect` | Preview a finished `records.json`. | Path to `records.json`. | Compact record summary. | Read-only. |
| `stats` | Summarize counts from a finished plan. | Path to `records.json`. | Count tables for plan metadata, review state, style, and palette use. | Read-only. |
| `validate` | Check a finished plan before handoff. | Path to `records.json`. | Validation report. | Exits nonzero for blocking validation errors; coverage warnings can be informational. |
| `recommend` | Print LoRA coverage additions. | Path to `records.json`. | Recommended additional shot counts. | Most useful for character LoRA plans. |
| `select` | Print one record or one field from a record. | Path to `records.json`, plus `--index` or `--id`, optional `--field`. | Selected record data. | Read-only. |
| `mark` | Update human review state on a record. | Path to `records.json`, selector, and review fields such as status, notes, selected, or needs-regen. | Updated review data. | Mutates `records.json`. |
| `review` | List records by review state and filters. | Path to `records.json`, optional review and planning filters. | Summary, ids, prompts, or JSON. | Read-only. |
| `qa` | Run local rule-based quality checks. | Path to `records.json`, optional planning filters. | QA summary or JSON. | Read-only. |
| `export-qa` | Write QA findings for handoff. | Path to `records.json`, `--out`, optional filters. | `qa_findings.json` and `qa_findings.csv`. | Derived helper files; source records stay unchanged. |
| `revision-summary` | Summarize records needing revision. | Path to `records.json`, optional review and QA filters. | Revision summary or JSON. | Combines review state and QA findings. |
| `export-revisions` | Write revision worklists. | Path to `records.json`, `--out`, optional filters. | `revision_worklist.json` and `revision_worklist.csv`. | Derived helper files; source records stay unchanged. |
| `copy-records` | Copy a filtered record subset into a new plan folder. | Path to `records.json`, `--out`, optional filters. | New `records.json` and `subset_manifest.json`. | Does not alter the source plan. |
| `attach-result` | Attach a generated result reference to a planned record. | Path to `records.json`, selector, `--path`, optional status and notes. | Updated result reference. | Mutates `records.json`. |
| `audit-results` | Check generated-result coverage. | Path to `records.json`, optional result filters. | Result coverage summary, missing list, or JSON. | Reads `result_refs`. |
| `export-missing-results` | Write worklists for records with no result files attached. | Path to `records.json`, `--out`, optional filters. | `missing_results.json` and `missing_results.csv`. | Derived helper files; source records stay unchanged. |
| `export-prompts` | Export prompt text files from a finished plan. | Path to `records.json`, `--out`, optional filters and `--include-negative`. | Prompt files, optional negative prompt files, and `prompt_manifest.json`. | Text handoff for downstream wrappers or manual generation. |

## Character bible

For character LoRA planning, add stable identity details that should appear in every record:

- `--identity`
- `--face`
- `--hair`
- `--body`
- `--outfit`
- `--accessories`
- `--must-keep`
- `--avoid`

These fields are stored as `character_bible`, injected into prompt text as an identity anchor, included in `records.json`, and summarized in `preview.html`.

For repeatable builds, put `subject`, `character_bible`, `packs`, `preset`, `style`, `style_profile`, `count`, and `out` fields in a JSON config file and pass it with `--config`.

## Style profiles

Style profiles are reusable planning modifiers. They add a consistent prompt phrase and matching negative guidance without changing shot coverage.

- `clean_reference`
- `cinematic_realism`
- `storybook_illustration`
- `technical_sheet`

Style intensity controls how strongly the profile enters the prompt:

- `light`
- `standard`
- `strong`

For multi-pack character LoRA configs, `style_profile` is the default and `pack_style_profiles` can override specific packs:

```json
{
  "style_profile": "clean_reference",
  "style_intensity": "standard",
  "pack_style_profiles": {
    "turnaround": "technical_sheet",
    "costume_details": "technical_sheet",
    "environment": "cinematic_realism"
  },
  "pack_style_intensity": {
    "turnaround": "light",
    "costume_details": "light",
    "environment": "strong"
  }
}
```

## Static planning palettes

Builds assign a static planning palette to every record. You can use the mode default or choose one with `--palette`.

These palettes are lightweight planning hints, not palette extraction. `shotplanner` stays focused on shot coverage, bbox planning, and reusable prompt records.

- `character_reference`
- `technical_neutral`
- `product_studio`
- `cinematic_poster`
- `watercolor_fantasy`
- `monochrome_ink`

## Presets

- `character_lora`: `mode=character_lora`, `count=50`
- `character_lora_core`: `mode=character_lora_core`, `count=30`
- `character_lora_turnaround`: `mode=character_lora_turnaround`, `count=24`
- `character_lora_expressions`: `mode=character_lora_expressions`, `count=20`
- `character_lora_costume_details`: `mode=character_lora_costume_details`, `count=20`
- `character_lora_action`: `mode=character_lora_action`, `count=24`
- `character_lora_environment`: `mode=character_lora_environment`, `count=18`
- `three_d_reference`: `mode=three_d_reference`, `count=30`
- `product_sheet`: `mode=product_sheet`, `count=24`
- `poster`: `mode=poster`, `count=12`

## Outputs

Each build writes:

- `records.json`: full structured `PromptRecord` data for downstream tools.
- `downstream_handoff.json`: optional downstream records with base prompt JSON, style fragments, element JSON strings, and palette JSON.
- `batch.csv`: human-friendly batch planning table.
- `review.csv`: compact planning table for sorting large plans by pack, shot type, template, palette, and prompt preview.
- `report.md`: summary of counts, templates, files, and limitations.
- `preview.html`: offline browser preview with search, filters, prompt text, bbox sketches, and structured JSON.

The `export-prompts` command can also turn a finished `records.json` into a `prompts/` folder of one `.txt` file per record. With `--include-negative`, it also writes `negative_prompts/`. Use `--pack`, `--mode`, `--shot-type`, or `--template` to export only part of a plan. A `prompt_manifest.json` file maps every exported file back to its record id, index, pack, shot type, angle, mode, and template.

### Output stability

For v1.0, all current outputs stay in the workflow.

- Canonical: `records.json`.
- Build review helpers: `batch.csv`, `review.csv`, `report.md`, `preview.html`.
- Optional downstream handoff: `downstream_handoff.json`.
- Prompt handoff: `prompts/`, `negative_prompts/`, `prompt_manifest.json`.
- Result audit helpers: `missing_results.json`, `missing_results.csv`.
- QA helpers: `qa_findings.json`, `qa_findings.csv`.
- Revision helpers: `revision_worklist.json`, `revision_worklist.csv`, `subset_manifest.json`.

Downstream tools should treat `records.json` as authoritative. Other files are derived helpers that can be regenerated from a finished plan or command-specific export.

Use `validate` before handoff to check for duplicate ids, missing prompt fields, broken bbox layouts, missing generated JSON, and character LoRA coverage warnings.

Use `stats` to quickly see pack, mode, shot type, template, aspect ratio, and palette counts before filtering or exporting prompts.

`stats` and `report.md` also summarize style profile/intensity counts, which helps confirm multi-pack style overrides.

Use `mark` to add human review state to a record after generation. Review fields are written to the record's `review` object.

Use `review` to list records by review status, selected flag, regeneration flag, pack, mode, shot type, or template.

`review --field` can print `summary`, `ids`, `prompts`, or `json`.

Review filters can be combined with pack, mode, shot type, and template filters when exporting prompts.

`stats` and `report.md` summarize review status and flags, including unreviewed records.

For `character_lora`, the report and preview also show LoRA coverage counts for portraits, full body, front/side/back views, three-quarter views, expressions, costume details, action poses, environments, and neutral references.

When coverage is missing or thin, `report.md` includes add-count recommendations with example shot types to strengthen the plan.

Use `recommend` to print only those add-count recommendations from an existing `records.json`.

Focused character LoRA packs use specialized bbox templates for expression strips, head and full-body turnarounds, hands, props, materials, costume layers, and accessory callouts.

The preview supports search plus pack, shot type, and template filters for reviewing larger multi-pack plans.

## Modes

- `character_lora`
- `character_lora_core`
- `character_lora_turnaround`
- `character_lora_expressions`
- `character_lora_costume_details`
- `character_lora_action`
- `character_lora_environment`
- `three_d_reference`
- `product_sheet`
- `poster`

## Future integration

The record format is designed so downstream wrappers can load `records.json`, select a record by index, and output prompt text, negative prompt, bbox layout, color palette, full Ideogram-style JSON, and metadata.

## License

MIT. See `LICENSE`.

Not included in v1.0: GUI, image generation, Ideogram API calls, ML analysis, color palette extraction from images, database, or web app.
