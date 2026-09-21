# Native PDF text extractor

The extractor reads only text embedded in a PDF. It does not use OCR, AI, field
parsing, inference, regulation screening, or scoring.

## Windows PowerShell

Run these commands from the repository root:

```powershell
cd .\MVP0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m switchmatter.pdf_extractor sample_pdfs\pet_bottle_cap_spec.pdf
python -m unittest discover -s tests -v
```

## macOS or Linux

Run these commands from the repository root:

```bash
cd MVP0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m switchmatter.pdf_extractor sample_pdfs/pet_bottle_cap_spec.pdf
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Python API

With `MVP0/src` on `PYTHONPATH`:

```python
from switchmatter.pdf_extractor import extract_text

text = extract_text("sample_pdfs/pet_bottle_cap_spec.pdf")
```

`extract_text` returns an empty string when a valid PDF contains no extractable
embedded text. It raises `PDFExtractionError` for missing, non-PDF, invalid, or
unreadable input. The command-line interface reports both situations as explicit
failures with exit status 1.
