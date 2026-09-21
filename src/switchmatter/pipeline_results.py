def group_results(screening, scoring):
    scores = {x["candidate_id"]: x for x in scoring["results"]}
    groups = {"eligible": [], "potential": [], "excluded": []}
    names = {"ELIGIBLE": "eligible", "POTENTIAL": "potential", "EXCLUDED": "excluded"}
    for item in screening:
        rules = item["rule_results"]
        output = {"candidate_id": item["candidate_id"], "status": item["status"],
                  "rule_results": rules, "scoring": scores[item["candidate_id"]]}
        unknown = [x for x in rules if x["result"] == "UNKNOWN"]
        failed = [x for x in rules if x["result"] == "FAIL"]
        if unknown:
            output["unknown_rule_ids"] = [x["rule_id"] for x in unknown]
            output["missing_fields"] = sorted({key for x in unknown for key, value
                                                in x["values_used"].items() if value is None})
        if failed:
            output["fail_rule_ids"] = [x["rule_id"] for x in failed]
        groups[names[item["status"]]].append(output)
    return groups
