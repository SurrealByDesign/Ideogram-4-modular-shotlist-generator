import argparse
import json
import tempfile
import unittest
from pathlib import Path

from shotplanner.cli import build_parser, character_bible_from_args, format_list, resolve_build_args, resolve_character_lora_args
from shotplanner.presets import BUILD_PRESETS, default_output_dir, slugify_subject


class PresetTests(unittest.TestCase):
    def test_slugify_subject(self):
        self.assertEqual(slugify_subject("Orc Mechanic Woman!"), "orc_mechanic_woman")

    def test_default_output_dir(self):
        self.assertEqual(
            Path(default_output_dir("Orc Mechanic Woman!", "character_lora")).as_posix(),
            "outputs/orc_mechanic_woman_character_lora",
        )

    def test_preset_fills_defaults(self):
        args = argparse.Namespace(
            preset="poster",
            subject="Moon Temple",
            mode=None,
            count=None,
            style=None,
            style_profile=None,
            style_intensity=None,
            out=None,
        )
        resolved = resolve_build_args(args)

        self.assertEqual(resolved.mode, "poster")
        self.assertEqual(resolved.count, 12)
        self.assertIn("poster", resolved.style)
        self.assertIn("moon_temple_poster", resolved.out)

    def test_explicit_args_override_preset(self):
        args = argparse.Namespace(
            preset="character_lora",
            subject="Moon Temple",
            mode="three_d_reference",
            count=7,
            style="custom style",
            style_profile=None,
            style_intensity=None,
            out="outputs/custom",
        )
        resolved = resolve_build_args(args)

        self.assertEqual(resolved.mode, "three_d_reference")
        self.assertEqual(resolved.count, 7)
        self.assertEqual(resolved.style, "custom style")
        self.assertEqual(resolved.out, "outputs/custom")

    def test_focused_lora_presets_exist(self):
        expected = {
            "character_lora_core",
            "character_lora_turnaround",
            "character_lora_expressions",
            "character_lora_costume_details",
            "character_lora_action",
            "character_lora_environment",
        }

        self.assertTrue(expected.issubset(BUILD_PRESETS))

    def test_build_character_lora_command_parses(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "build-character-lora",
                "--subject",
                "Moon Temple Knight",
                "--identity",
                "same knight",
                "--core-count",
                "3",
            ]
        )
        resolved = resolve_character_lora_args(args)

        self.assertEqual(resolved.command, "build-character-lora")
        self.assertEqual(resolved.core_count, 3)
        self.assertIn("moon_temple_knight_character_lora_multipack", resolved.out)

    def test_build_config_supplies_missing_args(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "build.json"
            config_path.write_text(
                json.dumps(
                    {
                        "subject": "Clockwork Bird",
                        "preset": "product_sheet",
                        "count": 4,
                        "style_profile": "technical_sheet",
                        "style_intensity": "strong",
                        "character_bible": {"identity": "same bird"},
                    }
                ),
                encoding="utf-8",
            )
            parser = build_parser()
            args = parser.parse_args(["build", "--config", str(config_path)])
            resolved = resolve_build_args(args)

            self.assertEqual(resolved.subject, "Clockwork Bird")
            self.assertEqual(resolved.mode, "product_sheet")
            self.assertEqual(resolved.count, 4)
            self.assertEqual(resolved.style_profile, "technical_sheet")
            self.assertEqual(resolved.style_intensity, "strong")
            self.assertEqual(character_bible_from_args(resolved)["identity"], "same bird")

    def test_cli_overrides_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "build.json"
            config_path.write_text(
                json.dumps({"subject": "Config Subject", "preset": "poster", "count": 12}),
                encoding="utf-8",
            )
            parser = build_parser()
            args = parser.parse_args(
                [
                    "build",
                    "--config",
                    str(config_path),
                    "--subject",
                    "CLI Subject",
                    "--count",
                    "2",
                ]
            )
            resolved = resolve_build_args(args)

            self.assertEqual(resolved.subject, "CLI Subject")
            self.assertEqual(resolved.count, 2)

    def test_character_lora_config_supplies_packs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "lora.json"
            config_path.write_text(
                json.dumps(
                    {
                        "subject": "Config Character",
                        "style_profile": "clean_reference",
                        "style_intensity": "standard",
                        "pack_style_profiles": {"turnaround": "technical_sheet"},
                        "pack_style_intensity": {"turnaround": "light"},
                        "character_bible": {"identity": "same character"},
                        "packs": {"core": 2, "turnaround": 3},
                    }
                ),
                encoding="utf-8",
            )
            parser = build_parser()
            args = parser.parse_args(["build-character-lora", "--config", str(config_path)])
            resolved = resolve_character_lora_args(args)

            self.assertEqual(resolved.subject, "Config Character")
            self.assertEqual(resolved.core_count, 2)
            self.assertEqual(resolved.turnaround_count, 3)
            self.assertEqual(resolved.style_profile, "clean_reference")
            self.assertEqual(resolved.style_intensity, "standard")
            self.assertEqual(resolved.pack_style_profiles["turnaround"], "technical_sheet")
            self.assertEqual(resolved.pack_style_intensity["turnaround"], "light")
            self.assertEqual(character_bible_from_args(resolved)["identity"], "same character")

    def test_list_command_parses(self):
        parser = build_parser()
        args = parser.parse_args(["list", "presets"])

        self.assertEqual(args.command, "list")
        self.assertEqual(args.resource, "presets")

    def test_list_outputs_include_expected_resources(self):
        self.assertIn("character_lora_core", format_list("presets"))
        self.assertIn("character_lora_expressions", format_list("modes"))
        self.assertIn("character_reference", format_list("palettes"))
        self.assertIn("technical_sheet", format_list("styles"))
        self.assertIn("expression_strip", format_list("templates"))
        self.assertIn("core", format_list("packs"))


if __name__ == "__main__":
    unittest.main()
