from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from switchmatter.final_scoring import calculate_final_score, combine_scoring_results, score_and_rank_component


class FinalScoringTests(unittest.TestCase):
    def test_formula_precision_and_missing(self):
        self.assertEqual(calculate_final_score(6, 6), 6)
        self.assertAlmostEqual(calculate_final_score(6, 8.89), 7.445)
        self.assertIsNone(calculate_final_score(None, 8))
        self.assertIsNone(calculate_final_score(8, None))

    def test_ties_unrankable_and_competition_ranks(self):
        status = [("A", "ELIGIBLE"), ("B", "ELIGIBLE"), ("C", "ELIGIBLE"),
                  ("D", "POTENTIAL"), ("E", "EXCLUDED"), ("F", "ELIGIBLE")]
        screening = [{"candidate_id": k, "status": v} for k, v in status]
        costs = [{"candidate_id": k, "cost_score": v} for k, v in
                 (("A", 8), ("B", 8), ("C", 7), ("D", 10), ("E", 10))]
        props = [{"candidate_id": k, "properties_score": v} for k, v in
                 (("A", 8), ("B", 8), ("C", 8), ("D", 10), ("E", 10), ("F", 8))]
        output = combine_scoring_results(screening, costs, props)
        self.assertEqual([(x["candidate_id"], x["rank"]) for x in output["ranking"]],
                         [("A", 1), ("B", 1), ("C", 3)])
        by_id = {x["candidate_id"]: x for x in output["results"]}
        for key in ("D", "E", "F"):
            self.assertIsNone(by_id[key]["final_score"])
            self.assertIsNone(by_id[key]["rank"])

    def test_cap_ranking_uses_full_precision(self):
        output = score_and_rank_component({"component": "cap", "food_contact": True})
        self.assertEqual([x["candidate_id"] for x in output["ranking"]],
                         ["ALT-CAP-001", "ALT-CAP-002", "ALT-CAP-003"])
        self.assertEqual(output["ranking"][0]["display_score"], 7.35)
        self.assertNotEqual(output["ranking"][0]["final_score"], 7.35)


if __name__ == "__main__":
    unittest.main()
