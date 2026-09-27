from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration, BitsAndBytesConfig

MODEL_ID = "Qwen/Qwen3-VL-4B-Instruct"
LOCAL_MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "Qwen3-VL-4B-Instruct"
GPU_MEMORY = "5GiB"
CPU_MEMORY = "24GiB"
MAX_NEW_TOKENS = 1200

ROW_PROMPT = r'''
Bạn là OCR engine chuyên đọc biểu mẫu sản xuất viết tay bằng tiếng Việt.

Ảnh đầu vào là MỘT DÒNG trong bảng báo cáo sản xuất. Hãy đọc đúng nội dung viết tay trong dòng này.

Quy tắc bắt buộc:
- Chỉ đọc dữ liệu nhìn thấy.
- Không tự sửa mã kỹ thuật thành từ có nghĩa.
- Không đoán phần bị che/mờ. Khi không đọc được rõ, trả null.
- Giữ nguyên số, dấu gạch, ký hiệu và dấu tiếng Việt khi nhìn thấy.
- Các ô trống phải là null.
- Không nhầm chữ viết tay ở dòng kế bên.
- Một ảnh tương ứng đúng một record.
- Không giải thích ngoài JSON.

Trả đúng JSON:
{
    "stt": null,
    "date": null,
    "order_code": null,
    "drawing_code": null,
    "work_code": null,
    "target_time": null,
    "start_time": null,
    "end_time": null,
    "total_time": null,
    "processed_qty": null,
    "good_qty": null,
    "ng_qty": null,
    "process_detail": null,
    "note": null
}
'''


def check_environment() -> None:
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA build: {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch chưa nhận NVIDIA GPU.")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")


def load_model():
    model_source = LOCAL_MODEL_DIR if LOCAL_MODEL_DIR.is_dir() else MODEL_ID
    processor = AutoProcessor.from_pretrained(model_source)
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        model_source,
        dtype=torch.float16,
        device_map="auto",
        max_memory={0: GPU_MEMORY, "cpu": CPU_MEMORY},
        quantization_config=quant_config,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    )
    return processor, model


def clean_json_text(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return text.strip()


def run_row_ocr(image_path: str | Path, processor, model) -> dict:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": str(image_path)},
            {"type": "text", "text": ROW_PROMPT},
        ],
    }]

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    )
    if "token_type_ids" in inputs:
        inputs.pop("token_type_ids")

    # With device_map=auto, the first model device is used for input staging.
    inputs = inputs.to(model.device)
    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
        )

    trimmed = [o[len(i):] for i, o in zip(inputs.input_ids, generated)]
    text = processor.batch_decode(
        trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]
    parsed = json.loads(clean_json_text(text))
    return parsed


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("python -m app.qwen_ocr path\\to\\row.png")
    check_environment()
    processor, model = load_model()
    result = run_row_ocr(sys.argv[1], processor, model)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
