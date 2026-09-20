import json
import sys
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import (
    AutoProcessor,
    Qwen3VLForConditionalGeneration,
    BitsAndBytesConfig,
)


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_ID = PROJECT_ROOT / "models" / "Qwen3-VL-4B-Instruct"

GPU_MEMORY = "5GiB"
CPU_MEMORY = "26GiB"

# Row crop is already small, so we can keep much more image detail.
MIN_IMAGE_PIXELS = 4_096
MAX_IMAGE_PIXELS = 1_048_576

MAX_NEW_TOKENS = 512

OUTPUT_DIR = PROJECT_ROOT / "data" / "ocr"
CROP_DIR = PROJECT_ROOT / "data" / "crops"


# ============================================================
# T1 FIXED TEMPLATE
# ============================================================
#
# T1 page rendered at 300 DPI:
#   width  = 3509
#   height = 2481
#
# These coordinates are based on the fixed T1 form.
#
# Row 1 approximately:
#   x1 = 80
#   x2 = 3420
#   y1 = 495
#   y2 = 570
#
# Row height is approximately 73 px.
#
# This is a TEST calibration only.
# Later we will move these values into form_v1.json.
# ============================================================

PAGE_WIDTH = 3509
PAGE_HEIGHT = 2481

TABLE_X1 = 80
TABLE_X2 = 3420

ROW1_Y1 = 495
ROW_HEIGHT = 73

# Slight vertical padding so handwriting near a border is not cut.
ROW_PADDING_Y = 5


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    print("=" * 70)
    print("QWEN3-VL-4B ROW OCR TEST")
    print("=" * 70)

    print("Torch:", torch.__version__)
    print("CUDA:", torch.version.cuda)

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available.")

    print("GPU:", torch.cuda.get_device_name(0))
    print(
        "VRAM:",
        torch.cuda.get_device_properties(0).total_memory / 1024**3,
        "GB",
    )
    print()

    print("Model path:")
    print(MODEL_ID)
    print()

    if not MODEL_ID.exists():
        raise FileNotFoundError(
            f"Model directory not found:\n{MODEL_ID}"
        )

    print("Loading processor...")

    processor = AutoProcessor.from_pretrained(
        str(MODEL_ID),
        trust_remote_code=True,
    )

    print("Processor OK")
    print()

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    print("Loading model...")

    model = Qwen3VLForConditionalGeneration.from_pretrained(
        str(MODEL_ID),
        quantization_config=quant_config,
        device_map="auto",
        max_memory={
            0: GPU_MEMORY,
            "cpu": CPU_MEMORY,
        },
        torch_dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    print("Model loaded")
    print()

    return processor, model


# ============================================================
# CROP ONE ROW
# ============================================================

def crop_row(
    image_path: Path,
    row_number: int,
) -> tuple[Image.Image, tuple[int, int, int, int]]:

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    print("=" * 70)
    print("SOURCE IMAGE")
    print("=" * 70)
    print("Path:", image_path)
    print("Size:", f"{width} x {height}")
    print()

    # Make sure this test template matches 300 DPI T1.
    if width != PAGE_WIDTH or height != PAGE_HEIGHT:
        print(
            "WARNING: Image size differs from calibrated T1 300 DPI."
        )
        print(
            f"Expected: {PAGE_WIDTH} x {PAGE_HEIGHT}"
        )
        print(
            f"Actual:   {width} x {height}"
        )
        print()

    y1 = ROW1_Y1 + (row_number - 1) * ROW_HEIGHT
    y2 = y1 + ROW_HEIGHT

    y1 = max(0, y1 - ROW_PADDING_Y)
    y2 = min(height, y2 + ROW_PADDING_Y)

    x1 = max(0, TABLE_X1)
    x2 = min(width, TABLE_X2)

    box = (x1, y1, x2, y2)

    cropped = image.crop(box)

    return cropped, box


# ============================================================
# OCR
# ============================================================

def run_ocr(
    processor,
    model,
    crop_image: Image.Image,
    image_path: Path,
    row_number: int,
):

    print("=" * 70)
    print("ROW CROP")
    print("=" * 70)

    print("Row:", row_number)
    print("Crop size:", f"{crop_image.width} x {crop_image.height}")
    print()

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": crop_image,
                },
                {
                    "type": "text",
                    "text": """
Bạn là hệ thống OCR đọc một dòng dữ liệu viết tay trong biểu mẫu sản xuất.

Hãy đọc chính xác toàn bộ nội dung xuất hiện trên dòng này.

Yêu cầu:

- Giữ nguyên tiếng Việt và dấu tiếng Việt.
- Giữ nguyên chữ hoa/chữ thường.
- Giữ nguyên số.
- Giữ nguyên dấu câu và ký hiệu.
- Không tự sửa chính tả.
- Không suy đoán nội dung không nhìn rõ.
- Nếu một phần thực sự không đọc được, ghi [UNK].
- Giữ nguyên thứ tự từ trái sang phải.
- Có thể xuống dòng giữa các trường nếu cần để dễ đọc.
- Chỉ trả về nội dung OCR.
- Không markdown.
- Không giải thích.
- Không thêm thông tin không nhìn thấy.
""",
                },
            ],
        }
    ]

    print("Preparing input...")

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
        processor_kwargs={
            "min_pixels": MIN_IMAGE_PIXELS,
            "max_pixels": MAX_IMAGE_PIXELS,
        },
    )

    # --------------------------------------------------------
    # VISUAL TOKENS
    # --------------------------------------------------------

    if "image_grid_thw" in inputs:
        visual_tokens = int(
            inputs["image_grid_thw"].prod().item() // 4
        )
        print(
            f"Visual-token budget: {visual_tokens} tokens"
        )

    print(
        f"Max new tokens: {MAX_NEW_TOKENS}"
    )
    print()

    inputs = inputs.to(model.device)

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # --------------------------------------------------------
    # INFERENCE
    # --------------------------------------------------------

    print("Starting inference...")

    start = time.perf_counter()

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            use_cache=True,
        )

    elapsed = time.perf_counter() - start

    # --------------------------------------------------------
    # TRIM PROMPT TOKENS
    # --------------------------------------------------------

    generated_ids_trimmed = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(
            inputs.input_ids,
            generated_ids,
        )
    ]

    # --------------------------------------------------------
    # DECODE
    # --------------------------------------------------------

    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()

    generated_token_count = len(
        generated_ids_trimmed[0]
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RAW MODEL OUTPUT")
    print("=" * 70)
    print(output_text)
    print()

    print("=" * 70)
    print("PERFORMANCE")
    print("=" * 70)

    print(f"Inference time: {elapsed:.2f} seconds")
    print(f"Generated tokens: {generated_token_count}")

    if generated_token_count >= MAX_NEW_TOKENS:
        print()
        print(
            "WARNING: Output reached max_new_tokens."
        )
        print(
            "OCR result may be truncated."
        )

    if torch.cuda.is_available():
        allocated = (
            torch.cuda.memory_allocated()
            / 1024**3
        )

        reserved = (
            torch.cuda.memory_reserved()
            / 1024**3
        )

        peak = (
            torch.cuda.max_memory_allocated()
            / 1024**3
        )

        print(
            f"GPU allocated: {allocated:.3f} GB"
        )
        print(
            f"GPU reserved:  {reserved:.3f} GB"
        )
        print(
            f"GPU peak:      {peak:.3f} GB"
        )

    print()

    # ========================================================
    # SAVE CROP
    # ========================================================

    CROP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    crop_file = (
        CROP_DIR
        / f"{image_path.stem}_row_{row_number:02d}.png"
    )

    crop_image.save(crop_file)

    # ========================================================
    # SAVE JSON
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_file = (
        OUTPUT_DIR
        / f"{image_path.stem}_row_{row_number:02d}_qwen_result.json"
    )

    result = {
        "page": image_path.stem,
        "row": row_number,
        "text": output_text,
        "generated_tokens": generated_token_count,
        "inference_time_seconds": round(
            elapsed,
            3,
        ),
        "crop": {
            "width": crop_image.width,
            "height": crop_image.height,
        },
    }

    with json_file.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2,
        )

    # ========================================================
    # SAVE RAW TXT
    # ========================================================

    raw_file = (
        OUTPUT_DIR
        / f"{image_path.stem}_row_{row_number:02d}_qwen_raw.txt"
    )

    with raw_file.open(
        "w",
        encoding="utf-8",
    ) as f:
        f.write(output_text)

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    print("=" * 70)
    print("OUTPUT")
    print("=" * 70)

    print("Crop saved:", crop_file)
    print("JSON saved:", json_file)
    print("RAW saved: ", raw_file)
    print()

    print("=" * 70)
    print("JSON VALIDATION")
    print("=" * 70)

    try:
        with json_file.open(
            "r",
            encoding="utf-8",
        ) as f:
            parsed = json.load(f)

        if not isinstance(parsed, dict):
            raise ValueError(
                "JSON root is not an object"
            )

        if "text" not in parsed:
            raise ValueError(
                "Missing field 'text'"
            )

        print("JSON: VALID")

    except Exception as exc:
        print("JSON: INVALID")
        print("Reason:", exc)


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) not in (2, 3):
        print(
            "Usage:\n"
            "  python .\\app\\test_qwen_4b_row.py "
            "<image_path> [row_number]\n\n"
            "Example:\n"
            "  python .\\app\\test_qwen_4b_row.py "
            ".\\data\\pages\\T1_page_001.png 1"
        )
        sys.exit(1)

    image_path = Path(
        sys.argv[1]
    ).resolve()

    row_number = (
        int(sys.argv[2])
        if len(sys.argv) == 3
        else 1
    )

    if not image_path.exists():
        print(
            "ERROR: Image not found:"
        )
        print(image_path)
        sys.exit(1)

    if not image_path.is_file():
        print(
            "ERROR: Path is not a file:"
        )
        print(image_path)
        sys.exit(1)

    if not 1 <= row_number <= 20:
        print(
            "ERROR: row_number must be between 1 and 20."
        )
        sys.exit(1)

    try:

        # ----------------------------------------------------
        # LOAD MODEL
        # ----------------------------------------------------

        processor, model = load_model()

        # ----------------------------------------------------
        # CROP
        # ----------------------------------------------------

        crop_image, box = crop_row(
            image_path,
            row_number,
        )

        print("=" * 70)
        print("CROP BOX")
        print("=" * 70)
        print(
            f"x1={box[0]}, "
            f"y1={box[1]}, "
            f"x2={box[2]}, "
            f"y2={box[3]}"
        )
        print()

        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        run_ocr(
            processor,
            model,
            crop_image,
            image_path,
            row_number,
        )

    except torch.cuda.OutOfMemoryError:

        print()
        print("=" * 70)
        print("CUDA OUT OF MEMORY")
        print("=" * 70)

        print(
            "GPU không đủ VRAM cho row crop hiện tại."
        )

        sys.exit(2)

    except Exception as exc:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)

        print(
            type(exc).__name__ + ":",
            exc,
        )

        sys.exit(3)


if __name__ == "__main__":
    main()