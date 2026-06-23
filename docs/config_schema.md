# Config File Schema

`shotplanner` accepts JSON config files with `--config`.

Config files are optional. Explicit CLI flags override config values.

## Shared Fields

Supported fields:

- `subject`: string.
- `preset`: string. Any build preset.
- `mode`: string. Any shotlist mode.
- `style`: string.
- `style_profile`: string. Named reusable style profile.
- `style_intensity`: string. One of `light`, `standard`, or `strong`.
- `count`: integer.
- `palette`: string. Static planning palette name.
- `out`: string. Output directory.
- `character_bible`: object.

`subject` is required unless provided explicitly on the command line.

## Character Bible

`character_bible` may include:

- `identity`
- `face`
- `hair`
- `body`
- `outfit`
- `accessories`
- `must_keep`
- `avoid`

Example:

```json
{
  "subject": "orc mechanic woman with red braid, brass goggles, patched leather coat",
  "character_bible": {
    "identity": "same orc mechanic woman in every shot",
    "hair": "single red braid",
    "outfit": "patched leather coat, oil-stained work gloves",
    "accessories": "brass goggles, tool belt",
    "must_keep": "green skin, tusks, red braid, brass goggles",
    "avoid": "different face, different age, missing goggles"
  },
  "out": "outputs/orc_mechanic_lora_plan"
}
```

## Single Build Config

Used with:

```powershell
python -m shotplanner build --config examples/product_sheet_config.json
```

Example:

```json
{
  "subject": "brass clockwork resin miniature kit with removable wings",
  "preset": "product_sheet",
  "style": "clean product concept sheet, studio lighting, readable materials",
  "style_profile": "technical_sheet",
  "style_intensity": "standard",
  "count": 12,
  "out": "outputs/brass_clockwork_product_sheet"
}
```

## Multi-Pack Character LoRA Config

Used with:

```powershell
python -m shotplanner build-character-lora --config examples/character_lora_multipack_config.json
```

Additional field:

- `packs`: object mapping pack names to integer counts.
- `pack_style_profiles`: object mapping pack names to style profile names.
- `pack_style_intensity`: object mapping pack names to style intensity names.

Supported pack keys:

- `core`
- `turnaround`
- `expressions`
- `costume_details`
- `action`
- `environment`

Example:

```json
{
  "subject": "orc mechanic woman with red braid, brass goggles, patched leather coat",
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
  },
  "character_bible": {
    "identity": "same orc mechanic woman in every shot",
    "hair": "single red braid"
  },
  "packs": {
    "core": 30,
    "turnaround": 24,
    "expressions": 20,
    "costume_details": 20,
    "action": 24,
    "environment": 18
  },
  "out": "outputs/orc_mechanic_lora_plan"
}
```

## Validation Behavior

- Missing config file: command exits with an error.
- Invalid JSON: command exits with an error.
- Config root must be a JSON object.
- `character_bible` must be an object when present.
- `packs` must be an object when present.
- `pack_style_profiles` must be an object when present.
- `pack_style_intensity` must be an object when present.
