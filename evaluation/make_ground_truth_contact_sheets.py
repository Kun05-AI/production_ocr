"""
Production OCR — Ground Truth Contact Sheet Builder

Reads rendered pages created by:
    evaluation/build_ground_truth.py --render --dpi 100

Creates:
    evaluation/ground_truth/contact_sheets/
        member_1207_NGUYEN_TRUONG_NHAN_01.jpg
        ...
        ground_truth_contact_sheets.pdf

The PDF is the convenient artifact to upload to GPT:
- one file
- all 143 rendered pages
- grouped by employee
- ordered by T1/T2/T3/T4 and page number
- labels show employee / document / page

Typical usage:
    python ./evaluation/make_ground_truth_contact_sheets.py

Optional:
    python ./evaluation/make_ground_truth_contact_sheets.py --dpi-label 100
    python ./evaluation/make_ground_truth_contact_sheets.py --columns 3 --rows 4
"""

from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.pdfgen import canvas
except ImportError as exc:
    raise SystemExit(
        "reportlab chưa được cài. Cài bằng:\n"
        "    pip install reportlab"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = (
    PROJECT_ROOT
    / "evaluation"
    / "ground_truth"
    / "source_pages"
)
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "evaluation"
    / "ground_truth"
    / "contact_sheets"
)
PDF_OUTPUT = OUTPUT_ROOT / "ground_truth_contact_sheets.pdf"


def natural_page_key(path: Path) -> tuple[str, int]:
    match = re.search(r"_page_(\d+)$", path.stem)
    page_number = int(match.group(1)) if match else 0
    return path.stem.split("_page_")[0], page_number


def document_sort_key(path: Path) -> tuple[int, str]:
    match = re.fullmatch(r"T(\d+)", path.name)
    if match:
        return int(match.group(1)), path.name
    return 999, path.name


def load_font(size: int, bold: bool = False):
    candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),
        (
            "C:/Windows/Fonts/arialbd.ttf"
            if bold
            else "C:/Windows/Fonts/arial.ttf"
        ),
    ]

    for font_path in candidates:
        path = Path(font_path)
        if path.is_file():
            return ImageFont.truetype(str(path), size)

    return ImageFont.load_default()


def discover_members() -> list[tuple[str, str, list[tuple[str, int, Path]]]]:
    if not SOURCE_ROOT.is_dir():
        raise FileNotFoundError(
            f"Rendered source directory not found:\n{SOURCE_ROOT}\n\n"
            "Run build_ground_truth.py with --render first."
        )

    members = []

    for member_dir in sorted(
        p for p in SOURCE_ROOT.iterdir() if p.is_dir()
    ):
        member_match = re.match(
            r"^(\d+)_(.+)$",
            member_dir.name,
        )
        if member_match:
            member_id = member_match.group(1)
            member_name = member_match.group(2)
        else:
            member_id = member_dir.name
            member_name = member_dir.name

        pages: list[tuple[str, int, Path]] = []

        for document_dir in sorted(
            (p for p in member_dir.iterdir() if p.is_dir()),
            key=document_sort_key,
        ):
            for image_path in sorted(
                document_dir.glob("*.png"),
                key=natural_page_key,
            ):
                match = re.search(
                    r"_(?:page)_(\d+)$",
                    image_path.stem,
                )
                if not match:
                    continue

                page_number = int(match.group(1))
                pages.append(
                    (
                        document_dir.name,
                        page_number,
                        image_path,
                    )
                )

        members.append(
            (
                member_id,
                member_name,
                pages,
            )
        )

    return members


def make_contact_sheet_image(
    member_id: str,
    member_name: str,
    pages: list[tuple[str, int, Path]],
    start_index: int,
    end_index: int,
    columns: int,
    rows: int,
    thumb_width: int,
    thumb_height: int,
) -> Image.Image:
    batch = pages[start_index:end_index]

    margin = 32
    title_height = 72
    label_height = 34
    gap_x = 18
    gap_y = 18

    sheet_width = (
        margin * 2
        + columns * thumb_width
        + (columns - 1) * gap_x
    )

    sheet_height = (
        margin * 2
        + title_height
        + rows * (thumb_height + label_height)
        + (rows - 1) * gap_y
    )

    sheet = Image.new(
        "RGB",
        (sheet_width, sheet_height),
        "white",
    )

    draw = ImageDraw.Draw(sheet)

    title_font = load_font(28, bold=True)
    label_font = load_font(18, bold=False)

    first_label = start_index + 1
    last_label = min(end_index, len(pages))

    title = (
        f"Member {member_id} - {member_name}    "
        f"Pages {first_label}-{last_label} / {len(pages)}"
    )

    draw.text(
        (margin, 22),
        title,
        fill="black",
        font=title_font,
    )

    for local_index, (document_id, page_number, path) in enumerate(batch):
        row = local_index // columns
        col = local_index % columns

        x = margin + col * (thumb_width + gap_x)
        y = (
            margin
            + title_height
            + row * (thumb_height + label_height + gap_y)
        )

        try:
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail(
                    (thumb_width, thumb_height),
                    Image.Resampling.LANCZOS,
                )

                canvas_x = x + (thumb_width - image.width) // 2
                canvas_y = y + (thumb_height - image.height) // 2

                sheet.paste(
                    image,
                    (canvas_x, canvas_y),
                )
        except Exception as exc:
            draw.rectangle(
                (x, y, x + thumb_width, y + thumb_height),
                outline="red",
                width=2,
            )
            draw.text(
                (x + 8, y + 8),
                f"ERROR\n{path.name}\n{exc}",
                fill="red",
                font=label_font,
            )

        label = f"{document_id}  page {page_number:03d}"

        draw.text(
            (x + 6, y + thumb_height + 4),
            label,
            fill="black",
            font=label_font,
        )

    return sheet


def write_member_jpegs(
    members,
    columns: int,
    rows: int,
    thumb_width: int,
    thumb_height: int,
) -> list[Path]:
    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_paths: list[Path] = []
    per_sheet = columns * rows

    for member_id, member_name, pages in members:
        chunks = math.ceil(len(pages) / per_sheet)

        for chunk_index in range(chunks):
            start = chunk_index * per_sheet
            end = min(
                start + per_sheet,
                len(pages),
            )

            sheet = make_contact_sheet_image(
                member_id=member_id,
                member_name=member_name,
                pages=pages,
                start_index=start,
                end_index=end,
                columns=columns,
                rows=rows,
                thumb_width=thumb_width,
                thumb_height=thumb_height,
            )

            safe_name = re.sub(
                r"[^A-Za-z0-9_.-]+",
                "_",
                member_name,
            )

            output_path = (
                OUTPUT_ROOT
                / (
                    f"member_{member_id}_"
                    f"{safe_name}_"
                    f"{chunk_index + 1:02d}.jpg"
                )
            )

            sheet.save(
                output_path,
                quality=92,
                optimize=True,
            )

            output_paths.append(output_path)

    return output_paths


def image_to_pdf_page(
    pdf: canvas.Canvas,
    image_path: Path,
    page_size,
) -> None:
    page_width, page_height = page_size

    image = Image.open(image_path)
    image_width, image_height = image.size

    scale = min(
        page_width / image_width,
        page_height / image_height,
    )

    draw_width = image_width * scale
    draw_height = image_height * scale

    x = (page_width - draw_width) / 2
    y = (page_height - draw_height) / 2

    pdf.drawImage(
        str(image_path),
        x,
        y,
        width=draw_width,
        height=draw_height,
        preserveAspectRatio=True,
        mask="auto",
    )

    pdf.showPage()


def write_pdf(
    image_paths: list[Path],
) -> None:
    page_size = landscape(A3)

    pdf = canvas.Canvas(
        str(PDF_OUTPUT),
        pagesize=page_size,
        pageCompression=1,
    )

    for image_path in image_paths:
        image_to_pdf_page(
            pdf,
            image_path,
            page_size,
        )

    pdf.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build contact sheets and one combined PDF "
            "for Production OCR Phase 2 Ground Truth review."
        )
    )

    parser.add_argument(
        "--columns",
        type=int,
        default=3,
        help="Contact-sheet columns (default: 3).",
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=4,
        help="Contact-sheet rows (default: 4).",
    )

    parser.add_argument(
        "--thumb-width",
        type=int,
        default=520,
        help="Thumbnail width in pixels (default: 520).",
    )

    parser.add_argument(
        "--thumb-height",
        type=int,
        default=360,
        help="Thumbnail height in pixels (default: 360).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.columns <= 0 or args.rows <= 0:
        raise SystemExit("columns/rows must be > 0.")

    if args.thumb_width <= 0 or args.thumb_height <= 0:
        raise SystemExit("thumb size must be > 0.")

    members = discover_members()

    if not members:
        raise SystemExit(
            f"No rendered member folders found under:\n{SOURCE_ROOT}"
        )

    total_pages = sum(
        len(pages)
        for _, _, pages in members
    )

    image_paths = write_member_jpegs(
        members=members,
        columns=args.columns,
        rows=args.rows,
        thumb_width=args.thumb_width,
        thumb_height=args.thumb_height,
    )

    write_pdf(image_paths)

    print("=" * 72)
    print("GROUND TRUTH CONTACT SHEETS")
    print("=" * 72)
    print(f"Source       : {SOURCE_ROOT}")
    print(f"Members      : {len(members)}")
    print(f"Pages        : {total_pages}")
    print(f"JPG sheets   : {len(image_paths)}")
    print(f"PDF          : {PDF_OUTPUT}")
    print()

    for member_id, member_name, pages in members:
        print(
            f"[{member_id}] {member_name}: "
            f"{len(pages)} page(s)"
        )

    print()
    print(
        "Upload the single PDF to GPT for visual dataset inspection:"
    )
    print(PDF_OUTPUT)


if __name__ == "__main__":
    main()
