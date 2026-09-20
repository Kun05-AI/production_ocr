# Setup Phase 1 — Windows dev machine

## Target architecture

Development machine (home): your local GPU is only used to accelerate development/testing.
Production target remains:
- Windows 11
- Intel i7-14700K
- 32 GB DDR5 RAM
- NVIDIA RTX 3060 6 GB

The production memory limits must therefore stay conservative even if the home machine has more GPU memory.

## 0. Prerequisites

Recommended:
- Python 3.11.x
- Git for Windows
- NVIDIA driver with CUDA support
- At least ~15 GB free disk space for the model + cache + temp files

The current Qwen3-VL-4B-Instruct repository is about 8.89 GB of files; 4-bit quantization is applied when loading the model, not by shrinking the repository download itself.

## 1. Create and activate venv

From the project root in PowerShell:

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
```

Verify:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

## 2. Verify NVIDIA before installing PyTorch

```powershell
nvidia-smi
```

The important part is that Windows sees the NVIDIA GPU and the driver successfully starts.

## 3. Install CUDA-enabled PyTorch

Use the official PyTorch install selector for Windows + Pip + Python + CUDA.
For the current project baseline, CUDA 12.8 wheels are a suitable starting point when the installed NVIDIA driver supports them:

```powershell
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

Verify immediately:

```powershell
python -c "import torch; print('torch=', torch.__version__); print('torch CUDA build=', torch.version.cuda); print('CUDA available=', torch.cuda.is_available()); print('GPU=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"
```

Do not continue to Qwen until `CUDA available=True`.

## 4. Install the remaining project libraries

Qwen3-VL currently advises using the latest Transformers code because the model support was added there around the 4.57 line.

```powershell
python -m pip install --upgrade accelerate bitsandbytes pillow pymupdf opencv-python numpy fastapi "uvicorn[standard]" python-multipart "pydantic>=2" openpyxl huggingface_hub qwen-vl-utils
python -m pip install --upgrade git+https://github.com/huggingface/transformers
```

We intentionally do NOT install FlashAttention2 in the first Windows baseline. Qwen recommends it for memory/speed, but the first milestone is a stable SDPA + 4-bit setup on Windows; performance optimization comes later.

## 5. Verify bitsandbytes

```powershell
python -m bitsandbytes
```

A successful report should show that the package can access the NVIDIA/CUDA backend. If this command reports a CUDA backend problem, stop here and fix the environment before trying to load Qwen.

## 6. Download Qwen3-VL-4B-Instruct

Create a predictable local model directory:

```powershell
New-Item -ItemType Directory -Force .\models | Out-Null
```

Download the entire model repository to the local project folder:

```powershell
hf download Qwen/Qwen3-VL-4B-Instruct --local-dir .\models\Qwen3-VL-4B-Instruct
```

You can verify the files:

```powershell
Get-ChildItem .\models\Qwen3-VL-4B-Instruct | Select-Object Name,Length
```

## 7. Optional: keep Hugging Face cache inside the project

For a fully portable dev folder:

```powershell
$env:HF_HOME = "$PWD\.hf_cache"
```

Do this before any model/processor download. If the model is already downloaded with `--local-dir`, the local model directory remains the primary checkpoint path.

## 8. Load test

From project root:

```powershell
python -c "import torch; from transformers import AutoProcessor, Qwen3VLForConditionalGeneration; from transformers import BitsAndBytesConfig; print('imports OK'); q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True); m=Qwen3VLForConditionalGeneration.from_pretrained('.\\models\\Qwen3-VL-4B-Instruct',device_map='auto',max_memory={0:'5GiB','cpu':'24GiB'},quantization_config=q,dtype=torch.float16,attn_implementation='sdpa',low_cpu_mem_usage=True); print('MODEL LOAD OK'); print(m.hf_device_map)"
```

This is intentionally only a load test. Do not yet feed the full 7-page PDF.

## 9. Run the first OCR smoke test

Put one rendered row crop under:

```text
data/crops/row_test.png
```

Then:

```powershell
python -m app.qwen_ocr .\data\crops\row_test.png
```

Expected milestone:
- PyTorch sees CUDA
- bitsandbytes works
- model loads successfully
- one image reaches the model
- model returns parseable JSON
- no Excel or Telegram side effects yet

## 10. Do not commit

Never commit these folders/files:

```text
.venv/
models/
.hf_cache/
__pycache__/
*.env
```

Add them to `.gitignore`.
