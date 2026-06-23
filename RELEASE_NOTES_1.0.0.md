# shotplanner v1.0.0

`shotplanner` is a local Python CLI for building modular shotlist records for character LoRA planning, product sheets, poster prompts, and reference workflows.

This release marks the stable CLI workflow. The canonical output is `records.json`; other files are reproducible helper outputs for review, QA, revision, prompt export, and downstream handoff.

## Highlights

- Stable command families for build, inspect, review, QA, result audit, revision, and prompt export workflows.
- Multi-pack character LoRA planning with character bible fields, pack coverage, and add-count recommendations.
- Local QA checks and exportable QA findings.
- Review state, selected-record workflows, revision worklists, and filtered record copying.
- Prompt export with optional negative prompt files and manifest metadata.
- Neutral `downstream_handoff.json` helper output for wrappers and manual workflows.
- Compact examples, schema docs, contribution notes, and release checklist.

## Install

```bash
python -m pip install -e .
```

## Verify

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m unittest discover -s tests
```

## Notes

- This tool does not generate images or call the Ideogram API.
- Generated folders such as `outputs/`, `build/`, and `*.egg-info/` should stay out of commits.
- Use `CHANGELOG.md` for the detailed change history.
