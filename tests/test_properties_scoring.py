import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from switchmatter.data_loader import load_alternative_materials, load_product_config
from switchmatter.properties_scoring import (
    calculate_candidate_properties, calculate_property_score,
    find_property_requirements, score_component_properties)


class PropertiesScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = {x["candidate_id"]: x for x in load_alternative_materials()}
        cls.req = find_property_requirements(load_product_config(), "cap")

    def test_property_formula(self):
        self.assertEqual(calculate_property_score(8, 8), 10)
        self.assertEqual(calculate_property_score(10, 8), 10)
        self.assertEqual(calculate_property_score(6, 8), 7.5)

    def test_average(self):
        result = calculate_candidate_properties(self.items["ALT-CAP-002"], self.req)
        self.assertAlmostEqual(result["properties_score"], (8.75 + 10 + 10) / 3)

    def test_missing_and_null_are_not_inferred_or_averaged(self):
        for value in ("missing", None):
            item = copy.deepcopy(self.items["ALT-CAP-001"])
            if value == "missing":
                item["properties"].pop("sealability")
                missing = "sealability"
            else:
                item["properties"]["stiffness"] = None
                missing = "stiffness"
            result = calculate_candidate_properties(item, self.req)
            self.assertIn(missing, result["missing_properties"])
            self.assertIsNone(result["properties_score"])
            self.assertEqual(result["property_results"], [])

    def test_only_eligible_are_scored(self):
        current = {"component": "cap", "food_contact": True}
        results = {x["candidate_id"]: x for x in score_component_properties(current)}
        for key in ("ALT-CAP-001", "ALT-CAP-002", "ALT-CAP-003"):
            self.assertIn("properties_score", results[key])
        for key in ("ALT-CAP-004", "ALT-CAP-005", "ALT-CAP-006"):
            self.assertEqual(results[key]["scoring_status"], "NOT_SCORED")
            self.assertNotIn("properties_score", results[key])


if __name__ == "__main__":
    unittest.main()
