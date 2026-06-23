# Stable CLI Workflow Example

This example shows the intended command-line loop for a character LoRA shot plan.

It stays local and file-based:

1. Build a multi-pack plan.
2. Inspect and validate the generated records.
3. Run QA checks.
4. Export QA findings.
5. Summarize and export revision work.
6. Copy a focused revision subset.
7. Export prompts for handoff.

Run the commands in `command.txt` from the project root.

The example uses `stable_cli_workflow_config.json` and writes to `examples/stable_cli_workflow/generated`.

The copied revision subset is expected to validate structurally, but may show coverage warnings because it is intentionally only a small focused slice of the full plan.
