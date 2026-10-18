# Pipeline Data Model

## Functional Envelope

`envelope_fields.json` defines field key, label, applicability, data type, unit, allowed values, tier, consumers, expected source, regulatory reference, and verification status. Each saved envelope value records SKU, optional component, value, unit, status, source, actor, and confirmation time. Replacements are appended to history.

Allowed statuses are `confirmed`, `extracted_unconfirmed`, `default_assumed`, and `unknown`.

## Component BOM and evidence

Each component records `component_id`, `sku_id`, optional parent, type, evidence documents, supplier references, and history. `measurements` is the long-form evidence table: subject, level, property, value, unit, method, conditions, value type, document, source locus, and status. `properties` is a materialized UI view, not the evidence authority.

## Legal rules and results

Each rule records ID, applicability, attribute, operator, threshold, unit, unknown/fail policy, source, locus, version, verification, and confidence. Results retain the rule/component IDs, result, values used, explanation, missing evidence, source metadata, evaluation timestamp, and registry version.

Only positively established scope exclusion yields `NOT_APPLICABLE`. Missing applicability or evidence yields `UNKNOWN`. Unverified rules cannot return definitive PASS or FAIL.
