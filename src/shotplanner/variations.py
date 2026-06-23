from __future__ import annotations

from typing import Any

from .models import PromptRecord


MODE_VARIATIONS: dict[str, dict[str, list[str]]] = {
    "character_lora": {
        "pose": [
            "neutral balanced stance",
            "relaxed natural posture",
            "clear silhouette pose",
            "subtle characterful gesture",
            "stable dataset-friendly pose",
        ],
        "framing": [
            "clean character reference framing",
            "subject isolated with readable proportions",
            "center-weighted composition",
            "uncluttered full subject visibility",
            "consistent dataset framing",
        ],
        "lighting": [
            "soft even studio lighting",
            "diffuse daylight",
            "gentle rim light with clear facial detail",
            "balanced front lighting",
            "low-contrast reference lighting",
        ],
        "background": [
            "plain light gray background",
            "simple neutral backdrop",
            "minimal studio background",
            "low-distraction background",
            "clean reference-sheet backdrop",
        ],
        "detail": [
            "preserve distinctive costume shapes and materials",
            "emphasize face, silhouette, and key identifiers",
            "show readable outfit construction",
            "keep accessories consistent and recognizable",
            "prioritize repeatable character identity",
        ],
    },
    "three_d_reference": {
        "pose": [
            "orthographic neutral pose",
            "symmetrical standing pose",
            "model-sheet reference pose",
            "rigging-friendly relaxed stance",
            "stable proportions with clear limb separation",
        ],
        "framing": [
            "strict reference framing",
            "full object visibility without cropping",
            "alignment suitable for 3D modeling",
            "consistent scale across views",
            "technical turnaround composition",
        ],
        "lighting": [
            "flat neutral lighting",
            "soft shadowless studio lighting",
            "even material-revealing light",
            "low-drama reference lighting",
            "clear form-defining light",
        ],
        "background": [
            "plain white background",
            "neutral gray background",
            "no scenic environment",
            "simple matte backdrop",
            "technical reference background",
        ],
        "detail": [
            "show construction, contours, and material breaks",
            "avoid perspective distortion",
            "make front, side, and back forms comparable",
            "prioritize readable silhouette and volume",
            "include closeups for complex surface details",
        ],
    },
    "product_sheet": {
        "pose": [
            "stable product hero placement",
            "upright centered display",
            "slight three-quarter product turn",
            "catalog-ready arrangement",
            "precise prop presentation",
        ],
        "framing": [
            "clean commercial product framing",
            "ample margin around the product",
            "centered ecommerce composition",
            "detail-forward catalog crop",
            "clear shape-first presentation",
        ],
        "lighting": [
            "softbox product lighting",
            "clean studio highlights",
            "controlled reflections",
            "bright catalog lighting",
            "subtle shadow grounding the object",
        ],
        "background": [
            "white product background",
            "matte neutral sweep",
            "clean studio surface",
            "minimal catalog backdrop",
            "simple background with no clutter",
        ],
        "detail": [
            "emphasize materials, edges, and finish",
            "show scale and distinctive product features",
            "make surface texture easy to inspect",
            "keep branding or text areas readable if present",
            "prioritize product clarity over atmosphere",
        ],
    },
    "poster": {
        "pose": [
            "dramatic hero pose",
            "strong graphic silhouette",
            "cinematic central stance",
            "dynamic poster-ready action",
            "iconic cover-art presence",
        ],
        "framing": [
            "bold poster composition",
            "clear hierarchy between title area and subject",
            "designed negative space for typography",
            "layered foreground and background composition",
            "high-impact vertical layout",
        ],
        "lighting": [
            "dramatic cinematic lighting",
            "strong rim light and atmospheric depth",
            "high-contrast key art lighting",
            "moody directional light",
            "glowing poster-style highlights",
        ],
        "background": [
            "designed background scene",
            "atmospheric but readable backdrop",
            "graphic environment shapes",
            "layered scenic background",
            "composition with safe text zones",
        ],
        "detail": [
            "reserve clean readable areas for text",
            "support Ideogram text and layout strengths",
            "balance subject, title, and supporting elements",
            "keep typography zones uncluttered",
            "make the poster hierarchy obvious",
        ],
    },
}

SHOT_TYPE_HINTS: dict[str, str] = {
    "portrait": "focus on face, expression, hair, and upper costume identity",
    "full_body": "show the entire figure from head to toe without cropping",
    "three_quarter": "use a readable three-quarter view with visible depth",
    "side_view": "show a clean side silhouette",
    "back_view": "show rear design details clearly",
    "action_pose": "show motion while keeping the character identity readable",
    "expression": "show multiple clear expressions with consistent identity",
    "costume_detail": "focus on clothing, accessories, materials, and fasteners",
    "environment": "place the subject in a readable contextual environment",
    "neutral_reference": "keep the pose and background simple for reuse",
    "left_side_view": "show the left profile reference",
    "right_side_view": "show the right profile reference",
    "three_quarter_front": "show a readable three-quarter front view",
    "three_quarter_back": "show rear construction in a three-quarter view",
    "expression_smile": "show a natural smile while preserving the same face",
    "expression_serious": "show a serious expression while preserving the same face",
    "expression_surprised": "show a surprised expression while preserving the same face",
    "expression_angry": "show an angry expression while preserving the same face",
    "expression_profile": "show expression consistency from a three-quarter or profile angle",
    "accessory_detail": "focus on signature accessories without changing their design",
    "material_detail": "show fabric, leather, metal, seams, and surface materials clearly",
    "hands_or_gloves": "show hand, glove, or sleeve details clearly",
    "footwear_detail": "show boots, shoes, or lower costume details clearly",
    "prop_detail": "show props and tools as consistent character identifiers",
    "walking_pose": "show a simple walking pose with the full identity readable",
    "turning_pose": "show a turning pose without losing costume or face consistency",
    "reaching_pose": "show a reaching gesture while preserving silhouette and outfit",
    "crouching_pose": "show a crouching pose with clear anatomy and readable costume",
    "hero_pose": "show a strong hero pose while keeping the character reusable",
    "workshop_context": "place the character in a simple workshop context without clutter",
    "street_context": "place the character in a simple street context without losing identity",
    "interior_context": "place the character in a simple interior context with clean visibility",
    "front_view": "show a direct front reference view",
    "left_side_view": "show the left profile reference",
    "right_side_view": "show the right profile reference",
    "detail_closeups": "isolate close details for inspection",
    "turnaround_sheet": "show aligned front, side, and back views",
    "head_turnaround": "show consistent head structure across front, three-quarter, side, and back views",
    "centered_product": "center the object with clean margins",
    "detail_closeup": "show surface details and construction close up",
    "poster_layout": "compose for a finished promotional poster",
    "hero_subject": "make the subject the strongest visual anchor",
    "large_title_area": "leave a prominent clean title zone",
    "background_scene": "build depth behind the main composition",
    "supporting_elements": "arrange secondary elements without crowding the subject",
    "bottom_text_area": "reserve a readable bottom text zone",
    "logo_safe_area": "keep a clean area for a mark or logo",
    "dramatic_lighting": "make lighting a primary design feature",
}


class PromptVariationAssigner:
    fields = ("pose", "framing", "lighting", "background", "detail")

    def apply(self, records: list[PromptRecord]) -> list[PromptRecord]:
        for record in records:
            index = int(record.metadata.get("sequence_index", 0))
            mode_values = MODE_VARIATIONS.get(record.mode, MODE_VARIATIONS["character_lora"])
            variation: dict[str, Any] = {}
            for offset, field in enumerate(self.fields):
                options = mode_values[field]
                variation[field] = options[(index + offset) % len(options)]
            variation["shot_hint"] = SHOT_TYPE_HINTS.get(record.shot_type, "")
            variation["source"] = "PromptVariationAssigner"
            record.metadata["prompt_variation"] = variation
        return records
