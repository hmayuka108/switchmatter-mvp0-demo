"""Multi-component BOM records and deterministic supplier-PDF mapping."""
from __future__ import annotations

import copy
import re
import uuid
from datetime import datetime, timezone

from .parser import parse_current_component

COMPONENT_TYPES = ("bottle_body", "closure", "label", "adhesive", "ink", "liner",
                   "barrier_layer", "coating", "seal_lid_film", "sleeve", "pump",
                   "spring", "valve", "insert")
PROPERTY_KEYS = ("polymer", "material_grade", "mass_g", "density_g_cm3", "colour",
                 "additives", "fillers", "adhesive_details", "coatings", "thickness_mm")


def new_component(sku_id: str, component_type: str, component_id: str | None = None,
                  parent_component_id: str | None = None) -> dict:
    if component_type not in COMPONENT_TYPES:
        raise ValueError(f"Unsupported component type: {component_type}")
    return {"component_id": component_id or f"CMP-{uuid.uuid4().hex[:8].upper()}",
            "sku_id": sku_id, "parent_component_id": parent_component_id,
            "component_type": component_type,
            "properties": {key: {"value": None, "unit": None, "status": "unknown",
                                  "source_ref": None, "source_type": None} for key in PROPERTY_KEYS},
            "measurements": [], "supplier_references": [], "evidence_documents": [], "history": []}


def set_component_property(component: dict, key: str, value, *, unit=None, status="confirmed",
                           source_ref=None, source_type=None, confirmed_by=None):
    if status not in {"confirmed", "extracted_unconfirmed", "default_assumed", "unknown"}:
        raise ValueError(status)
    if key not in component["properties"]:
        component["properties"][key] = {"value": None, "unit": None, "status": "unknown",
                                         "source_ref": None, "source_type": None}
    old = component["properties"][key]
    if old["status"] == "confirmed" and status != "confirmed":
        return component
    component["history"].append({"property_key": key, **copy.deepcopy(old)})
    component["properties"][key] = {"value": value, "unit": unit, "status": status,
        "source_ref": source_ref, "source_type": source_type, "confirmed_by": confirmed_by,
        "confirmed_at": datetime.now(timezone.utc).isoformat() if status == "confirmed" else None}
    component["measurements"].append({"subject_id": component["component_id"], "level": "component",
        "property_key": key, "value": value, "unit": unit, "test_method": None,
        "test_conditions": None, "value_type": "measured" if source_type == "supplier_pdf" else "declared",
        "doc_id": source_ref.split(":", 1)[0] if source_ref and ":" in source_ref else None,
        "page_or_cell": source_ref, "status": status})
    return component


def component_from_pdf_text(text: str, sku_id: str, doc_id: str, source_name: str | None = None) -> dict:
    parsed = parse_current_component(text)
    component_type = {"cap": "closure", "label": "label", "bottle_body": "bottle_body"}.get(parsed["component"])
    if component_type is None:
        return {"status": "manual_review_required", "reason": "Component type was not found in a supported field-local section", "component": None}
    component = new_component(sku_id, component_type)
    component["evidence_documents"].append({"doc_id": doc_id, "source_name": source_name, "extraction_status": "text_extracted"})
    if parsed["current_material"] is not None:
        set_component_property(component, "polymer", parsed["current_material"], status="extracted_unconfirmed",
                               source_ref=f"{doc_id}:Material", source_type="supplier_pdf")
    if parsed["thickness"] is not None:
        value, unit = parsed["thickness"]["value"], parsed["thickness"]["unit"]
        if unit in {"um", "µm", "μm"}:
            value, unit = value / 1000, "mm"
        set_component_property(component, "thickness_mm", value, unit=unit, status="extracted_unconfirmed",
                               source_ref=f"{doc_id}:Thickness", source_type="supplier_pdf")
    mass = re.search(r"(?im)^\s*(?:component\s+)?mass\s*:\s*(\d+(?:\.\d+)?)\s*(mg|g|kg)\b", text)
    if mass:
        value, unit = float(mass.group(1)), mass.group(2).lower()
        factor = {"mg": .001, "g": 1, "kg": 1000}[unit]
        set_component_property(component, "mass_g", value * factor, unit="g", status="extracted_unconfirmed",
                               source_ref=f"{doc_id}:Mass", source_type="supplier_pdf")
    return {"status": "extracted_unconfirmed", "component": component}


def bom_for_sku(components: list[dict], sku_id: str) -> list[dict]:
    return [component for component in components if component["sku_id"] == sku_id]


def import_bom_xlsx(data: bytes, sku_id: str) -> dict:
    """Import a row-based component BOM workbook without guessing unknown columns."""
    from .excel_intake import read_xlsx, _column, _norm
    known = {"component id": "component_id", "component type": "component_type", "parent component id": "parent_component_id",
             "polymer": "polymer", "material grade": "material_grade", "mass g": "mass_g", "density g cm3": "density_g_cm3",
             "colour": "colour", "color": "colour", "additives": "additives", "fillers": "fillers", "adhesive details": "adhesive_details",
             "coatings": "coatings", "thickness mm": "thickness_mm"}
    components, unmapped = [], []
    for sheet in read_xlsx(data):
        if not sheet["rows"]: continue
        headers = {_column(ref): value for ref, value in sheet["rows"][0].items()}
        for row in sheet["rows"][1:]:
            values = {}
            for ref, value in row.items():
                header = headers.get(_column(ref)); key = known.get(_norm(header)) if header is not None else None
                if key: values[key] = {"value": value, "source_ref": f"{sheet['name']}!{ref}"}
                elif header is not None: unmapped.append({"header": header, "value": value, "source_ref": f"{sheet['name']}!{ref}"})
            component_type = _norm(values.get("component_type", {}).get("value", "")).replace(" ", "_")
            aliases = {"cap": "closure", "bottle_body": "bottle_body", "barrier": "barrier_layer"}
            component_type = aliases.get(component_type, component_type)
            if component_type not in COMPONENT_TYPES:
                unmapped.append({"header": "component_type", "value": component_type, "source_ref": f"{sheet['name']}!row"}); continue
            component = new_component(sku_id, component_type,
                str(values.get("component_id", {}).get("value") or "") or None,
                str(values.get("parent_component_id", {}).get("value") or "") or None)
            for key, item in values.items():
                if key in {"component_id", "component_type", "parent_component_id"}: continue
                value = item["value"]
                if key in {"mass_g", "density_g_cm3", "thickness_mm"} and value not in (None, ""): value = float(value)
                unit = {"mass_g": "g", "density_g_cm3": "g/cm3", "thickness_mm": "mm"}.get(key)
                set_component_property(component, key, value, unit=unit, status="extracted_unconfirmed", source_ref=item["source_ref"], source_type="supplier_excel")
            components.append(component)
    return {"components": components, "unmapped": unmapped}
