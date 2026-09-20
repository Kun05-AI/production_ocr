from __future__ import annotations

from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from .form_template import FormTemplate


def row_has_ink(row_image: Image.Image, threshold: float = 0.006) -> bool:
    arr = np.array(row_image.convert("L"))
    # Dark-pixel ratio. Printed grid is present on every row, so mask long
    # horizontal and vertical lines before estimating handwriting/text occupancy.
    bw = arr < 150
    if bw.size == 0:
        return False
    h, w = bw.shape
    horizontal = bw.sum(axis=1) / max(w, 1)
    line_rows = horizontal > 0.55
    bw[line_rows, :] = False
    vertical = bw.sum(axis=0) / max(h, 1)
    line_columns = vertical > 0.55
    bw[:, line_columns] = False
    return float(bw.mean()) > threshold


def detect_active_rows(image_path: str | Path, template: FormTemplate) -> list[int]:
    img = Image.open(image_path).convert("RGB")
    active: list[int] = []
    for idx in range(int(template.cfg["page_slots"])):
        row = template.row_crop(img, idx)
        if row_has_ink(row):
            active.append(idx)
    return active
