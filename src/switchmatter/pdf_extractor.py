"""Native PDF text extraction for SwitchMatter MVP0."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import fitz


class PDFExtractionError(RuntimeError):
    """Raised when a PDF cannot be opened or its text cannot be extracted."""


def extract_text(pdf_path: str | Path) -> str:
    """Return embedded text from a PDF without OCR or content inference.

    A valid PDF with no extractable embedded text returns an empty string.
    Missing, non-file, or invalid PDF inputs raise ``PDFExtractionError``.
    """

    path = Path(pdf_path)
    if not path.is_file():
        raise PDFExtractionError(f"PDF file does not exist: {path}")
    if path.suffix.lower() != ".pdf":
        raise PDFExtractionError(f"Expected a PDF file: {path}")

    try:
        with fitz.open(path) as document:
            if not document.is_pdf:
                raise PDFExtractionError(f"File is not a valid PDF: {path}")
            return "".join(page.get_text() for page in document)
    except PDFExtractionError:
        raise
    except (fitz.FileDataError, OSError, RuntimeError, ValueError) as exc:
        raise PDFExtractionError(f"Could not extract text from PDF: {path}") from exc


def extract_text_bytes(pdf_bytes: bytes) -> str:
    """Return embedded text from in-memory PDF bytes without a temporary file."""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            if not document.is_pdf:
                raise PDFExtractionError("Uploaded file is not a valid PDF")
            return "".join(page.get_text() for page in document)
    except PDFExtractionError:
        raise
    except (fitz.FileDataError, OSError, RuntimeError, ValueError) as exc:
        raise PDFExtractionError("Could not extract text from uploaded PDF") from exc


def main(argv: Sequence[str] | None = None) -> int:
    """Print extracted PDF text for simple local/command-line use."""

    parser = argparse.ArgumentParser(description="Extract embedded text from a PDF.")
    parser.add_argument("pdf_path", type=Path, help="Path to a text-embedded PDF")
    args = parser.parse_args(argv)

    try:
        text = extract_text(args.pdf_path)
    except PDFExtractionError as exc:
        parser.exit(1, f"Extraction failed: {exc}\n")

    if not text:
        parser.exit(1, "Extraction failed: PDF contains no extractable embedded text.\n")

    print(text, end="" if text.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
