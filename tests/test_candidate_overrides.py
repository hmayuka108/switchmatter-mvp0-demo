from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.candidate_overrides import (
    apply_candidate_overrides, missing_field_specs, reset_override_state,
    run_analysis_with_overrides,
)
from switchmatter.data_loader import load_alternative_materials, load_regulations

CURRENT = {"component": "cap", "food_contact": True}


class CandidateOverrideTests(unittest.TestCase):
    def test_override_is_copy_only_and_file_unchanged(self):
        path = ROOT / "data" / "alternative_materials.json"
        before_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        source = load_alternative_materials()
        original = deepcopy(source)
        updated = apply_candidate_overrides(source, {"ALT-CAP-005": {"pfas_compliant": True}})
        self.assertIsNone(next(x for x in source if x["candidate_id"] == "ALT-CAP-005")
                          ["regulation_data"]["pfas_compliant"])
        self.assertTrue(next(x for x in updated if x["candidate_id"] == "ALT-CAP-005")
                        ["regulation_data"]["pfas_compliant"])
        self.assertEqual(source, original)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before_hash)

    def test_transitions_and_scoring(self):
        eligible = run_analysis_with_overrides(
            CURRENT, {"ALT-CAP-005": {"pfas_compliant": True}})
        self.assertIn("ALT-CAP-005", [x["candidate_id"] for x in eligible["screening"]["eligible"]])
        self.assertIn("ALT-CAP-005", [x["candidate_id"] for x in eligible["ranking"]])
        excluded = run_analysis_with_overrides(
            CURRENT, {"ALT-CAP-005": {"pfas_compliant": False}})
        self.assertIn("ALT-CAP-005", [x["candidate_id"] for x in excluded["screening"]["excluded"]])
        self.assertNotIn("ALT-CAP-005", [x["candidate_id"] for x in excluded["ranking"]])
        potential = run_analysis_with_overrides(CURRENT, {})
        self.assertIn("ALT-CAP-005", [x["candidate_id"] for x in potential["screening"]["potential"]])

    def test_only_target_and_explicit_values_change(self):
        source = load_alternative_materials()
        updated = apply_candidate_overrides(source, {"ALT-CAP-005": {"pfas_compliant": True}})
        for old, new in zip(source, updated):
            if old["candidate_id"] != "ALT-CAP-005":
                self.assertEqual(old, new)
        target = next(x for x in updated if x["candidate_id"] == "ALT-CAP-005")
        self.assertEqual(set(target["regulation_data"]),
                         set(next(x for x in source if x["candidate_id"] == "ALT-CAP-005")["regulation_data"]))

    def test_input_specs_and_reset(self):
        specs = missing_field_specs(["pfas_compliant", "recycled_content_pct"],
                                    load_regulations())
        self.assertEqual([x["input_type"] for x in specs], ["boolean", "number"])
        state = {"candidate_overrides": {"A": {"x": 1}}, "analysis": "keep"}
        reset_override_state(state)
        self.assertNotIn("candidate_overrides", state)
        self.assertEqual(state["analysis"], "keep")


if __name__ == "__main__":
    unittest.main()
