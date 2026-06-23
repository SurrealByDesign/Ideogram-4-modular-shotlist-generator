import json
import unittest
from pathlib import Path

from shotplanner.bbox import validate_layout
from shotplanner.generator import build_character_lora_records, build_records
from shotplanner.models import PromptRecord


REQUIRED_RECORD_FIELDS = {
    "id",
    "subject",
    "mode",
    "shot_type",
    "angle",
    "aspect_ratio",
    "prompt_text",
    "negative_prompt",
    "character_bible",
    "style_description",
    "bbox_layout",
    "color_palette",
    "ideogram_json",
    "metadata",
    "review",
    "result_refs",
    "extra",
}


class SchemaTests(unittest.TestCase):
    def test_prompt_record_schema_fields_are_stable(self):
        record = build_records("test subject", "watercolor", "character_lora_core", 1)[0]

        self.assertEqual(set(record.to_dict()), REQUIRED_RECORD_FIELDS)

    def test_generated_records_have_valid_layout_schema(self):
        records = build_character_lora_records(
            "test subject",
            character_bible={"identity": "same character"},
            pack_counts={
                "core": 1,
                "turnaround": 1,
                "expressions": 1,
                "costume_details": 1,
                "action": 1,
                "environment": 1,
            },
        )

        for record in records:
            with self.subTest(record_id=record.id):
                data = record.to_dict()
                self.assertTrue(REQUIRED_RECORD_FIELDS.issubset(data))
                validate_layout(data["bbox_layout"])
                self.assertEqual(data["ideogram_json"]["character_bible"], data["character_bible"])

    def test_multipack_records_include_pack_metadata(self):
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

        for record in records:
            with self.subTest(record_id=record.id):
                self.assertIn("pack", record.metadata)
                self.assertIn("pack_preset", record.metadata)
                self.assertIn("pack_record_id", record.metadata)
                self.assertTrue(record.id.startswith(f"{record.metadata['pack']}-"))

    def test_unknown_future_fields_are_preserved_in_extra(self):
        record = PromptRecord.from_dict(
            {
                "id": "future-0001",
                "subject": "subject",
                "mode": "character_lora_core",
                "future_schema_field": {"keep": True},
            }
        )

        self.assertEqual(record.extra["future_schema_field"], {"keep": True})

    def test_example_configs_are_valid_json_objects(self):
        for path in [
            Path("examples/character_lora_multipack_config.json"),
            Path("examples/product_sheet_config.json"),
        ]:
            with self.subTest(path=str(path)):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)
                self.assertIn("subject", data)


if __name__ == "__main__":
    unittest.main()
