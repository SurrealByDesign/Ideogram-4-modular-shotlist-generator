import unittest

from shotplanner.generator import build_character_lora_records, build_records
from shotplanner.shotlists import SHOTLISTS


class ShotlistTests(unittest.TestCase):
    def test_shotlist_generation_count(self):
        records = build_records("test subject", "watercolor", "character_lora", 25)
        self.assertEqual(len(records), 25)
        self.assertTrue(records[0].prompt_text)
        self.assertTrue(records[0].bbox_layout)
        self.assertTrue(records[0].ideogram_json)
        self.assertIn("prompt_variation", records[0].metadata)
        self.assertIn("Guidance:", records[0].prompt_text)

    def test_prompt_variation_is_deterministic(self):
        first = build_records("test subject", "watercolor", "poster", 5)
        second = build_records("test subject", "watercolor", "poster", 5)

        self.assertEqual(first[2].metadata["prompt_variation"], second[2].metadata["prompt_variation"])
        self.assertEqual(first[2].prompt_text, second[2].prompt_text)

    def test_prompt_lead_does_not_repeat_matching_shot_and_angle(self):
        records = build_records("test subject", "watercolor", "character_lora_turnaround", 1)

        self.assertNotIn("front view, front view", records[0].prompt_text)
        self.assertIn("test subject, front view, watercolor.", records[0].prompt_text)

    def test_style_profile_is_applied_to_prompt_and_negative_prompt(self):
        records = build_records(
            "test subject",
            "watercolor",
            "poster",
            1,
            style_profile_name="technical_sheet",
        )

        self.assertIn("technical design sheet", records[0].prompt_text)
        self.assertIn("technical_sheet", records[0].style_description["profile"]["name"])
        self.assertEqual(records[0].style_description["profile"]["intensity"], "standard")
        self.assertIn("dramatic perspective", records[0].negative_prompt)
        self.assertEqual(records[0].ideogram_json["style"]["profile"]["name"], "technical_sheet")

    def test_style_profile_intensity_changes_prompt_phrase(self):
        light = build_records(
            "test subject",
            "",
            "poster",
            1,
            style_profile_name="technical_sheet",
            style_intensity="light",
        )[0]
        strong = build_records(
            "test subject",
            "",
            "poster",
            1,
            style_profile_name="technical_sheet",
            style_intensity="strong",
        )[0]

        self.assertIn("subtle technical design sheet", light.prompt_text)
        self.assertEqual(light.style_description["profile"]["intensity"], "light")
        self.assertIn("strongly emphasize technical design sheet", strong.prompt_text)
        self.assertEqual(strong.style_description["profile"]["intensity"], "strong")

    def test_focused_character_lora_modes_exist(self):
        expected = {
            "character_lora_core",
            "character_lora_turnaround",
            "character_lora_expressions",
            "character_lora_costume_details",
            "character_lora_action",
            "character_lora_environment",
        }

        self.assertTrue(expected.issubset(SHOTLISTS))

    def test_focused_character_lora_generation(self):
        records = build_records("test subject", "watercolor", "character_lora_expressions", 7)

        self.assertEqual(len(records), 7)
        self.assertEqual(records[0].mode, "character_lora_expressions")
        self.assertTrue(any(record.shot_type.startswith("expression") for record in records))

    def test_focused_lora_packs_use_specialized_templates(self):
        expressions = build_records("test subject", "watercolor", "character_lora_expressions", 7)
        details = build_records("test subject", "watercolor", "character_lora_costume_details", 7)
        turnaround = build_records("test subject", "watercolor", "character_lora_turnaround", 9)

        expression_templates = {record.metadata["bbox_template"] for record in expressions}
        detail_templates = {record.metadata["bbox_template"] for record in details}
        turnaround_templates = {record.metadata["bbox_template"] for record in turnaround}

        self.assertIn("expression_strip", expression_templates)
        self.assertIn("head_turnaround_strip", expression_templates)
        self.assertIn("hands_detail_pair", detail_templates)
        self.assertIn("prop_detail_triptych", detail_templates)
        self.assertIn("full_body_turnaround_four_panel", turnaround_templates)

    def test_multi_pack_character_lora_generation(self):
        records = build_character_lora_records(
            "test subject",
            character_bible={"identity": "same character"},
            style_profile_name="clean_reference",
            pack_counts={
                "core": 2,
                "turnaround": 2,
                "expressions": 2,
                "costume_details": 2,
                "action": 2,
                "environment": 2,
            },
        )

        self.assertEqual(len(records), 12)
        self.assertEqual(len({record.id for record in records}), 12)
        self.assertEqual(records[0].metadata["pack"], "core")
        self.assertIn("pack_preset", records[0].metadata)
        self.assertEqual(records[0].character_bible["identity"], "same character")
        self.assertEqual(records[0].style_description["profile"]["name"], "clean_reference")

    def test_multi_pack_style_profile_overrides(self):
        records = build_character_lora_records(
            "test subject",
            style_profile_name="clean_reference",
            style_intensity="light",
            pack_style_profiles={"turnaround": "technical_sheet", "environment": "cinematic_realism"},
            pack_style_intensity={"environment": "strong"},
            pack_counts={
                "core": 1,
                "turnaround": 1,
                "environment": 1,
            },
        )

        by_pack = {record.metadata["pack"]: record for record in records}
        self.assertEqual(by_pack["core"].style_description["profile"]["name"], "clean_reference")
        self.assertEqual(by_pack["turnaround"].style_description["profile"]["name"], "technical_sheet")
        self.assertEqual(by_pack["environment"].style_description["profile"]["name"], "cinematic_realism")
        self.assertEqual(by_pack["turnaround"].style_description["profile"]["intensity"], "light")
        self.assertEqual(by_pack["environment"].style_description["profile"]["intensity"], "strong")
        self.assertIn("strongly emphasize cinematic realistic concept art", by_pack["environment"].prompt_text)
        self.assertIn("orthographic clarity", by_pack["turnaround"].prompt_text)
        self.assertIn("controlled contrast", by_pack["environment"].prompt_text)


if __name__ == "__main__":
    unittest.main()
