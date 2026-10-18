from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from switchmatter.bom import new_component,set_component_property
from switchmatter.envelope import empty_envelope,set_value
from switchmatter.legal_gates import evaluate_rule,evaluate_legal_gates
from switchmatter.verdict import aggregate_results,build_verdict

def rule(**kw):
 base={"rule_id":"R","applies_when":{},"attribute":"x","operator":"max","value":10,"ref_verified":True,"source_doc":"law"};base.update(kw);return base
class LegalVerdictTests(unittest.TestCase):
 def setUp(self):self.env=empty_envelope("A");self.c=new_component("A","closure","C")
 def test_missing_and_unknown_applicability(self):
  self.assertEqual(evaluate_rule(rule(),self.env,self.c)["result"],"UNKNOWN");self.assertEqual(evaluate_rule(rule(applies_when={"food_contact":True}),self.env,self.c)["result"],"UNKNOWN")
 def test_confirmed_out_of_scope(self):
  set_value(self.env,"food_contact",False,status="confirmed");self.assertEqual(evaluate_rule(rule(applies_when={"food_contact":True}),self.env,self.c)["result"],"NOT_APPLICABLE")
 def test_fail_pass_and_unverified(self):
  set_component_property(self.c,"x",11,status="confirmed");self.assertEqual(evaluate_rule(rule(),self.env,self.c)["result"],"FAIL")
  set_component_property(self.c,"x",9,status="confirmed");self.assertEqual(evaluate_rule(rule(),self.env,self.c)["result"],"PASS");self.assertEqual(evaluate_rule(rule(ref_verified=False),self.env,self.c)["result"],"UNKNOWN")
 def test_verdict_priority_and_coverage(self):
  p={"result":"PASS","reason":"p","missing":[]};u={"result":"UNKNOWN","reason":"u","missing":["x"]};f={"result":"FAIL","reason":"f","missing":[]}
  self.assertEqual(aggregate_results([p],True)["verdict"],"KEEP");self.assertEqual(aggregate_results([p,u],True)["verdict"],"HOLD");self.assertEqual(aggregate_results([u,f],True)["verdict"],"REMOVE");self.assertEqual(aggregate_results([p],False)["verdict"],"HOLD")
 def test_default_registry_holds_component_and_sku(self):
  verdict=build_verdict(evaluate_legal_gates(self.env,[self.c]),[self.c]);self.assertEqual(verdict["verdict"],"HOLD");self.assertEqual(verdict["components"]["C"]["verdict"],"HOLD");self.assertTrue(verdict["missing_information"])
if __name__=="__main__":unittest.main()
