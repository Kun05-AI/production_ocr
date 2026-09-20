from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np

from app.form_registry import FormRegistry
from app.template_registration import (
    TemplateRegistrar,
    create_alignment_overlay,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "preprocessed"
    / "pages"
)

DEFAULT_DEBUG_DIR = (
    PROJECT_ROOT
    / "data"
    / "preprocessed"
    / "registration_debug"
)


def find_pages(
    input_dir: Path,
    pattern: str,
) -> list[Path]:
    files = sorted(
        p
        for p in input_dir.iterdir()
        if p.is_file()
        and p.suffix.lower()
        in {".png", ".jpg", ".jpeg"}
    )

    if pattern:
        files = [
            p
            for p in files
            if pattern.lower() in p.name.lower()
        ]

    return files


def save_json(
    path: Path,
    data: dict,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def resize_keep_ratio(
    image: np.ndarray,
    width: int = 900,
) -> np.ndarray:
    h, w = image.shape[:2]
    scale = width / w

    height = max(
        1,
        int(round(h * scale)),
    )

    return cv2.resize(
        image,
        (width, height),
        interpolation=cv2.INTER_AREA,
    )


def make_contact_sheet(
    items: list[tuple[str, np.ndarray]],
    output: Path,
    columns: int = 2,
) -> None:
    if not items:
        return

    thumbs = []

    for name, image in items:
        thumb = resize_keep_ratio(image)

        label_h = 36

        canvas = np.full(
            (
                thumb.shape[0] + label_h,
                thumb.shape[1],
                3,
            ),
            245,
            dtype=np.uint8,
        )

        canvas[label_h:] = thumb

        cv2.putText(
            canvas,
            name,
            (12, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (30, 30, 30),
            1,
            cv2.LINE_AA,
        )

        thumbs.append(canvas)

    rows = math.ceil(
        len(thumbs) / columns
    )

    cell_w = max(
        img.shape[1]
        for img in thumbs
    )

    cell_h = max(
        img.shape[0]
        for img in thumbs
    )

    sheet = np.full(
        (
            rows * cell_h,
            columns * cell_w,
            3,
        ),
        220,
        dtype=np.uint8,
    )

    for i, img in enumerate(thumbs):
        r = i // columns
        c = i % columns

        y = r * cell_h
        x = c * cell_w

        sheet[
            y:y + img.shape[0],
            x:x + img.shape[1],
        ] = img

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cv2.imwrite(
        str(output),
        sheet,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            92,
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "PHASE 4 - robust template registration test"
        )
    )

    parser.add_argument(
        "--form",
        required=True,
    )

    parser.add_argument(
        "--version",
        required=True,
    )

    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
    )

    parser.add_argument(
        "--debug-dir",
        default=str(DEFAULT_DEBUG_DIR),
    )

    parser.add_argument(
        "--pattern",
        default="",
        help=(
            "Optional filename substring, "
            "e.g. T1_ or T2_."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_dir = Path(
        args.input_dir
    ).resolve()

    debug_dir = Path(
        args.debug_dir
    ).resolve()

    aligned_dir = (
        debug_dir / "aligned"
    )

    overlay_dir = (
        debug_dir / "overlays"
    )

    print("=" * 72)
    print("PHASE 4 - ROBUST TEMPLATE REGISTRATION TEST")
    print("=" * 72)

    print(
        f"Form       : {args.form}/{args.version}"
    )

    print(
        f"Input dir  : {input_dir}"
    )

    print(
        f"Debug dir  : {debug_dir}"
    )

    print()

    registry = FormRegistry()

    profile = registry.resolve(
        args.form,
        args.version,
    )

    registrar = TemplateRegistrar(profile)

    if not input_dir.is_dir():
        raise FileNotFoundError(
            f"Input directory not found:\n{input_dir}"
        )

    pages = find_pages(
        input_dir,
        args.pattern,
    )

    if not pages:
        raise FileNotFoundError(
            f"No image pages found in {input_dir}"
            + (
                f" matching {args.pattern!r}"
                if args.pattern
                else ""
            )
        )

    aligned_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    overlay_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    reference = registrar.reference

    results: list[dict] = []
    contact_items: list[
        tuple[str, np.ndarray]
    ] = []

    print(
        f"Found {len(pages)} page(s)."
    )

    print()

    for index, page_path in enumerate(
        pages,
        start=1,
    ):
        print(
            f"[{index:02d}/{len(pages):02d}] "
            f"{page_path.name}"
        )

        aligned, result = registrar.register(
            page_path
        )

        result_dict = result.to_dict()

        results.append(
            result_dict
        )

        aligned_path = (
            aligned_dir
            / page_path.name
        )

        overlay_path = (
            overlay_dir
            / page_path.name
        )

        cv2.imwrite(
            str(aligned_path),
            aligned,
        )

        overlay = create_alignment_overlay(
            reference,
            aligned,
        )

        cv2.imwrite(
            str(overlay_path),
            overlay,
        )

        contact_items.append(
            (
                page_path.name,
                overlay,
            )
        )

        print(
            f"   Status       : "
            f"{result.status}"
        )

        print(
            f"   Method       : "
            f"{result.method}"
        )

        if result.quality_score is not None:
            print(
                f"   Quality      : "
                f"{result.quality_score:.4f}"
            )

        if result.ecc_correlation is not None:
            print(
                f"   ECC          : "
                f"{result.ecc_correlation:.4f}"
            )

        if result.translation_x_px is not None:
            print(
                "   Translation  : "
                f"({result.translation_x_px:.2f}, "
                f"{result.translation_y_px:.2f}) px"
            )

        if result.rotation_deg is not None:
            print(
                f"   Rotation     : "
                f"{result.rotation_deg:.4f} deg"
            )

        if result.scale_x is not None:
            print(
                "   Scale        : "
                f"({result.scale_x:.6f}, "
                f"{result.scale_y:.6f})"
            )

        if result.shear is not None:
            print(
                f"   Shear        : "
                f"{result.shear:.6f}"
            )

        if result.inliers is not None:
            print(
                f"   RANSAC       : "
                f"{result.inliers} inliers"
            )

        if result.inlier_ratio is not None:
            print(
                f"   Inlier ratio : "
                f"{result.inlier_ratio:.3f}"
            )

        print(
            f"   Message      : "
            f"{result.message}"
        )

        print()

    contact_path = (
        debug_dir / "contact_sheet.jpg"
    )

    make_contact_sheet(
        contact_items,
        contact_path,
    )

    pass_count = sum(
        1
        for x in results
        if x["status"] == "PASS"
    )

    review_count = sum(
        1
        for x in results
        if x["status"] == "REVIEW"
    )

    error_count = sum(
        1
        for x in results
        if x["status"] == "ERROR"
    )

    methods = {}

    for result in results:
        method = result.get(
            "method"
        )

        if method:
            methods[method] = (
                methods.get(method, 0)
                + 1
            )

    report = {
        "form_id": args.form,
        "version": args.version,
        "reference_image": str(
            profile.reference_image
        ),
        "input_dir": str(
            input_dir
        ),
        "total_pages": len(
            results
        ),
        "summary": {
            "pass": pass_count,
            "review": review_count,
            "error": error_count,
            "methods": methods,
        },
        "pages": results,
        "artifacts": {
            "aligned_dir": str(
                aligned_dir
            ),
            "overlay_dir": str(
                overlay_dir
            ),
            "contact_sheet": str(
                contact_path
            ),
        },
    }

    report_path = (
        debug_dir
        / "registration_report.json"
    )

    save_json(
        report_path,
        report,
    )

    print("=" * 72)
    print("REGISTRATION TEST COMPLETE")
    print("=" * 72)

    print(
        f"PASS   : "
        f"{pass_count} / {len(results)}"
    )

    print(
        f"REVIEW : "
        f"{review_count} / {len(results)}"
    )

    print(
        f"ERROR  : "
        f"{error_count} / {len(results)}"
    )

    print(
        f"Methods  : {methods}"
    )

    print()

    print(
        f"Report       : "
        f"{report_path}"
    )

    print(
        f"Contact sheet: "
        f"{contact_path}"
    )

    print(
        f"Aligned dir  : "
        f"{aligned_dir}"
    )

    print(
        f"Overlay dir  : "
        f"{overlay_dir}"
    )

    print()

    print(
        "IMPORTANT: PASS means the "
        "registration acceptance checks passed."
    )

    print(
        "It does not mean OCR accuracy is "
        "production-ready."
    )


if __name__ == "__main__":
    main()