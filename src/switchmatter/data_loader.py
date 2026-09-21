"""Load MVP0 JSON data without changing source values."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class DataLoadError(RuntimeError):
    """Raised for unreadable or structurally invalid data files."""


def _read(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"Could not load JSON data from {path}") from exc


def _records(path: Path, key: str, id_key: str) -> list[dict[str, Any]]:
    data = _read(path)
    if not isinstance(data, dict) or not isinstance(data.get(key), list):
        raise DataLoadError(f"Expected '{key}' list in {path}")
    records = data[key]
    if not all(isinstance(item, dict) for item in records):
        raise DataLoadError(f"Invalid '{key}' record in {path}")
    identifiers = [item.get(id_key) for item in records]
    if any(not isinstance(value, str) or not value for value in identifiers):
        raise DataLoadError(f"Missing '{id_key}' in {path}")
    if len(identifiers) != len(set(identifiers)):
        raise DataLoadError(f"Duplicate '{id_key}' in {path}")
    return records


def load_alternative_materials(path: str | Path | None = None) -> list[dict[str, Any]]:
    source = Path(path) if path is not None else DATA_DIR / "alternative_materials.json"
    return _records(source, "candidates", "candidate_id")


def load_regulations(path: str | Path | None = None) -> list[dict[str, Any]]:
    source = Path(path) if path is not None else DATA_DIR / "regulations.json"
    return _records(source, "rules", "rule_id")


def load_product_config(path: str | Path | None = None) -> dict[str, Any]:
    source = Path(path) if path is not None else DATA_DIR / "product_config.json"
    data = _read(source)
    if not isinstance(data, dict) or not isinstance(data.get("components"), list):
        raise DataLoadError(f"Expected product with 'components' list in {source}")
    return data


def filter_candidates_by_component(
    candidates: list[dict[str, Any]], component: str | None
) -> list[dict[str, Any]]:
    if component is None:
        return []
    return [item for item in candidates if item.get("component") == component]


def load_candidates_for_component(component: str | None) -> list[dict[str, Any]]:
    return filter_candidates_by_component(load_alternative_materials(), component)
