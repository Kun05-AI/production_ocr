from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from PIL import Image


class FormTemplate:
    def __init__(self, config_path: str | Path):
        with open(config_path, encoding="utf-8") as f:
            self.cfg: dict[str, Any] = json.load(f)

    def crop(self, image: Image.Image, x0: float, y0: float, x1: float, y1: float) -> Image.Image:
        w, h = image.size
        box = (round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))
        return image.crop(box)

    def row_crop(self, image: Image.Image, row_index: int) -> Image.Image:
        table = self.cfg["table"]
        page_slots = int(self.cfg["page_slots"])
        header_fraction = float(table["header_fraction"])
        body_y0 = table["y0"] + (table["y1"] - table["y0"]) * header_fraction
        body_y1 = table["y1"]
        row_h = (body_y1 - body_y0) / page_slots
        y0 = body_y0 + row_h * row_index
        y1 = y0 + row_h
        return self.crop(image, table["x0"], y0, table["x1"], y1)

    def field_crop(self, row_image: Image.Image, field: str) -> Image.Image:
        x0, x1 = self.cfg["columns"][field]
        table_x0 = self.cfg["table"]["x0"]
        table_x1 = self.cfg["table"]["x1"]
        table_width = table_x1 - table_x0
        # Column coordinates are page-relative; row_image is table-relative.
        x0 = max(0.0, min(1.0, (x0 - table_x0) / table_width))
        x1 = max(0.0, min(1.0, (x1 - table_x0) / table_width))
        w, h = row_image.size
        return row_image.crop((round(x0 * w), 0, round(x1 * w), h))
