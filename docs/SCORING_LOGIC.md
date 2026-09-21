# SwitchMatter MVP0 Screening and Scoring Logic

## 1. Regulation Screening

Evaluate each candidate only against applicable sample rules.

### Rule result

For an applicable rule:

- required value exists and meets rule -> `PASS`
- required value exists and violates rule -> `FAIL`
- required value is missing (`null`) -> `UNKNOWN`

For a non-applicable rule -> `NOT_APPLICABLE`

### Candidate status

Use this priority:

1. If **any applicable rule = FAIL** -> `EXCLUDED`
2. Else if **any applicable rule = UNKNOWN** -> `POTENTIAL`
3. Else -> `ELIGIBLE`

Only `ELIGIBLE` candidates enter scoring.

## 2. Cost Simulation

MVP0 assumes a fixed geometry and fixed component volume for all candidate materials.

### Candidate mass

`candidate_mass_g = component_volume_cm3 * candidate_density_g_cm3`

### Candidate material cost

`candidate_cost_eur = candidate_mass_g * candidate_price_per_g_eur`

### Current material baseline mass

`current_mass_g = component_volume_cm3 * current_density_g_cm3`

### Current material baseline cost

`current_cost_eur = current_mass_g * current_price_per_g_eur`

## 3. Cost Score

The current material is the reference point and receives a conceptual score of 5 when candidate cost equals current cost.

Formula:

`raw_cost_score = 5 + 5 * (current_cost_eur - candidate_cost_eur) / current_cost_eur`

Then clip:

`cost_score = min(10, max(0, raw_cost_score))`

Interpretation:

- same cost as current -> 5
- cheaper than current -> above 5
- more expensive than current -> below 5
- zero candidate cost -> 10
- 2x current cost or higher -> 0 after clipping

Do **not** use candidate-set min-max normalization in MVP0.

## 4. Properties Score

Each selected component defines required property values in `product_config.json`.

For every required property:

`property_score = min(candidate_value / required_value, 1) * 10`

If candidate value is missing, the scoring function should not invent a value. MVP0 implementation should mark the candidate as `SCORING_DATA_INCOMPLETE` and not produce a final ranking score until the missing property is provided or the candidate is excluded from the current analysis.

Overall Properties Score:

`properties_score = mean(all individual property scores)`

All configured required properties are equally weighted in MVP0.

## 5. Final Score

Fixed MVP0 weights:

- Cost Score = 50%
- Properties Score = 50%

Formula:

`final_score = 0.5 * cost_score + 0.5 * properties_score`

No user-defined weight control in MVP0.

## 6. Ranking

Rank only candidates that are:

- `ELIGIBLE` after regulation screening, and
- complete enough to calculate both Cost and Properties scores.

Order:

`final_score DESC`

If two scores are equal to displayed precision, preserve deterministic order by `candidate_id ASC`.

## 7. Recyclability

Recyclability is **not a scoring dimension in MVP0**.

Do not invent fixed recyclability scores or compatibility matrices.

A simplified regulation fixture may contain a recyclability-related boolean/status only to exercise regulation-screening architecture. This must not be presented as a calculated Recyclability Score.
