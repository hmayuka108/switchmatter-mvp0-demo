import re

NEGATIVE = (r"not\s+suitable\s+for\s+(?:direct\s+)?food[\s-]*contact",
            r"not\s+intended\s+for\s+(?:direct\s+)?food[\s-]*contact")
POSITIVE = (r"suitable\s+for\s+(?:direct\s+)?food[\s-]*contact",
            r"food[\s-]*contact\s+compliant",
            r"approved\s+for\s+(?:direct\s+)?food[\s-]*contact",
            r"intended\s+for\s+direct\s+contact\s+with\s+food(?:\s+and\s+beverages)?")


def food_contact(text):
    section = re.search(r"(?ims)^\s*food[\s-]*contact\s+statement\s*\r?\n"
                        r"(.*?)(?=^\s*(?:general\s+notes|why\s+this\s+sample)\s*$|\Z)", text)
    search = section.group(1) if section else re.sub(r'"[^"]*"', "", text)
    if any(re.search(x, search, re.I) for x in NEGATIVE):
        return False
    if any(re.search(x, search, re.I) for x in POSITIVE):
        return True
    return None
