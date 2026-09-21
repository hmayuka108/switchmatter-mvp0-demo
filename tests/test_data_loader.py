from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.data_loader import (
    filter_candidates_by_component,
    load_alternative_materials,
    load_candidates_for_component,
    load_product_config,
    load_regulations,
)


class DataLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = load_alternative_materials()

    def test_databases_load_and_ids_are_unique(self):
        self.assertTrue(self.candidates)
        candidate_ids = [item["candidate_id"] for item in self.candidates]
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        rules = load_regulations()
        self.assertTrue(rules)
        rule_ids = [item["rule_id"] for item in rules]
        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        self.assertTrue(load_product_config()["components"])

    def test_cap_filter(self):
        matches = filter_candidates_by_component(self.candidates, "cap")
        self.assertTrue(matches)
        self.assertTrue(all(item["component"] == "cap" for item in matches))

    def test_label_filter(self):
        matches = filter_candidates_by_component(self.candidates, "label")
        self.assertTrue(matches)
        self.assertTrue(all(item["component"] == "label" for item in matches))

    def test_unknown_component_returns_empty_list(self):
        self.assertEqual(load_candidates_for_component("unknown_component"), [])
        self.assertEqual(load_candidates_for_component(None), [])

    def test_null_values_are_preserved(self):
        item = next(x for x in self.candidates if x["candidate_id"] == "ALT-CAP-005")
        self.assertIsNone(item["regulation_data"]["pfas_compliant"])
        self.assertIsNone(item["regulation_data"]["compostable"])


if __name__ == "__main__":
    unittest.main()
