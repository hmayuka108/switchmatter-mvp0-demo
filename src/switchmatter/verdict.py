"""Deterministic KEEP/HOLD/REMOVE verdict aggregation."""
from __future__ import annotations


def aggregate_results(results: list[dict], coverage_complete: bool) -> dict:
    failures = [r for r in results if r["result"] == "FAIL"]
    unknowns = [r for r in results if r["result"] == "UNKNOWN"]
    if failures:
        verdict = "REMOVE"
    elif unknowns or not coverage_complete or not results:
        verdict = "HOLD"
    else:
        verdict = "KEEP"
    return {"verdict": verdict, "reasons_for_remove": [r["reason"] for r in failures],
            "reasons_for_hold": [r["reason"] for r in unknowns] + ([] if coverage_complete else ["Applicable verified rule coverage is incomplete"]),
            "missing_information": sorted({item for r in results for item in r.get("missing", [])})}


def build_verdict(evaluation: dict, components: list[dict]) -> dict:
    by_component = {}
    for component in components:
        results = [r for r in evaluation["rule_results"] if r["component_id"] == component["component_id"]]
        by_component[component["component_id"]] = aggregate_results(results, evaluation["coverage_complete"])
    sku = aggregate_results(evaluation["rule_results"], evaluation["coverage_complete"])
    return {"sku_id": evaluation["sku_id"], "verdict": sku["verdict"], "components": by_component,
            "rule_results": evaluation["rule_results"], "missing_information": sku["missing_information"],
            "reasons_for_hold": sku["reasons_for_hold"], "reasons_for_remove": sku["reasons_for_remove"],
            "evaluation_timestamp": evaluation["evaluated_at"], "rule_registry_version": evaluation["registry_version"]}
