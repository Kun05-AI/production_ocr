$ErrorActionPreference = 'Stop'

if (-not (Get-Command hf -ErrorAction SilentlyContinue)) {
    throw "The 'hf' command is not available. Activate the venv and install huggingface_hub first."
}

New-Item -ItemType Directory -Force .\models | Out-Null
hf download Qwen/Qwen3-VL-4B-Instruct --local-dir .\models\Qwen3-VL-4B-Instruct
Write-Host "Model download/check complete."
