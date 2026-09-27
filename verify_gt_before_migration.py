import json
from pathlib import Path

p = Path("evaluation/ground_truth/selection/dev_annotations.jsonl")
records = []

with p.open("r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print("PAGES:", len(records))
print("ROWS:", sum(len(r["rows"]) for r in records))

first = records[0]
print("FIRST_SAMPLE:", first["sample_id"])
print("FIRST_ROW_FIELDS:", list(first["rows"][0]["ground_truth"].keys()))
print("FIRST_ANNOTATION_SCHEMA:", first.get("annotation_schema"))
print("FIRST_NON_OCR_FORM_FIELDS:", first.get("non_ocr_form_fields"))
