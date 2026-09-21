# SwitchMatter MVP0 Product Specification

## 1. Objective

SwitchMatter MVP0 validates whether the core material-selection workflow can function end to end.

The core flow is:

`PDF Extraction -> Regulation Screening -> Scoring -> Ranking`

MVP0 is not intended to be a complete PPWR compliance product.

## 2. Sample product

MVP0 uses one sample packaging system:

**PET Beverage Bottle Package**

Supported components:

- `bottle_body`
- `cap`
- `label`

The user does not choose between unrelated product categories. The product context is fixed for MVP0; the replaceable unit is the component.

## 3. PDF input

Current product/component data must come from an actual uploaded PDF containing embedded text.

The system must not return hard-coded extracted values based on filename or sample identity.

### Extraction target

Parse only:

1. `component`
2. `current_material`
3. `thickness`
4. `food_contact`

If a field cannot be determined from explicit text using the deterministic rules, return `null`.

## 4. User confirmation

The extraction result must be editable before downstream processing.

The user-confirmed value is authoritative.

The system must never silently overwrite a user-confirmed value using parser output or database assumptions.

## 5. Component selection

If `component` is missing, show a component selector:

- Bottle Body
- Cap
- Label

The user may also correct an extracted component before confirmation.

## 6. Alternative material source

MVP0 alternative candidates are stored in `data/alternative_materials.json`.

Do not search the web, query suppliers, generate new candidates, or use AI to discover materials.

Candidates must be filtered by `component` before regulation screening.

## 7. Regulation screening

MVP0 uses the simplified rules in `data/regulations.json`.

Each applicable rule returns:

- `PASS`
- `FAIL`
- `UNKNOWN`
- `NOT_APPLICABLE`

Candidate-level status:

### EXCLUDED

At least one applicable rule returns `FAIL`.

Excluded candidates never enter scoring.

### POTENTIAL

No rule returns `FAIL`, but at least one applicable rule returns `UNKNOWN`.

Potential Candidates do not automatically enter scoring.

The user can either:

- provide the missing data and re-run screening, or
- exclude the candidate from the current analysis.

### ELIGIBLE

All applicable evaluated rules return `PASS` and no applicable rule is UNKNOWN.

Eligible Candidates enter scoring.

## 8. Scoring

MVP0 scoring contains only:

- Cost Score
- Properties Score

Recyclability Score is explicitly excluded from MVP0 because a defensible scoring model requires additional package-design and recycling-system data.

## 9. Cost simulation assumption

For a selected component, geometry and volume are fixed for all candidates.

Candidate mass is determined from configured component volume and candidate density.

Candidate material cost is determined from candidate mass and price per gram.

Do not optimize candidate thickness or geometry.

## 10. Properties fit

Each component has configured required properties.

Each alternative candidate stores values for those properties.

Properties Score measures candidate values against component requirements.

## 11. Final score

MVP0 uses fixed equal weights:

- Cost: 50%
- Properties: 50%

User-configurable weights are future scope.

## 12. Ranking

Only Eligible Candidates are ranked.

Ranking order is Final Score descending.

Potential and Excluded Candidates must remain visible in a separate section with reasons.

## 13. Out of scope

MVP0 does not include:

- LLM / AI extraction
- OCR fallback
- automatic supplier search
- external material database integration
- AI-generated candidate materials
- full PPWR legal-compliance coverage
- Recyclability Score
- material-specific geometry optimization
- material-specific thickness optimization
- mechanical / FEA simulation
- user-defined scoring weights
- automatic guessing of missing information

## 14. Future-compatible architecture

The parser boundary must be replaceable.

MVP0:

`raw PDF text -> deterministic parser -> CurrentComponent JSON`

Future:

`raw PDF text -> LLM extractor -> same CurrentComponent JSON`

Downstream screening and scoring must not depend on which extraction method produced the confirmed JSON.
