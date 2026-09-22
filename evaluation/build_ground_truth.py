"""
Production OCR — Ground Truth Dataset Builder

Purpose
-------
Phase 2 utility for building a reproducible Ground Truth inventory before
OCR tuning.

This script:
1. Scans real GCCK member folders and PDF files.
2. Treats T1.pdf ... T4.pdf as WEEK/DOCUMENT identifiers, not form IDs.
3. Counts pages dynamically (no hard-coded "7 pages per PDF" assumption).
4. Optionally renders PDF pages to PNG for annotation.
5. Loads the current form profile (optional) to obtain row count + canonical
   OCR field names.
6. Creates:
      evaluation/ground_truth/manifest.json
      evaluation/ground_truth/page_annotations.jsonl
      evaluation/ground_truth/README.md

Important
---------
Ground Truth values must be entered/verified by a human.
This script NEVER invents transcription values.

Typical usage
-------------
Inventory only:
    python .\evaluation\build_ground_truth.py

Inventory + render source pages:
    python .\evaluation\build_ground_truth.py --render --dpi 150

Use the current T1/v1 form profile:
    python .\evaluation\build_ground_truth.py --form T1 --version v1

Build everything:
    python .\evaluation\build_ground_truth.py --form T1 --version v1 --render --dpi 150
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise SystemExit(
        "PyMuPDF chưa được cài. Cài bằng:\n"
        "    pip install pymupdf"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GCCK_ROOT = PROJECT_ROOT / "gcck" / "BÁO CÁO"
EVALUATION_ROOT = PROJECT_ROOT / "evaluation"
GROUND_TRUTH_ROOT = EVALUATION_ROOT / "ground_truth"

DEFAULT_FORM_ID = "T1"
DEFAULT_FORM_VERSION = "v1"


@dataclass(frozen=True)
class DocumentRecord:
    member_id: str
    member_name: str
    document_id: str
    week_number: int | None
    pdf_path: str
    page_count: int
    pages: list[dict[str, Any]]


def parse_member_folder(folder_name: str) -> tuple[str, str]:
    """
    Parse:
        '1207. NGUYEN TRUONG NHAN'
    into:
        ('1207', 'NGUYEN TRUONG NHAN')
    """
    match = re.match(r"^\s*(\d+)\.\s*(.+?)\s*$", folder_name)
    if not match:
        raise ValueError(
            f"Invalid member folder name: {folder_name!r}. "
            "Expected '<employee_id>. <name>'."
        )
    return match.group(1), match.group(2)


def parse_document_name(pdf_path: Path) -> tuple[str, int | None]:
    """
    T1.pdf ... T4.pdf represent weekly document instances in GCCK data.
    They are NOT automatically form IDs or form versions.
    """
    stem = pdf_path.stem.strip().upper()
    match = re.fullmatch(r"T(\d+)", stem)
    if match:
        number = int(match.group(1))
        return stem, number
    return stem, None


def load_form_profile(
    form_id: str | None,
    version: str | None,
) -> dict[str, Any]:
    if not form_id or not version:
        return {}

    profile_path = (
        PROJECT_ROOT
        / "config"
        / "forms"
        / form_id
        / version
        / "form.json"
    )

    if not profile_path.is_file():
        raise FileNotFoundError(
            f"Form profile not found:\n{profile_path}"
        )

    with profile_path.open("r", encoding="utf-8") as handle:
        profile = json.load(handle)

    if not isinstance(profile, dict):
        raise ValueError("form.json root must be an object.")

    return profile


def discover_documents() -> list[DocumentRecord]:
    if not GCCK_ROOT.is_dir():
        raise FileNotFoundError(
            f"GCCK root not found:\n{GCCK_ROOT}"
        )

    member_dirs = sorted(
        path
        for path in GCCK_ROOT.iterdir()
        if path.is_dir()
    )

    if not member_dirs:
        raise FileNotFoundError(
            f"No member directories found in:\n{GCCK_ROOT}"
        )

    documents: list[DocumentRecord] = []

    for member_dir in member_dirs:
        member_id, member_name = parse_member_folder(member_dir.name)

        pdfs = sorted(
            path
            for path in member_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".pdf"
        )

        for pdf_path in pdfs:
            document_id, week_number = parse_document_name(pdf_path)

            with fitz.open(pdf_path) as document:
                page_count = len(document)
                pages = [
                    {
                        "page": page_number,
                        "source_pdf": str(pdf_path),
                    }
                    for page_number in range(1, page_count + 1)
                ]

            documents.append(
                DocumentRecord(
                    member_id=member_id,
                    member_name=member_name,
                    document_id=document_id,
                    week_number=week_number,
                    pdf_path=str(pdf_path),
                    page_count=page_count,
                    pages=pages,
                )
            )

    return documents


def render_pages(
    documents: list[DocumentRecord],
    output_root: Path,
    dpi: int,
) -> int:
    if dpi <= 0:
        raise ValueError("DPI must be > 0.")

    output_root.mkdir(parents=True, exist_ok=True)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    rendered = 0

    for record in documents:
        member_dir = (
            output_root
            / record.member_id
            / record.document_id
        )
        member_dir.mkdir(parents=True, exist_ok=True)

        with fitz.open(record.pdf_path) as document:
            for page_index, page_info in enumerate(
                record.pages,
                start=1,
            ):
                page = document.load_page(page_index - 1)
                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                output_path = (
                    member_dir
                    / f"{record.document_id}_page_{page_index:03d}.png"
                )

                pixmap.save(str(output_path))
                rendered += 1

    return rendered


def build_page_annotations(
    documents: list[DocumentRecord],
    form_profile: dict[str, Any],
) -> list[dict[str, Any]]:
    fields = form_profile.get(
        "fields",
        [
            "stt",
            "date",
            "order_code",
            "drawing_code",
            "revision",
            "work_code",
            "target_time",
            "start_time",
            "end_time",
            "processed_qty",
            "good_qty",
            "ng_qty",
            "process_detail",
            "note",
        ],
    )

    if not isinstance(fields, list):
        raise ValueError("form.json 'fields' must be a list.")

    row_strategy = form_profile.get("row_strategy", {})
    row_count = row_strategy.get("count", 20)

    if not isinstance(row_count, int) or row_count <= 0:
        raise ValueError(
            "form.json row_strategy.count must be a positive integer."
        )

    records: list[dict[str, Any]] = []

    for document in documents:
        for page in document.pages:
            sample_id = (
                f"{document.member_id}_"
                f"{document.document_id}_"
                f"p{page['page']:03d}"
            )

            records.append(
                {
                    "sample_id": sample_id,
                    "member_id": document.member_id,
                    "member_name": document.member_name,
                    "document_id": document.document_id,
                    "week_number": document.week_number,
                    "page": page["page"],
                    "source_pdf": document.pdf_path,
                    "source_image": None,
                    "form_id": form_profile.get("form_id"),
                    "form_version": form_profile.get("version"),
                    "annotation_status": "UNLABELED",
                    "rows": [
                        {
                            "row_number": row_number,
                            "active": None,
                            "ground_truth": {
                                field: None
                                for field in fields
                            },
                        }
                        for row_number in range(1, row_count + 1)
                    ],
                }
            )

    return records


def write_json(
    path: Path,
    payload: Any,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            payload,
            handle,
            ensure_ascii=False,
            indent=2,
        )


def write_jsonl(
    path: Path,
    records: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def write_readme(
    path: Path,
    form_profile: dict[str, Any],
    total_members: int,
    total_documents: int,
    total_pages: int,
) -> None:
    form_id = form_profile.get("form_id")
    form_version = form_profile.get("version")

    profile_text = (
        f"{form_id}/{form_version}"
        if form_id and form_version
        else "not specified"
    )

    content = f"""# Ground Truth Dataset

## Purpose

Phase 2 dataset scaffold for Production OCR.

The current GCCK dataset contains:

- members: {total_members}
- PDF document instances: {total_documents}
- total pages discovered: {total_pages}

The PDF names `T1.pdf` ... `T4.pdf` are treated as **weekly document
instances**, not automatically as form IDs or form versions.

Current form profile used to generate the row/field template:

```text
{profile_text}
```

## Files

### `manifest.json`

Inventory of all members, PDFs and page counts.

### `page_annotations.jsonl`

One JSON record per source page.

Each page contains fixed row slots and the canonical OCR fields.
Human annotators fill the values.

## Annotation rules

- Do not invent unreadable text.
- Use `null` when the field is genuinely blank or not readable.
- Preserve Vietnamese diacritics.
- Preserve capitalization, numbers, punctuation and technical codes when visible.
- Do not normalize business meaning during transcription.
- Keep `member_id`, `document_id`, `page`, and `row_number` unchanged.
- `active` means the row contains report data and is therefore eligible for OCR.
- Ground Truth is human verified; this file is only a scaffold.

## Important separation

```text
Phase 2
    build + verify Ground Truth

Phase 7
    OCR prediction

Phase 9
    compare predictions with Ground Truth
    ↓
    Character Accuracy
    Field Accuracy
    Row Accuracy
    Page Accuracy
```

## Recommended sampling strategy

Do not label only one employee.

Use a representative subset across:

```text
multiple members
multiple weekly PDFs
multiple pages
different handwriting
technical codes / numbers
blank rows
filled rows
```
"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_manifest(
    documents: list[DocumentRecord],
    form_profile: dict[str, Any],
    rendered_root: Path | None,
) -> dict[str, Any]:
    members = sorted(
        {
            document.member_id
            for document in documents
        }
    )

    total_pages = sum(
        document.page_count
        for document in documents
    )

    document_payloads: list[dict[str, Any]] = []

    for document in documents:
        pages: list[dict[str, Any]] = []

        for page in document.pages:
            page_number = page["page"]

            rendered_path = None
            if rendered_root is not None:
                rendered_path = str(
                    rendered_root
                    / document.member_id
                    / document.document_id
                    / (
                        f"{document.document_id}"
                        f"_page_{page_number:03d}.png"
                    )
                )

            pages.append(
                {
                    "page": page_number,
                    "source_pdf": document.pdf_path,
                    "rendered_image": rendered_path,
                }
            )

        document_payloads.append(
            {
                "member_id": document.member_id,
                "member_name": document.member_name,
                "document_id": document.document_id,
                "week_number": document.week_number,
                "pdf_path": document.pdf_path,
                "page_count": document.page_count,
                "pages": pages,
            }
        )

    return {
        "schema_version": 1,
        "purpose": "Production OCR Phase 2 Ground Truth inventory",
        "form_profile": {
            "form_id": form_profile.get("form_id"),
            "version": form_profile.get("version"),
        },
        "source_root": str(GCCK_ROOT),
        "summary": {
            "members": len(members),
            "documents": len(documents),
            "pages": total_pages,
        },
        "documents": document_payloads,
    }


def print_summary(
    documents: list[DocumentRecord],
    rendered_pages: int,
    manifest_path: Path,
    annotations_path: Path,
) -> None:
    members = {
        record.member_id
        for record in documents
    }

    total_pages = sum(
        record.page_count
        for record in documents
    )

    print("=" * 72)
    print("PRODUCTION OCR — PHASE 2 GROUND TRUTH BUILDER")
    print("=" * 72)
    print(f"Source root    : {GCCK_ROOT}")
    print(f"Members        : {len(members)}")
    print(f"PDF documents  : {len(documents)}")
    print(f"Total pages    : {total_pages}")
    print(f"Rendered pages : {rendered_pages}")
    print()
    print("Documents:")

    for record in documents:
        print(
            f"  [{record.member_id}] "
            f"{record.member_name} -> "
            f"{record.document_id}.pdf : "
            f"{record.page_count} pages"
        )

    print()
    print(f"Manifest       : {manifest_path}")
    print(f"Annotations    : {annotations_path}")
    print()
    print(
        "IMPORTANT: page_annotations.jsonl is a HUMAN-LABEL TEMPLATE. "
        "No OCR value is invented by this script."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build Production OCR Phase 2 Ground Truth inventory "
            "and annotation scaffold."
        )
    )

    parser.add_argument(
        "--form",
        default=DEFAULT_FORM_ID,
        help="Optional form profile ID, e.g. T1.",
    )

    parser.add_argument(
        "--version",
        default=DEFAULT_FORM_VERSION,
        help="Optional form profile version, e.g. v1.",
    )

    parser.add_argument(
        "--no-form-profile",
        action="store_true",
        help=(
            "Do not load config/forms/<FORM>/<VERSION>/form.json. "
            "Use default canonical fields and 20 row slots."
        ),
    )

    parser.add_argument(
        "--render",
        action="store_true",
        help="Render every discovered PDF page to PNG.",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Rendering DPI when --render is used (default: 150).",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite generated Ground Truth files.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    form_profile = (
        {}
        if args.no_form_profile
        else load_form_profile(
            args.form,
            args.version,
        )
    )

    documents = discover_documents()

    render_root = (
        GROUND_TRUTH_ROOT / "source_pages"
        if args.render
        else None
    )

    manifest_path = GROUND_TRUTH_ROOT / "manifest.json"
    annotations_path = (
        GROUND_TRUTH_ROOT / "page_annotations.jsonl"
    )
    readme_path = GROUND_TRUTH_ROOT / "README.md"

    existing_outputs = [
        path
        for path in (
            manifest_path,
            annotations_path,
        )
        if path.exists()
    ]

    if existing_outputs and not args.force:
        raise FileExistsError(
            "Ground Truth output already exists:\n"
            + "\n".join(str(path) for path in existing_outputs)
            + "\n\nUse --force to regenerate."
        )

    rendered_pages = 0

    if args.render:
        rendered_pages = render_pages(
            documents,
            render_root,
            args.dpi,
        )

    page_annotations = build_page_annotations(
        documents,
        form_profile,
    )

    manifest = build_manifest(
        documents,
        form_profile,
        render_root,
    )

    if render_root is not None:
        for record in page_annotations:
            source_image = (
                render_root
                / record["member_id"]
                / record["document_id"]
                / (
                    f"{record['document_id']}"
                    f"_page_{record['page']:03d}.png"
                )
            )
            record["source_image"] = str(source_image)

    write_json(
        manifest_path,
        manifest,
    )

    write_jsonl(
        annotations_path,
        page_annotations,
    )

    write_readme(
        readme_path,
        form_profile,
        manifest["summary"]["members"],
        manifest["summary"]["documents"],
        manifest["summary"]["pages"],
    )

    print_summary(
        documents,
        rendered_pages,
        manifest_path,
        annotations_path,
    )


if __name__ == "__main__":
    main()
