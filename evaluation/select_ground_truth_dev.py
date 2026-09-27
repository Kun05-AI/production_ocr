r"""
Production OCR - Phase 2 DEV Ground Truth Selector

Selects a small, reproducible development Ground Truth subset from the
143-page GCCK corpus, renders the selected pages at higher DPI, and creates
one uploadable PDF.

Current selection:
- 19 coverage pages: at least one page from every existing PDF document.
- 5 challenge pages: dense / marked / handwriting-heavy examples.

The selection is intentionally fixed for reproducibility. Change only after
reviewing the generated selection PDF.

Usage:
    python .\evaluation\select_ground_truth_dev.py

Higher/lower rendering DPI:
    python .\evaluation\select_ground_truth_dev.py --dpi 150

Overwrite existing selection:
    python .\evaluation\select_ground_truth_dev.py --force
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise SystemExit(
        "PyMuPDF chưa được cài. Cài bằng:\n"
        "    python -m pip install pymupdf"
    ) from exc

try:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.pdfgen import canvas
except ImportError as exc:
    raise SystemExit(
        "ReportLab chưa được cài. Cài bằng:\n"
        "    python -m pip install reportlab"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH_ROOT = PROJECT_ROOT / "evaluation" / "ground_truth"
MANIFEST_PATH = GROUND_TRUTH_ROOT / "manifest.json"

DEV_ROOT = GROUND_TRUTH_ROOT / "selection"
SELECTED_PAGES_ROOT = DEV_ROOT / "selected_pages"
SELECTION_JSON = DEV_ROOT / "dev_selection.json"
INDEX_CSV = DEV_ROOT / "dev_selection_index.csv"
DEV_ANNOTATIONS_JSONL = DEV_ROOT / "dev_annotations.jsonl"
DEV_GUIDE = DEV_ROOT / "DEV_ANNOTATION_GUIDE.md"
DEV_PDF = DEV_ROOT / "ground_truth_dev_24pages.pdf"


# One coverage page from every currently existing PDF document.
# Each tuple is: (member_id, document_id, page, rationale)
COVERAGE_SELECTION = [
    ("1207", "T1", 3, "coverage:dense"),
    ("1207", "T2", 4, "coverage:dense"),
    ("1207", "T3", 5, "coverage:medium_dense"),
    ("1207", "T4", 6, "coverage:dense"),
    ("1236", "T1", 4, "coverage:dense"),
    ("1236", "T2", 2, "coverage:medium_dense"),
    ("1236", "T3", 4, "coverage:dense"),
    ("1236", "T4", 6, "coverage:dense"),
    ("1263", "T1", 2, "coverage:medium_dense"),
    ("1263", "T2", 4, "coverage:dense"),
    ("1263", "T3", 4, "coverage:dense"),
    ("1263", "T4", 6, "coverage:medium_dense"),
    ("1570", "T1", 2, "coverage:dense"),
    ("1570", "T2", 2, "coverage:dense"),
    ("1570", "T3", 2, "coverage:dense"),
    ("1575", "T1", 5, "coverage:dense"),
    ("1575", "T2", 4, "coverage:dense"),
    ("1575", "T3", 2, "coverage:medium_dense"),
    ("1575", "T4", 6, "coverage:dense"),
]

# Additional challenge pages. These are deliberately not duplicates of the
# mandatory coverage page for the same document where possible.
CHALLENGE_SELECTION = [
    ("1207", "T3", 1, "challenge:high_density"),
    ("1236", "T2", 1, "challenge:highlighted_dense"),
    ("1263", "T3", 1, "challenge:high_density"),
    ("1570", "T1", 3, "challenge:high_density"),
    ("1575", "T3", 1, "challenge:high_density"),
]


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"Manifest not found:\n{MANIFEST_PATH}\n"
            "Run build_ground_truth.py first."
        )

    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("manifest.json root must be an object.")

    return payload


def index_manifest(
    manifest: dict[str, Any],
) -> dict[tuple[str, str, int], dict[str, Any]]:
    index: dict[tuple[str, str, int], dict[str, Any]] = {}

    for document in manifest.get("documents", []):
        member_id = str(document["member_id"])
        document_id = str(document["document_id"])

        for page in document.get("pages", []):
            page_number = int(page["page"])
            key = (member_id, document_id, page_number)
            index[key] = {
                "member_id": member_id,
                "member_name": document["member_name"],
                "document_id": document_id,
                "page": page_number,
                "pdf_path": document["pdf_path"],
                "page_count": int(document["page_count"]),
            }

    return index


def validate_selection(
    selection_index: dict[tuple[str, str, int], dict[str, Any]],
) -> list[dict[str, Any]]:
    combined = [
        (*item, "coverage")
        for item in COVERAGE_SELECTION
    ] + [
        (*item, "challenge")
        for item in CHALLENGE_SELECTION
    ]

    seen: set[tuple[str, str, int]] = set()
    records: list[dict[str, Any]] = []

    for member_id, document_id, page, rationale, group in combined:
        key = (member_id, document_id, page)

        if key in seen:
            raise ValueError(
                f"Duplicate selected page: {member_id}/{document_id}/p{page:03d}"
            )
        seen.add(key)

        if key not in selection_index:
            raise ValueError(
                "Selected page does not exist in manifest: "
                f"{member_id}/{document_id}/p{page:03d}"
            )

        base = selection_index[key]
        records.append(
            {
                **base,
                "selection_group": group,
                "rationale": rationale,
            }
        )

    if len(records) != 24:
        raise AssertionError(
            f"Expected exactly 24 selected pages, got {len(records)}."
        )

    # Coverage invariant: every manifest PDF document must be represented.
    selected_documents = {
        (record["member_id"], record["document_id"])
        for record in records
    }

    manifest_documents = {
        (str(document["member_id"]), str(document["document_id"]))
        for document in selection_index.values()
        # selection_index has one entry per page; reduce to unique documents
    }

    # Rebuild unique manifest document set from the page index.
    manifest_documents = {
        (value["member_id"], value["document_id"])
        for value in selection_index.values()
    }

    missing = sorted(manifest_documents - selected_documents)
    if missing:
        missing_text = ", ".join(
            f"{member}/{doc}"
            for member, doc in missing
        )
        raise ValueError(
            "Coverage selection is missing PDF documents: "
            f"{missing_text}"
        )

    return records


def render_selected_pages(
    records: list[dict[str, Any]],
    output_root: Path,
    dpi: int,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for record in records:
        member_id = record["member_id"]
        document_id = record["document_id"]
        page_number = record["page"]
        pdf_path = Path(record["pdf_path"])

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"Source PDF not found:\n{pdf_path}"
            )

        member_dir = output_root / member_id
        member_dir.mkdir(parents=True, exist_ok=True)

        output_path = (
            member_dir
            / (
                f"{member_id}_{document_id}_"
                f"page_{page_number:03d}.png"
            )
        )

        with fitz.open(pdf_path) as document:
            page = document.load_page(page_number - 1)
            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )
            pixmap.save(str(output_path))

        record["rendered_image"] = str(output_path)
        record["render_dpi"] = dpi


def write_dev_annotations(
    records: list[dict[str, Any]],
) -> None:
    source_path = GROUND_TRUTH_ROOT / "page_annotations.jsonl"
    if not source_path.is_file():
        raise FileNotFoundError(
            f"Page annotations not found:\n{source_path}\n"
            "Run build_ground_truth.py first."
        )

    selected_sample_ids = {
        f"{record['member_id']}_{record['document_id']}_"
        f"p{record['page']:03d}"
        for record in records
    }

    selected_records: dict[str, dict[str, Any]] = {}

    with source_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            payload = json.loads(line)
            sample_id = str(payload.get("sample_id", ""))

            if sample_id in selected_sample_ids:
                selected_records[sample_id] = payload

    missing = selected_sample_ids - set(selected_records)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(
            "Selected pages missing from page_annotations.jsonl: "
            f"{missing_text}"
        )

    with DEV_ANNOTATIONS_JSONL.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for record in records:
            sample_id = (
                f"{record['member_id']}_{record['document_id']}_"
                f"p{record['page']:03d}"
            )
            handle.write(
                json.dumps(
                    selected_records[sample_id],
                    ensure_ascii=False,
                )
                + "\n"
            )


def write_dev_guide(
    records: list[dict[str, Any]],
) -> None:
    lines = [
        "# Phase 2 - DEV Ground Truth Annotation",
        "",
        "This directory contains the fixed 24-page development Ground Truth subset.",
        "",
        "## Scope",
        "",
        f"- selected pages: {len(records)}",
        f"- coverage pages: {len(COVERAGE_SELECTION)}",
        f"- challenge pages: {len(CHALLENGE_SELECTION)}",
        "- final validation pages are intentionally excluded",
        "",
        "## Annotation source",
        "",
        "`dev_annotations.jsonl` contains one scaffold record per selected page.",
        "",
        "Annotate the `rows[*]` objects only.",
        "",
        "For each row:",
        "- `active=true` when the row contains report data.",
        "- `active=false` when the row is blank and should not produce OCR data.",
        "- Keep blank/unreadable field values as `null`.",
        "- Preserve Vietnamese diacritics, capitalization, digits, punctuation and visible technical codes.",
        "- Do not infer or normalize business meaning.",
        "",
        "## Canonical OCR fields",
        "",
        "```text",
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
        "```",
        ""
        "Page-level derived values:",
        "- Page-level total: when a page shows a total for the `total_time` column,",
        "- it is the sum of `total_time` across the page's rows (rows 1..20).",
        "- This page-level value is not stored inside `rows[*].ground_truth`.",
        "- It is not stored inside `rows[*].ground_truth`.",
        ""
        "",
        "## Separation rule",
        "",
        "This DEV set is for development/debugging only.",
        "Do not use these same pages as the final Phase 9 validation set.",
        "",
        "## Selected pages",
        "",
    ]

    for index, record in enumerate(records, start=1):
        lines.append(
            f"{index:02d}. "
            f"{record['member_id']} / "
            f"{record['document_id']} / "
            f"page {record['page']:03d} / "
            f"{record['selection_group']} / "
            f"{record['rationale']}"
        )

    DEV_GUIDE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_index_csv(
    records: list[dict[str, Any]],
) -> None:
    lines = [
        "index,selection_group,member_id,member_name,document_id,page,rationale,pdf_path,rendered_image"
    ]

    for index, record in enumerate(records, start=1):
        def csv_escape(value: Any) -> str:
            text = str(value)
            text = text.replace('"', '""')
            return f'"{text}"'

        lines.append(
            ",".join(
                [
                    str(index),
                    csv_escape(record["selection_group"]),
                    csv_escape(record["member_id"]),
                    csv_escape(record["member_name"]),
                    csv_escape(record["document_id"]),
                    str(record["page"]),
                    csv_escape(record["rationale"]),
                    csv_escape(record["pdf_path"]),
                    csv_escape(record.get("rendered_image", "")),
                ]
            )
        )

    INDEX_CSV.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def create_combined_pdf(
    records: list[dict[str, Any]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_width, page_height = landscape(A3)
    margin_x = 24
    margin_top = 28
    margin_bottom = 24
    header_height = 46
    available_width = page_width - 2 * margin_x
    available_height = (
        page_height
        - margin_top
        - margin_bottom
        - header_height
    )

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=landscape(A3),
    )

    for index, record in enumerate(records, start=1):
        image_path = Path(record["rendered_image"])

        with fitz.open(record["pdf_path"]) as source_document:
            page = source_document.load_page(record["page"] - 1)
            page_rect = page.rect

        image_width = float(page_rect.width)
        image_height = float(page_rect.height)

        scale = min(
            available_width / image_width,
            available_height / image_height,
        )
        draw_width = image_width * scale
        draw_height = image_height * scale

        x = margin_x + (available_width - draw_width) / 2
        y = (
            margin_bottom
            + (available_height - draw_height) / 2
        )

        pdf.setFont("Helvetica-Bold", 12)
        title = (
            f"DEV GT {index:02d}/24  |  "
            f"Member {record['member_id']}  |  "
            f"{record['document_id']} page {record['page']:03d}  |  "
            f"{record['selection_group']}"
        )
        pdf.drawString(
            margin_x,
            page_height - margin_top,
            title,
        )

        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(
            page_width - margin_x,
            page_height - margin_top,
            record["rationale"],
        )

        pdf.drawImage(
            str(image_path),
            x,
            y,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        pdf.setFont("Helvetica", 7)
        footer = (
            f"source: {record['pdf_path']} | "
            f"sample_id: {record['member_id']}_"
            f"{record['document_id']}_p{record['page']:03d}"
        )
        pdf.drawString(
            margin_x,
            margin_bottom - 10,
            footer,
        )

        pdf.showPage()

    pdf.save()


def write_selection_json(
    records: list[dict[str, Any]],
    manifest: dict[str, Any],
    dpi: int,
) -> None:
    payload = {
        "schema_version": 1,
        "purpose": "Production OCR Phase 2 DEV Ground Truth selection",
        "selection_note": (
            "19 coverage pages (one per PDF document) + 5 challenge pages. "
            "This is a development set, not the final validation set."
        ),
        "source_summary": manifest.get("summary", {}),
        "render_dpi": dpi,
        "total_selected_pages": len(records),
        "coverage_pages": len(COVERAGE_SELECTION),
        "challenge_pages": len(CHALLENGE_SELECTION),
        "pages": records,
    }

    SELECTION_JSON.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def print_summary(
    records: list[dict[str, Any]],
    dpi: int,
) -> None:
    print("=" * 72)
    print("PRODUCTION OCR - PHASE 2 DEV GROUND TRUTH SELECTION")
    print("=" * 72)
    print(f"Selected pages : {len(records)}")
    print(f"Coverage pages : {len(COVERAGE_SELECTION)}")
    print(f"Challenge pages: {len(CHALLENGE_SELECTION)}")
    print(f"Render DPI     : {dpi}")
    print()
    print("Selected pages:")

    for index, record in enumerate(records, start=1):
        print(
            f"  {index:02d}. "
            f"{record['member_id']} / "
            f"{record['document_id']} / "
            f"page {record['page']:03d} "
            f"[{record['selection_group']}]"
        )

    print()
    print(f"Selection JSON : {SELECTION_JSON}")
    print(f"Index CSV      : {INDEX_CSV}")
    print(f"Annotations    : {DEV_ANNOTATIONS_JSONL}")
    print(f"Guide          : {DEV_GUIDE}")
    print(f"Selected PNGs  : {SELECTED_PAGES_ROOT}")
    print(f"DEV PDF        : {DEV_PDF}")
    print()
    print(
        "Next: inspect ground_truth_dev_24pages.pdf before transcribing."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create the fixed 24-page Phase 2 DEV Ground Truth subset."
        )
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Render DPI for selected pages (default: 150).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing selection outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dpi <= 0:
        raise ValueError("--dpi must be > 0.")

    if not args.force:
        existing = [
            path for path in (
                SELECTION_JSON,
                INDEX_CSV,
                DEV_ANNOTATIONS_JSONL,
                DEV_GUIDE,
                DEV_PDF,
            )
            if path.exists()
        ]
        if existing:
            raise FileExistsError(
                "DEV Ground Truth selection already exists:\n"
                + "\n".join(str(path) for path in existing)
                + "\n\nUse --force to regenerate."
            )

    manifest = load_manifest()
    selection_index = index_manifest(manifest)
    records = validate_selection(selection_index)

    # Clean only generated selected PNGs when --force is used.
    SELECTED_PAGES_ROOT.mkdir(parents=True, exist_ok=True)
    if args.force:
        for png in SELECTED_PAGES_ROOT.rglob("*.png"):
            png.unlink()

    render_selected_pages(
        records,
        SELECTED_PAGES_ROOT,
        args.dpi,
    )

    write_selection_json(
        records,
        manifest,
        args.dpi,
    )
    write_index_csv(records)
    write_dev_annotations(records)
    write_dev_guide(records)
    create_combined_pdf(records, DEV_PDF)

    print_summary(records, args.dpi)


if __name__ == "__main__":
    main()
