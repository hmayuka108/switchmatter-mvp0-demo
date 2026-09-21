# SwitchMatter MVP0 Data Schema

## 1. Confirmed Current Component

The extraction/parser output before confirmation and the user-confirmed object use the same basic shape.

```json
{
  "product": "PET Beverage Bottle Package",
  "component": "cap",
  "current_material": "HDPE",
  "thickness": {
    "value": 1.2,
    "unit": "mm"
  },
  "food_contact": true
}
```

### Nullable fields

The parser may output `null` when information is not explicitly found.

```json
{
  "product": "PET Beverage Bottle Package",
  "component": null,
  "current_material": "HDPE",
  "thickness": null,
  "food_contact": null
}
```

### Allowed component values

- `bottle_body`
- `cap`
- `label`
- `null`

### Thickness

```json
{
  "value": 1.2,
  "unit": "mm"
}
```

MVP0 should preserve the unit extracted from the PDF. Conversion can happen in a helper function only when a downstream calculation requires a normalized unit.

## 2. Product Configuration

Stored in `data/product_config.json`.

This is sample configuration used for scoring. It is not extracted from the PDF in MVP0.

Each component contains:

- fixed volume
- baseline current-material cost inputs
- property requirements

Example:

```json
{
  "component": "cap",
  "volume_cm3": 3.0,
  "baseline": {
    "material": "HDPE",
    "density_g_cm3": 0.95,
    "price_per_g_eur": 0.0017
  },
  "property_requirements": {
    "stiffness": 8,
    "chemical_resistance": 7,
    "sealability": 9
  }
}
```

## 3. Alternative Material Candidate

Stored in `data/alternative_materials.json`.

Scores are never stored directly.

```json
{
  "candidate_id": "ALT-CAP-001",
  "name": "Recycled PP 35",
  "component": "cap",
  "material": "rPP",
  "density_g_cm3": 0.90,
  "price_per_g_eur": 0.0019,
  "properties": {
    "stiffness": 8,
    "chemical_resistance": 8,
    "sealability": 9
  },
  "regulation_data": {
    "heavy_metals_mg_kg": 35,
    "pfas_compliant": true,
    "recycled_content_pct": 35,
    "recyclability_ready": true,
    "compostable": null
  }
}
```

### Missing alternative data

Use `null`. Do not supply a guessed value.

## 4. Regulation Rule

Stored in `data/regulations.json`.

Rules are declarative where practical.

```json
{
  "rule_id": "REG-001",
  "source": "PPWR sample rule",
  "article_reference": "Article 5(4)",
  "name": "Heavy metals total limit",
  "description": "Sample MVP0 screening rule for total Pb + Cd + Hg + Cr(VI).",
  "applicability": {
    "components": ["bottle_body", "cap", "label"]
  },
  "required_fields": ["heavy_metals_mg_kg"],
  "evaluation": {
    "type": "numeric_max",
    "field": "heavy_metals_mg_kg",
    "max": 100,
    "unit": "mg/kg"
  },
  "mvp0_note": "Simplified test fixture; not a complete legal-compliance determination."
}
```

## 5. Regulation Evaluation Result

```json
{
  "rule_id": "REG-001",
  "result": "PASS",
  "values_used": {
    "heavy_metals_mg_kg": 35
  },
  "reason": "35 mg/kg is at or below the configured maximum of 100 mg/kg."
}
```

Allowed results:

- `PASS`
- `FAIL`
- `UNKNOWN`
- `NOT_APPLICABLE`

## 6. Candidate Screening Result

```json
{
  "candidate_id": "ALT-CAP-001",
  "status": "ELIGIBLE",
  "rule_results": []
}
```

Allowed statuses:

- `ELIGIBLE`
- `POTENTIAL`
- `EXCLUDED`

## 7. Candidate Score Result

```json
{
  "candidate_id": "ALT-CAP-001",
  "cost": {
    "mass_g": 2.7,
    "material_cost_eur": 0.00513,
    "current_material_cost_eur": 0.004845,
    "score": 4.7059
  },
  "properties": {
    "individual_scores": {
      "stiffness": 10.0,
      "chemical_resistance": 10.0,
      "sealability": 10.0
    },
    "score": 10.0
  },
  "final_score": 7.35295
}
```

Final UI values may be rounded to two decimals, but calculations should retain more precision internally.
