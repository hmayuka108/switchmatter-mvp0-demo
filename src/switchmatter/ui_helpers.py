"""Pure helpers for translating editable UI values into confirmed input."""

COMPONENT_OPTIONS = ("", "bottle_body", "cap", "label")
FOOD_CONTACT_OPTIONS = ("Unknown", "Yes", "No")


def form_defaults(parsed):
    thickness = parsed.get("thickness") or {}
    food_contact = parsed.get("food_contact")
    food_label = "Unknown" if food_contact is None else ("Yes" if food_contact else "No")
    component = parsed.get("component")
    return {
        "component": component if component in COMPONENT_OPTIONS else "",
        "current_material": parsed.get("current_material") or "",
        "thickness_value": thickness.get("value"),
        "thickness_unit": thickness.get("unit") or "",
        "food_contact": food_label,
    }


def build_confirmed_component(component, current_material, thickness_value,
                              thickness_unit, food_contact):
    """Build the source-of-truth object solely from current form values."""
    material = current_material.strip() or None
    unit = thickness_unit.strip()
    thickness = None
    if thickness_value is not None:
        thickness = {"value": float(thickness_value), "unit": unit}
    food_value = {"Yes": True, "No": False, "Unknown": None}[food_contact]
    return {
        "component": component or None,
        "current_material": material,
        "thickness": thickness,
        "food_contact": food_value,
    }
