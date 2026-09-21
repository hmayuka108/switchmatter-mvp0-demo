# AI Coding Agent Instructions - SwitchMatter MVP0

## 1. Source of truth

The files in `docs/` define the product and implementation contract. Read all of them before changing code.

When implementation convenience conflicts with these documents, follow the documents.

## 2. Do not invent requirements

Do not add fields, scoring dimensions, regulations, AI features, external APIs, supplier search, or recommendation logic unless explicitly requested.

If a value is absent from the source PDF or configured data, use `null` / `UNKNOWN`. Never infer a value from general knowledge.

Examples of forbidden inference:

- `HDPE -> component must be cap`
- `PET -> food_contact must be true`
- missing thickness -> use a typical industry thickness

## 3. MVP0 has no AI / LLM

PDF information extraction must use:

- native text extraction, e.g. PyMuPDF or pdfplumber
- regex
- keyword dictionaries
- deterministic normalization rules

Do not add OpenAI, Anthropic, Gemini, OCR, embeddings, vector databases, or other AI services in MVP0.

## 4. Required pipeline

Implement the following order:

1. User uploads a text-embedded PDF.
2. Extract raw text from the PDF.
3. Parse only the four current-component fields defined in `DATA_SCHEMA.md`.
4. Missing fields become `null`.
5. Show extracted fields to the user for confirmation/editing.
6. Confirmed user values become the source of truth.
7. User selects the component to replace if component is missing or wishes to change it.
8. Load alternative candidates matching that component.
9. Run regulation screening.
10. `FAIL` candidates are excluded.
11. Candidates with no FAIL but one or more UNKNOWN are Potential Candidates and do not automatically enter scoring.
12. All-PASS candidates are Eligible and enter scoring.
13. Calculate Cost Score and Properties Score.
14. Calculate Final Score using fixed 50/50 weights.
15. Rank Eligible Candidates by Final Score descending.

## 5. Scoring rules are fixed

Do not change formulas in `docs/SCORING_LOGIC.md`.

MVP0 scoring dimensions are only:

- Cost
- Properties

Do not implement Recyclability Score in MVP0.

## 6. Geometry assumption

For each component, all alternative materials use the same configured component volume and geometry.

Do not attempt thickness optimization, structural simulation, finite element analysis, or material-specific geometry optimization.

## 7. Regulation rules

`data/regulations.json` is a sample test fixture. Keep regulation evaluation deterministic.

The application must distinguish:

- rule result: `PASS | FAIL | UNKNOWN | NOT_APPLICABLE`
- candidate status: `ELIGIBLE | POTENTIAL | EXCLUDED`

## 8. Preserve explainability

For every regulation result, keep:

- rule id
- evaluated field(s)
- value used
- result
- human-readable reason

For every score, retain intermediate calculations so the UI can explain where the score came from.

## 9. Tests

Before considering a task complete, verify the acceptance criteria in `docs/TASKS.md` and the examples in `tests/expected_behaviour.json`.
