import json
import tempfile
import unittest
import csv
from pathlib import Path

from shotplanner.cli import (
    attach_result_ref,
    build_parser,
    copy_record_subset,
    export_missing_result_worklist,
    export_prompt_files,
    export_qa_findings,
    export_revision_worklist,
    filter_records,
    filter_records_by_qa,
    filter_result_records,
    format_plan_qa,
    format_recommendations,
    format_revision_summary,
    format_result_audit,
    format_review_records,
    format_records_inspection,
    format_records_stats,
    format_selected_record,
    load_records,
    mark_record,
    save_records,
    select_record,
)
from shotplanner.exporters import Exporter
from shotplanner.generator import build_character_lora_records, build_records
from shotplanner.validation import format_validation_report, validate_records_for_handoff


class RecordsCliTests(unittest.TestCase):
    def test_inspect_and_select_commands_parse(self):
        parser = build_parser()
        inspect_args = parser.parse_args(["inspect", "outputs/example/records.json"])
        stats_args = parser.parse_args(["stats", "outputs/example/records.json"])
        validate_args = parser.parse_args(["validate", "outputs/example/records.json"])
        qa_args = parser.parse_args(
            [
                "qa",
                "outputs/example/records.json",
                "--pack",
                "expressions",
                "--code",
                "repeated_prompt_words",
                "--severity",
                "info",
                "--field",
                "json",
            ]
        )
        audit_args = parser.parse_args(
            [
                "audit-results",
                "outputs/example/records.json",
                "--pack",
                "core",
                "--has-results",
                "false",
                "--result-status",
                "accepted",
                "--field",
                "missing",
            ]
        )
        recommend_args = parser.parse_args(["recommend", "outputs/example/records.json"])
        review_args = parser.parse_args(["review", "outputs/example/records.json", "--status", "selected", "--selected", "true", "--field", "ids"])
        select_args = parser.parse_args(["select", "outputs/example/records.json", "--index", "1"])
        mark_args = parser.parse_args(["mark", "outputs/example/records.json", "--index", "1", "--status", "selected"])
        attach_args = parser.parse_args(["attach-result", "outputs/example/records.json", "--index", "1", "--path", "outputs/images/a.png", "--status", "accepted"])
        export_qa_args = parser.parse_args(["export-qa", "outputs/example/records.json", "--out", "outputs/example/qa", "--pack", "expressions", "--severity", "info"])
        export_revisions_args = parser.parse_args(["export-revisions", "outputs/example/records.json", "--out", "outputs/example/revisions", "--review-status", "needs_regen", "--qa-code", "empty_negative_prompt"])
        revision_summary_args = parser.parse_args(["revision-summary", "outputs/example/records.json", "--qa-severity", "warning", "--field", "json"])
        copy_records_args = parser.parse_args(["copy-records", "outputs/example/records.json", "--out", "outputs/example/subset", "--selected", "true", "--qa-severity", "warning"])
        export_missing_args = parser.parse_args(["export-missing-results", "outputs/example/records.json", "--out", "outputs/example/missing", "--pack", "core"])

        self.assertEqual(inspect_args.command, "inspect")
        self.assertEqual(stats_args.command, "stats")
        self.assertEqual(validate_args.command, "validate")
        self.assertEqual(qa_args.command, "qa")
        self.assertEqual(qa_args.pack, "expressions")
        self.assertEqual(qa_args.code, "repeated_prompt_words")
        self.assertEqual(qa_args.severity, "info")
        self.assertEqual(qa_args.field, "json")
        self.assertEqual(audit_args.command, "audit-results")
        self.assertEqual(audit_args.pack, "core")
        self.assertEqual(audit_args.has_results, "false")
        self.assertEqual(audit_args.result_status, "accepted")
        self.assertEqual(audit_args.field, "missing")
        self.assertEqual(recommend_args.command, "recommend")
        self.assertEqual(review_args.command, "review")
        self.assertEqual(review_args.status, "selected")
        self.assertEqual(review_args.selected, "true")
        self.assertEqual(review_args.field, "ids")
        self.assertEqual(select_args.command, "select")
        self.assertEqual(mark_args.command, "mark")
        self.assertEqual(attach_args.command, "attach-result")
        self.assertEqual(export_qa_args.command, "export-qa")
        self.assertEqual(export_revisions_args.command, "export-revisions")
        self.assertEqual(revision_summary_args.command, "revision-summary")
        self.assertEqual(copy_records_args.command, "copy-records")
        self.assertEqual(export_missing_args.command, "export-missing-results")
        self.assertEqual(select_args.index, 1)
        self.assertEqual(attach_args.path, "outputs/images/a.png")
        self.assertEqual(attach_args.status, "accepted")
        self.assertEqual(export_qa_args.pack, "expressions")
        self.assertEqual(export_qa_args.severity, "info")
        self.assertEqual(export_revisions_args.review_status, "needs_regen")
        self.assertEqual(export_revisions_args.qa_code, "empty_negative_prompt")
        self.assertEqual(revision_summary_args.qa_severity, "warning")
        self.assertEqual(revision_summary_args.field, "json")
        self.assertEqual(copy_records_args.selected, "true")
        self.assertEqual(copy_records_args.qa_severity, "warning")
        self.assertEqual(export_missing_args.pack, "core")

    def test_export_prompts_command_parses(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "export-prompts",
                "outputs/example/records.json",
                "--out",
                "outputs/example/prompts",
                "--pack",
                "expressions",
                "--shot-type",
                "expression_smile",
                "--review-status",
                "selected",
                "--selected",
                "true",
            ]
        )

        self.assertEqual(args.command, "export-prompts")
        self.assertEqual(args.records_path, "outputs/example/records.json")
        self.assertEqual(args.out, "outputs/example/prompts")
        self.assertEqual(args.pack, "expressions")
        self.assertEqual(args.shot_type, "expression_smile")
        self.assertEqual(args.review_status, "selected")
        self.assertEqual(args.selected, "true")

    def test_inspect_summarizes_records(self):
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
            loaded = load_records(files["records_json"])
            summary = format_records_inspection(loaded, files["records_json"])

            self.assertIn("Total records: 6", summary)
            self.assertIn("Packs:", summary)
            self.assertIn("Shot types:", summary)
            self.assertIn("Templates:", summary)

    def test_stats_reports_compact_count_tables(self):
        records = build_character_lora_records(
            "test subject",
            pack_counts={
                "core": 2,
                "turnaround": 2,
                "expressions": 2,
                "costume_details": 2,
                "action": 2,
                "environment": 2,
            },
            style_profile_name="clean_reference",
            style_intensity="strong",
        )
        text = format_records_stats(records, "records.json")

        self.assertIn("Total records: 12", text)
        self.assertIn("Packs:", text)
        self.assertIn("- core: 2", text)
        self.assertIn("Modes:", text)
        self.assertIn("Shot types:", text)
        self.assertIn("Templates:", text)
        self.assertIn("Aspect ratios:", text)
        self.assertIn("Palettes:", text)
        self.assertIn("Style profiles:", text)
        self.assertIn("- clean_reference / strong: 12", text)
        self.assertIn("Review status:", text)
        self.assertIn("- unreviewed: 12", text)
        self.assertIn("Review flags:", text)

    def test_stats_reports_review_summary(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 3})
        mark_record(records, index=0, status="selected", selected=True)
        mark_record(records, index=1, status="needs_regen", needs_regen=True)
        text = format_records_stats(records, "records.json")

        self.assertIn("Review status:", text)
        self.assertIn("- needs_regen: 1", text)
        self.assertIn("- selected: 1", text)
        self.assertIn("- unreviewed:", text)
        self.assertIn("Review flags:", text)
        self.assertIn("- selected=true: 1", text)
        self.assertIn("- needs_regen=true: 1", text)

    def test_plan_qa_reports_clean_generated_character_plan(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            2,
            character_bible={"identity": "same test subject"},
        )

        text = format_plan_qa(records, "records.json")
        payload = json.loads(format_plan_qa(records, "records.json", field="json"))

        self.assertIn("Status: CLEAN", text)
        self.assertEqual(payload["status"], "clean")
        self.assertEqual(payload["total_findings"], 0)

    def test_plan_qa_flags_prompt_quality_findings(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 2)
        records[0].character_bible = {"identity": "same test subject"}
        records[0].prompt_text = "pose pose pose pose pose pose frame"
        records[0].negative_prompt = ""
        records[1].prompt_text = records[0].prompt_text

        payload = json.loads(format_plan_qa(records, "records.json", field="json"))
        codes = {item["code"] for item in payload["findings"]}
        text = format_plan_qa(records, "records.json")

        self.assertEqual(payload["status"], "review")
        self.assertIn("missing_identity_anchor", codes)
        self.assertIn("empty_negative_prompt", codes)
        self.assertIn("duplicate_prompt", codes)
        self.assertIn("repeated_prompt_words", codes)
        self.assertIn("Finding types:", text)

    def test_plan_qa_filters_findings_by_code_and_severity(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 2)
        records[0].prompt_text = "pose pose pose pose pose pose frame"
        records[0].negative_prompt = ""

        repeated = json.loads(format_plan_qa(records, "records.json", field="json", code="repeated_prompt_words", severity="info"))
        warnings = json.loads(format_plan_qa(records, "records.json", field="json", severity="warning"))

        self.assertEqual(repeated["code_counts"], {"repeated_prompt_words": 1})
        self.assertEqual(repeated["severity_counts"], {"info": 1})
        self.assertTrue(all(item["severity"] == "warning" for item in warnings["findings"]))

    def test_plan_qa_preserves_source_indexes_for_filtered_records(self):
        records = build_character_lora_records(
            "test subject",
            character_bible={"identity": "same test subject"},
            pack_counts={
                "core": 1,
                "turnaround": 1,
                "expressions": 1,
                "costume_details": 1,
                "action": 1,
                "environment": 1,
            },
        )
        records[2].negative_prompt = ""
        filtered = filter_records(records, pack="expressions")

        payload = json.loads(format_plan_qa(filtered, "records.json", field="json", source_records=records, code="empty_negative_prompt"))

        self.assertEqual(payload["total_records"], 1)
        self.assertEqual(payload["findings"][0]["index"], 2)
        self.assertEqual(payload["findings"][0]["pack"], "expressions")

    def test_export_qa_findings_writes_json_and_csv(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            3,
            character_bible={"identity": "same test subject"},
        )
        records[1].negative_prompt = ""
        filtered = records[1:]
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_qa_findings(
                filtered,
                temp_dir,
                source_records=records,
                filters={"severity": "warning"},
                severity="warning",
            )
            payload = json.loads(Path(files["json"]).read_text(encoding="utf-8"))
            with Path(files["csv"]).open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(files["finding_count"], 1)
            self.assertEqual(payload["filters"], {"severity": "warning"})
            self.assertEqual(payload["findings"][0]["index"], 1)
            self.assertEqual(payload["findings"][0]["code"], "empty_negative_prompt")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["id"], records[1].id)

    def test_export_revision_worklist_writes_review_and_qa_records(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            3,
            character_bible={"identity": "same test subject"},
        )
        mark_record(records, index=0, status="needs_regen", notes="hands drifted", needs_regen=True)
        records[1].negative_prompt = ""
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_revision_worklist(records, temp_dir, source_records=records)
            payload = json.loads(Path(files["json"]).read_text(encoding="utf-8"))
            with Path(files["csv"]).open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(files["revision_count"], 2)
            self.assertEqual(payload["revision_count"], 2)
            self.assertEqual(payload["records"][0]["index"], 0)
            self.assertIn("needs_regen=true", payload["records"][0]["reasons"])
            self.assertEqual(payload["records"][1]["index"], 1)
            self.assertEqual(payload["records"][1]["qa_codes"], ["empty_negative_prompt"])
            self.assertIn("qa:empty_negative_prompt", payload["records"][1]["reasons"])
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["id"], records[0].id)

    def test_export_revision_worklist_supports_review_and_qa_filters(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            3,
            character_bible={"identity": "same test subject"},
        )
        mark_record(records, index=0, status="selected", selected=True)
        records[1].negative_prompt = ""
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_revision_worklist(
                records,
                temp_dir,
                source_records=records,
                filters={"qa_code": "empty_negative_prompt"},
                qa_code="empty_negative_prompt",
            )
            payload = json.loads(Path(files["json"]).read_text(encoding="utf-8"))

            self.assertEqual(payload["filters"], {"qa_code": "empty_negative_prompt"})
            self.assertEqual(payload["revision_count"], 2)
            self.assertEqual(payload["records"][1]["id"], records[1].id)
            self.assertEqual(payload["records"][1]["qa_codes"], ["empty_negative_prompt"])

    def test_format_revision_summary_reports_review_and_qa_counts(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            3,
            character_bible={"identity": "same test subject"},
        )
        mark_record(records, index=0, status="selected", selected=True)
        records[1].negative_prompt = ""

        text = format_revision_summary(records, "records.json")
        payload = json.loads(format_revision_summary(records, "records.json", field="json"))

        self.assertIn("Revision records: 2", text)
        self.assertIn("Review records: 1", text)
        self.assertIn("QA records: 1", text)
        self.assertEqual(payload["revision_count"], 2)
        self.assertEqual(payload["review_records"], 1)
        self.assertEqual(payload["qa_records"], 1)
        self.assertEqual(payload["qa_codes"], {"empty_negative_prompt": 1})

    def test_format_revision_summary_supports_filters(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            3,
            character_bible={"identity": "same test subject"},
        )
        records[1].negative_prompt = ""

        payload = json.loads(format_revision_summary(records, "records.json", field="json", qa_code="empty_negative_prompt"))

        self.assertEqual(payload["revision_count"], 1)
        self.assertEqual(payload["records"][0]["index"], 1)
        self.assertEqual(payload["records"][0]["reasons"], ["qa:empty_negative_prompt"])

    def test_filter_records_by_qa_returns_records_with_findings(self):
        records = build_records(
            "test subject",
            "clean reference",
            "character_lora_core",
            3,
            character_bible={"identity": "same test subject"},
        )
        records[1].negative_prompt = ""

        filtered = filter_records_by_qa(records, source_records=records, qa_code="empty_negative_prompt")

        self.assertEqual([record.id for record in filtered], [records[1].id])

    def test_copy_record_subset_writes_records_and_manifest(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 3)
        subset = records[1:]
        with tempfile.TemporaryDirectory() as temp_dir:
            files = copy_record_subset(
                subset,
                temp_dir,
                source_records=records,
                filters={"selected": "true"},
            )
            copied = load_records(files["records_json"])
            manifest = json.loads(Path(files["manifest"]).read_text(encoding="utf-8"))

            self.assertEqual(files["copied_count"], 2)
            self.assertEqual([record.id for record in copied], [records[1].id, records[2].id])
            self.assertEqual(manifest["source_count"], 3)
            self.assertEqual(manifest["copied_count"], 2)
            self.assertEqual(manifest["filters"], {"selected": "true"})
            self.assertEqual([item["source_index"] for item in manifest["records"]], [1, 2])

    def test_select_record_by_index_and_id(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 2})

        by_index = select_record(records, index=1)
        by_id = select_record(records, record_id=by_index.id)

        self.assertEqual(by_index.id, by_id.id)

    def test_format_selected_record_fields(self):
        record = build_character_lora_records("test subject", pack_counts={"core": 1})[0]

        self.assertEqual(format_selected_record(record, "prompt"), record.prompt_text)
        self.assertEqual(format_selected_record(record, "negative"), record.negative_prompt)
        self.assertEqual(json.loads(format_selected_record(record, "metadata")), record.metadata)
        self.assertEqual(json.loads(format_selected_record(record, "record"))["id"], record.id)
        self.assertEqual(json.loads(format_selected_record(record, "result_refs")), [])

    def test_mark_record_updates_review_fields(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 2})

        marked = mark_record(
            records,
            index=1,
            status="selected",
            notes="best identity shot",
            selected=True,
            needs_regen=False,
        )

        self.assertEqual(marked.review["review_status"], "selected")
        self.assertEqual(marked.review["review_notes"], "best identity shot")
        self.assertTrue(marked.review["selected"])
        self.assertFalse(marked.review["needs_regen"])
        self.assertEqual(json.loads(format_selected_record(marked, "review"))["review_status"], "selected")

    def test_attach_result_ref_adds_result_reference(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 1})

        record = attach_result_ref(
            records,
            index=0,
            path="outputs/images/a.png",
            status="accepted",
            notes="best face consistency",
        )

        self.assertEqual(record.result_refs[0]["path"], "outputs/images/a.png")
        self.assertEqual(record.result_refs[0]["status"], "accepted")
        self.assertEqual(record.result_refs[0]["notes"], "best face consistency")
        self.assertEqual(json.loads(format_selected_record(record, "result_refs"))[0]["status"], "accepted")

    def test_format_result_audit_summarizes_result_refs(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 3)
        attach_result_ref(records, index=0, path="outputs/images/a.png", status="accepted")
        attach_result_ref(records, index=1, path="outputs/images/b.png", status="needs_regen")

        text = format_result_audit(records, "records.json")

        self.assertIn("Total records: 3", text)
        self.assertIn("Records with results: 2", text)
        self.assertIn("Records without results: 1", text)
        self.assertIn("Total result refs: 2", text)
        self.assertIn("- accepted: 1", text)
        self.assertIn("- needs_regen: 1", text)
        self.assertIn(records[2].id, text)

    def test_format_result_audit_supports_missing_and_json_fields(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 2)
        attach_result_ref(records, index=0, path="outputs/images/a.png", status="accepted")

        missing = format_result_audit(records, "records.json", field="missing")
        payload = json.loads(format_result_audit(records, "records.json", field="json"))

        self.assertIn("Records without results: 1", missing)
        self.assertIn(records[1].id, missing)
        self.assertEqual(payload["records_with_results"], 1)
        self.assertEqual(payload["records_without_results"], 1)
        self.assertEqual(payload["result_status"], {"accepted": 1})

    def test_filter_result_records_supports_has_results_and_status(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 3)
        attach_result_ref(records, index=0, path="outputs/images/a.png", status="accepted")
        attach_result_ref(records, index=1, path="outputs/images/b.png", status="needs_regen")

        with_results = filter_result_records(records, has_results=True)
        missing = filter_result_records(records, has_results=False)
        accepted = filter_result_records(records, result_status="accepted")

        self.assertEqual([record.id for record in with_results], [records[0].id, records[1].id])
        self.assertEqual([record.id for record in missing], [records[2].id])
        self.assertEqual([record.id for record in accepted], [records[0].id])

    def test_format_result_audit_preserves_source_indexes_for_filtered_records(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 3)
        attach_result_ref(records, index=0, path="outputs/images/a.png", status="accepted")
        filtered = filter_result_records(records, has_results=False)

        text = format_result_audit(filtered, "records.json", field="missing", source_records=records)

        self.assertIn("index=1", text)
        self.assertIn("index=2", text)
        self.assertNotIn("index=0", text)

    def test_format_review_records_lists_review_state(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 3})
        mark_record(records, index=0, status="selected", notes="best identity shot", selected=True)
        mark_record(records, index=1, status="needs_regen", notes="hands drifted", needs_regen=True)

        selected = filter_records(records, review_status="selected", selected=True)
        text = format_review_records(selected, "records.json", source_records=records)

        self.assertIn("Matched records: 1", text)
        self.assertIn("index=0", text)
        self.assertIn("core-character_lora_core-0001", text)
        self.assertIn("status=selected", text)
        self.assertIn("[selected]", text)
        self.assertIn("best identity shot", text)

    def test_format_review_records_supports_output_fields(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 2})
        mark_record(records, index=0, status="selected", selected=True)
        selected = filter_records(records, review_status="selected", selected=True)

        ids = format_review_records(selected, "records.json", source_records=records, field="ids")
        prompts = format_review_records(selected, "records.json", source_records=records, field="prompts")
        json_text = format_review_records(selected, "records.json", source_records=records, field="json")
        payload = json.loads(json_text)

        self.assertEqual(ids.strip(), selected[0].id)
        self.assertIn(selected[0].prompt_text, prompts)
        self.assertEqual(payload[0]["index"], 0)
        self.assertEqual(payload[0]["review"]["review_status"], "selected")

    def test_format_review_records_reports_none_for_empty_matches(self):
        text = format_review_records([], "records.json")

        self.assertIn("Matched records: 0", text)
        self.assertIn("- none", text)

    def test_save_records_preserves_review_fields(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 1})
        mark_record(records, index=0, status="needs_regen", notes="hands drifted", needs_regen=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "records.json"
            save_records(records, path)
            loaded = load_records(path)

            self.assertEqual(loaded[0].review["review_status"], "needs_regen")
            self.assertEqual(loaded[0].review["review_notes"], "hands drifted")
            self.assertTrue(loaded[0].review["needs_regen"])

    def test_export_missing_result_worklist_writes_json_and_csv(self):
        records = build_records("test subject", "clean reference", "character_lora_core", 3)
        attach_result_ref(records, index=0, path="outputs/images/a.png", status="accepted")
        filtered = records[1:]
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_missing_result_worklist(
                filtered,
                temp_dir,
                source_records=records,
                filters={"pack": "core"},
            )
            payload = json.loads(Path(files["json"]).read_text(encoding="utf-8"))
            with Path(files["csv"]).open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(files["missing_count"], 2)
            self.assertEqual(payload["source_count"], 3)
            self.assertEqual(payload["filtered_count"], 2)
            self.assertEqual(payload["missing_count"], 2)
            self.assertEqual(payload["filters"], {"pack": "core"})
            self.assertEqual([item["index"] for item in payload["records"]], [1, 2])
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["id"], records[1].id)

    def test_export_prompt_files_writes_prompts_and_manifest(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 2})
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_prompt_files(records, temp_dir, include_negative=True)

            prompt_files = sorted((Path(temp_dir) / "prompts").glob("*.txt"))
            negative_files = sorted((Path(temp_dir) / "negative_prompts").glob("*.txt"))
            manifest = json.loads(Path(files["manifest"]).read_text(encoding="utf-8"))

            self.assertEqual(len(prompt_files), len(records))
            self.assertEqual(len(negative_files), len(records))
            self.assertEqual(prompt_files[0].read_text(encoding="utf-8").strip(), records[0].prompt_text)
            self.assertEqual(negative_files[0].read_text(encoding="utf-8").strip(), records[0].negative_prompt)
            self.assertEqual(manifest["source_count"], len(records))
            self.assertEqual(manifest["exported_count"], len(records))
            self.assertEqual(manifest["records"][0]["id"], records[0].id)

    def test_filter_records_combines_pack_shot_type_and_template(self):
        records = build_character_lora_records("test subject")

        filtered = filter_records(
            records,
            pack="expressions",
            shot_type="expression_smile",
            template="centered_portrait",
        )

        self.assertTrue(filtered)
        self.assertTrue(all(record.metadata.get("pack") == "expressions" for record in filtered))
        self.assertTrue(all(record.shot_type == "expression_smile" for record in filtered))
        self.assertTrue(all(record.metadata.get("bbox_template") == "centered_portrait" for record in filtered))

    def test_filter_records_supports_review_filters(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 3})
        mark_record(records, index=0, status="selected", selected=True)
        mark_record(records, index=1, status="needs_regen", needs_regen=True)

        selected = filter_records(records, review_status="selected", selected=True)
        regen = filter_records(records, needs_regen=True)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].review["review_status"], "selected")
        self.assertEqual(len(regen), 1)
        self.assertTrue(regen[0].review["needs_regen"])

    def test_export_prompt_files_records_filters_in_manifest(self):
        records = build_character_lora_records("test subject")
        filtered = filter_records(records, pack="expressions")
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_prompt_files(
                filtered,
                temp_dir,
                source_count=len(records),
                filters={"pack": "expressions"},
            )
            manifest = json.loads(Path(files["manifest"]).read_text(encoding="utf-8"))

            self.assertLess(manifest["exported_count"], manifest["source_count"])
            self.assertEqual(manifest["filters"], {"pack": "expressions"})
            self.assertTrue(all(item["pack"] == "expressions" for item in manifest["records"]))

    def test_export_prompt_files_with_review_filtered_records(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 3})
        mark_record(records, index=0, status="selected", selected=True)
        mark_record(records, index=1, status="needs_regen", needs_regen=True)
        filtered = filter_records(records, review_status="selected", selected=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_prompt_files(
                filtered,
                temp_dir,
                source_count=len(records),
                filters={"review_status": "selected", "selected": "true"},
            )
            manifest = json.loads(Path(files["manifest"]).read_text(encoding="utf-8"))

            self.assertEqual(manifest["exported_count"], 1)
            self.assertEqual(manifest["filters"], {"review_status": "selected", "selected": "true"})

    def test_format_recommendations_reports_additions_for_weak_plan(self):
        records = build_records("test subject", "cinematic", "character_lora", 3)
        text = format_recommendations(records, "records.json")

        self.assertIn("Recommended additions:", text)
        self.assertIn("Add at least", text)
        self.assertIn("Example shot types:", text)

    def test_format_recommendations_reports_none_for_ready_plan(self):
        records = build_character_lora_records(
            "test subject",
            pack_counts={
                "core": 30,
                "turnaround": 24,
                "expressions": 20,
                "costume_details": 20,
                "action": 24,
                "environment": 18,
            },
        )
        text = format_recommendations(records, "records.json")

        self.assertIn("Coverage status: ready", text)
        self.assertIn("Recommended additions:\n- none", text)

    def test_validate_records_reports_valid_plan(self):
        records = build_character_lora_records(
            "test subject",
            character_bible={"identity": "same test subject"},
            pack_counts={
                "core": 2,
                "turnaround": 2,
                "expressions": 2,
                "costume_details": 2,
                "action": 2,
                "environment": 2,
            },
        )

        report = validate_records_for_handoff(records)
        text = format_validation_report(report, "records.json")

        self.assertEqual(report["status"], "valid")
        self.assertIn("Status: VALID", text)
        self.assertIn("Errors:\n- none", text)

    def test_validate_records_reports_errors(self):
        records = build_character_lora_records("test subject", pack_counts={"core": 2})
        records[1].id = records[0].id
        records[0].prompt_text = ""
        records[0].bbox_layout = {}

        report = validate_records_for_handoff(records)
        text = format_validation_report(report, "records.json")

        self.assertEqual(report["status"], "invalid")
        self.assertIn("duplicate record id", text)
        self.assertIn("missing prompt_text", text)
        self.assertIn("missing bbox_layout", text)


if __name__ == "__main__":
    unittest.main()
