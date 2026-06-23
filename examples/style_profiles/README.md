# Style Profiles Example

This example shows v0.4 style controls on a small multi-pack character LoRA plan.

It uses:

- `style_profile` as the global default.
- `style_intensity` as the global default strength.
- `pack_style_profiles` to make turnaround and costume detail packs more technical.
- `pack_style_intensity` to make environment shots more cinematic while keeping technical packs subtle.

Build:

```powershell
python -m shotplanner build-character-lora --config examples/style_profiles/style_profile_config.json
```

Review style counts:

```powershell
python -m shotplanner stats examples/style_profiles/generated/records.json
```
