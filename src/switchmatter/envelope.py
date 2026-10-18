"""Functional Envelope registry, values, confirmation, and completeness."""
from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

VALID_STATUSES = {"confirmed", "extracted_unconfirmed", "default_assumed", "unknown"}
VALID_TIERS = {"T1", "T2", "T3", "T4"}
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_registry(path: str | Path | None = None) -> dict:
    source = Path(path) if path else DATA_DIR / "envelope_fields.json"
    registry = json.loads(source.read_text(encoding="utf-8"))
    seen = set()
    for field in registry["fields"]:
        key = field["field_key"]
        if key in seen or field["tier"] not in VALID_TIERS:
            raise ValueError(f"Invalid envelope field definition: {key}")
        seen.add(key)
    return registry


def empty_envelope(sku_id: str, registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    return {
        "sku_id": sku_id,
        "values": {
            field["field_key"]: _record(sku_id, field["field_key"], None, None, "unknown")
            for field in registry["fields"]
        },
        "history": [],
    }


def _record(sku_id, field_key, value, unit, status, **metadata):
    if status not in VALID_STATUSES:
        raise ValueError(f"Unsupported field status: {status}")
    return {"sku_id": sku_id, "field_key": field_key, "component_id": metadata.pop("component_id", None),
            "value": value, "unit": unit, "status": status, "source_type": metadata.pop("source_type", None),
            "source_ref": metadata.pop("source_ref", None), "entered_by": metadata.pop("entered_by", None),
            "confirmed_by": metadata.pop("confirmed_by", None), "confirmed_at": metadata.pop("confirmed_at", None),
            **metadata}


def validate_value(definition: dict, value, unit):
    if value is None:
        return
    kind = definition["data_type"]
    if kind == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{definition['field_key']} must be true or false")
    if kind == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
        raise ValueError(f"{definition['field_key']} must be numeric")
    if definition.get("unit") and unit != definition["unit"]:
        raise ValueError(f"{definition['field_key']} requires unit {definition['unit']}")
    allowed = definition.get("allowed_values")
    if allowed is not None and value not in allowed:
        raise ValueError(f"{definition['field_key']} has an unsupported value")


def set_value(envelope: dict, field_key: str, value, *, unit=None, status: str,
              source_type=None, source_ref=None, entered_by=None, confirmed_by=None,
              registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    definitions = {item["field_key"]: item for item in registry["fields"]}
    if field_key not in definitions:
        raise KeyError(field_key)
    validate_value(definitions[field_key], value, unit)
    old = envelope["values"].get(field_key)
    if old and old["status"] == "confirmed" and status != "confirmed" and source_type != "user":
        return envelope
    if old:
        envelope["history"].append(copy.deepcopy(old))
    timestamp = datetime.now(timezone.utc).isoformat() if status == "confirmed" else None
    envelope["values"][field_key] = _record(
        envelope["sku_id"], field_key, value, unit, status, source_type=source_type,
        source_ref=source_ref, entered_by=entered_by, confirmed_by=confirmed_by,
        confirmed_at=timestamp,
    )
    return envelope


def tier_completeness(envelope: dict, registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    result = {}
    for tier in ("T1", "T2", "T3", "T4"):
        keys = [f["field_key"] for f in registry["fields"] if f["tier"] == tier]
        confirmed = sum(envelope["values"].get(k, {}).get("status") == "confirmed" and
                        envelope["values"].get(k, {}).get("value") is not None for k in keys)
        result[tier] = {"confirmed": confirmed, "total": len(keys),
                        "percent": 100.0 if not keys else round(100 * confirmed / len(keys), 1),
                        "missing": [k for k in keys if envelope["values"].get(k, {}).get("status") != "confirmed" or envelope["values"].get(k, {}).get("value") is None]}
    return result


def confirmed_value(envelope: dict, field_key: str):
    item = envelope.get("values", {}).get(field_key, {})
    return item.get("value") if item.get("status") == "confirmed" else None
