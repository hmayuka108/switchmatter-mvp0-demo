"""Evidence-based legal gates; unverified rules can never yield definitive results."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .envelope import confirmed_value

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RESULTS = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}


def load_rule_registry(path: str | Path | None = None) -> dict:
    source = Path(path) if path else DATA_DIR / "legal_rules.json"
    return json.loads(source.read_text(encoding="utf-8"))


def _property(component, key):
    item = component.get("properties", {}).get(key, {})
    return item.get("value") if item.get("status") == "confirmed" else None


def _applicability(rule, envelope, component):
    for key, expected in rule.get("applies_when", {}).items():
        actual = component.get("component_type") if key == "component_type" else confirmed_value(envelope, key)
        if actual is None:
            return "unknown", f"Applicability input {key} is not confirmed"
        if actual != expected:
            return "excluded", f"Confirmed {key} is outside this rule's scope"
    return "applies", "Scope conditions are confirmed"


def evaluate_rule(rule: dict, envelope: dict, component: dict) -> dict:
    base = {"rule_id": rule["rule_id"], "rule_version": rule.get("source_version"),
            "source_doc": rule.get("source_doc"), "source_locus": rule.get("source_locus"),
            "ref_verified": bool(rule.get("ref_verified")), "component_id": component["component_id"]}
    applicability, reason = _applicability(rule, envelope, component)
    if applicability == "unknown":
        return {**base, "result": "UNKNOWN", "reason": reason, "missing": [reason]}
    if applicability == "excluded":
        return {**base, "result": "NOT_APPLICABLE", "reason": reason, "missing": []}
    if not rule.get("ref_verified"):
        return {**base, "result": "UNKNOWN", "reason": "Rule is not activated because its legal basis or threshold is unverified", "missing": ["verified regulatory rule"]}
    attribute = rule["attribute"]
    value = _property(component, attribute)
    if value is None:
        return {**base, "result": "UNKNOWN", "reason": f"Confirmed measured attribute {attribute} is missing", "missing": [attribute]}
    expected, operator = rule.get("value"), rule["operator"]
    passed = ((operator == "max" and value <= expected) or (operator == "min" and value >= expected)
              or (operator == "equals" and value == expected))
    return {**base, "result": "PASS" if passed else "FAIL", "reason":
            f"Confirmed {attribute} value {value!r} {'meets' if passed else 'does not meet'} the verified {operator} condition {expected!r}",
            "values_used": {attribute: value}, "missing": []}


def evaluate_legal_gates(envelope: dict, components: list[dict], registry: dict | None = None) -> dict:
    registry = registry or load_rule_registry()
    results = [evaluate_rule(rule, envelope, component)
               for component in components for rule in registry["rules"]]
    return {"sku_id": envelope["sku_id"], "registry_version": registry["metadata"]["registry_version"],
            "evaluated_at": datetime.now(timezone.utc).isoformat(), "rule_results": results,
            "coverage_complete": bool(registry["rules"]) and all(r.get("ref_verified") for r in registry["rules"])}
