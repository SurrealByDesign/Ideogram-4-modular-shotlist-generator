# Examples

These examples show small, readable `shotplanner` builds. They are intentionally short so the record shape is easy to inspect.

Each example includes:

- `command.txt`: the command used to generate the sample.
- `records.sample.json`: a trimmed records export.
- `report.sample.md`: the generated report for the sample batch.
- `character_bible.json`: included for character LoRA examples.

`workflow_handoff/` shows how to export prompt text files from a finished `records.json` plan.

`style_profiles/` shows how to use global and per-pack style profiles and intensity controls.

`review_workflow/` shows how to mark, list, and export reviewed records.

`stable_cli_workflow/` shows the v1.0 command loop from build through QA, revision, subset copying, and prompt export.

Only minimal stable workflow artifacts are checked in. Regenerate full `generated/` folders locally when you want to inspect previews, CSVs, prompt text files, or other derived handoff files.

The examples are documentation fixtures, not generated image results.
