from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_mapping(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def map_row(row: dict[str, Any], mapping_cfg: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for src, dst in mapping_cfg["production_mapping"].items():
        out[dst] = row.get(src)
    for src, dst in mapping_cfg.get("optional_mapping", {}).items():
        out[dst] = row.get(src)
    return out
