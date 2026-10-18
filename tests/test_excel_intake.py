from io import BytesIO
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from switchmatter.excel_intake import import_envelope_xlsx

def workbook(rows):
 sheet=''.join(f'<row r="{i}">'+''.join(f'<c r="{chr(65+j)}{i}" t="inlineStr"><is><t>{v}</t></is></c>' for j,v in enumerate(row))+'</row>' for i,row in enumerate(rows,1))
 out=BytesIO()
 with ZipFile(out,'w',ZIP_DEFLATED) as z:
  z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Products" sheetId="1" r:id="rId1"/></sheets></workbook>')
  z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="x"/></Relationships>')
  z.writestr('xl/worksheets/sheet1.xml',f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet}</sheetData></worksheet>')
 return out.getvalue()

class ExcelIntakeTests(unittest.TestCase):
 def test_mapping_unmapped_missing_and_confirmation(self):
  result=import_envelope_xlsx(workbook([["Pack Format","Mystery"],["Bottle","raw"]]),"SKU");rec=result["envelope"]["values"]["pack_format"]
  self.assertEqual((rec["value"],rec["status"],rec["source_ref"]),("Bottle","extracted_unconfirmed","Products!A2"));self.assertEqual(result["envelope"]["values"]["food_contact"]["status"],"unknown");self.assertEqual(result["unmapped"][0]["value"],"raw")
 def test_conflicts_are_not_silently_resolved(self):
  result=import_envelope_xlsx(workbook([["Market","Target Markets"],["EU","JP"]]),"SKU")
  self.assertEqual(len(result["conflicts"]),1);self.assertEqual(result["envelope"]["values"]["target_markets"]["status"],"unknown")
if __name__=="__main__":unittest.main()
