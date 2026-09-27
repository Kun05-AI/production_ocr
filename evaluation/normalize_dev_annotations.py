"""
Production OCR - Normalize DEV Ground Truth annotations

Purpose:
    Normalize the Phase 2 DEV annotation scaffold to the canonical
    T1/v1 row schema shared by form.json and app/qwen_ocr.py.

Input:
    evaluation/ground_truth/selection/dev_annotations.jsonl

Output:
    same file, after making a timestamp-free .bak backup once per run:
    evaluation/ground_truth/selection/dev_annotations.jsonl.bak

Canonical fields:
    stt
    date
    order_code
    drawing_code
    work_code
    target_time
    start_time
    end_time
    total_time
    processed_qty
    good_qty
    ng_qty
    process_detail
    note

Schema rules:
    - `revision` is not a T1/v1 row field.
    - `total_time` is a canonical row field.
    - Page-level totals such as `33,75` are derived values and are not
      stored inside rows[*].ground_truth.

This script only changes the row schema scaffold.
It does NOT fill Ground Truth values and does NOT change the selected pages.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "ground_truth"
    / "selection"
    / "dev_annotations.jsonl"
)

CANONICAL_FIELDS = [
    "stt",
    "date",
    "order_code",
    "drawing_code",
    "work_code",
    "target_time",
    "start_time",
    "end_time",
    "total_time",
    "processed_qty",
    "good_qty",
    "ng_qty",
    "process_detail",
    "note",
]

def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    rows = record.get("rows")
    if not isinstance(rows, list):
        raise ValueError(
            f"{record.get('sample_id', '<unknown>')}: rows must be a list."
        )

    normalized_rows: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(
                f"{record.get('sample_id', '<unknown>')}: row must be an object."
            )

        old_gt = row.get("ground_truth", {})
        if not isinstance(old_gt, dict):
            old_gt = {}

        new_gt = {
            field: old_gt.get(field)
            for field in CANONICAL_FIELDS
        }

        normalized_rows.append(
            {
                "row_number": row.get("row_number"),
                "active": row.get("active"),
                "ground_truth": new_gt,
            }
        )

    output = dict(record)
    output.pop("non_ocr_form_fields", None)

    output["annotation_schema"] = "qwen_row_v1"
    output["annotation_status"] = record.get(
        "annotation_status",
        "UNLABELED",
    )
    output["rows"] = normalized_rows

    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_PATH,
        help="DEV annotations JSONL to normalize.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing .bak backup.",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()

    if not input_path.is_file():
        raise FileNotFoundError(
            f"DEV annotations not found:\n{input_path}"
        )

    backup_path = input_path.with_suffix(input_path.suffix + ".bak")

    if backup_path.exists() and not args.force:
        raise FileExistsError(
            f"Backup already exists:\n{backup_path}\n"
            "Use --force to replace the backup."
        )

    shutil.copy2(input_path, backup_path)

    records: list[dict[str, Any]] = []

    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {line_number}: {exc}"
                ) from exc

            records.append(normalize_record(record))

    with input_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    total_rows = sum(
        len(record["rows"])
        for record in records
    )

    print("=" * 72)
    print("NORMALIZE DEV GROUND TRUTH ANNOTATIONS")
    print("=" * 72)
    print(f"Input/output : {input_path}")
    print(f"Backup       : {backup_path}")
    print(f"Pages        : {len(records)}")
    print(f"Rows         : {total_rows}")
    print()
    print("Canonical OCR fields:")
    for field in CANONICAL_FIELDS:
        print(f"  - {field}")
    print()
    print(
        "No Ground Truth values were filled; selected pages are unchanged."
    )


if __name__ == "__main__":
    main()
