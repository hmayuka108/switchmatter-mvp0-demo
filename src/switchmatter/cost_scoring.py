"""MVP0 fixed-volume cost simulation and Cost Score."""
from .data_loader import load_alternative_materials, load_product_config
from .regulation_engine import screen_component_candidates


class CostDataError(RuntimeError):
    pass


def _number(record, field, positive=False):
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CostDataError(f"Required numeric field '{field}' is missing or invalid.")
    if value < 0 or (positive and value == 0):
        raise CostDataError(f"Required numeric field '{field}' must be positive.")
    return float(value)


def calculate_cost_score(candidate_cost, current_cost):
    if current_cost <= 0:
        raise CostDataError("Current material cost must be greater than zero.")
    raw = 5 + 5 * (current_cost - candidate_cost) / current_cost
    return min(10.0, max(0.0, raw))


def find_component_config(config, component):
    for item in config.get("components", []):
        if item.get("component") == component:
            return item
    raise CostDataError(f"No product configuration for component '{component}'.")


def calculate_candidate_cost(candidate, component_config):
    volume = _number(component_config, "volume_cm3", True)
    baseline = component_config.get("baseline")
    if not isinstance(baseline, dict):
        raise CostDataError("Component baseline is missing or invalid.")
    current_density = _number(baseline, "density_g_cm3", True)
    current_price = _number(baseline, "price_per_g_eur", True)
    density = _number(candidate, "density_g_cm3", True)
    price = _number(candidate, "price_per_g_eur")
    mass, current_mass = volume * density, volume * current_density
    cost, current_cost = mass * price, current_mass * current_price
    return {
        "candidate_id": candidate["candidate_id"], "volume_cm3": volume,
        "density_g_cm3": density, "mass_g": mass,
        "price_per_g_eur": price, "material_cost_eur": cost,
        "current_mass_g": current_mass,
        "current_material_cost_eur": current_cost,
        "cost_score": calculate_cost_score(cost, current_cost),
    }


def score_screened_candidate(candidate, screening, component_config):
    if screening.get("status") != "ELIGIBLE":
        return {"candidate_id": candidate["candidate_id"],
                "scoring_status": "NOT_SCORED",
                "reason": f"Candidate status is {screening.get('status')}."}
    result = calculate_candidate_cost(candidate, component_config)
    result["scoring_status"] = "SCORED"
    return result


def score_component_candidates(current):
    component = current.get("component")
    component_config = find_component_config(load_product_config(), component)
    candidates = {x["candidate_id"]: x for x in load_alternative_materials()
                  if x.get("component") == component}
    return [score_screened_candidate(candidates[x["candidate_id"]], x, component_config)
            for x in screen_component_candidates(current)]
