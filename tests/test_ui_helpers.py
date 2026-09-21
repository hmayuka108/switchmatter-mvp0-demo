from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.ui_helpers import build_confirmed_component, form_defaults


class UIHelperTests(unittest.TestCase):
    def test_defaults_preserve_unknowns(self):
        values = form_defaults({"component": None, "current_material": None,
                                "thickness": None, "food_contact": None})
        self.assertEqual(values["component"], "")
        self.assertEqual(values["current_material"], "")
        self.assertIsNone(values["thickness_value"])
        self.assertEqual(values["food_contact"], "Unknown")

    def test_confirmed_data_uses_edited_values(self):
        current = build_confirmed_component("label", " edited PP ", 0.08, " mm ", "No")
        self.assertEqual(current, {
            "component": "label", "current_material": "edited PP",
            "thickness": {"value": 0.08, "unit": "mm"}, "food_contact": False,
        })

    def test_unknown_values_are_not_defaulted(self):
        current = build_confirmed_component("", "", None, "", "Unknown")
        self.assertEqual(current, {"component": None, "current_material": None,
                                  "thickness": None, "food_contact": None})


if __name__ == "__main__":
    unittest.main()
