# shotplanner build report

- Subject: moon temple knight with silver mask, blue cloak, crystal spear
- Mode: character_lora_multipack
- Count: 20

## Templates used
- accessory_callout_sheet: 1
- centered_full_body: 9
- centered_portrait: 3
- costume_layer_detail_grid: 1
- expression_strip: 1
- material_swatches_grid: 1
- wide_environment: 4

## Color palettes
- character_reference: 16
- technical_neutral: 4

## Style profiles
- cinematic_realism / strong: 3
- clean_reference / standard: 10
- technical_sheet / light: 7

## Review summary
- unreviewed: 20

## Review flags
- None

## Shot type counts
- accessory_detail: 1
- action_pose: 1
- back_view: 1
- costume_detail: 1
- environment: 1
- expression: 1
- expression_smile: 1
- front_view: 1
- full_body: 1
- left_side_view: 1
- material_detail: 1
- portrait: 2
- right_side_view: 1
- side_view: 1
- street_context: 1
- three_quarter: 1
- turning_pose: 1
- walking_pose: 1
- workshop_context: 1

## Angle counts
- back_view: 1
- detail_closeups: 1
- dynamic_front: 1
- dynamic_three_quarter: 2
- front_view: 4
- left_side_view: 2
- macro_details: 2
- right_side_view: 1
- soft_smile: 1
- three_quarter_front: 1
- varied_expressions: 1
- wide_context: 3

## Aspect ratio counts
- 16:9: 6
- 1:1: 1
- 2:3: 9
- 3:4: 3
- 4:3: 1

## Character LoRA coverage
- Status: needs_review
- Decision: This character lora multipack plan is missing required coverage: neutral reference.
- Recommended next action: Add records or increase pack counts before using this as a real LoRA planning set.
- Required coverage for this plan: portrait, full body, front view, three quarter, side view, back view, action pose, expression, costume detail, environment, neutral reference
- Coverage profile: Complete multi-pack character LoRA plan.

### Coverage counts
- portrait: 2
- full body: 1
- front view: 4
- three quarter: 1
- side view: 3
- back view: 1
- action pose: 3
- expression: 2
- costume detail: 3
- environment: 3
- neutral reference: 0
- Missing: neutral reference
- Thin coverage: full body, three quarter, back view

### Add-count recommendations
- Add at least 1 full-body record. Example shot types: full_body.
- Add at least 1 three-quarter reference record. Example shot types: three_quarter_front or three_quarter_back.
- Add at least 1 back-view reference record. Example shot types: back_view.
- Add at least 2 neutral reference records. Example shot types: neutral_reference, turnaround_sheet, or head_turnaround.

## Files written
- records.json
- downstream_handoff.json
- batch.csv
- review.csv
- report.md
- preview.html

## Known limitations
- This tool does not generate images.
- It does not call the Ideogram API.
- Color palette data uses static planning palettes, not image analysis or extraction.
- Downstream handoff is file-based; it does not install or run external wrappers.
