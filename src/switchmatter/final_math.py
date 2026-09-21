def final_score(cost, properties):
    return None if cost is None or properties is None else .5 * cost + .5 * properties


def combine(screening, costs, properties):
    costs = {x["candidate_id"]: x for x in costs}
    properties = {x["candidate_id"]: x for x in properties}
    results = []
    for source in screening:
        key, status = source["candidate_id"], source["status"]
        cost_details, property_details = costs.get(key, {}), properties.get(key, {})
        cost = cost_details.get("cost_score")
        prop = property_details.get("properties_score")
        final = final_score(cost, prop) if status == "ELIGIBLE" else None
        item = {"candidate_id": key, "candidate_status": status,
                "cost_score": cost, "properties_score": prop, "final_score": final,
                "display_score": None if final is None else round(final, 2), "rank": None,
                "cost_details": cost_details, "properties_details": property_details}
        if status != "ELIGIBLE":
            item.update(scoring_status="NOT_RANKED", reason=f"Candidate status is {status}.")
        elif final is None:
            missing = "Cost Score" if cost is None else "Properties Score"
            item.update(scoring_status="INCOMPLETE", reason=f"Missing {missing}.")
        else:
            item["scoring_status"] = "SCORED"
        results.append(item)
    ranked = sorted((x for x in results if x["candidate_status"] == "ELIGIBLE"
                     and x["final_score"] is not None),
                    key=lambda x: (-x["final_score"], x["candidate_id"]))
    previous = rank = None
    for position, item in enumerate(ranked, 1):
        if item["final_score"] != previous:
            rank = position
        item["rank"], previous = rank, item["final_score"]
    return {"results": results, "ranking": ranked}
