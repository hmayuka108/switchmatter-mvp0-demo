import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.data_loader import (
    load_alternative_materials, load_product_config, load_regulations
)
from switchmatter.regulation_engine import evaluate_rule, screen_candidate


CURRENT = {"component": "cap", "current_material": "HDPE",
           "thickness": {"value": 1.2, "unit": "mm"}, "food_contact": True}


class RegulationEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = {x["candidate_id"]: x for x in load_alternative_materials()}
        cls.rules = load_regulations()
        cls.config = load_product_config()

    def screen(self, candidate_id):
        return screen_candidate(
            self.candidates[candidate_id], CURRENT, self.rules, self.config
        )

    def test_all_pass_candidate_is_eligible(self):
        self.assertEqual(self.screen("ALT-CAP-001")["status"], "ELIGIBLE")

    def test_one_fail_excludes_candidate(self):
        self.assertEqual(self.screen("ALT-CAP-004")["status"], "EXCLUDED")

    def test_unknown_without_fail_is_potential(self):
        result = self.screen("ALT-CAP-005")
        self.assertEqual(result["status"], "POTENTIAL")
        pfas = next(x for x in result["rule_results"] if x["rule_id"] == "REG-002")
        self.assertEqual(pfas["result"], "UNKNOWN")

    def test_fail_takes_precedence_over_unknown(self):
        candidate = copy.deepcopy(self.candidates["ALT-CAP-005"])
        candidate["regulation_data"]["heavy_metals_mg_kg"] = 135
        result = screen_candidate(candidate, CURRENT, self.rules, self.config)
        self.assertEqual(result["status"], "EXCLUDED")
        outcomes = {x["result"] for x in result["rule_results"]}
        self.assertIn("FAIL", outcomes)
        self.assertIn("UNKNOWN", outcomes)

    def test_not_applicable_does_not_affect_status(self):
        result = self.screen("ALT-CAP-001")
        compost = next(x for x in result["rule_results"] if x["rule_id"] == "REG-005")
        self.assertEqual(compost["result"], "NOT_APPLICABLE")
        self.assertEqual(result["status"], "ELIGIBLE")

    def test_unrelated_component_rule_is_not_applied(self):
        rule = next(x for x in self.rules if x["rule_id"] == "REG-005")
        result = evaluate_rule(rule, self.candidates["ALT-CAP-001"], CURRENT, self.config)
        self.assertEqual(result["result"], "NOT_APPLICABLE")

    def test_null_remains_unknown_not_fail(self):
        result = self.screen("ALT-CAP-005")
        pfas = next(x for x in result["rule_results"] if x["rule_id"] == "REG-002")
        self.assertIsNone(pfas["values_used"]["pfas_compliant"])
        self.assertEqual(pfas["result"], "UNKNOWN")

    def test_expected_behaviour_fixture(self):
        expected = json.loads((ROOT / "tests" / "expected_behaviour.json").read_text())
        statuses = expected["screening_examples_for_cap_food_contact_true"]
        actual = {candidate_id: self.screen(candidate_id)["status"] for candidate_id in statuses}
        self.assertEqual(actual, statuses)


if __name__ == "__main__":
    unittest.main()
