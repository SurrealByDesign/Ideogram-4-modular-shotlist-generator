from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bbox import validate_layout


LAYOUT_TEMPLATES: dict[str, dict[str, Any]] = {
    "centered_portrait": {
        "name": "centered_portrait",
        "aspect_ratio": "3:4",
        "elements": [{"type": "obj", "bbox": [90, 260, 760, 740], "desc": "head and shoulders portrait, centered"}],
    },
    "centered_full_body": {
        "name": "centered_full_body",
        "aspect_ratio": "2:3",
        "elements": [{"type": "obj", "bbox": [80, 320, 940, 680], "desc": "main character, full body, centered"}],
    },
    "wide_environment": {
        "name": "wide_environment",
        "aspect_ratio": "16:9",
        "elements": [{"type": "obj", "bbox": [360, 430, 820, 570], "desc": "subject within a wide environment"}],
    },
    "three_panel_turnaround": {
        "name": "three_panel_turnaround",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [110, 80, 900, 290], "desc": "front view panel"},
            {"type": "obj", "bbox": [110, 395, 900, 605], "desc": "side view panel"},
            {"type": "obj", "bbox": [110, 710, 900, 920], "desc": "back view panel"},
        ],
    },
    "front_side_back_sheet": {
        "name": "front_side_back_sheet",
        "aspect_ratio": "4:3",
        "elements": [
            {"type": "obj", "bbox": [140, 80, 920, 300], "desc": "front view"},
            {"type": "obj", "bbox": [140, 390, 920, 610], "desc": "side view"},
            {"type": "obj", "bbox": [140, 700, 920, 920], "desc": "back view"},
        ],
    },
    "expression_grid": {
        "name": "expression_grid",
        "aspect_ratio": "1:1",
        "elements": [
            {"type": "obj", "bbox": [80, 80, 430, 430], "desc": "expression panel one"},
            {"type": "obj", "bbox": [80, 570, 430, 920], "desc": "expression panel two"},
            {"type": "obj", "bbox": [570, 80, 920, 430], "desc": "expression panel three"},
            {"type": "obj", "bbox": [570, 570, 920, 920], "desc": "expression panel four"},
        ],
    },
    "detail_grid": {
        "name": "detail_grid",
        "aspect_ratio": "1:1",
        "elements": [
            {"type": "obj", "bbox": [80, 80, 450, 450], "desc": "material or costume detail"},
            {"type": "obj", "bbox": [80, 550, 450, 920], "desc": "prop or accessory detail"},
            {"type": "obj", "bbox": [550, 80, 920, 450], "desc": "texture or trim detail"},
            {"type": "obj", "bbox": [550, 550, 920, 920], "desc": "secondary detail"},
        ],
    },
    "poster_title_top": {
        "name": "poster_title_top",
        "aspect_ratio": "2:3",
        "elements": [
            {"type": "text", "bbox": [40, 90, 210, 910], "desc": "large title area at top"},
            {"type": "obj", "bbox": [260, 180, 900, 820], "desc": "hero subject below title"},
        ],
    },
    "poster_title_bottom": {
        "name": "poster_title_bottom",
        "aspect_ratio": "2:3",
        "elements": [
            {"type": "obj", "bbox": [70, 170, 720, 830], "desc": "hero subject above title"},
            {"type": "text", "bbox": [760, 90, 950, 910], "desc": "large title area at bottom"},
        ],
    },
    "product_centered": {
        "name": "product_centered",
        "aspect_ratio": "1:1",
        "elements": [{"type": "obj", "bbox": [180, 180, 820, 820], "desc": "centered product on clean background"}],
    },
    "product_detail_pair": {
        "name": "product_detail_pair",
        "aspect_ratio": "4:3",
        "elements": [
            {"type": "obj", "bbox": [120, 90, 880, 480], "desc": "primary product view"},
            {"type": "obj", "bbox": [180, 570, 820, 930], "desc": "detail closeup view"},
        ],
    },
    "character_reference_sheet": {
        "name": "character_reference_sheet",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [110, 50, 890, 280], "desc": "main full body reference"},
            {"type": "obj", "bbox": [120, 340, 470, 590], "desc": "portrait closeup"},
            {"type": "obj", "bbox": [530, 340, 880, 590], "desc": "costume detail"},
            {"type": "obj", "bbox": [120, 660, 880, 950], "desc": "accessory and color notes"},
        ],
    },
    "hands_detail_pair": {
        "name": "hands_detail_pair",
        "aspect_ratio": "4:3",
        "elements": [
            {"type": "obj", "bbox": [150, 90, 850, 460], "desc": "left hand or glove detail"},
            {"type": "obj", "bbox": [150, 540, 850, 910], "desc": "right hand or tool grip detail"},
        ],
    },
    "prop_detail_triptych": {
        "name": "prop_detail_triptych",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [150, 60, 850, 300], "desc": "main prop full view"},
            {"type": "obj", "bbox": [180, 380, 820, 610], "desc": "prop mechanism or material closeup"},
            {"type": "obj", "bbox": [180, 690, 820, 940], "desc": "prop alternate angle or scale reference"},
        ],
    },
    "material_swatches_grid": {
        "name": "material_swatches_grid",
        "aspect_ratio": "1:1",
        "elements": [
            {"type": "obj", "bbox": [80, 80, 430, 430], "desc": "primary fabric or leather material"},
            {"type": "obj", "bbox": [80, 570, 430, 920], "desc": "metal or hardware material"},
            {"type": "obj", "bbox": [570, 80, 920, 430], "desc": "trim, stitching, or edge detail"},
            {"type": "obj", "bbox": [570, 570, 920, 920], "desc": "weathering, dirt, or wear pattern"},
        ],
    },
    "expression_strip": {
        "name": "expression_strip",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [180, 40, 820, 200], "desc": "neutral expression portrait"},
            {"type": "obj", "bbox": [180, 235, 820, 395], "desc": "smile expression portrait"},
            {"type": "obj", "bbox": [180, 430, 820, 590], "desc": "serious expression portrait"},
            {"type": "obj", "bbox": [180, 625, 820, 785], "desc": "surprised expression portrait"},
            {"type": "obj", "bbox": [180, 820, 820, 970], "desc": "angry expression portrait"},
        ],
    },
    "head_turnaround_strip": {
        "name": "head_turnaround_strip",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [170, 60, 830, 260], "desc": "front head view"},
            {"type": "obj", "bbox": [170, 290, 830, 490], "desc": "three-quarter head view"},
            {"type": "obj", "bbox": [170, 520, 830, 720], "desc": "side head view"},
            {"type": "obj", "bbox": [170, 750, 830, 950], "desc": "back head view"},
        ],
    },
    "full_body_turnaround_four_panel": {
        "name": "full_body_turnaround_four_panel",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [90, 50, 930, 240], "desc": "front full body"},
            {"type": "obj", "bbox": [90, 285, 930, 475], "desc": "left side full body"},
            {"type": "obj", "bbox": [90, 525, 930, 715], "desc": "right side full body"},
            {"type": "obj", "bbox": [90, 760, 930, 950], "desc": "back full body"},
        ],
    },
    "costume_layer_detail_grid": {
        "name": "costume_layer_detail_grid",
        "aspect_ratio": "4:3",
        "elements": [
            {"type": "obj", "bbox": [90, 80, 450, 450], "desc": "upper costume layers"},
            {"type": "obj", "bbox": [90, 550, 450, 920], "desc": "belt, waist, and fastening details"},
            {"type": "obj", "bbox": [540, 80, 910, 450], "desc": "lower costume layers"},
            {"type": "obj", "bbox": [540, 550, 910, 920], "desc": "wear, trim, patches, and repairs"},
        ],
    },
    "accessory_callout_sheet": {
        "name": "accessory_callout_sheet",
        "aspect_ratio": "16:9",
        "elements": [
            {"type": "obj", "bbox": [120, 70, 880, 360], "desc": "main accessory full view"},
            {"type": "obj", "bbox": [160, 430, 480, 620], "desc": "fastener or attachment closeup"},
            {"type": "obj", "bbox": [160, 680, 480, 900], "desc": "material or surface detail"},
            {"type": "obj", "bbox": [560, 430, 880, 900], "desc": "accessory worn on character"},
        ],
    },
}


def get_template(name: str) -> dict[str, Any]:
    if name not in LAYOUT_TEMPLATES:
        raise KeyError(f"unknown bbox template: {name}")
    return deepcopy(LAYOUT_TEMPLATES[name])


def validate_templates() -> None:
    for template in LAYOUT_TEMPLATES.values():
        validate_layout(template)
