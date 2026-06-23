import unittest

from shotplanner.models import PromptRecord
from shotplanner.modules import BBoxLayoutAssigner, ColorPaletteAssigner, PromptTextBuilder
from shotplanner.variations import PromptVariationAssigner


class RecordTests(unittest.TestCase):
    def test_record_preserves_unknown_fields_in_extra(self):
        record = PromptRecord.from_dict({"id": "a", "subject": "x", "mode": "poster", "future_field": 123})
        self.assertEqual(record.extra["future_field"], 123)

    def test_record_round_trips_review_fields(self):
        record = PromptRecord.from_dict(
            {
                "id": "a",
                "subject": "x",
                "mode": "poster",
                "review": {
                    "review_status": "selected",
                    "review_notes": "best identity shot",
                    "selected": True,
                    "needs_regen": False,
                },
            }
        )

        self.assertEqual(record.review["review_status"], "selected")
        self.assertTrue(record.to_dict()["review"]["selected"])

    def test_record_round_trips_result_refs(self):
        record = PromptRecord.from_dict(
            {
                "id": "a",
                "subject": "x",
                "mode": "poster",
                "result_refs": [
                    {
                        "path": "outputs/images/a.png",
                        "status": "accepted",
                        "notes": "best composition",
                    }
                ],
            }
        )

        self.assertEqual(record.result_refs[0]["path"], "outputs/images/a.png")
        self.assertEqual(record.to_dict()["result_refs"][0]["status"], "accepted")

    def test_modules_preserve_fields_they_do_not_own(self):
        record = PromptRecord(
            id="test-0001",
            subject="subject",
            mode="character_lora",
            shot_type="portrait",
            angle="front_view",
            metadata={"bbox_template": "centered_portrait", "custom": "keep"},
            extra={"future": {"keep": True}},
        )
        records = BBoxLayoutAssigner().apply([record])
        records = ColorPaletteAssigner().apply(records)
        records = PromptVariationAssigner().apply(records)
        records = PromptTextBuilder().apply(records)

        self.assertEqual(records[0].metadata["custom"], "keep")
        self.assertEqual(records[0].extra["future"], {"keep": True})
        self.assertEqual(records[0].result_refs, [])
        self.assertIn("prompt_variation", records[0].metadata)


if __name__ == "__main__":
    unittest.main()
