"""Deterministic MVP0 regulation screening."""
from typing import Any
from .data_loader import load_candidates_for_component, load_product_config, load_regulations


class RegulationSchemaError(RuntimeError):
    pass


def _applicable(rule, candidate, current, config):
    applicability = rule.get("applicability", {})
    unknown = set(applicability) - {
        "components", "requires_current_food_contact", "target_year_min"
    }
    if unknown:
        raise RegulationSchemaError(f"Unsupported applicability: {sorted(unknown)}")
    components = applicability.get("components")
    if components is not None and candidate.get("component") not in components:
        return False, "Candidate component is not listed in rule applicability."
    if "requires_current_food_contact" in applicability:
        required = applicability["requires_current_food_contact"]
        if current.get("food_contact") is not required:
            return False, "Current food-contact context does not match rule applicability."
    if "target_year_min" in applicability:
        year = config.get("target_year")
        if year is None:
            raise RegulationSchemaError("Product configuration has no target_year.")
        if year < applicability["target_year_min"]:
            return False, "Target year is below the rule applicability minimum."
    return True, "Rule is applicable to the explicit context."


def evaluate_rule(rule, candidate, current, config):
    applicable, reason = _applicable(rule, candidate, current, config)
    if not applicable:
        return {"rule_id": rule["rule_id"], "result": "NOT_APPLICABLE",
                "values_used": {}, "reason": reason}
    evaluation = rule.get("evaluation", {})
    kind, field = evaluation.get("type"), evaluation.get("field")
    if not isinstance(field, str):
        raise RegulationSchemaError(f"Rule {rule.get('rule_id')} has no field.")
    value = candidate.get("regulation_data", {}).get(field)
    if value is None:
        return {"rule_id": rule["rule_id"], "result": "UNKNOWN",
                "values_used": {field: None},
                "reason": f"Required field '{field}' is missing or null."}
    if kind in {"numeric_max", "numeric_min"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RegulationSchemaError(f"Field '{field}' must be numeric.")
        key = "max" if kind == "numeric_max" else "min"
        if key not in evaluation:
            raise RegulationSchemaError(f"Rule {rule['rule_id']} has no {key}.")
        threshold = evaluation[key]
        passed = value <= threshold if key == "max" else value >= threshold
        operator = "<=" if key == "max" else ">="
        reason = f"Observed {field}={value}; required {operator} {threshold}."
    elif kind in {"boolean_required", "boolean_status_required"}:
        required = evaluation.get("required")
        if not isinstance(value, bool) or not isinstance(required, bool):
            raise RegulationSchemaError(f"Field '{field}' must be boolean.")
        passed = value is required
        reason = f"Observed {field}={value}; required {required}."
    else:
        raise RegulationSchemaError(f"Unsupported evaluation type: {kind}")
    return {"rule_id": rule["rule_id"], "result": "PASS" if passed else "FAIL",
            "values_used": {field: value}, "reason": reason}


def screen_candidate(candidate, current, rules, config):
    rule_results = [evaluate_rule(rule, candidate, current, config) for rule in rules]
    results = {item["result"] for item in rule_results}
    status = "EXCLUDED" if "FAIL" in results else (
        "POTENTIAL" if "UNKNOWN" in results else "ELIGIBLE"
    )
    return {"candidate_id": candidate["candidate_id"], "status": status,
            "rule_results": rule_results}


def screen_component_candidates(current: dict[str, Any]):
    candidates = load_candidates_for_component(current.get("component"))
    rules, config = load_regulations(), load_product_config()
    return [screen_candidate(item, current, rules, config) for item in candidates]
