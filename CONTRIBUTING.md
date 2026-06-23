# Contributing

Thanks for helping improve `shotplanner`.

## Development setup

Install the project in editable mode from the repository root:

```bash
python -m pip install -e .
```

Run the test suite before opening or merging changes:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Scope

`shotplanner` is a planning and prompt-record CLI. Keep changes focused on building, reviewing, validating, and exporting shotlist records. Image generation, model training, and UI wrappers should stay outside the core unless they are expressed as optional handoff data.

## Output files

Generated folders such as `outputs/`, Python caches, build artifacts, and local environment folders should not be committed. If you add a reusable example, place it under `examples/` and keep it small enough to review.

The canonical plan artifact is `records.json`. Derived files such as QA exports, revision worklists, prompt exports, reports, and previews should remain reproducible from that source data.

## Documentation

Update `README.md`, `CHANGELOG.md`, and the relevant file in `docs/` when a change affects commands, config fields, output shape, or user workflow.
