# Migration from MVP0

The previous MVP0 primary flow was one PDF, one current component, sample regulation booleans, then cost/property scoring and ranking. The upgraded primary flow starts with a per-SKU Functional Envelope, supports a multi-component BOM, evaluates evidence-based legal gates, and stops at a traceable legal verdict.

Reusable native PDF extraction, deterministic parsing, upload error handling, and reset behavior are preserved. The visual shell was adapted from `mvp0-ui-polish` without merging that branch. Legacy candidate and scoring modules remain available to future Steps 4–6 and their regression tests still run, but the main application no longer calls them.

`product_config.json`, `alternative_materials.json`, and the old sample `regulations.json` remain legacy fixtures only. The primary application uses `envelope_fields.json`, `legal_rules.json`, saved SKU envelopes, and saved component BOM records.

No automatic data migration is performed because MVP0's hard-coded product configuration and fictional pre-computed compliance flags are not valid authoritative SKU evidence. Users must create and confirm SKU-specific records.
