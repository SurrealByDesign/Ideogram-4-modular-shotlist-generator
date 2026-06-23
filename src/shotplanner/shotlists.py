from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShotSpec:
    shot_type: str
    angle: str
    template: str


SHOTLISTS: dict[str, list[ShotSpec]] = {
    "character_lora": [
        ShotSpec("portrait", "front_view", "centered_portrait"),
        ShotSpec("full_body", "front_view", "centered_full_body"),
        ShotSpec("three_quarter", "three_quarter_front", "centered_full_body"),
        ShotSpec("side_view", "left_side_view", "centered_full_body"),
        ShotSpec("back_view", "back_view", "centered_full_body"),
        ShotSpec("action_pose", "dynamic_three_quarter", "wide_environment"),
        ShotSpec("expression", "varied_expressions", "expression_grid"),
        ShotSpec("costume_detail", "detail_closeups", "detail_grid"),
        ShotSpec("environment", "wide_context", "wide_environment"),
        ShotSpec("neutral_reference", "plain_background", "character_reference_sheet"),
    ],
    "character_lora_core": [
        ShotSpec("portrait", "front_view", "centered_portrait"),
        ShotSpec("full_body", "front_view", "centered_full_body"),
        ShotSpec("three_quarter", "three_quarter_front", "centered_full_body"),
        ShotSpec("side_view", "left_side_view", "centered_full_body"),
        ShotSpec("back_view", "back_view", "centered_full_body"),
        ShotSpec("neutral_reference", "plain_background", "character_reference_sheet"),
    ],
    "character_lora_turnaround": [
        ShotSpec("front_view", "front_view", "centered_full_body"),
        ShotSpec("left_side_view", "left_side_view", "centered_full_body"),
        ShotSpec("right_side_view", "right_side_view", "centered_full_body"),
        ShotSpec("back_view", "back_view", "centered_full_body"),
        ShotSpec("three_quarter_front", "three_quarter_front", "centered_full_body"),
        ShotSpec("three_quarter_back", "three_quarter_back", "centered_full_body"),
        ShotSpec("turnaround_sheet", "front_side_back", "full_body_turnaround_four_panel"),
        ShotSpec("head_turnaround", "front_side_back", "head_turnaround_strip"),
        ShotSpec("neutral_reference", "plain_background", "character_reference_sheet"),
    ],
    "character_lora_expressions": [
        ShotSpec("portrait", "front_view", "centered_portrait"),
        ShotSpec("expression", "varied_expressions", "expression_strip"),
        ShotSpec("expression_smile", "soft_smile", "centered_portrait"),
        ShotSpec("expression_serious", "serious_expression", "centered_portrait"),
        ShotSpec("expression_surprised", "surprised_expression", "centered_portrait"),
        ShotSpec("expression_angry", "angry_expression", "centered_portrait"),
        ShotSpec("expression_profile", "three_quarter_front", "head_turnaround_strip"),
    ],
    "character_lora_costume_details": [
        ShotSpec("costume_detail", "detail_closeups", "costume_layer_detail_grid"),
        ShotSpec("accessory_detail", "macro_details", "accessory_callout_sheet"),
        ShotSpec("material_detail", "macro_details", "material_swatches_grid"),
        ShotSpec("hands_or_gloves", "detail_closeups", "hands_detail_pair"),
        ShotSpec("footwear_detail", "detail_closeups", "costume_layer_detail_grid"),
        ShotSpec("prop_detail", "macro_details", "prop_detail_triptych"),
        ShotSpec("full_body", "front_view", "centered_full_body"),
    ],
    "character_lora_action": [
        ShotSpec("action_pose", "dynamic_three_quarter", "wide_environment"),
        ShotSpec("walking_pose", "dynamic_front", "centered_full_body"),
        ShotSpec("turning_pose", "dynamic_three_quarter", "centered_full_body"),
        ShotSpec("reaching_pose", "dynamic_front", "centered_full_body"),
        ShotSpec("crouching_pose", "dynamic_three_quarter", "wide_environment"),
        ShotSpec("hero_pose", "dramatic_front", "centered_full_body"),
        ShotSpec("neutral_reference", "plain_background", "character_reference_sheet"),
    ],
    "character_lora_environment": [
        ShotSpec("environment", "wide_context", "wide_environment"),
        ShotSpec("workshop_context", "wide_context", "wide_environment"),
        ShotSpec("street_context", "wide_context", "wide_environment"),
        ShotSpec("interior_context", "wide_context", "wide_environment"),
        ShotSpec("full_body", "front_view", "centered_full_body"),
        ShotSpec("portrait", "front_view", "centered_portrait"),
        ShotSpec("neutral_reference", "plain_background", "character_reference_sheet"),
    ],
    "three_d_reference": [
        ShotSpec("front_view", "front_view", "centered_full_body"),
        ShotSpec("left_side_view", "left_side_view", "centered_full_body"),
        ShotSpec("right_side_view", "right_side_view", "centered_full_body"),
        ShotSpec("back_view", "back_view", "centered_full_body"),
        ShotSpec("three_quarter_front", "three_quarter_front", "centered_full_body"),
        ShotSpec("three_quarter_back", "three_quarter_back", "centered_full_body"),
        ShotSpec("neutral_pose", "orthographic_front", "centered_full_body"),
        ShotSpec("detail_closeups", "macro_details", "detail_grid"),
        ShotSpec("plain_background", "front_view", "centered_full_body"),
        ShotSpec("turnaround_sheet", "front_side_back", "full_body_turnaround_four_panel"),
    ],
    "product_sheet": [
        ShotSpec("centered_product", "front_view", "product_centered"),
        ShotSpec("front_view", "front_view", "product_centered"),
        ShotSpec("side_view", "side_view", "product_centered"),
        ShotSpec("back_view", "back_view", "product_centered"),
        ShotSpec("detail_closeup", "macro_detail", "product_detail_pair"),
        ShotSpec("packaging_style", "three_quarter_front", "product_detail_pair"),
        ShotSpec("white_background", "front_view", "product_centered"),
        ShotSpec("poster_layout", "hero_layout", "poster_title_bottom"),
    ],
    "poster": [
        ShotSpec("hero_subject", "dramatic_front", "poster_title_bottom"),
        ShotSpec("large_title_area", "graphic_layout", "poster_title_top"),
        ShotSpec("background_scene", "wide_context", "wide_environment"),
        ShotSpec("supporting_elements", "layered_composition", "poster_title_bottom"),
        ShotSpec("bottom_text_area", "graphic_layout", "poster_title_bottom"),
        ShotSpec("logo_safe_area", "clean_layout", "poster_title_top"),
        ShotSpec("dramatic_lighting", "cinematic_front", "poster_title_bottom"),
    ],
}

MODES = sorted(SHOTLISTS)


def get_mode_specs(mode: str) -> list[ShotSpec]:
    if mode not in SHOTLISTS:
        valid = ", ".join(sorted(SHOTLISTS))
        raise ValueError(f"unknown mode '{mode}'. Choose one of: {valid}")
    return SHOTLISTS[mode]
