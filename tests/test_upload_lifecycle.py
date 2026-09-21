from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.pdf_extractor import PDFExtractionError
from switchmatter.streamlit_ui import load_upload
from switchmatter.ui_safety import extraction_error_message


class UploadLifecycleTests(unittest.TestCase):
    def test_corrupt_upload_preserves_original_extraction_error(self):
        with self.assertRaises(PDFExtractionError) as context:
            load_upload(b"not a PDF")
        message = extraction_error_message(context.exception)
        self.assertIn("could not be read", message)
        self.assertNotIn("PermissionError", message)
        self.assertNotIn("Traceback", message)
