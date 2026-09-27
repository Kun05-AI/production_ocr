from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


class FormTemplate:
    """
    Geometry/cropping utilities for a versioned form profile.

    Canonical geometry source:
        cfg["geometry"]["table"]
        cfg["geometry"]["horizontal_lines"]
        cfg["geometry"]["vertical_lines"]

    Coordinates are absolute pixels in the registered page coordinate
    system. This matches the current T1/v1 form.json.
    """

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path).resolve()

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            self.cfg: dict[str, Any] = json.load(f)

        self._validate_config()

    # ------------------------------------------------------------------
    # Profile properties
    # ------------------------------------------------------------------

    @property
    def page_width(self) -> int:
        return int(self.cfg["page"]["width"])

    @property
    def page_height(self) -> int:
        return int(self.cfg["page"]["height"])

    @property
    def page_slots(self) -> int:
        return int(self.cfg["row_strategy"]["count"])

    @property
    def table_bbox(self) -> tuple[int, int, int, int]:
        """
        Return absolute page coordinates:
            (x1, y1, x2, y2)
        """
        table = self.cfg["geometry"]["table"]

        return (
            int(table["x1"]),
            int(table["y1"]),
            int(table["x2"]),
            int(table["y2"]),
        )

    @property
    def horizontal_lines(self) -> tuple[int, ...]:
        return tuple(
            int(value)
            for value in self.cfg["geometry"]["horizontal_lines"]
        )

    @property
    def vertical_lines(self) -> tuple[int, ...]:
        return tuple(
            int(value)
            for value in self.cfg["geometry"]["vertical_lines"]
        )

    @property
    def fields(self) -> tuple[str, ...]:
        return tuple(
            str(field)
            for field in self.cfg["fields"]
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_config(self) -> None:
        if not isinstance(self.cfg, dict):
            raise ValueError(
                f"Form config root must be an object: {self.config_path}"
            )

        page = self.cfg.get("page")
        if not isinstance(page, dict):
            raise ValueError("form.json missing page object")

        for key in ("width", "height"):
            if key not in page:
                raise ValueError(
                    f"form.json page missing '{key}'"
                )

        geometry = self.cfg.get("geometry")
        if not isinstance(geometry, dict):
            raise ValueError(
                "form.json missing geometry object"
            )

        table = geometry.get("table")
        if not isinstance(table, dict):
            raise ValueError(
                "form.json missing geometry.table"
            )

        for key in ("x1", "x2", "y1", "y2"):
            if key not in table:
                raise ValueError(
                    f"geometry.table missing '{key}'"
                )

        horizontal_lines = geometry.get(
            "horizontal_lines"
        )
        if not isinstance(horizontal_lines, list):
            raise ValueError(
                "geometry.horizontal_lines must be a list"
            )

        vertical_lines = geometry.get(
            "vertical_lines"
        )
        if not isinstance(vertical_lines, list):
            raise ValueError(
                "geometry.vertical_lines must be a list"
            )

        row_strategy = self.cfg.get("row_strategy")
        if not isinstance(row_strategy, dict):
            raise ValueError(
                "form.json missing row_strategy object"
            )

        row_count = row_strategy.get("count")
        if not isinstance(row_count, int) or row_count <= 0:
            raise ValueError(
                "row_strategy.count must be a positive integer"
            )

        fields = self.cfg.get("fields")
        if not isinstance(fields, list):
            raise ValueError(
                "form.json fields must be a list"
            )

        if len(horizontal_lines) != row_count + 1:
            raise ValueError(
                "horizontal_lines count must equal "
                "row_strategy.count + 1: "
                f"{len(horizontal_lines)} != {row_count + 1}"
            )

        if len(vertical_lines) != len(fields) + 1:
            raise ValueError(
                "vertical_lines count must equal "
                "len(fields) + 1: "
                f"{len(vertical_lines)} != {len(fields) + 1}"
            )

        # Validate monotonic geometry.
        horizontal = [
            int(value)
            for value in horizontal_lines
        ]

        vertical = [
            int(value)
            for value in vertical_lines
        ]

        if any(
            current <= previous
            for previous, current
            in zip(horizontal, horizontal[1:])
        ):
            raise ValueError(
                "geometry.horizontal_lines must be strictly increasing"
            )

        if any(
            current <= previous
            for previous, current
            in zip(vertical, vertical[1:])
        ):
            raise ValueError(
                "geometry.vertical_lines must be strictly increasing"
            )

        x1 = int(table["x1"])
        x2 = int(table["x2"])
        y1 = int(table["y1"])
        y2 = int(table["y2"])

        if not (x1 < x2 and y1 < y2):
            raise ValueError(
                "geometry.table has invalid bounds: "
                f"({x1}, {y1}, {x2}, {y2})"
            )

        if horizontal[0] != y1 or horizontal[-1] != y2:
            raise ValueError(
                "horizontal_lines endpoints must match table y bounds"
            )

        if vertical[0] != x1 or vertical[-1] != x2:
            raise ValueError(
                "vertical_lines endpoints must match table x bounds"
            )

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------

    def _validate_image_size(
        self,
        image: Image.Image,
    ) -> None:
        expected = (
            self.page_width,
            self.page_height,
        )

        if image.size != expected:
            raise ValueError(
                "Image size does not match form profile: "
                f"expected {expected}, got {image.size}"
            )

    def crop_abs(
        self,
        image: Image.Image,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> Image.Image:
        """
        Crop using absolute page-pixel coordinates.
        """
        self._validate_image_size(image)

        if not (
            0 <= x1 < x2 <= image.width
            and 0 <= y1 < y2 <= image.height
        ):
            raise ValueError(
                "Invalid absolute crop bounds: "
                f"({x1}, {y1}, {x2}, {y2})"
            )

        return image.crop(
            (x1, y1, x2, y2)
        )

    def crop_normalized(
        self,
        image: Image.Image,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
    ) -> Image.Image:
        """
        Legacy/general helper for normalized 0..1 coordinates.

        This is kept separate from canonical form geometry so that
        pixel-based profile geometry is never silently interpreted as
        normalized coordinates.
        """
        self._validate_image_size(image)

        if not (
            0.0 <= x0 < x1 <= 1.0
            and 0.0 <= y0 < y1 <= 1.0
        ):
            raise ValueError(
                "Normalized crop coordinates must satisfy "
                "0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1"
            )

        box = (
            round(x0 * image.width),
            round(y0 * image.height),
            round(x1 * image.width),
            round(y1 * image.height),
        )

        return image.crop(box)

    # ------------------------------------------------------------------
    # Row geometry
    # ------------------------------------------------------------------

    def row_bbox(
        self,
        row_index: int,
    ) -> tuple[int, int, int, int]:
        """
        Return the exact pixel bbox for a row slot.

        Row index is zero-based:
            0 -> first row
            page_slots - 1 -> last row
        """
        if not (
            isinstance(row_index, int)
            and 0 <= row_index < self.page_slots
        ):
            raise IndexError(
                f"row_index out of range: {row_index}; "
                f"valid range = 0..{self.page_slots - 1}"
            )

        x1, _, x2, _ = self.table_bbox
        lines = self.horizontal_lines

        y1 = lines[row_index]
        y2 = lines[row_index + 1]

        return (
            x1,
            y1,
            x2,
            y2,
        )

    def row_crop(
        self,
        image: Image.Image,
        row_index: int,
    ) -> Image.Image:
        """
        Crop one exact row slot from the canonical form geometry.
        """
        x1, y1, x2, y2 = self.row_bbox(
            row_index
        )

        return self.crop_abs(
            image,
            x1,
            y1,
            x2,
            y2,
        )

    # ------------------------------------------------------------------
    # Field geometry
    # ------------------------------------------------------------------

    def field_bbox(
        self,
        field: str,
    ) -> tuple[int, int]:
        """
        Return absolute x bounds (x1, x2) for a field.

        Field order comes from form.json["fields"] and maps to the
        corresponding interval in geometry.vertical_lines.
        """
        if field not in self.fields:
            raise KeyError(
                f"Unknown field '{field}'. "
                f"Available fields: {list(self.fields)}"
            )

        field_index = self.fields.index(field)
        lines = self.vertical_lines

        return (
            lines[field_index],
            lines[field_index + 1],
        )

    def field_crop(
        self,
        row_image: Image.Image,
        field: str,
    ) -> Image.Image:
        """
        Crop one field from a row crop.

        row_image must be produced from row_crop(), so its width equals
        table width and its x-origin is table.x1.
        """
        x1, x2 = self.field_bbox(field)
        table_x1, _, table_x2, _ = self.table_bbox

        expected_width = table_x2 - table_x1

        if row_image.width != expected_width:
            raise ValueError(
                "row_image width does not match table geometry: "
                f"expected {expected_width}, "
                f"got {row_image.width}"
            )

        relative_x1 = x1 - table_x1
        relative_x2 = x2 - table_x1

        if not (
            0 <= relative_x1 < relative_x2 <= row_image.width
        ):
            raise ValueError(
                f"Invalid field crop for '{field}': "
                f"{relative_x1}:{relative_x2}"
            )

        return row_image.crop(
            (
                relative_x1,
                0,
                relative_x2,
                row_image.height,
            )
        )