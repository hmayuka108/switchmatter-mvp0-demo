from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.data_loader import load_alternative_materials, load_regulations
from switchmatter.pipeline import run_analysis
from switchmatter.ui_results import prepare_screening, screening_summary


class UIResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        analysis = run_analysis({"component": "cap", "food_contact": True})
        cls.view = prepare_screening(
            analysis["screening"], load_alternative_materials(), load_regulations())

    def test_summary_uses_existing_groups(self):
        self.assertEqual(screening_summary(self.view),
                         {"eligible": 3, "potential": 1, "excluded": 2})

    def test_candidate_and_rule_names_are_joined_from_databases(self):
        candidate = self.view["eligible"][0]
        self.assertEqual(candidate["candidate_name"], "Recycled PP 35")
        self.assertEqual(candidate["material"], "rPP")
        self.assertEqual(candidate["status"], "Eligible")
        self.assertEqual(candidate["rule_details"][0]["Rule name"],
                         "Heavy metals total limit")

    def test_potential_and_excluded_details_are_preserved(self):
        potential = self.view["potential"][0]
        self.assertEqual(potential["unknown_rule_ids"], ["REG-002"])
        self.assertEqual(potential["missing_fields"], ["pfas_compliant"])
        excluded = self.view["excluded"]
        self.assertTrue(any(item["fail_rule_ids"] for item in excluded))
        failure = next(row for item in excluded for row in item["rule_details"]
                       if row["Result"] == "FAIL")
        self.assertIsNotNone(failure["Observed value"])
        self.assertIn("Observed", failure["Reason"])


if __name__ == "__main__":
    unittest.main()
