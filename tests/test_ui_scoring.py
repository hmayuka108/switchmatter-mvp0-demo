from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.data_loader import load_alternative_materials
from switchmatter.pipeline import run_analysis
from switchmatter.ui_scoring import prepare_scoring, ranking_summary


class UIScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis = run_analysis({"component": "cap", "food_contact": True})
        cls.details = prepare_scoring(cls.analysis["ranking"], load_alternative_materials())

    def test_only_ranked_eligible_candidates_are_prepared(self):
        self.assertEqual([x["candidate_id"] for x in self.details],
                         ["ALT-CAP-001", "ALT-CAP-002", "ALT-CAP-003"])
        self.assertTrue(all(x["regulation_status"] == "Eligible" for x in self.details))

    def test_summary_preserves_existing_scores(self):
        source = self.analysis["ranking"][0]
        row = ranking_summary(self.details)[0]
        self.assertEqual(row["Final Score"], source["display_score"])
        self.assertEqual(row["Cost Score"], source["cost_score"])
        self.assertEqual(row["Properties Score"], source["properties_score"])

    def test_cost_inputs_and_outputs_are_preserved(self):
        source = self.analysis["ranking"][0]["cost_details"]
        shown = self.details[0]["cost"]
        for field in ("volume_cm3", "density_g_cm3", "mass_g", "price_per_g_eur",
                      "material_cost_eur", "current_material_cost_eur", "cost_score"):
            self.assertEqual(shown[field], source[field])

    def test_property_and_final_values_are_preserved(self):
        source = self.analysis["ranking"][0]
        first_property = source["properties_details"]["property_results"][0]
        shown = self.details[0]
        self.assertEqual(shown["properties"][0], {
            "Property": first_property["property"],
            "Required Value": first_property["required_value"],
            "Candidate Value": first_property["candidate_value"],
            "Property Score": first_property["score"],
        })
        self.assertEqual(shown["properties_score"], source["properties_score"])
        self.assertEqual(shown["final_score"], source["final_score"])


if __name__ == "__main__":
    unittest.main()
