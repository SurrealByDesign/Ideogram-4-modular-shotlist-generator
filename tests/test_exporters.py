import json
import tempfile
import unittest
import csv
from pathlib import Path

from shotplanner.exporters import Exporter
from shotplanner.generator import build_character_lora_records, build_records
from shotplanner.cli import mark_record


class ExporterTests(unittest.TestCase):
    def test_export_writes_preview_html(self):
        records = build_records("test subject", "ink sketch", "poster", 3)
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)
            preview_path = files["preview_html"]

            self.assertTrue(Path(preview_path).exists())
            self.assertIn("preview.html", Path(preview_path).name)
            self.assertIn("test subject", Path(preview_path).read_text(encoding="utf-8"))

            records_json = Path(files["records_json"]).read_text(encoding="utf-8")
            self.assertEqual(len(json.loads(records_json)), 3)

    def test_export_writes_downstream_handoff(self):
        records = build_records("test subject", "ink sketch", "poster", 2)
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)
            handoff = json.loads(Path(files["downstream_handoff_json"]).read_text(encoding="utf-8"))

            self.assertEqual(handoff["schema_version"], "shotplanner.downstream_handoff.v1")
            self.assertEqual(len(handoff["records"]), 2)
            first = handoff["records"][0]
            self.assertIn("base_prompt_json_text", first)
            self.assertIn("style_json_fragment_text", first)
            self.assertIn("compositional_json_text", first)
            self.assertIn("element_json_strings", first)
            self.assertEqual(first["base_prompt_json"]["metadata"]["source"], "shotplanner")
            self.assertEqual(
                first["base_prompt_json"]["style_description"]["color_palette"],
                records[0].color_palette["colors"],
            )

    def test_export_writes_review_csv(self):
        records = build_character_lora_records(
            "test subject",
            pack_counts={
                "core": 2,
                "turnaround": 0,
                "expressions": 0,
                "costume_details": 0,
                "action": 0,
                "environment": 0,
            },
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)
            with Path(files["review_csv"]).open(encoding="utf-8") as review_file:
                rows = list(csv.DictReader(review_file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["index"], "0")
            self.assertEqual(rows[0]["pack"], "core")
            self.assertIn("prompt_short", rows[0])
            self.assertLessEqual(len(rows[0]["prompt_short"]), 180)

    def test_report_includes_style_profile_counts(self):
        records = build_character_lora_records(
            "test subject",
            style_profile_name="clean_reference",
            style_intensity="standard",
            pack_style_profiles={"turnaround": "technical_sheet"},
            pack_style_intensity={"turnaround": "light"},
            pack_counts={
                "core": 2,
                "turnaround": 2,
                "expressions": 0,
                "costume_details": 0,
                "action": 0,
                "environment": 0,
            },
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)
            report = Path(files["report_md"]).read_text(encoding="utf-8")

            self.assertIn("## Style profiles", report)
            self.assertIn("- clean_reference / standard: 2", report)
            self.assertIn("- technical_sheet / light: 2", report)

    def test_report_includes_review_summary(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 3})
        mark_record(records, index=0, status="selected", selected=True)
        mark_record(records, index=1, status="needs_regen", needs_regen=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)
            report = Path(files["report_md"]).read_text(encoding="utf-8")

            self.assertIn("## Review summary", report)
            self.assertIn("- selected: 1", report)
            self.assertIn("- needs_regen: 1", report)
            self.assertIn("## Review flags", report)
            self.assertIn("- selected=true: 1", report)
            self.assertIn("- needs_regen=true: 1", report)

    def test_preview_includes_pack_and_template_review_controls(self):
        records = build_character_lora_records(
            "test subject",
            pack_counts={
                "core": 1,
                "turnaround": 1,
                "expressions": 1,
                "costume_details": 1,
                "action": 1,
                "environment": 1,
            },
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            files = Exporter().export(records, temp_dir)
            preview = Path(files["preview_html"]).read_text(encoding="utf-8")

            self.assertIn('id="packFilter"', preview)
            self.assertIn("All packs", preview)
            self.assertIn("Packs", preview)
            self.assertIn("Templates", preview)
            self.assertIn('data-pack="core"', preview)
            self.assertIn("template:", preview)


if __name__ == "__main__":
    unittest.main()
