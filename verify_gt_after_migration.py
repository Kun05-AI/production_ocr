import json
from pathlib import Path

p = Path("evaluation/ground_truth/selection/dev_annotations.jsonl")

expected = [
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

records = []

with p.open("r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print("PAGES:", len(records))
print("ROWS:", sum(len(r["rows"]) for r in records))

bad = []

for record in records:
    for row in record["rows"]:
        keys = list(row["ground_truth"].keys())
        if keys != expected:
            bad.append(
                (
                    record["sample_id"],
                    row["row_number"],
                    keys,
                )
            )

print("SCHEMA_ERRORS:", len(bad))

if bad:
    for item in bad[:10]:
        print(item)

first = records[0]

print("FIRST_SAMPLE:", first["sample_id"])
print(
    "FIRST_ROW_FIELDS:",
    list(first["rows"][0]["ground_truth"].keys()),
)
print(
    "FIRST_NON_OCR_FORM_FIELDS:",
    first.get("non_ocr_form_fields"),
)
print(
    "REVISION_PRESENT:",
    "revision" in first["rows"][0]["ground_truth"],
)
print(
    "TOTAL_TIME_PRESENT:",
    "total_time" in first["rows"][0]["ground_truth"],
)
