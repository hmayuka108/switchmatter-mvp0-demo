"""Small JSON persistence layer for SKU envelopes and component BOMs."""
from __future__ import annotations

import json
from pathlib import Path


class PipelineStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return {"envelopes": {}, "components": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save_envelope(self, envelope):
        data = self.load()
        data["envelopes"][envelope["sku_id"]] = envelope
        self._write(data)

    def save_components(self, sku_id, components):
        data = self.load()
        data["components"] = [c for c in data["components"] if c["sku_id"] != sku_id] + list(components)
        self._write(data)

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, indent=2, ensure_ascii=False)
        self.path.write_text(payload, encoding="utf-8")
