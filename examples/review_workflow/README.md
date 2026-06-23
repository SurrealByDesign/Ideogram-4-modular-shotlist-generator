# Review Workflow Example

This example shows how to annotate a generated plan after review.

Build the plan:

```powershell
python -m shotplanner build-character-lora --config examples/review_workflow/review_workflow_config.json
```

Mark records:

```powershell
python -m shotplanner mark examples/review_workflow/generated/records.json --id core-character_lora_core-0001 --status selected --selected true --notes "best identity anchor"
python -m shotplanner mark examples/review_workflow/generated/records.json --id core-character_lora_core-0002 --status needs_regen --needs-regen true --notes "retry full body proportions"
```

List reviewed records:

```powershell
python -m shotplanner review examples/review_workflow/generated/records.json --status selected
python -m shotplanner review examples/review_workflow/generated/records.json --needs-regen true --field json
```

Export only selected prompts:

```powershell
python -m shotplanner export-prompts examples/review_workflow/generated/records.json --out examples/review_workflow/generated/selected_prompt_export --review-status selected --selected true
```
