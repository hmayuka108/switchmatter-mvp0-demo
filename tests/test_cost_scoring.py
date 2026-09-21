import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.cost_scoring import (
    CostDataError, calculate_candidate_cost, calculate_cost_score,
    find_component_config, score_component_candidates,
)
from switchmatter.data_loader import load_alternative_materials, load_product_config

CURRENT = {"component": "cap", "current_material": "HDPE", "food_contact": True}


class CostScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = {x["candidate_id"]: x for x in load_alternative_materials()}
        cls.cap = find_component_config(load_product_config(), "cap")

    def test_mass_and_cost_formulas(self):
        result = calculate_candidate_cost(self.items["ALT-CAP-001"], self.cap)
        self.assertAlmostEqual(result["mass_g"], 3.0 * 0.90)
        self.assertAlmostEqual(result["material_cost_eur"], 2.7 * 0.0019)
        self.assertAlmostEqual(result["current_mass_g"], 2.85)
        self.assertAlmostEqual(result["current_material_cost_eur"], 0.004845)
        self.assertAlmostEqual(result["cost_score"], 4.7058823529)

    def test_score_relationship_and_clipping(self):
        self.assertEqual(calculate_cost_score(5, 5), 5)
        self.assertGreater(calculate_cost_score(4, 5), 5)
        self.assertLess(calculate_cost_score(6, 5), 5)
        self.assertEqual(calculate_cost_score(20, 5), 0)
        self.assertEqual(calculate_cost_score(-1, 5), 10)

    def test_missing_density_and_price_raise(self):
        for field in ("density_g_cm3", "price_per_g_eur"):
            with self.subTest(field=field):
                item = copy.deepcopy(self.items["ALT-CAP-001"])
                item[field] = None
                with self.assertRaises(CostDataError):
                    calculate_candidate_cost(item, self.cap)

    def test_potential_and_excluded_are_not_scored(self):
        results = {x["candidate_id"]: x for x in score_component_candidates(CURRENT)}
        for candidate_id in ("ALT-CAP-001", "ALT-CAP-002", "ALT-CAP-003"):
            self.assertIn("cost_score", results[candidate_id])
        for candidate_id in ("ALT-CAP-004", "ALT-CAP-005", "ALT-CAP-006"):
            self.assertEqual(results[candidate_id]["scoring_status"], "NOT_SCORED")
            self.assertNotIn("cost_score", results[candidate_id])


if __name__ == "__main__":
    unittest.main()
