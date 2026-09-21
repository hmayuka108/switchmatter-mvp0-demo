from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from switchmatter.pipeline import extract_and_parse,run_analysis,run_pipeline
class PipelineTests(unittest.TestCase):
 def test_boundary(self):
  path=ROOT/"sample_pdfs"/"pet_bottle_cap_spec.pdf";out=run_pipeline(path)
  self.assertNotIn("screening",out);self.assertNotIn("ranking",out)
  self.assertEqual(run_analysis(extract_and_parse(path)["current_component"])["analysis_status"],"COMPLETE")
 def test_stop(self):
  self.assertEqual(run_analysis({"component":None})["analysis_status"],"STOPPED")
if __name__=="__main__":unittest.main()
