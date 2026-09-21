import re

COMPONENTS = ((r"\b(?:bottle\s+cap|closure|cap)\b", "cap"),
              (r"\b(?:wrap[\s-]*around\s+label|sleeve\s+label|label)\b", "label"),
              (r"\b(?:bottle\s+body|bottle)\b", "bottle_body"))
MATERIALS = ((r"\b(?:polyethylene\s+terephthalate|PET)\b", "PET"),
             (r"\b(?:high[\s-]*density\s+polyethylene|HDPE)\b", "HDPE"),
             (r"\b(?:polypropylene|PP)\b", "PP"))


def normalized(text, patterns):
    found = [(m.start(), i, value) for i, (pattern, value) in enumerate(patterns)
             if (m := re.search(pattern, text, re.I))]
    return min(found)[2] if found else None


def component(text):
    field = re.search(r"(?im)^\s*(?:component|product\s*/\s*component)\s*"
                      r"(?::\s*|\r?\n\s*)([^\r\n]+)", text)
    return normalized(field.group(1) if field else text, COMPONENTS)


def material(text):
    field = re.search(r"(?im)^\s*(?:material|resin)\s*"
                      r"(?::\s*|\r?\n\s*)([^\r\n]+)", text)
    return normalized(field.group(1), MATERIALS) if field else None
