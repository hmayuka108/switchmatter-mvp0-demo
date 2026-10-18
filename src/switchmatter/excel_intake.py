"""Deterministic XLSX intake with cell provenance and conflict preservation."""
from __future__ import annotations

import io
import re
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from .envelope import empty_envelope, load_registry, set_value

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower()).strip()


def _cell_value(cell, shared):
    kind = cell.get("t")
    if kind == "inlineStr":
        return "".join(t.text or "" for t in cell.findall(".//m:t", NS))
    node = cell.find("m:v", NS)
    if node is None:
        return None
    raw = node.text or ""
    if kind == "s":
        return shared[int(raw)]
    if kind == "b":
        return raw == "1"
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def read_xlsx(data: bytes) -> list[dict]:
    try:
        archive = ZipFile(io.BytesIO(data))
    except (BadZipFile, OSError) as exc:
        raise ValueError("Unsupported or invalid Excel file; upload an .xlsx workbook") from exc
    with archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.findall(".//m:t", NS)) for si in root]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.findall("p:Relationship", REL_NS)}
        sheets = []
        for sheet in workbook.findall(".//m:sheet", NS):
            target = targets[sheet.get(f"{{{NS['r']}}}id")]
            path = target.lstrip("/") if target.startswith("/xl/") else "xl/" + target.lstrip("/")
            root = ET.fromstring(archive.read(path))
            rows = []
            for row in root.findall(".//m:sheetData/m:row", NS):
                rows.append({cell.get("r"): _cell_value(cell, shared) for cell in row.findall("m:c", NS)})
            sheets.append({"name": sheet.get("name"), "rows": rows})
        return sheets


def _column(ref):
    return re.match(r"[A-Z]+", ref).group(0)


def import_envelope_xlsx(data: bytes, sku_id: str, registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    aliases = {}
    for definition in registry["fields"]:
        for alias in [definition["field_key"], definition["label"], *definition.get("aliases", [])]:
            aliases[_norm(alias)] = definition["field_key"]
    envelope = empty_envelope(sku_id, registry)
    raw, conflicts, mapped = [], [], {}
    for sheet in read_xlsx(data):
        if not sheet["rows"]:
            continue
        header_row = sheet["rows"][0]
        headers = {_column(ref): value for ref, value in header_row.items()}
        for row in sheet["rows"][1:]:
            for ref, value in row.items():
                col, header = _column(ref), headers.get(_column(ref))
                if header is None:
                    continue
                source_ref = f"{sheet['name']}!{ref}"
                key = aliases.get(_norm(header))
                raw.append({"header": header, "value": value, "source_ref": source_ref, "mapped_field": key})
                if key is None or value in (None, ""):
                    continue
                if key in mapped and mapped[key]["value"] != value:
                    conflicts.append({"field_key": key, "values": [mapped[key], {"value": value, "source_ref": source_ref}]})
                    continue
                mapped[key] = {"value": value, "source_ref": source_ref}
    definitions = {f["field_key"]: f for f in registry["fields"]}
    conflict_keys = {c["field_key"] for c in conflicts}
    for key, item in mapped.items():
        if key in conflict_keys:
            continue
        value = item["value"]
        definition = definitions[key]
        if definition["data_type"] == "boolean" and not isinstance(value, bool):
            normalized = _norm(value)
            if normalized in {"yes", "true", "1"}: value = True
            elif normalized in {"no", "false", "0"}: value = False
            else: continue
        if definition["data_type"] == "list" and not isinstance(value, list):
            value = [x.strip() for x in re.split(r"[,;]", str(value)) if x.strip()]
        unit = definition.get("unit")
        set_value(envelope, key, value, unit=unit, status="extracted_unconfirmed",
                  source_type="brand_excel", source_ref=item["source_ref"], registry=registry)
    return {"envelope": envelope, "raw_values": raw, "conflicts": conflicts,
            "unmapped": [item for item in raw if item["mapped_field"] is None]}
