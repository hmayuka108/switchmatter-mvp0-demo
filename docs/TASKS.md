# SwitchMatter MVP0 Implementation Tasks

Implement in this order. Do not build later steps before the previous step has a passing smoke test.

## Task 0 - Project setup

- Keep existing application framework if one already exists.
- Add a backend/server function layer if needed for PDF parsing.
- Add deterministic test commands.
- Do not add AI dependencies.

Acceptance:

- App runs locally.
- Tests can run locally.

## Task 1 - Load sample configuration and databases

Load:

- `data/product_config.json`
- `data/alternative_materials.json`
- `data/regulations.json`

Acceptance:

- JSON validates at startup/test time.
- Candidate IDs and regulation IDs are unique.

## Task 2 - PDF native text extraction

Use PyMuPDF or pdfplumber.

Input: uploaded text-embedded PDF.

Output: raw text string.

Acceptance using `pet_bottle_cap_spec.pdf`:

Raw text contains all of these fragments:

- `Component: Bottle Cap`
- `Material: High-density polyethylene (HDPE)`
- `Nominal thickness: 1.20 mm`
- `Suitable for direct food contact`

No OCR is required.

## Task 3 - Rule-based field parser

Extract:

- component
- current_material
- thickness.value + thickness.unit
- food_contact

Acceptance for cap sample:

```json
{
  "component": "cap",
  "current_material": "HDPE",
  "thickness": {"value": 1.2, "unit": "mm"},
  "food_contact": true
}
```

Acceptance for label sample:

- component = `label`
- current_material = `PP`
- thickness = 0.05 mm
- food_contact = null because the PDF deliberately does not explicitly state food-contact status

Parser must not infer missing food-contact status from material or product context.

## Task 4 - Confirmation UI

Show extracted fields in editable controls.

Acceptance:

- User can edit every field.
- Missing fields are clearly shown.
- Clicking Confirm creates the confirmed CurrentComponent object.
- Downstream logic uses confirmed values, not original parser values.

## Task 5 - Component candidate filtering

Filter alternative materials by confirmed/selected component.

Acceptance:

- `cap` shows only cap candidates.
- `label` shows only label candidates.

## Task 6 - Regulation engine

Implement evaluation types used by sample data:

- `numeric_max`
- `boolean_required`
- `numeric_min`
- `boolean_status_required`

Implement applicability filters used by the fixtures.

Acceptance:

- any FAIL -> EXCLUDED
- no FAIL + UNKNOWN -> POTENTIAL
- all applicable PASS -> ELIGIBLE
- non-applicable rules do not cause UNKNOWN
- every rule result includes an explanation

## Task 7 - Potential Candidate flow

Acceptance:

- Potential candidates are not scored automatically.
- Missing regulation fields are displayed.
- User can exclude the candidate for this run.
- Architecture allows future manual completion + re-screening.

Full database-editing UI is not required for MVP0 unless explicitly requested.

## Task 8 - Cost simulation

Acceptance:

- Uses component volume from product config.
- Uses candidate density and price/g.
- Computes candidate mass and cost.
- Computes current baseline mass and cost.
- Cost Score exactly follows `SCORING_LOGIC.md`.

## Task 9 - Properties scoring

Acceptance:

- Uses requirements from selected component config.
- Uses candidate property values.
- Each property is capped at score 10.
- Overall Properties Score is arithmetic mean.
- Missing required property does not get guessed.

## Task 10 - Final score and ranking

Acceptance:

- Final = 0.5 Cost + 0.5 Properties.
- Display score rounded to 2 decimals.
- Sort eligible, score-complete candidates descending.
- Potential and Excluded sections remain separate.

## Task 11 - Results UI

For each scored candidate display:

- candidate name/material
- regulation status
- estimated mass
- estimated material cost per component
- Cost Score
- Properties Score
- Final Score
- rank

For Potential / Excluded display reason(s).

## Task 12 - End-to-end smoke test

Required path:

1. Upload cap sample PDF.
2. Extract text.
3. Parse fields.
4. Confirm fields.
5. Load cap alternatives.
6. Run screening.
7. Observe at least one Eligible, one Potential, and one Excluded candidate.
8. Score Eligible candidates.
9. Display deterministic ranking.
