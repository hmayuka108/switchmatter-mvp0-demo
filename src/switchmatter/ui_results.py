"""Presentation-only preparation for regulation screening results."""


def screening_summary(groups):
    return {name: len(groups.get(name, []))
            for name in ("eligible", "potential", "excluded")}


def _observed_value(values):
    if not values:
        return None
    if len(values) == 1:
        return next(iter(values.values()))
    return values


def prepare_candidate(candidate_result, candidates, regulations):
    candidate_by_id = {item["candidate_id"]: item for item in candidates}
    rule_by_id = {item["rule_id"]: item for item in regulations}
    source = candidate_by_id.get(candidate_result["candidate_id"], {})
    rule_details = []
    for result in candidate_result["rule_results"]:
        rule = rule_by_id.get(result["rule_id"], {})
        rule_details.append({
            "Rule ID": result["rule_id"],
            "Rule name": rule.get("name"),
            "Result": result["result"],
            "Observed value": _observed_value(result.get("values_used", {})),
            "Reason": result["reason"],
        })
    return {
        "candidate_id": candidate_result["candidate_id"],
        "candidate_name": source.get("name"),
        "material": source.get("material"),
        "status": candidate_result["status"].title(),
        "unknown_rule_ids": [row["Rule ID"] for row in rule_details
                             if row["Result"] == "UNKNOWN"],
        "missing_fields": candidate_result.get("missing_fields", []),
        "fail_rule_ids": [row["Rule ID"] for row in rule_details
                          if row["Result"] == "FAIL"],
        "rule_details": rule_details,
    }


def prepare_screening(groups, candidates, regulations):
    return {
        name: [prepare_candidate(item, candidates, regulations)
               for item in groups.get(name, [])]
        for name in ("eligible", "potential", "excluded")
    }
