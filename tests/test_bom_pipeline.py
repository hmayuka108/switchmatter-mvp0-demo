from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from switchmatter.bom import component_from_pdf_text,import_bom_xlsx,new_component,set_component_property,bom_for_sku
from switchmatter.pdf_extractor import extract_text
from test_excel_intake import workbook

class BOMTests(unittest.TestCase):
 def test_existing_pdf_and_multi_component(self):
  result=component_from_pdf_text(extract_text(ROOT/"sample_pdfs"/"pet_bottle_cap_spec.pdf"),"A","D1")
  self.assertEqual(result["component"]["component_type"],"closure");self.assertEqual(result["component"]["properties"]["polymer"]["value"],"HDPE")
  self.assertEqual(len(bom_for_sku([result["component"],new_component("A","label"),new_component("B","ink")],"A")),2)
 def test_units_and_no_unrelated_inference(self):
  result=component_from_pdf_text("Component: Label\nFilm thickness: 50 um\nProduct: PET bottle","A","D")
  self.assertEqual(result["component"]["properties"]["thickness_mm"]["value"],.05);self.assertIsNone(result["component"]["properties"]["polymer"]["value"])
 def test_missing_evidence_and_override_history(self):
  c=new_component("A","adhesive");self.assertEqual(c["properties"]["polymer"]["status"],"unknown")
  set_component_property(c,"polymer","PP",status="extracted_unconfirmed",source_ref="D:p1");set_component_property(c,"polymer","PE",status="confirmed",confirmed_by="u")
  self.assertEqual(c["properties"]["polymer"]["value"],"PE");self.assertEqual(c["history"][-1]["source_ref"],"D:p1")
 def test_bom_excel_intake(self):
  result=import_bom_xlsx(workbook([["Component ID","Component Type","Polymer","Mass g","Extra"],["C1","cap","HDPE","2.5","keep"]]),"A")
  c=result["components"][0];self.assertEqual(c["component_type"],"closure");self.assertEqual(c["properties"]["mass_g"]["value"],2.5);self.assertEqual(c["properties"]["polymer"]["status"],"extracted_unconfirmed");self.assertEqual(result["unmapped"][0]["value"],"keep")
if __name__=="__main__":unittest.main()
