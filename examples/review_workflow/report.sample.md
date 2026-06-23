# shotplanner build report

- Subject: clockwork ranger with bronze mask, green cloak, folding bow
- Mode: character_lora_multipack
- Count: 14

## Templates used
- accessory_callout_sheet: 1
- centered_full_body: 6
- centered_portrait: 2
- costume_layer_detail_grid: 1
- expression_strip: 1
- wide_environment: 3

## Color palettes
- character_reference: 12
- technical_neutral: 2

## Style profiles
- clean_reference / standard: 14

## Review summary
- needs_regen: 1
- selected: 1
- unreviewed: 12

## Review flags
- needs_regen=true: 1
- selected=true: 1

## Shot type counts
- accessory_detail: 1
- action_pose: 1
- costume_detail: 1
- environment: 1
- expression: 1
- front_view: 1
- full_body: 1
- left_side_view: 1
- portrait: 2
- side_view: 1
- three_quarter: 1
- walking_pose: 1
- workshop_context: 1

## Angle counts
- detail_closeups: 1
- dynamic_front: 1
- dynamic_three_quarter: 1
- front_view: 4
- left_side_view: 2
- macro_details: 1
- three_quarter_front: 1
- varied_expressions: 1
- wide_context: 2

## Aspect ratio counts
- 16:9: 5
- 2:3: 6
- 3:4: 2
- 4:3: 1

## Character LoRA coverage
- Status: needs_review
- Decision: This character lora multipack plan is missing required coverage: back view, neutral reference.
- Recommended next action: Add records or increase pack counts before using this as a real LoRA planning set.
- Required coverage for this plan: portrait, full body, front view, three quarter, side view, back view, action pose, expression, costume detail, environment, neutral reference
- Coverage profile: Complete multi-pack character LoRA plan.

### Coverage counts
- portrait: 2
- full body: 1
- front view: 4
- three quarter: 1
- side view: 2
- back view: 0
- action pose: 2
- expression: 1
- costume detail: 2
- environment: 2
- neutral reference: 0
- Missing: back view, neutral reference
- Thin coverage: full body, three quarter, expression

### Add-count recommendations
- Add at least 1 full-body record. Example shot types: full_body.
- Add at least 1 three-quarter reference record. Example shot types: three_quarter_front or three_quarter_back.
- Add at least 2 back-view reference records. Example shot types: back_view.
- Add at least 1 expression record. Example shot types: expression_smile, expression_serious, or expression_surprised.
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
