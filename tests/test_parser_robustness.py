from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from switchmatter.parser import parse_current_component,parse_pdf
class ParserRobustnessTests(unittest.TestCase):
 def test_variant(self):
  actual=parse_pdf(ROOT/"sample_pdfs"/"pet_bottle_cap_spec_variant.pdf")
  self.assertEqual(actual,{"component":"cap","current_material":"HDPE",
   "thickness":{"value":1.1,"unit":"mm"},"food_contact":True})
 def test_pet_context_is_not_cap_material(self):
  text="Product / component\nClosure for PET beverage bottles\nResin\nUnspecified"
  self.assertIsNone(parse_current_component(text)["current_material"])
 def test_quoted_food_phrase_is_not_evidence(self):
  text='Testing note: phrase "suitable for food contact" is not present.'
  self.assertIsNone(parse_current_component(text)["food_contact"])
if __name__=="__main__":unittest.main()
