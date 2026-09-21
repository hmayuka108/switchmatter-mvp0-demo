import re


def thickness(text):
    match = re.search(r"(?im)^\s*(?:(?:nominal|film)\s+)?"
                      r"(?:wall\s+thickness|thickness|wall\s+gauge)\s*"
                      r"(?::\s*|[=-]\s*|\r?\n\s*)"
                      r"(\d+(?:\.\d+)?)\s*(mm|millimetres?|µm|um)\b", text)
    if not match:
        return None
    unit = "mm" if match.group(2).lower().startswith("m") else "µm"
    return {"value": float(match.group(1)), "unit": unit}
