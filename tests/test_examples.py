import json
import unittest
from pathlib import Path


EXAMPLE_DIRS = [
    Path("examples/character_lora_core"),
    Path("examples/character_lora_expressions"),
    Path("examples/product_sheet"),
    Path("examples/style_profiles"),
    Path("examples/review_workflow"),
]

WORKFLOW_ONLY_DIRS = [
    Path("examples/workflow_handoff"),
    Path("examples/stable_cli_workflow"),
]


class ExampleTests(unittest.TestCase):
    def test_examples_have_required_files(self):
        for example_dir in EXAMPLE_DIRS:
            with self.subTest(example=str(example_dir)):
                self.assertTrue((example_dir / "command.txt").exists())
                self.assertTrue((example_dir / "records.sample.json").exists())
                self.assertTrue((example_dir / "report.sample.md").exists())

    def test_workflow_only_examples_have_required_files(self):
        for example_dir in WORKFLOW_ONLY_DIRS:
            with self.subTest(example=str(example_dir)):
                self.assertTrue((example_dir / "README.md").exists())
                self.assertTrue((example_dir / "command.txt").exists())

    def test_stable_cli_workflow_generated_outputs_exist(self):
        example_dir = Path("examples/stable_cli_workflow")

        self.assertTrue((example_dir / "stable_cli_workflow_config.json").exists())
        self.assertTrue((example_dir / "generated" / "records.json").exists())
        self.assertTrue((example_dir / "generated" / "qa_findings" / "qa_findings.json").exists())
        self.assertTrue((example_dir / "generated" / "revision_worklist" / "revision_worklist.json").exists())
        self.assertTrue((example_dir / "generated" / "revision_records" / "subset_manifest.json").exists())
        self.assertTrue((example_dir / "generated" / "prompt_export" / "prompt_manifest.json").exists())

    def test_example_records_are_valid_json_lists(self):
        for example_dir in EXAMPLE_DIRS:
            with self.subTest(example=str(example_dir)):
                records = json.loads((example_dir / "records.sample.json").read_text(encoding="utf-8"))
                self.assertIsInstance(records, list)
                self.assertGreater(len(records), 0)
                self.assertIn("id", records[0])
                self.assertIn("prompt_text", records[0])
                self.assertIn("bbox_layout", records[0])

    def test_character_examples_include_bible(self):
        for example_dir in [Path("examples/character_lora_core"), Path("examples/character_lora_expressions")]:
            with self.subTest(example=str(example_dir)):
                self.assertTrue((example_dir / "character_bible.json").exists())
                bible = json.loads((example_dir / "character_bible.json").read_text(encoding="utf-8"))
                records = json.loads((example_dir / "records.sample.json").read_text(encoding="utf-8"))
                self.assertEqual(records[0]["character_bible"]["identity"], bible["identity"])


if __name__ == "__main__":
    unittest.main()
