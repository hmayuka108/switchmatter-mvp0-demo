"""MVP0 component property-fit scoring."""
from .data_loader import load_alternative_materials, load_product_config
from .regulation_engine import screen_component_candidates


class PropertyDataError(RuntimeError):
    pass


def calculate_property_score(value, required):
    valid_required = isinstance(required, (int, float)) and not isinstance(required, bool)
    valid_value = isinstance(value, (int, float)) and not isinstance(value, bool)
    if not valid_required or required <= 0 or not valid_value or value < 0:
        raise PropertyDataError("Property values must be valid non-negative numbers.")
    return min(value / required, 1) * 10


def find_property_requirements(config, component):
    matches = [x for x in config.get("components", []) if x.get("component") == component]
    if not matches or not isinstance(matches[0].get("property_requirements"), dict):
        raise PropertyDataError(f"No property requirements for '{component}'.")
    requirements = matches[0]["property_requirements"]
    if not requirements:
        raise PropertyDataError("Property requirements are empty.")
    return requirements


def calculate_candidate_properties(candidate, requirements):
    properties = candidate.get("properties")
    properties = properties if isinstance(properties, dict) else {}
    missing = [name for name in requirements if properties.get(name) is None]
    if missing:
        return {"candidate_id": candidate["candidate_id"],
                "scoring_status": "SCORING_DATA_INCOMPLETE",
                "property_results": [], "missing_properties": missing,
                "properties_score": None}
    results = [{"property": name, "required_value": required,
                "candidate_value": properties[name],
                "score": calculate_property_score(properties[name], required)}
               for name, required in requirements.items()]
    return {"candidate_id": candidate["candidate_id"], "scoring_status": "SCORED",
            "property_results": results, "missing_properties": [],
            "properties_score": sum(x["score"] for x in results) / len(results)}


def score_component_properties(current):
    component = current.get("component")
    requirements = find_property_requirements(load_product_config(), component)
    candidates = {x["candidate_id"]: x for x in load_alternative_materials()
                  if x.get("component") == component}
    output = []
    for screening in screen_component_candidates(current):
        candidate = candidates[screening["candidate_id"]]
        if screening["status"] == "ELIGIBLE":
            output.append(calculate_candidate_properties(candidate, requirements))
        else:
            output.append({"candidate_id": candidate["candidate_id"],
                           "scoring_status": "NOT_SCORED",
                           "reason": f"Candidate status is {screening['status']}."})
    return output
