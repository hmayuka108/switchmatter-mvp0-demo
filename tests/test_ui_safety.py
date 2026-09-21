from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.confirmation_boundary import PipelineError
from switchmatter.pdf_extractor import PDFExtractionError
from switchmatter.ui_safety import (
    extraction_error_message, missing_parsed_fields, reset_analysis_state,
    scoring_empty_message, validate_confirmation,
)


class UISafetyTests(unittest.TestCase):
    def test_extraction_errors_are_controlled(self):
        self.assertIn("No extractable text", extraction_error_message(PipelineError("internal")))
        self.assertIn("could not be read", extraction_error_message(PDFExtractionError("path")))
        self.assertNotIn("internal", extraction_error_message(RuntimeError("internal secret")))

    def test_missing_component_blocks_but_supported_unknowns_do_not(self):
        current = {"component": None, "current_material": None,
                   "thickness": None, "food_contact": None}
        self.assertEqual(validate_confirmation(current),
                         ["Component must be selected before analysis can run."])
        current["component"] = "cap"
        self.assertEqual(validate_confirmation(current), [])
        self.assertEqual(missing_parsed_fields(current),
                         ["current_material", "thickness", "food_contact"])

    def test_negative_thickness_is_rejected(self):
        current = {"component": "cap", "thickness": {"value": -0.1, "unit": "mm"}}
        self.assertEqual(validate_confirmation(current), ["Thickness must not be negative."])

    def test_safe_scoring_empty_states(self):
        self.assertIn("Additional information", scoring_empty_message(
            {"eligible": [], "potential": [{}], "excluded": []}, []))
        self.assertIn("incomplete", scoring_empty_message(
            {"eligible": [{}], "potential": [], "excluded": []}, []))
        self.assertIsNone(scoring_empty_message({}, [{}]))

    def test_reset_clears_analysis_and_overrides(self):
        state = {"upload_identity": "x", "analysis": {}, "confirmed": {},
                 "candidate_overrides": {"A": {}}, "override::A::x": True,
                 "upload_widget_version": 2, "unrelated": "keep"}
        reset_analysis_state(state)
        for key in ("upload_identity", "analysis", "confirmed", "candidate_overrides",
                    "override::A::x"):
            self.assertNotIn(key, state)
        self.assertEqual(state["upload_widget_version"], 3)
        self.assertEqual(state["unrelated"], "keep")


if __name__ == "__main__":
    unittest.main()
