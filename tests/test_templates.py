import unittest

from shotplanner.templates import LAYOUT_TEMPLATES, validate_templates


class TemplateTests(unittest.TestCase):
    def test_all_templates_are_valid(self):
        validate_templates()

    def test_minimum_template_count(self):
        self.assertGreaterEqual(len(LAYOUT_TEMPLATES), 10)

    def test_lora_specific_templates_exist(self):
        expected = {
            "hands_detail_pair",
            "prop_detail_triptych",
            "material_swatches_grid",
            "expression_strip",
            "head_turnaround_strip",
            "full_body_turnaround_four_panel",
            "costume_layer_detail_grid",
            "accessory_callout_sheet",
        }

        self.assertTrue(expected.issubset(LAYOUT_TEMPLATES))


if __name__ == "__main__":
    unittest.main()
