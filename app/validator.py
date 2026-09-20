from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

DATE_PATTERNS = [re.compile(r"^\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?$"), re.compile(r"^\d{4}-\d{2}-\d{2}$")]
TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")


@dataclass
class ValidationResult:
    active: bool
    review_score: int
    issues: list[str]
    normalized: dict[str, Any]


def _is_blank(v: Any) -> bool:
    return v is None or str(v).strip() == ""


def _valid_date(v: Any) -> bool:
    if _is_blank(v):
        return True
    s = str(v).strip()
    return any(p.match(s) for p in DATE_PATTERNS)


def _valid_time(v: Any) -> bool:
    if _is_blank(v):
        return True
    return bool(TIME_PATTERN.match(str(v).strip()))


def validate_row(row: dict[str, Any]) -> ValidationResult:
    issues: list[str] = []
    ocr_fields = {
        "stt", "date", "order_code", "drawing_code", "revision", "work_code",
        "target_time", "start_time", "end_time", "processed_qty", "good_qty",
        "ng_qty", "process_detail", "note",
    }
    normalized = {
        key: (None if _is_blank(value) else str(value).strip())
        for key, value in row.items()
        if key in ocr_fields
    }
    active = any(value is not None for value in normalized.values())
    if row.get("_error"):
        return ValidationResult(True, 0, ["ocr_error"], normalized)
    if not active:
        return ValidationResult(False, 100, [], normalized)

    score = 100
    if not _valid_date(normalized.get("date")):
        issues.append("invalid_date")
        score -= 20
    for key in ("start_time", "end_time"):
        if not _valid_time(normalized.get(key)):
            issues.append(f"invalid_{key}")
            score -= 15

    for key in ("processed_qty", "good_qty", "ng_qty"):
        v = normalized.get(key)
        if v is not None and not re.fullmatch(r"\d+(?:[.,]\d+)?", v):
            issues.append(f"invalid_{key}")
            score -= 15

    for key in ("order_code", "drawing_code", "revision", "work_code"):
        v = normalized.get(key)
        if v is not None and len(v) > 120:
            issues.append(f"too_long_{key}")
            score -= 10

    return ValidationResult(True, max(score, 0), issues, normalized)


def validate_page(rows: list[dict[str, Any]]) -> dict[str, Any]:
    results = [validate_row(r) for r in rows]
    active = [r for r in results if r.active]
    return {
        "rows": [asdict(r) for r in results],
        "active_row_count": len(active),
        "min_review_score": min((r.review_score for r in active), default=100),
        "needs_review": any(r.review_score < 75 or r.issues for r in active),
    }
