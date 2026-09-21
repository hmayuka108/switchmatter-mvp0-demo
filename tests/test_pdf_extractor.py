"""Tests for native PDF text extraction."""

from pathlib import Path
import sys
import unittest


MVP0_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MVP0_ROOT / "src"))

from switchmatter.pdf_extractor import PDFExtractionError, extract_text


class PDFExtractorTests(unittest.TestCase):
    def test_cap_sample_contains_expected_native_text(self) -> None:
        text = extract_text(MVP0_ROOT / "sample_pdfs" / "pet_bottle_cap_spec.pdf")

        expected_fragments = (
            "Component: Bottle Cap",
            "Material: High-density polyethylene (HDPE)",
            "Nominal thickness: 1.20 mm",
            "Suitable for direct food contact",
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_label_sample_returns_embedded_text(self) -> None:
        text = extract_text(MVP0_ROOT / "sample_pdfs" / "pet_bottle_label_spec.pdf")

        self.assertIn("Component: Wraparound Label", text)
        self.assertIn("Material: Polypropylene (PP)", text)
        self.assertIn("Film thickness: 0.05 mm", text)

    def test_missing_pdf_raises_explicit_error(self) -> None:
        missing_pdf = MVP0_ROOT / "sample_pdfs" / "does_not_exist.pdf"

        with self.assertRaisesRegex(PDFExtractionError, "does not exist"):
            extract_text(missing_pdf)


if __name__ == "__main__":
    unittest.main()
