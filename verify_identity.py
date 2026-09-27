import json
from pathlib import Path

selection_path = Path("evaluation/ground_truth/selection/dev_selection.json")
root = Path("evaluation/ground_truth/selection/selected_pages_300dpi")

sel = json.loads(selection_path.read_text(encoding="utf-8"))["pages"]

expected = {
    f"{r['member_id']}_{r['document_id']}_page_{int(r['page']):03d}.png"
    for r in sel
}

actual = {p.name for p in root.rglob("*.png")}

print("MISSING:", sorted(expected - actual))
print("UNEXPECTED:", sorted(actual - expected))
print("EXPECTED_COUNT:", len(expected))
print("ACTUAL_COUNT:", len(actual))
