"""Session-only candidate overrides and analysis orchestration."""
from copy import deepcopy

from .cost_scoring import find_component_config, score_screened_candidate
from .data_loader import load_candidates_for_component, load_product_config, load_regulations
from .final_math import combine
from .pipeline_analysis import stopped
from .pipeline_results import group_results
from .properties_scoring import calculate_candidate_properties, find_property_requirements
from .regulation_engine import screen_candidate


class OverrideSchemaError(RuntimeError):
    pass


def apply_candidate_overrides(candidates, overrides):
    """Return deep copies with only explicitly supplied regulation values applied."""
    output = deepcopy(candidates)
    by_id = {item["candidate_id"]: item for item in output}
    for candidate_id, values in overrides.items():
        if candidate_id not in by_id:
            raise OverrideSchemaError(f"Unknown candidate override: {candidate_id}")
        regulation_data = by_id[candidate_id].setdefault("regulation_data", {})
        for field, value in values.items():
            regulation_data[field] = value
    return output


def missing_field_specs(missing_fields, regulations):
    """Describe controls using only fields/types declared by UNKNOWN rules."""
    evaluations = {rule.get("evaluation", {}).get("field"): rule.get("evaluation", {})
                   for rule in regulations}
    specs = []
    for field in missing_fields:
        evaluation = evaluations.get(field)
        if not evaluation:
            raise OverrideSchemaError(f"No regulation schema for missing field '{field}'.")
        kind = evaluation.get("type")
        if kind in {"numeric_max", "numeric_min"}:
            input_type = "number"
        elif kind in {"boolean_required", "boolean_status_required"}:
            input_type = "boolean"
        else:
            raise OverrideSchemaError(f"Unsupported input type for field '{field}': {kind}")
        specs.append({"field": field, "input_type": input_type,
                      "unit": evaluation.get("unit")})
    return specs


def analyze_candidates(current, candidates):
    """Run existing screening/scoring functions against analysis-time candidates."""
    rules, config = load_regulations(), load_product_config()
    screening = [screen_candidate(item, current, rules, config) for item in candidates]
    component_config = find_component_config(config, current["component"])
    requirements = find_property_requirements(config, current["component"])
    costs, properties = [], []
    for candidate, result in zip(candidates, screening):
        costs.append(score_screened_candidate(candidate, result, component_config))
        if result["status"] == "ELIGIBLE":
            properties.append(calculate_candidate_properties(candidate, requirements))
        else:
            properties.append({"candidate_id": candidate["candidate_id"],
                               "scoring_status": "NOT_SCORED",
                               "reason": f"Candidate status is {result['status']}."})
    scoring = combine(screening, costs, properties)
    return {"confirmed_current_component": current, "analysis_status": "COMPLETE",
            "screening": group_results(screening, scoring), "ranking": scoring["ranking"]}


def run_analysis_with_overrides(current, overrides):
    component = current.get("component")
    if component is None:
        return stopped(current, "Component confirmation is required.")
    candidates = load_candidates_for_component(component)
    if not candidates:
        return stopped(current, f"No candidates for component '{component}'.")
    updated = apply_candidate_overrides(candidates, overrides)
    return analyze_candidates(current, updated)


def reset_override_state(state):
    state.pop("candidate_overrides", None)
