r"""
Production OCR - Phase 2 - 300 DPI Annotation-Master Renderer

Purpose
-------
Render the already-frozen 24-page DEV Ground Truth selection at 300 DPI,
directly from the original source PDFs, into a NEW directory:

    evaluation/ground_truth/selection/selected_pages_300dpi/

This script does NOT:
- change the 24-page selection (reads dev_selection.json read-only),
- touch source_pages/ (100 DPI),
- touch selection/selected_pages/ (150 DPI),
- touch dev_selection.json, dev_selection_index.csv, dev_annotations.jsonl,
  DEV_ANNOTATION_GUIDE.md, or ground_truth_dev_24pages.pdf,
- modify select_ground_truth_dev.py or app/pdf_processor.py,
- modify any schema (OCR or Ground Truth).

It reuses the existing render_selected_pages() function
from evaluation/select_ground_truth_dev.py.

Usage:
    python .\evaluation\render_dev_annotation_300dpi.py

Run this ONLY after Gate #2 approval, on the real D:\production_ocr repo.

This script has NOT been executed against the real repository.
"""

from __future__ import annotations

import json
from pathlib import Path

from select_ground_truth_dev import (
    DEV_ROOT,
    SELECTION_JSON,
    render_selected_pages,
)

OUTPUT_ROOT = DEV_ROOT / "selected_pages_300dpi"
TARGET_DPI = 300


def load_frozen_selection() -> list[dict]:
    if not SELECTION_JSON.is_file():
        raise FileNotFoundError(
            f"Frozen selection not found:\n{SELECTION_JSON}\n"
            "This script must not create a new selection. "
            "Run select_ground_truth_dev.py first if this is missing "
            "(it should already exist)."
        )

    with SELECTION_JSON.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    records = payload.get("pages")

    if not isinstance(records, list) or len(records) != 24:
        raise ValueError(
            "dev_selection.json did not contain exactly 24 pages. "
            f"Found: {len(records) if isinstance(records, list) else 'N/A'}. "
            "Refusing to proceed — the selection must remain frozen at 24 pages."
        )

    return records


def main() -> None:
    records = load_frozen_selection()

    print("=" * 72)
    print("PHASE 2 - 300 DPI ANNOTATION-MASTER RENDER")
    print("=" * 72)
    print(f"Frozen selection : {SELECTION_JSON}")
    print(f"Records loaded   : {len(records)}")
    print(f"Output directory : {OUTPUT_ROOT}")
    print(f"Target DPI       : {TARGET_DPI}")
    print()

    if OUTPUT_ROOT.exists() and any(OUTPUT_ROOT.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty:\n{OUTPUT_ROOT}\n"
            "Refusing to overwrite. This script never deletes files itself."
        )

    # render_selected_pages() mutates each record dict in-memory
    # (sets record["rendered_image"], record["render_dpi"]).
    # It does NOT write back to dev_selection.json.
    render_selected_pages(records, OUTPUT_ROOT, TARGET_DPI)

    rendered_files = sorted(OUTPUT_ROOT.rglob("*.png"))

    print(f"Rendered {len(rendered_files)} PNG file(s).")
    print()

    if len(rendered_files) != 24:
        raise RuntimeError(
            f"Expected 24 rendered PNG files, got {len(rendered_files)}. "
        )

    for path in rendered_files:
        print(f"  {path}")

    print()
    print(
        "Next: run the verification checklist manually "
        "(count, identity, dimensions, preservation, visual inspection) "
        "before any annotation work begins."
    )


if __name__ == "__main__":
    main()