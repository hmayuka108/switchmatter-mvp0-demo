from .data_loader import load_candidates_for_component, load_product_config
from .final_scoring import score_and_rank_component
from .pipeline_results import group_results
from .regulation_engine import screen_component_candidates


def stopped(current, reason):
    return {"confirmed_current_component": current, "analysis_status": "STOPPED",
            "reason": reason, "screening": {"eligible": [], "potential": [], "excluded": []},
            "ranking": []}


def run_analysis(current):
    component = current.get("component")
    if component is None:
        return stopped(current, "Component confirmation is required.")
    if not load_candidates_for_component(component):
        return stopped(current, f"No candidates for component '{component}'.")
    config = load_product_config()
    if not any(x.get("component") == component for x in config.get("components", [])):
        return stopped(current, f"Product configuration is missing for '{component}'.")
    screening = screen_component_candidates(current)
    scoring = score_and_rank_component(current)
    return {"confirmed_current_component": current, "analysis_status": "COMPLETE",
            "screening": group_results(screening, scoring), "ranking": scoring["ranking"]}
