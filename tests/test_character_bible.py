import json
import tempfile
import unittest
from pathlib import Path

from shotplanner.character import build_character_bible, lora_coverage_report
from shotplanner.exporters import Exporter
from shotplanner.generator import build_character_lora_records, build_records


class CharacterBibleTests(unittest.TestCase):
    def test_character_bible_is_added_to_records_and_prompts(self):
        bible = build_character_bible(
            identity="orc mechanic woman",
            hair="red braid",
            outfit="patched leather coat",
            must_keep="brass goggles",
            avoid="different face",
        )
        records = build_records("orc mechanic", "cinematic", "character_lora", 3, character_bible=bible)

        self.assertEqual(records[0].character_bible["hair"], "red braid")
        self.assertIn("Identity anchor:", records[0].prompt_text)
        self.assertIn("Identity anchor: orc mechanic woman", records[0].prompt_text)
        self.assertNotIn("Identity anchor: identity:", records[0].prompt_text)
        self.assertIn("brass goggles", records[0].prompt_text)
        self.assertIn("different face", records[0].negative_prompt)
        self.assertEqual(records[0].ideogram_json["character_bible"], bible)

    def test_empty_character_bible_ignores_none_values(self):
        bible = build_character_bible(identity=None, hair="")
        records = build_records("orc mechanic", "cinematic", "character_lora", 1, character_bible=bible)

        self.assertEqual(bible, {})
        self.assertNotIn("Identity anchor: None", records[0].prompt_text)
        self.assertNotIn("hair: None", records[0].prompt_text)

    def test_lora_coverage_reports_missing_categories_for_small_batches(self):
        records = build_records("orc mechanic", "cinematic", "character_lora", 3)
        coverage = lora_coverage_report(records)

        self.assertTrue(coverage["applies"])
        self.assertEqual(coverage["status"], "needs_review")
        self.assertIn("missing required coverage", coverage["decision"]["summary"])
        self.assertIn("side_view", coverage["missing"])
        self.assertTrue(coverage["recommendations"])
        side_view_recs = [item for item in coverage["recommendations"] if item["category"] == "side_view"]
        self.assertEqual(side_view_recs[0]["add_count"], 2)
        self.assertIn("side-view reference records", side_view_recs[0]["summary"])

    def test_lora_coverage_reports_thin_complete_batches(self):
        records = build_records("orc mechanic", "cinematic", "character_lora", 10)
        coverage = lora_coverage_report(records)

        self.assertEqual(coverage["status"], "ready_with_thin_coverage")
        self.assertIn("thin categories", coverage["decision"]["summary"])
        self.assertFalse(coverage["missing"])
        self.assertIn("portrait", coverage["thin"])
        portrait_recs = [item for item in coverage["recommendations"] if item["category"] == "portrait"]
        self.assertEqual(portrait_recs[0]["add_count"], 1)

    def test_lora_coverage_is_pack_aware(self):
        records = build_records("orc mechanic", "cinematic", "character_lora_expressions", 7)
        coverage = lora_coverage_report(records)

        self.assertEqual(coverage["mode"], "character_lora_expressions")
        self.assertIn("expression", coverage["required"])
        self.assertNotIn("back_view", coverage["required"])
        self.assertEqual(coverage["status"], "ready_with_thin_coverage")

    def test_lora_coverage_detects_multipack(self):
        records = build_character_lora_records(
            "orc mechanic",
            pack_counts={
                "core": 2,
                "turnaround": 2,
                "expressions": 2,
                "costume_details": 2,
                "action": 2,
                "environment": 2,
            },
        )
        coverage = lora_coverage_report(records)

        self.assertEqual(coverage["mode"], "character_lora_multipack")
        self.assertIn("back_view", coverage["required"])
        self.assertIn("Complete multi-pack", coverage["description"])

    def test_lora_coverage_has_no_recommendations_when_ready(self):
        records = build_character_lora_records(
            "orc mechanic",
            pack_counts={
                "core": 30,
                "turnaround": 24,
                "expressions": 20,
                "costume_details": 20,
                "action": 24,
                "environment": 18,
            },
        )
        coverage = lora_coverage_report(records)

        self.assertEqual(coverage["status"], "ready")
        self.assertEqual(coverage["recommendations"], [])

    def test_export_includes_bible_and_coverage(self):
        bible = build_character_bible(identity="orc mechanic woman", hair="red braid")
        records = build_records("orc mechanic", "cinematic", "character_lora", 10, character_bible=bible)
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)

            report = Path(files["report_md"]).read_text(encoding="utf-8")
            preview = Path(files["preview_html"]).read_text(encoding="utf-8")
            handoff = json.loads(Path(files["downstream_handoff_json"]).read_text(encoding="utf-8"))

            self.assertIn("## Character LoRA coverage", report)
            self.assertIn("Decision:", report)
            self.assertIn("Recommended next action:", report)
            self.assertIn("### Add-count recommendations", report)
            self.assertIn("Character Bible", preview)
            self.assertEqual(handoff["records"][0]["character_bible"], bible)


if __name__ == "__main__":
    unittest.main()
