from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException

from .pdf_processor import render_pdf
from .form_template import FormTemplate
from .row_detector import detect_active_rows
from .qwen_ocr import load_model, run_row_ocr
from .validator import validate_page

app = FastAPI(title="QC OCR Local Service")
BASE = Path(__file__).resolve().parent.parent
TEMPLATE = FormTemplate(BASE / "config" / "form_v1.json")

_processor = None
_model = None


def get_model():
    global _processor, _model
    if _processor is None or _model is None:
        _processor, _model = load_model()
    return _processor, _model


@app.get("/health")
def health():
    return {"status": "ok", "model": "Qwen/Qwen3-VL-4B-Instruct"}


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    filename = Path(file.filename or "upload").name
    suffix = Path(filename).suffix.lower()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / filename
        source.write_bytes(await file.read())

        if suffix == ".pdf":
            pages = render_pdf(source, root / "pages", dpi=300)
        elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            pages = [source]
        else:
            raise HTTPException(400, "Chỉ nhận PDF/JPG/JPEG/PNG/WEBP")

        processor, model = get_model()
        page_results = []
        for page_path in pages:
            active_rows = detect_active_rows(page_path, TEMPLATE)
            rows = []
            from PIL import Image
            img = Image.open(page_path).convert("RGB")
            for idx in active_rows:
                row_img = TEMPLATE.row_crop(img, idx)
                crop_path = root / f"row_{idx+1:02d}.png"
                row_img.save(crop_path)
                try:
                    result = run_row_ocr(crop_path, processor, model)
                except Exception as exc:
                    result = {"_error": str(exc)}
                rows.append({"row_index": idx + 1, **result})
            page_results.append({"page": page_path.name, "rows": rows, "validation": validate_page(rows)})

        return {"filename": filename, "pages": page_results}
