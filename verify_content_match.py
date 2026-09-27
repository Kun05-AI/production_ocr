from pathlib import Path

import numpy as np
from PIL import Image


R150 = Path("evaluation/ground_truth/selection/selected_pages")
R300 = Path("evaluation/ground_truth/selection/selected_pages_300dpi")


rows = []

for p300 in sorted(R300.rglob("*.png")):
    p150 = R150 / p300.parent.name / p300.name

    if not p150.is_file():
        print(f"ERROR: missing 150 DPI pair: {p150}")
        continue

    a = np.asarray(
        Image.open(p150).convert("L"),
        dtype=np.float32,
    )

    b = np.asarray(
        Image.open(p300).convert("L").resize(
            (a.shape[1], a.shape[0]),
            Image.Resampling.LANCZOS,
        ),
        dtype=np.float32,
    )

    diff = np.abs(a - b)

    mae = float(diff.mean())
    rmse = float(np.sqrt(np.mean((a - b) ** 2)))

    a0 = a - a.mean()
    b0 = b - b.mean()

    denom = float(np.sqrt(np.sum(a0 * a0) * np.sum(b0 * b0)))
    corr = float(np.sum(a0 * b0) / denom) if denom > 0 else 0.0

    rows.append((p300.name, mae, rmse, corr))

print("=== CONTENT MATCH: 150 DPI vs 300 DPI ===")

for name, mae, rmse, corr in sorted(rows, key=lambda x: x[1], reverse=True):
    print(
        f"{name}: "
        f"MAE={mae:.2f} "
        f"RMSE={rmse:.2f} "
        f"CORR={corr:.6f}"
    )

if rows:
    maes = np.array([r[1] for r in rows], dtype=np.float64)
    rmses = np.array([r[2] for r in rows], dtype=np.float64)
    corrs = np.array([r[3] for r in rows], dtype=np.float64)

    print("\n=== DISTRIBUTION ===")
    print(f"MAE   median={np.median(maes):.2f}  max={np.max(maes):.2f}")
    print(f"RMSE  median={np.median(rmses):.2f}  max={np.max(rmses):.2f}")
    print(f"CORR  median={np.median(corrs):.6f}  min={np.min(corrs):.6f}")
    print(f"FILES compared: {len(rows)}")
