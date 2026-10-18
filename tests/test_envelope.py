from pathlib import Path
import sys, unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from switchmatter.envelope import empty_envelope,load_registry,set_value,tier_completeness

class EnvelopeTests(unittest.TestCase):
 def test_registry_and_unknowns(self):
  registry=load_registry();self.assertTrue({"pack_format","target_markets","food_contact","filling_line_temperature"}.issubset({f["field_key"] for f in registry["fields"]}))
  env=empty_envelope("A",registry);self.assertIsNone(env["values"]["food_contact"]["value"]);self.assertEqual(env["values"]["food_contact"]["status"],"unknown")
 def test_units_confirmation_priority_and_history(self):
  env=empty_envelope("A")
  with self.assertRaises(ValueError):set_value(env,"filling_line_temperature",85,unit="F",status="confirmed")
  set_value(env,"food_contact",False,status="extracted_unconfirmed",source_ref="S!B2");set_value(env,"food_contact",True,status="confirmed",confirmed_by="u");set_value(env,"food_contact",False,status="default_assumed")
  self.assertIs(env["values"]["food_contact"]["value"],True);self.assertEqual(env["history"][1]["source_ref"],"S!B2")
 def test_completeness_and_sku_isolation(self):
  a,b=empty_envelope("A"),empty_envelope("B");set_value(a,"pack_format","bottle",status="confirmed")
  self.assertNotEqual(tier_completeness(a)["T1"]["confirmed"],tier_completeness(b)["T1"]["confirmed"]);self.assertEqual(b["values"]["pack_format"]["status"],"unknown")
  set_value(a,"pack_format",None,status="unknown",source_type="user");self.assertIn("pack_format",tier_completeness(a)["T1"]["missing"])
if __name__=="__main__":unittest.main()
