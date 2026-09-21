"""Tests for deterministic Current Component parsing."""

from pathlib import Path
import sys
import unittest


MVP0_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MVP0_ROOT / "src"))

from switchmatter.parser import parse_current_component, parse_pdf


class CurrentComponentParserTests(unittest.TestCase):
    def test_cap_sample_pdf(self) -> None:
        result = parse_pdf(MVP0_ROOT / "sample_pdfs" / "pet_bottle_cap_spec.pdf")

        self.assertEqual(
            result,
            {
                "component": "cap",
                "current_material": "HDPE",
                "thickness": {"value": 1.2, "unit": "mm"},
                "food_contact": True,
            },
        )

    def test_label_sample_pdf(self) -> None:
        result = parse_pdf(MVP0_ROOT / "sample_pdfs" / "pet_bottle_label_spec.pdf")

        self.assertEqual(
            result,
            {
                "component": "label",
                "current_material": "PP",
                "thickness": {"value": 0.05, "unit": "mm"},
                "food_contact": None,
            },
        )

    def test_missing_information_remains_none(self) -> None:
        result = parse_current_component("Supplier specification with no relevant fields.")

        self.assertEqual(
            result,
            {
                "component": None,
                "current_material": None,
                "thickness": None,
                "food_contact": None,
            },
        )

    def test_material_alone_does_not_infer_component(self) -> None:
        result = parse_current_component("Material: High-density polyethylene (HDPE)")

        self.assertIsNone(result["component"])
        self.assertEqual(result["current_material"], "HDPE")

    def test_negative_food_contact_takes_precedence(self) -> None:
        result = parse_current_component(
            "Not suitable for food contact; suitable for food contact wording is obsolete."
        )

        self.assertFalse(result["food_contact"])


if __name__ == "__main__":
    unittest.main()
