from pathlib import Path
import json
import math

import cv2
import numpy as np


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "data" / "pages"

OUTPUT_DIR = PROJECT_ROOT / "data" / "preprocessed"

NORMALIZED_DIR = OUTPUT_DIR / "pages"

PREVIEW_DIR = OUTPUT_DIR / "preview"

REPORT_FILE = OUTPUT_DIR / "preprocess_report.json"

CONTACT_SHEET_FILE = PREVIEW_DIR / "contact_sheet.jpg"


# T1 standard page rendered at 300 DPI.
TARGET_WIDTH = 3509
TARGET_HEIGHT = 2481

TARGET_SIZE = (
    TARGET_WIDTH,
    TARGET_HEIGHT,
)


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


# ============================================================
# UTILS
# ============================================================

def ensure_directories():
    NORMALIZED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    PREVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def find_images():
    images = []

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Input directory not found:\n{INPUT_DIR}"
        )

    for path in INPUT_DIR.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        images.append(path)

    images.sort()

    return images


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(image_path: Path):
    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            f"Cannot read image:\n{image_path}"
        )

    return image


# ============================================================
# ORIENTATION
# ============================================================

def normalize_orientation(image):
    """
    T1 is landscape.

    If an image arrives in portrait orientation,
    rotate it 90 degrees clockwise.

    This is intentionally simple for now.
    Template registration comes later.
    """

    height, width = image.shape[:2]

    if height > width:
        image = cv2.rotate(
            image,
            cv2.ROTATE_90_CLOCKWISE,
        )

        rotated = True

    else:
        rotated = False

    return image, rotated


# ============================================================
# RESIZE
# ============================================================

def resize_to_target(image):
    """
    Resize the complete page to the canonical T1 size.

    For this project we want a deterministic coordinate system
    because the form layout is fixed.
    """

    height, width = image.shape[:2]

    if (
        width == TARGET_WIDTH
        and height == TARGET_HEIGHT
    ):
        return image, False

    # Downscale with INTER_AREA.
    if (
        width > TARGET_WIDTH
        or height > TARGET_HEIGHT
    ):
        interpolation = cv2.INTER_AREA

    # Upscale with INTER_CUBIC.
    else:
        interpolation = cv2.INTER_CUBIC

    resized = cv2.resize(
        image,
        TARGET_SIZE,
        interpolation=interpolation,
    )

    return resized, True


# ============================================================
# LIGHT NORMALIZATION
# ============================================================

def normalize_contrast(image):
    """
    Very conservative contrast normalization.

    We do NOT apply aggressive sharpening, thresholding,
    denoising or binarization yet because handwriting
    information must be preserved.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB,
    )

    l_channel, a_channel, b_channel = cv2.split(
        lab
    )

    clahe = cv2.createCLAHE(
        clipLimit=1.5,
        tileGridSize=(8, 8),
    )

    l_channel = clahe.apply(
        l_channel
    )

    normalized = cv2.merge(
        [
            l_channel,
            a_channel,
            b_channel,
        ]
    )

    normalized = cv2.cvtColor(
        normalized,
        cv2.COLOR_LAB2BGR,
    )

    return normalized


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

def process_image(
    image_path: Path,
):

    image = load_image(
        image_path
    )

    original_height, original_width = (
        image.shape[:2]
    )

    # --------------------------------------------------------
    # Orientation
    # --------------------------------------------------------

    image, rotated = normalize_orientation(
        image
    )

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image, resized = resize_to_target(
        image
    )

    # --------------------------------------------------------
    # Conservative contrast normalization
    # --------------------------------------------------------

    normalized = normalize_contrast(
        image
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output_name = (
        image_path.stem
        + ".png"
    )

    output_path = (
        NORMALIZED_DIR
        / output_name
    )

    success = cv2.imwrite(
        str(output_path),
        normalized,
    )

    if not success:
        raise IOError(
            f"Failed to save:\n{output_path}"
        )

    final_height, final_width = (
        normalized.shape[:2]
    )

    report = {
        "input": str(image_path),
        "output": str(output_path),
        "original_size": {
            "width": original_width,
            "height": original_height,
        },
        "final_size": {
            "width": final_width,
            "height": final_height,
        },
        "rotated": rotated,
        "resized": resized,
        "target_size": {
            "width": TARGET_WIDTH,
            "height": TARGET_HEIGHT,
        },
    }

    return normalized, report


# ============================================================
# PREVIEW
# ============================================================

def create_thumbnail(
    image,
    max_width=500,
):

    height, width = image.shape[:2]

    scale = min(
        1.0,
        max_width / width,
    )

    new_width = int(
        width * scale
    )

    new_height = int(
        height * scale
    )

    thumbnail = cv2.resize(
        image,
        (
            new_width,
            new_height,
        ),
        interpolation=cv2.INTER_AREA,
    )

    return thumbnail


def build_contact_sheet(
    processed_images,
):

    if not processed_images:
        return

    thumbnails = []

    for image_path, image in processed_images:

        thumb = create_thumbnail(
            image,
            max_width=500,
        )

        # Add filename label.
        canvas = np.full(
            (
                thumb.shape[0] + 35,
                thumb.shape[1],
                3,
            ),
            255,
            dtype=np.uint8,
        )

        canvas[
            35:,
            :,
        ] = thumb

        cv2.putText(
            canvas,
            image_path.name,
            (
                10,
                24,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                0,
                0,
                0,
            ),
            1,
            cv2.LINE_AA,
        )

        thumbnails.append(
            canvas
        )

    columns = 3

    rows = math.ceil(
        len(thumbnails)
        / columns
    )

    cell_width = max(
        image.shape[1]
        for image in thumbnails
    )

    cell_height = max(
        image.shape[0]
        for image in thumbnails
    )

    sheet = np.full(
        (
            rows * cell_height,
            columns * cell_width,
            3,
        ),
        240,
        dtype=np.uint8,
    )

    for index, image in enumerate(
        thumbnails
    ):

        row = index // columns
        col = index % columns

        y = (
            row
            * cell_height
        )

        x = (
            col
            * cell_width
        )

        h, w = image.shape[:2]

        sheet[
            y:y + h,
            x:x + w,
        ] = image

    cv2.imwrite(
        str(CONTACT_SHEET_FILE),
        sheet,
    )


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    reports,
):

    summary = {
        "total_images": len(
            reports
        ),
        "target_size": {
            "width": TARGET_WIDTH,
            "height": TARGET_HEIGHT,
        },
        "images": reports,
    }

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("IMAGE PREPROCESSING / NORMALIZATION")
    print("=" * 70)

    print(
        "Input :",
        INPUT_DIR,
    )

    print(
        "Output:",
        NORMALIZED_DIR,
    )

    print(
        "Target:",
        f"{TARGET_WIDTH} x {TARGET_HEIGHT}",
    )

    print()

    ensure_directories()

    images = find_images()

    if not images:
        print(
            "No images found."
        )
        return

    print(
        f"Found {len(images)} images."
    )

    print()

    reports = []
    processed_images = []

    # --------------------------------------------------------
    # PROCESS ALL IMAGES
    # --------------------------------------------------------

    for index, image_path in enumerate(
        images,
        start=1,
    ):

        print(
            f"[{index:03d}/{len(images):03d}]"
            f" {image_path.name}"
        )

        try:

            normalized, report = process_image(
                image_path
            )

            reports.append(
                report
            )

            output_path = Path(
                report["output"]
            )

            processed_images.append(
                (
                    output_path,
                    normalized,
                )
            )

            print(
                "      OK →",
                output_path.name,
            )

        except Exception as exc:

            print(
                "      ERROR:",
                type(exc).__name__,
                exc,
            )

        print()

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    save_report(
        reports
    )

    # --------------------------------------------------------
    # CONTACT SHEET
    # --------------------------------------------------------

    print(
        "Creating contact sheet..."
    )

    build_contact_sheet(
        processed_images
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print("=" * 70)
    print("DONE")
    print("=" * 70)

    print(
        "Processed:",
        len(reports),
        "/",
        len(images),
    )

    print(
        "Normalized images:",
        NORMALIZED_DIR,
    )

    print(
        "Contact sheet:",
        CONTACT_SHEET_FILE,
    )

    print(
        "Report:",
        REPORT_FILE,
    )


if __name__ == "__main__":
    main()