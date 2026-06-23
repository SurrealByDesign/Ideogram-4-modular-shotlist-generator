# Release Checklist

Use this checklist before tagging a release.

## Pre-tag checks

- Confirm `README.md`, `CHANGELOG.md`, `pyproject.toml`, and `src/shotplanner/__init__.py` show the same version.
- Run the test suite:

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m unittest discover -s tests
```

- Run the quickstart read-only checks:

```powershell
python -m shotplanner inspect examples/stable_cli_workflow/generated/records.json
python -m shotplanner stats examples/stable_cli_workflow/generated/records.json
```

- Build a wheel in a temporary folder and confirm the package contains only `shotplanner` modules, metadata, entry point data, and `LICENSE`.
- Confirm generated folders are absent from the release tree: `build/`, `dist/`, `outputs/`, `*.egg-info/`, `__pycache__/`.
- Confirm private planning files are absent from the release tree.

## Tag

- Commit the release changes.
- Create a version tag, such as `v1.0.0`.
- Push the commit and tag.

## GitHub release notes

Use `RELEASE_NOTES_1.0.0.md` as the GitHub release note draft, with `CHANGELOG.md` as the detailed change history.
