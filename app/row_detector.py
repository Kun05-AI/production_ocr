from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from .form_template import FormTemplate


DARK_PIXEL_THRESHOLD = 150
INK_RATIO_THRESHOLD = 0.006

# Registration can leave a grid line displaced/slanted relative to the
# canonical profile. Search locally around the known geometry instead of
# assuming the residual line is exactly at the profile coordinate.
GRID_X_SEARCH_PX = 20
GRID_Y_SEARCH_PX = 12
GRID_LINE_HALF_WIDTH_PX = 5
GRID_BOUNDARY_HALF_HEIGHT_PX = 5

# Printed static content that must not make a row active.
# T1/v1 has pre-printed STT numbers 1..20.
ACTIVITY_IGNORED_FIELDS = ("stt",)


def _mask_shifted_vertical_lines(
    bw: np.ndarray,
    template: FormTemplate,
    *,
    search_px: int = GRID_X_SEARCH_PX,
    half_width_px: int = GRID_LINE_HALF_WIDTH_PX,
) -> np.ndarray:
    """Mask vertical grid lines near canonical x coordinates.

    The actual registered line may be displaced a few pixels from the profile
    or become slightly slanted. A local occupancy search finds its strongest
    x-position, then masks a small neighborhood around it.
    """
    masked = bw.copy()
    h, w = masked.shape

    table_x1, _, table_x2, _ = template.table_bbox
    expected_width = table_x2 - table_x1
    if w != expected_width:
        raise ValueError(
            "Row image width does not match form table geometry: "
            f"expected {expected_width}, got {w}"
        )

    for page_x in template.vertical_lines:
        expected_x = int(page_x) - table_x1
        if expected_x < 0 or expected_x > w:
            raise ValueError(
                "Vertical line falls outside table geometry: "
                f"page_x={page_x}, table_x1={table_x1}, table_x2={table_x2}"
            )

        left = max(0, expected_x - search_px)
        right = min(w, expected_x + search_px + 1)

        band = masked[:, left:right]
        if band.size == 0:
            continue

        occupancy = band.sum(axis=0) / 255.0 / max(h, 1)

        # Smooth the occupancy so a slightly slanted line still produces
        # one strong local peak.
        if occupancy.size >= 3:
            kernel = np.ones(3, dtype=np.float32) / 3.0
            smooth = np.convolve(occupancy, kernel, mode="same")
        else:
            smooth = occupancy

        local_index = int(np.argmax(smooth))
        actual_x = left + local_index

        mask_left = max(0, actual_x - half_width_px)
        mask_right = min(w, actual_x + half_width_px + 1)
        masked[:, mask_left:mask_right] = False

    return masked


def _mask_shifted_horizontal_boundaries(
    bw: np.ndarray,
    *,
    search_px: int = GRID_Y_SEARCH_PX,
    half_height_px: int = GRID_BOUNDARY_HALF_HEIGHT_PX,
) -> np.ndarray:
    """Mask top/bottom row boundaries after local image-based alignment."""
    masked = bw.copy()
    h, w = masked.shape

    if h == 0 or w == 0:
        return masked

    # Top boundary: search only near the crop's top edge.
    top_right = min(h, search_px + 1)
    top_band = masked[:top_right, :]
    top_occ = top_band.sum(axis=1) / 255.0 / max(w, 1)

    if top_occ.size:
        top_y = int(np.argmax(top_occ))
        top_left = max(0, top_y - half_height_px)
        top_right_mask = min(h, top_y + half_height_px + 1)
        masked[top_left:top_right_mask, :] = False

    # Bottom boundary: search only near the crop's bottom edge.
    bottom_left = max(0, h - search_px - 1)
    bottom_band = masked[bottom_left:, :]
    bottom_occ = bottom_band.sum(axis=1) / 255.0 / max(w, 1)

    if bottom_occ.size:
        bottom_y = bottom_left + int(np.argmax(bottom_occ))
        bottom_mask_left = max(0, bottom_y - half_height_px)
        bottom_mask_right = min(h, bottom_y + half_height_px + 1)
        masked[bottom_mask_left:bottom_mask_right, :] = False

    return masked


def _mask_known_geometry(
    bw: np.ndarray,
    template: FormTemplate,
) -> np.ndarray:
    """Remove printed grid geometry using profile-anchored local searches."""
    if bw.ndim != 2:
        raise ValueError(f"Expected 2-D binary image, got shape={bw.shape}")

    masked = bw.copy()

    masked = _mask_shifted_horizontal_boundaries(
        masked,
    )
    masked = _mask_shifted_vertical_lines(
        masked,
        template,
    )

    # Remove static printed STT numbers.
    table_x1, _, table_x2, _ = template.table_bbox
    expected_width = table_x2 - table_x1

    for field in ACTIVITY_IGNORED_FIELDS:
        if field not in template.fields:
            continue

        field_x1, field_x2 = template.field_bbox(field)
        rel_x1 = max(0, field_x1 - table_x1)
        rel_x2 = min(expected_width, field_x2 - table_x1)

        if rel_x1 < rel_x2:
            masked[:, rel_x1:rel_x2] = False

    return masked


def row_ink_score(
    row_image: Image.Image,
    template: FormTemplate,
    dark_pixel_threshold: int = DARK_PIXEL_THRESHOLD,
) -> float:
    """Return non-static dark-pixel occupancy for row activity scoring."""
    arr = np.asarray(row_image.convert("L"))
    if arr.size == 0:
        return 0.0

    bw = arr < dark_pixel_threshold
    bw = _mask_known_geometry(bw, template)

    return float(bw.mean())


def row_has_ink(
    row_image: Image.Image,
    template: FormTemplate,
    threshold: float = INK_RATIO_THRESHOLD,
    *,
    dark_pixel_threshold: int = DARK_PIXEL_THRESHOLD,
) -> bool:
    """Return True when the row contains enough non-static dark pixels."""
    return row_ink_score(
        row_image,
        template,
        dark_pixel_threshold=dark_pixel_threshold,
    ) > threshold


def detect_active_rows(
    image_path: str | Path,
    template: FormTemplate,
) -> list[int]:
    img = Image.open(image_path).convert("RGB")
    active: list[int] = []

    for idx in range(template.page_slots):
        row = template.row_crop(img, idx)

        if row_has_ink(row, template):
            active.append(idx)

    return active
