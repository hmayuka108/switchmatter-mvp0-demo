# SwitchMatter MVP0 Starter Pack

This repository starter defines the implementation contract for SwitchMatter MVP0.

## MVP0 goal

Build and validate this end-to-end flow:

`PDF -> native text extraction -> rule-based JSON extraction -> user confirmation -> component selection -> PPWR-based sample regulation screening -> scoring -> ranking`

MVP0 deliberately does **not** use an LLM. Missing information must never be guessed.

## Read before coding

1. `AGENTS.md`
2. `docs/SPEC.md`
3. `docs/DATA_SCHEMA.md`
4. `docs/SCORING_LOGIC.md`
5. `docs/TASKS.md`

## Sample data

- `data/product_config.json`
- `data/alternative_materials.json`
- `data/regulations.json`

## Sample PDFs

- `sample_pdfs/pet_bottle_cap_spec.pdf`
- `sample_pdfs/pet_bottle_label_spec.pdf`

These PDFs contain embedded text and are intended to test native PDF extraction without OCR or AI.

## Legal note

The regulation dataset is a simplified MVP0 test fixture inspired by PPWR. It is **not** a production compliance engine and must not be presented as legal advice or definitive PPWR compliance.
