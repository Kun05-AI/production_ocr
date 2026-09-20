from __future__ import annotations

import sys
from pathlib import Path

import pymupdf  # PyMuPDF


DPI = 300


def render_pdf(pdf_path: str | Path, output_dir: str | Path, dpi: int = DPI) -> list[Path]:
    """Render every PDF page and return the image paths for downstream OCR."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF, got: {pdf_path.name}")
    if dpi <= 0:
        raise ValueError("dpi must be positive")

    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = pymupdf.Matrix(dpi / 72, dpi / 72)
    pages: list[Path] = []
    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            output_file = output_dir / f"{pdf_path.stem}_page_{page_number:03d}.png"
            page.get_pixmap(matrix=matrix, alpha=False).save(output_file)
            pages.append(output_file)
    return pages


def pdf_to_images(pdf_path: str | Path) -> list[Path]:
    """CLI helper using the project's fixed 300-DPI output."""
    pdf_path = Path(pdf_path)
    output_dir = Path("data/pages")
    print("=" * 70)
    print("PDF -> PAGE IMAGES")
    print("=" * 70)
    print("Input :", pdf_path.resolve())
    print("Output:", output_dir.resolve())
    print("DPI   :", DPI)
    print()

    pages = render_pdf(pdf_path, output_dir, DPI)
    for page_number, output_file in enumerate(pages, start=1):
        print(f"[{page_number:03d}/{len(pages):03d}] Rendered -> {output_file.name}")
    print(f"Generated {len(pages)} page images.")
    return pages


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("python -m app.pdf_processor path\\to\\input.pdf")
    pdf_to_images(sys.argv[1])


if __name__ == "__main__":
    main()
