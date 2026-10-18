# SwitchMatter Evidence Pipeline

This application implements the primary packaging compliance workflow through Step 3:

`Functional Envelope -> Component BOM -> Legal Gates -> KEEP / HOLD / REMOVE`

Legacy MVP0 extraction and scoring modules remain in the repository for regression compatibility, but scoring and ranking are not part of the primary Streamlit workflow. The new workflow does not load or require `data/product_config.json`.

## Architecture

- Step 0 stores independent per-SKU Functional Envelopes. Each field has a status, source, unit where required, and override history. Completeness is calculated separately for T1 through T4.
- Step 1 stores multiple components per SKU. A component has a materialized property view plus long-form measurements, evidence references, provenance, and history.
- Step 2 evaluates versioned rules as `PASS`, `FAIL`, `UNKNOWN`, or `NOT_APPLICABLE`. Unknown applicability never becomes non-applicable.
- Step 3 aggregates any FAIL to REMOVE, otherwise any UNKNOWN or incomplete rule coverage to HOLD, and only fully evaluated passing coverage to KEEP.

Runtime data is stored locally in `.switchmatter_data/pipeline.json` and is excluded from Git.

## Supported intake

- Brand product information: `.xlsx` worksheets with deterministic header aliases from `data/envelope_fields.json`. Mapped cells remain `extracted_unconfirmed`; absent fields remain unknown; unmapped cells and conflicting values are preserved.
- Supplier evidence: text-embedded PDF files using native PyMuPDF extraction and field-local deterministic parsing.
- Component BOM: `.xlsx` row tables with `Component Type` and optional component/property columns.

Scanned or image-only PDFs, `.xls`, password-protected workbooks, OCR, AI extraction, and hidden inference are not supported.

## Confirmation and unknowns

Imported values never become confirmed automatically. Users can confirm, edit, or explicitly mark values unknown. Confirmed user values supersede extracted or assumed values and prior records remain in history. A partial envelope or BOM can be saved. Missing and unknown T1 data is visible and prevents a KEEP verdict.

## Regulatory limitation

The supplied specification says its regulatory references, thresholds, methods, scope rules, and dates were not verified against source law. The included rule registry therefore keeps PFAS, heavy metals, food-contact, recycled-content, and tethered-closure rules unverified. They return UNKNOWN/HOLD and do not make definitive compliance claims. Verified source text, locus, version, applicability, and thresholds must be supplied before a rule can be activated.

## Functional Envelope limitation

The referenced full Functional Envelope specification was not supplied. The registry contains only the envelope fields explicitly named in the implementation brief. Add authoritative definitions to `data/envelope_fields.json`; the application and completeness logic are data-driven.

## Tests

From `MVP0` in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

The suite includes legacy PDF/parser regression tests and new envelope, Excel, BOM, legal-gate, and verdict tests.
