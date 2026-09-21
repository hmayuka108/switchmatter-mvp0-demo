"""Display preparation using scoring outputs without recalculation."""


def prepare_scoring(ranking, candidates):
    candidate_by_id = {item["candidate_id"]: item for item in candidates}
    output = []
    for result in ranking:
        source = candidate_by_id.get(result["candidate_id"], {})
        cost = result.get("cost_details", {})
        properties = result.get("properties_details", {})
        property_rows = [{
            "Property": row["property"],
            "Required Value": row["required_value"],
            "Candidate Value": row["candidate_value"],
            "Property Score": row["score"],
        } for row in properties.get("property_results", [])]
        output.append({
            "candidate_id": result["candidate_id"],
            "candidate_name": source.get("name"),
            "material": source.get("material"),
            "regulation_status": result["candidate_status"].title(),
            "rank": result["rank"],
            "cost": cost,
            "properties": property_rows,
            "cost_score": result["cost_score"],
            "properties_score": result["properties_score"],
            "final_score": result["final_score"],
            "display_score": result["display_score"],
        })
    return output


def ranking_summary(details):
    return [{
        "Rank": item["rank"],
        "Candidate": item["candidate_name"],
        "Material": item["material"],
        "Material Cost": item["cost"].get("material_cost_eur"),
        "Cost Score": item["cost_score"],
        "Properties Score": item["properties_score"],
        "Final Score": item["display_score"],
    } for item in details]


def incomplete_eligible(screening_groups, candidates):
    candidate_by_id = {item["candidate_id"]: item for item in candidates}
    output = []
    for item in screening_groups.get("eligible", []):
        scoring = item.get("scoring", {})
        if scoring.get("scoring_status") == "SCORED":
            continue
        source = candidate_by_id.get(item["candidate_id"], {})
        output.append({"candidate_id": item["candidate_id"],
                       "candidate_name": source.get("name"),
                       "material": source.get("material"),
                       "reason": scoring.get("reason", "Scoring data is incomplete."),
                       "missing_properties": scoring.get("properties_details", {}).get(
                           "missing_properties", [])})
    return output
