from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image

from app.pdf_processor import render_pdf


PDF = ROOT / "data" / "input" / "T1.pdf"
RAW_DIR = ROOT / "data" / "pages"
PRE_DIR = ROOT / "data" / "preprocessed" / "pages"
PREVIEW_DIR = ROOT / "data" / "preprocessed" / "preview"
REPORT = ROOT / "data" / "preprocessed" / "preprocess_report.json"
TMP_DIR = ROOT / "data" / "_phase34_verify_input"

EXPECTED = [f"T1_page_{i:03d}.png" for i in range(1, 8)]
EXPECTED_SIZE = (3509, 2481)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


print("=" * 72)
print("PHASE 3 + PHASE 4 ACCEPTANCE CHECK")
print("=" * 72)

# ------------------------------------------------------------
# Basic paths
# ------------------------------------------------------------
assert_true(PDF.is_file(), f"Missing input PDF: {PDF}")
assert_true(RAW_DIR.is_dir(), f"Missing raw page dir: {RAW_DIR}")
assert_true(PRE_DIR.is_dir(), f"Missing preprocessed dir: {PRE_DIR}")

# ------------------------------------------------------------
# Phase 3: existing rendered pages
# ------------------------------------------------------------
raw_files = sorted(p.name for p in RAW_DIR.glob("*.png"))
assert_true(raw_files == EXPECTED, f"RAW pages mismatch: {raw_files}")

print("PHASE 3A - Existing raw pages     : PASS")

raw_dimensions = {}
for name in EXPECTED:
    path = RAW_DIR / name
    assert_true(path.is_file(), f"Missing raw page: {path}")
    with Image.open(path) as im:
        raw_dimensions[name] = im.size

assert_true(
    all(size == EXPECTED_SIZE for size in raw_dimensions.values()),
    f"Raw page dimensions mismatch: {raw_dimensions}",
)

print("PHASE 3B - Raw page dimensions    : PASS")

# ------------------------------------------------------------
# Phase 3: deterministic rerender test
# Render to TEMP, do not touch data/pages
# ------------------------------------------------------------
if TMP_DIR.exists():
    shutil.rmtree(TMP_DIR)

TMP_DIR.mkdir(parents=True)

try:
    rendered = render_pdf(PDF, TMP_DIR, dpi=300)
    rendered_names = sorted(p.name for p in rendered)

    assert_true(
        rendered_names == EXPECTED,
        f"Rerendered names mismatch: {rendered_names}",
    )

    for name in EXPECTED:
        old = RAW_DIR / name
        new = TMP_DIR / name

        assert_true(new.is_file(), f"Missing rerendered file: {new}")

        assert_true(
            sha256(old) == sha256(new),
            f"Non-deterministic render detected: {name}",
        )

        with Image.open(new) as im:
            assert_true(
                im.size == EXPECTED_SIZE,
                f"Rerendered size mismatch {name}: {im.size}",
            )

    print("PHASE 3C - Deterministic rerender : PASS")

finally:
    shutil.rmtree(TMP_DIR, ignore_errors=True)

# ------------------------------------------------------------
# Phase 4: preprocessed pages
# ------------------------------------------------------------
pre_files = sorted(p.name for p in PRE_DIR.glob("*.png"))
assert_true(pre_files == EXPECTED, f"PRE pages mismatch: {pre_files}")

print("PHASE 4A - Preprocessed page set  : PASS")

for name in EXPECTED:
    raw = RAW_DIR / name
    pre = PRE_DIR / name

    assert_true(pre.is_file(), f"Missing preprocessed page: {pre}")

    with Image.open(pre) as im:
        assert_true(
            im.size == EXPECTED_SIZE,
            f"Preprocessed size mismatch {name}: {im.size}",
        )

    assert_true(
        not raw.samefile(pre),
        f"Raw/preprocessed unexpectedly share same file: {name}",
    )

print("PHASE 4B - Dimensions + separation : PASS")

# ------------------------------------------------------------
# Phase 4: contact sheet
# ------------------------------------------------------------
contact_candidates = list(PREVIEW_DIR.glob("contact_sheet.*"))
assert_true(
    contact_candidates,
    f"Missing contact sheet in {PREVIEW_DIR}",
)

for path in contact_candidates:
    assert_true(path.stat().st_size > 0, f"Empty contact sheet: {path}")

print("PHASE 4C - Contact sheet          : PASS")

# ------------------------------------------------------------
# Phase 4: report
# ------------------------------------------------------------
assert_true(REPORT.is_file(), f"Missing preprocess report: {REPORT}")

with REPORT.open("r", encoding="utf-8") as f:
    report = json.load(f)

assert_true(report is not None, "Preprocess report is empty/null")

print("PHASE 4D - Preprocess report      : PASS")

# ------------------------------------------------------------
# Final
# ------------------------------------------------------------
print()
print("=" * 72)
print("FINAL RESULT")
print("=" * 72)
print("PHASE 3 - Input Engine baseline       : PASS")
print("PHASE 4 - Image Normalization        : PASS")
print()
print("No project data was modified by this verifier.")
print("Ready to proceed to Phase 5.")
