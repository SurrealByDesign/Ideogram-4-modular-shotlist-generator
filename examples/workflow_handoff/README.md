# Workflow Handoff Example

Use this after a plan has already been built and reviewed.

Export prompts:

```powershell
python -m shotplanner export-prompts examples/stable_cli_workflow/generated/records.json --out outputs/workflow_prompt_export
```

Export prompts and negative prompts:

```powershell
python -m shotplanner export-prompts examples/stable_cli_workflow/generated/records.json --out outputs/workflow_prompt_export --include-negative
```

Export only one pack:

```powershell
python -m shotplanner export-prompts examples/stable_cli_workflow/generated/records.json --out outputs/workflow_expression_prompt_export --pack expressions --include-negative
```

Export only one shot type:

```powershell
python -m shotplanner export-prompts examples/stable_cli_workflow/generated/records.json --out outputs/workflow_side_view_prompt_export --shot-type left_side_view
```

The command writes:

- `prompts/`: one prompt text file per record.
- `negative_prompts/`: negative prompt files when `--include-negative` is used.
- `prompt_manifest.json`: an index that maps exported files back to record ids, packs, shot types, and angles.
