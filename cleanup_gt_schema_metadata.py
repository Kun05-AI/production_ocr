import json
from pathlib import Path

p = Path("evaluation/ground_truth/selection/dev_annotations.jsonl")

records = []

with p.open("r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

for record in records:
    record.pop("non_ocr_form_fields", None)

with p.open("w", encoding="utf-8") as f:
    for record in records:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print("Pages:", len(records))
print(
    "Rows:",
    sum(len(record["rows"]) for record in records)
)
print(
    "Legacy metadata remaining:",
    sum(
        1
        for record in records
        if "non_ocr_form_fields" in record
    )
)
