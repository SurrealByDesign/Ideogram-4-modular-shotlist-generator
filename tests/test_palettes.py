import unittest

from shotplanner.generator import build_records
from shotplanner.palettes import COLOR_PALETTES, get_palette, validate_palettes


class PaletteTests(unittest.TestCase):
    def test_all_palettes_are_valid(self):
        validate_palettes()

    def test_minimum_palette_count(self):
        self.assertGreaterEqual(len(COLOR_PALETTES), 5)

    def test_build_assigns_default_palette(self):
        records = build_records("test subject", "watercolor", "poster", 2)

        self.assertEqual(records[0].color_palette["name"], "cinematic_poster")
        self.assertIn("color_palette", records[0].ideogram_json)
        self.assertIn("Palette guidance:", records[0].prompt_text)

    def test_build_accepts_explicit_palette(self):
        records = build_records("test subject", "watercolor", "character_lora", 2, palette_name="monochrome_ink")

        self.assertEqual(records[0].color_palette["name"], "monochrome_ink")
        self.assertIn("#111111", records[0].color_palette["colors"])
        self.assertIn("monochrome ink", records[0].prompt_text)
        self.assertNotIn("#111111", records[0].prompt_text)

    def test_get_palette_returns_a_copy(self):
        palette = get_palette("product_studio")
        palette["colors"].append("#000000")

        self.assertNotIn("#000000", get_palette("product_studio")["colors"])


if __name__ == "__main__":
    unittest.main()
