# Production OCR Project — Full Context / Handoff README

> **Purpose:** This file is the handoff/context document for continuing the company's production handwriting OCR project in a new ChatGPT conversation.
>
> Read this file first. Continue from **CURRENT STATUS / NEXT STEP** instead of restarting the project.

---

# 0. PROJECT SUMMARY

## Goal

Build a handwriting OCR system for scanned **production report forms** used by a company.

The system should:

- Accept **PDF / JPG / PNG** input.
- Receive files through the existing **Telegram + n8n workflow**.
- Transfer the document/image to the OCR server/PC.
- Convert PDFs into page images.
- Normalize pages.
- Identify the relevant form/profile.
- Align/register the page according to a **flexible, configuration-driven template system**.
- Segment rows/regions/fields.
- Use **Qwen3-VL-4B-Instruct** for handwriting OCR.
- Preserve Vietnamese text and diacritics.
- Preserve numbers, capitalization, punctuation, symbols and technical codes.
- Validate OCR results deterministically.
- Re-OCR uncertain fields/regions.
- Target approximately **95% accuracy** across the agreed evaluation metrics.
- Map extracted values into an existing **Excel Sheet 05**.
- Send OCR results to Telegram for employee confirmation/correction.
- Produce one consolidated Excel output for the relevant input set.
- Retain original images and intermediate crops/results for traceability/debugging.

## Core architectural principle

The company may have multiple departments, different report forms, different layouts, and future form revisions.

Therefore the system **must NOT be hard-coded around one form such as T1**.

Target architecture:

> **One reusable OCR engine + many versioned form profiles/configurations.**

A new/revised form should normally be onboarded by adding/updating configuration/reference assets instead of rewriting the generic OCR/segmentation engine.

---

# 1. IMPORTANT WORKING PRINCIPLES

## 1.1 Test first, production integration later

All experimental work is currently done with `test_*.py` scripts.

Workflow:

```text
TEST / EXPERIMENT
    ↓
compare results
    ↓
tune parameters / logic
    ↓
validate on real data
    ↓
freeze behavior
    ↓
refactor / consolidate
    ↓
production modules
```

Do **NOT** prematurely put experimental logic into `qwen_ocr.py`.

`qwen_ocr.py` should be assembled only after OCR behavior has been tested and accepted.

## 1.2 Accuracy has higher priority than speed

The user explicitly prioritizes OCR quality over raw throughput.

Do not optimize for speed at the expense of handwriting recognition quality unless there is a clear production reason.

## 1.3 Qwen should not be responsible for deterministic work

Qwen should primarily perform visual interpretation/OCR.

Python should handle:

- JSON serialization,
- field mapping,
- format validation,
- confidence/review logic,
- retry logic,
- form selection,
- row/field coordinates,
- Excel generation.

Model-generated confidence is not ground truth by itself.

## 1.4 Full-page OCR is only a smoke test

A full-page Qwen test proved that the model can load/infer when visual-token input is controlled, but full-page OCR with aggressive downscaling loses handwriting detail and produced weak recognition.

The intended production strategy is **region/row/field-level OCR**, not huge 300-DPI full-page inference.

## 1.5 Flexible form architecture is mandatory

Do not build generic logic that assumes:

```text
T1 is the only form
T1 always has 20 rows
T1 always has 14 columns
all departments use the same layout
future revisions keep the same geometry
```

Instead use versioned profiles under `config/forms/`.

---

# 2. ENVIRONMENT

## Development/home machine

Confirmed from `nvidia-smi` and PyTorch:

```text
OS: Windows 11
Python: 3.11.9
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
VRAM available to PyTorch: ~6 GB
```

Windows Task Manager also shows Intel UHD shared memory around 7.9 GB. That is **shared system RAM for the Intel iGPU**, not additional RTX 4050 VRAM.

## Production/company machine

Production baseline:

```text
CPU: Intel Core i7-14700K
RAM: 32 GB DDR5
GPU: NVIDIA RTX 3060 6 GB
OS: Windows 11
```

Production constraints are more important than the home machine.

Current production-baseline Qwen memory targets:

```text
GPU_MEMORY = "5GiB"
CPU_MEMORY = "24GiB"
```

Home testing may temporarily use `26GiB` CPU memory.

## Project root

```text
D:\production_ocr
```

## Virtual environment

```text
D:\production_ocr\.venv
```

Executable:

```text
D:\production_ocr\.venv\Scripts\python.exe
```

PowerShell activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

---

# 3. CURRENT LIBRARY / MODEL STACK

Confirmed development stack:

```text
Python                  3.11.9
torch                   2.11.0+cu128
torchvision             0.26.0+cu128
torchaudio              2.11.0+cu128
transformers            5.17.0
accelerate              1.15.0
bitsandbytes            0.50.2
PyMuPDF                 1.28.2
opencv-python           5.0.0.93
```

Other installed libraries include FastAPI/Uvicorn/OpenPyXL and related project dependencies.

## CUDA clarification

The current PyTorch build is CUDA 12.8.

`nvidia-smi` previously showed a newer driver-level CUDA compatibility value. Do not equate the `nvidia-smi` "CUDA Version" display with the exact CUDA Toolkit or PyTorch build.

Do not change PyTorch/Transformers just because the driver reports a newer CUDA version. The current Qwen environment already loads/infer successfully.

---

# 4. QWEN MODEL

Model:

```text
Qwen/Qwen3-VL-4B-Instruct
```

Local path:

```text
D:\production_ocr\models\Qwen3-VL-4B-Instruct
```

Approximate local model size was 8.89 GB.

4-bit configuration:

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
```

Model loading uses:

```python
device_map="auto"

max_memory={
    0: "5GiB",
    "cpu": "24GiB",
}
```

---

# 5. INPUT DATA / T1 SAMPLE

A real sample `T1.pdf` was provided and tested.

It contains:

```text
7 pages
```

Each page uses the same T1 form layout.

Each page has:

```text
20 row slots
```

and approximately:

```text
14 grid columns
```

Page orientation:

```text
landscape
```

Current normalized/rendered page size:

```text
3509 × 2481 px
```

at 300 DPI.

---

# 6. INTENDED PROJECT STRUCTURE

Original intended structure:

```text
D:\production_ocr
│
├── app/
│   ├── pdf_processor.py
│   ├── image_preprocess.py
│   ├── form_template.py
│   ├── row_detector.py
│   ├── qwen_ocr.py
│   ├── validator.py
│   ├── mapper.py
│   ├── excel_writer.py
│   └── api.py
│
├── config/
│   ├── form_v1.json
│   ├── mapping.json
│   └── settings.json
│
├── data/
│   ├── input/
│   ├── pages/
│   ├── preprocessed/
│   ├── crops/
│   ├── ocr/
│   ├── validated/
│   ├── reviewed/
│   └── output/
│
├── evaluation/
│   └── ground_truth/
│
├── logs/
│
├── requirements.txt
├── PHASES.md
├── N8N_INTEGRATION.md
├── README.md
└── main.py
```

This has evolved to a more flexible form-profile structure, especially under `config/forms/`.

---

# 7. FILES CURRENTLY USED / CREATED

## `app/pdf_processor.py`

Purpose:

```text
PDF → page images
```

Uses modern PyMuPDF import style:

```python
import pymupdf
```

rather than deprecated:

```python
import fitz
```

Successful test:

```powershell
python .\app\pdf_processor.py .\data\input\T1.pdf
```

Output:

```text
data/pages/T1_page_001.png
...
data/pages/T1_page_007.png
```

## `app/image_preprocess.py`

Purpose:

- scan `data/pages/`,
- normalize orientation,
- normalize page size,
- conservative contrast normalization,
- preserve originals,
- create processed pages,
- create previews/contact sheet,
- write preprocessing report.

User already ran this successfully.

Current output:

```text
data/preprocessed/pages/
    T1_page_001.png
    ...
    T1_page_007.png

data/preprocessed/preview/
    contact_sheet.jpg

data/preprocessed/preprocess_report.json
```

Phase 3 is complete for the current T1 sample.

## `app/test_qwen_4b_infer.py`

Purpose:

- load local Qwen,
- load processor,
- test CUDA,
- control image pixels,
- run inference,
- report visual tokens/memory/time,
- save JSON + raw text,
- validate JSON structure.

It is a smoke-test file, not final production OCR logic.

## `app/test_qwen_4b_row.py`

Purpose:

- crop one row,
- send the crop to Qwen,
- save crop,
- save structured JSON,
- save raw TXT,
- test row-level OCR quality.

An early version contained hard-coded T1 coordinates. This was useful for experimentation but must NOT become the permanent generic design.

## Phase-4 architecture files

The new flexible architecture prepared these files:

```text
app/form_registry.py
app/test_template_registration.py

config/forms/registry.json
config/forms/T1/v1/form.json
config/forms/T1/v1/reference.png
```

The package created for this work was:

```text
production_ocr_phase4_v2_files.zip
```

There is also a Phase-4 README package:

```text
production_ocr_phase4_v2/README_PHASE4.md
```

---

# 8. CURRENT T1 REFERENCE GEOMETRY

The current T1 candidate reference is `T1_page_001.png` after preprocessing.

Page size:

```text
3509 × 2481
```

Reference table:

```text
x1 = 94
x2 = 3466
y1 = 495
y2 = 2080
```

Reference horizontal grid lines:

```text
495
574
654
733
813
892
972
1050
1129
1209
1287
1366
1446
1525
1603
1683
1762
1842
1921
2001
2080
```

There are:

```text
21 horizontal lines
20 row intervals
```

Reference vertical grid lines:

```text
94
184
349
592
967
1360
1522
1687
1852
2016
2179
2344
2508
3159
3466
```

There are:

```text
15 vertical lines
14 column intervals
```

This geometry belongs to **T1/v1** only. It is not a universal company-wide geometry.

---

# 9. T1 FORM FIELDS

The T1 table includes:

```text
STT
Ngày
Mã Đơn Hàng
Mã bản Vẽ
Mã Công Việc
Thời gian thực hiện
Thời gian bắt đầu
Thời gian kết thúc
Tổng thời gian
SL gia công
SL Đạt
SL NG
Công đoạn, nội dung diễn giải chi tiết
Ghi chú
```

Header/page fields include:

```text
Tổ/Nhóm
Nhân viên
Mã nhân viên
Ngày
Tuần
```

The generic engine should not hard-code these as universal fields; they belong in the form profile.

---

# 10. EXCEL SHEET 05 TARGET

Current Sheet 05 columns:

```text
RunID
Ngày
Ca
Mã đơn hàng
Mã bản vẽ
Rev
Dòng/Lô
Mã dòng hệ thống
Thứ tự CĐ
OperationCode
OperationPlanID
Nhân viên
Máy
ActivityType
Bắt đầu
Kết thúc
Nghỉ
Setup TT
Downtime
Run TT
SL xử lý
SL đạt
SL đạt lần đầu
SL cần sửa
SL phế
SL chờ
Cân đối SL
Earned Min
Labor Min
Hiệu suất
Chi phí LĐ
Chi phí máy
Chi phí chuyển đổi
Duyệt
Kiểm tra dữ liệu
Ghi chú
```

Confirmed paper → Sheet 05 mappings so far:

```text
Ngày
    → Ngày

Mã đơn hàng
    → Mã đơn hàng

Mã bản vẽ
    → Mã bản vẽ

Rev
    → Rev

Thời gian bắt đầu
    → Bắt đầu

Thời gian kết thúc
    → Kết thúc

SL gia công
    → SL xử lý

SL đạt
    → SL đạt

SL NG
    → SL chờ

Ghi chú
    → Ghi chú
```

Potential mappings that are NOT yet final:

```text
Mã Công Việc → OperationCode
Nhân viên → Nhân viên
Công đoạn/nội dung → Ghi chú
```

These are candidates only until the actual workbook/template is inspected and confirmed.

Other requirements:

- Fields not present on paper should not be invented.
- Existing formulas must be preserved.
- Previously manual/yellow input cells are intended to become automatically populated once OCR is working.
- Blue cells are formula-derived and should remain formula-driven.
- The real workbook is the source of truth when Phase 9 is implemented.

---

# 11. OCR ACCURACY REQUIREMENT

User stated that the ~95% target applies to all four agreed metrics:

```text
1. Character Accuracy
2. Field Accuracy
3. Row Accuracy
4. Page Accuracy
```

A manual ground-truth set will eventually be created under:

```text
evaluation/ground_truth/
```

JSON validity alone is NOT an OCR-quality acceptance criterion.

Actual handwriting recognition quality must be measured on representative pages/writers/forms.

---

# 12. CURRENT QWEN RESULTS / LESSONS

## Full-page test

The original full-page 300-DPI input caused CUDA OOM.

Representative error:

```text
CUDA out of memory
Tried to allocate 9.12 GiB
GPU total capacity: 6.00 GiB
```

After limiting image size, full-page test ran with:

```text
Visual-token budget: 988 tokens
```

but output hit:

```text
Generated tokens: 768
```

and the result was incomplete/poor in places.

Inference time was about 140.59 s.

This confirmed:

- Qwen 4B loads on the development RTX 4050 6 GB.
- visual-token limiting can prevent the previous OOM.
- full-page OCR at aggressively reduced detail is not the right production approach.

## Row-level test

Early row-level tests produced roughly 40–60% correct output by user inspection.

Examples:

Row 2 output:

```text
2
PRC 25N2-06Z
11h15 14h20 2h20
Hướng dẫn NV Qm
```

Metadata:

```text
generated_tokens: 38
inference_time_seconds: 5.602
crop: 3340 × 83
```

Row 3:

```text
3/1
8h10 14h50 5h40 4 4 0 Gc Pin +hu²
```

Metadata:

```text
generated_tokens: 32
inference_time_seconds: 3.199
crop: 3340 × 83
```

Row 4:

```text
[UNK] [UNK] 25055 14 31 15h 16h40 16h40 Set up chấu
```

Metadata:

```text
generated_tokens: 39
inference_time_seconds: 7.073
crop: 3340 × 83
```

These results are not production-acceptable yet.

---

# 13. OCR OUTPUT DESIGN

Important architectural decision:

> **Qwen should return raw OCR text, not generate the final JSON structure.**

Preferred:

```text
Qwen
  ↓
raw OCR text
  ↓
Python
  ↓
valid JSON
```

Example:

```json
{
  "text": "nội dung OCR..."
}
```

Always retain the raw output for debugging.

Recommended pair:

```text
*_qwen_result.json
*_qwen_raw.txt
```

---

# 14. FORM-REGISTRY ARCHITECTURE

The system must support many departments and future form revisions.

Conceptual structure:

```text
config/
└── forms/
    ├── registry.json
    │
    ├── T1/
    │   ├── v1/
    │   │   ├── form.json
    │   │   └── reference.png
    │   └── v2/
    │       ├── form.json
    │       └── reference.png
    │
    ├── QC01/
    │   └── v1/
    │       ├── form.json
    │       └── reference.png
    │
    └── ...
```

Example registry concept:

```json
{
  "forms": [
    {
      "form_id": "T1",
      "department": "SanXuat",
      "version": "v1",
      "config_path": "forms/T1/v1"
    },
    {
      "form_id": "QC01",
      "department": "QC",
      "version": "v1",
      "config_path": "forms/QC01/v1"
    }
  ]
}
```

A future T1 change should preferably be:

```text
T1/v2/
```

rather than rewriting generic engine code.

---

# 15. FORM PROFILE SCHEMA CONCEPT

A form profile may eventually define:

```text
form_id
department
version
page orientation
page size
reference image
registration method
registration ROI
segmentation strategy
row strategy
row count
column geometry
field definitions
OCR prompt
validation rules
Excel mappings
```

Example concept:

```json
{
  "form_id": "T1",
  "department": "SanXuat",
  "version": "v1",

  "page": {
    "width": 3509,
    "height": 2481,
    "orientation": "landscape"
  },

  "registration": {
    "method": "template",
    "reference_image": "reference.png"
  },

  "row_strategy": {
    "type": "fixed",
    "count": 20
  },

  "columns": [],
  "fields": [],

  "ocr": {
    "model": "Qwen3-VL-4B-Instruct"
  }
}
```

Exact final schema is NOT yet frozen.

---

# 16. TEMPLATE CALIBRATION TEST — LESSON

An earlier `app/test_template_calibrator.py` independently detected horizontal/vertical table lines on every page.

Results on the 7 T1 pages:

```text
Page 1: H=21, V=15 → PASS
Page 2: H=0,  V=15 → REVIEW
Page 3: H=20, V=15 → REVIEW
Page 4: H=20, V=15 → REVIEW
Page 5: H=20, V=15 → REVIEW
Page 6: H=0,  V=15 → REVIEW
Page 7: H=0,  V=15 → REVIEW
```

The vertical geometry was relatively stable, with maximum deltas approximately:

```text
Page 2: 18 px
Page 3: 28 px
Page 4: 28 px
Page 5: 23 px
Page 6: 10 px
Page 7: 7 px
```

The horizontal-line detector itself was not robust across all scans.

Conclusion:

> Do not make "each page must independently detect all horizontal lines" a core assumption.

Because the form is fixed within a version, a better approach is reference-based registration/alignment followed by configuration-defined geometry.

---

# 17. CURRENT PHASE-4 DIRECTION

The flexible approach is:

```text
REFERENCE FORM PROFILE
        ↓
template/reference geometry
        ↓
register each page to the profile
        ↓
use profile geometry after registration
        ↓
generic segmentation
```

This is an image-registration/template-alignment problem, not only a line-detection problem.

Why:

- scans may be shifted,
- line contrast can vary,
- some lines may not be detected reliably,
- different forms have different geometry,
- future form revisions require versioning.

---

# 18. REGISTRATION CONCEPT

Desired behavior:

```text
Page image
   ↓
identify form/profile
   ↓
load form.json + reference.png
   ↓
image registration / alignment
   ↓
aligned page
   ↓
apply profile geometry
   ↓
row/region/field segmentation
```

Configuration concept:

```json
{
  "registration": {
    "method": "template",
    "reference_image": "reference.png",
    "max_translation_px": 50,
    "max_rotation_deg": 2
  }
}
```

This exact schema/algorithm is not yet final; it must be tested.

---

# 19. WHY NOT HAVE QWEN UNDERSTAND ARBITRARY FORMS BY ITSELF?

Rejected approach:

```text
arbitrary image
   ↓
Qwen
   ↓
understand form
   ↓
find fields
   ↓
extract everything
```

Reasons:

- too many variables,
- harder to reach ~95% accuracy,
- harder to validate,
- harder to reproduce/debug,
- harder to support versioning.

Preferred:

```text
form identification
      ↓
configuration
      ↓
registration
      ↓
segmentation
      ↓
Qwen OCR
      ↓
deterministic validation
      ↓
mapping
```

---

# 20. ROW-LEVEL / ROI OCR TERMINOLOGY

The current method can be called:

> **Template-based Row-level OCR**

or:

> **Template-based ROI Segmentation + Row-level OCR**

Related terms:

- ROI-based OCR
- Region-based OCR
- Row-level OCR
- template-based segmentation
- tiled/segmented OCR

Cropping is not only a workaround for token limits. It also preserves higher handwriting detail while reducing the vision burden per inference.

---

# 21. FIELD-LEVEL OCR — FUTURE OPTION

If whole-row OCR is insufficient, a row may be subdivided into fields:

```text
row
 ├── Ngày
 ├── Mã đơn hàng
 ├── Mã bản vẽ
 ├── Mã Công Việc
 ├── Thời gian bắt đầu
 ├── Thời gian kết thúc
 ├── SL gia công
 ├── SL đạt
 ├── SL NG
 ├── Công đoạn
 └── Ghi chú
```

Do NOT immediately make dozens of model calls per row.

First establish robust registration + segmentation, then identify which fields are difficult and selectively apply field-level OCR/re-OCR.

---

# 22. VALIDATION / CONFIDENCE DESIGN

Confidence should be based on multiple signals, for example:

```text
format validation
field-specific rules
cross-field consistency
pass-1 / pass-2 agreement
required-field presence
numeric/date/time structure
re-OCR agreement
```

Conceptual flow:

```text
Pass 1 OCR
   ↓
validation
   ↓
confidence sufficient?
 ├── YES → accept
 └── NO
       ↓
smaller field crop
       ↓
re-OCR
       ↓
compare
       ↓
accept if valid/agreement
otherwise → human review
```

---

# 23. TELEGRAM + N8N WORKFLOW

Existing workflow should be reused, not rebuilt.

Known workflow name:

```text
WF04_01_CoCongNo
```

Earlier inspection found concepts/nodes for:

- Telegram Trigger
- media download
- OCR via Gemini/rescue
- parsing
- Google Sheets
- callback/state/error handling

A real API key had previously appeared hard-coded in an HTTP node.

Do not reproduce it.

Security action:

- rotate/revoke it if real,
- move secrets to n8n credentials/environment/secure storage.

Future local OCR integration should replace/augment the current OCR portion while preserving the working Telegram/state/callback design.

---

# 24. TELEGRAM USER FLOW

Target flow:

```text
Employee
   ↓
send PDF/JPG/PNG
   ↓
existing n8n
   ↓
download
   ↓
OCR server/PC
   ↓
OCR pipeline
   ↓
validation
   ↓
Telegram result
   ↓
employee confirms/corrects
   ↓
final approved data
   ↓
Excel
```

Requirements:

- PDF, JPG, PNG all accepted.
- Correction is initially directly in Telegram.
- All relevant pages/files should be consolidated into the final workbook when appropriate.
- Original + intermediate artifacts should be preserved for traceability.

---

# 25. TRACEABILITY REQUIREMENT

The pipeline should make it possible to trace:

```text
original input
   ↓
rendered page
   ↓
preprocessed page
   ↓
registered/aligned page
   ↓
row crop
   ↓
field crop
   ↓
raw OCR text
   ↓
structured JSON
   ↓
validated result
   ↓
review/correction
   ↓
Excel
```

Exact cleanup/retention policy remains to be finalized.

---

# 26. LARGE PIPELINE / PHASES

Current agreed high-level flow:

```text
PHASE 0  Requirement Freeze
    ↓
PHASE 1  Runtime + Qwen
    ↓
PHASE 2  Input Engine
    ↓
PHASE 3  Image Normalization
    ↓
PHASE 4  Form Registry + Calibration
    ↓
PHASE 5  Generic Registration + Segmentation
    ↓
PHASE 6  Qwen OCR
    ↓
PHASE 7  Validation + Confidence
    ↓
PHASE 8  Ground Truth + Accuracy
    ↓
PHASE 9  Excel Sheet 05
    ↓
PHASE 10 Telegram QC
    ↓
PHASE 11 n8n Integration
    ↓
PHASE 12 Production Hardening
```

---

# 27. PHASE DETAILS

## PHASE 0 — Requirement Freeze

Goals:

- define supported inputs,
- define fields,
- define Excel mapping,
- define acceptance criteria,
- define Telegram behavior.

Status:

Mostly defined conceptually. Final workbook details must be verified against the real workbook during Phase 9.

---

## PHASE 1 — Runtime + Qwen

Goals:

- Python environment,
- GPU/CUDA validation,
- Qwen3-VL-4B loading,
- 4-bit NF4,
- CPU/GPU memory mapping.

Status:

**PASS for development inference setup.**

---

## PHASE 2 — Input Engine

Goals:

- PDF/JPG/PNG input,
- deterministic PDF page rendering,
- preserve original inputs.

Status:

**Basic PDF → PNG successfully tested.**

---

## PHASE 3 — Image Normalization

Goals:

- normalize orientation,
- normalize page size,
- conservative image normalization,
- previews/reports.

Status:

**PASS on the current 7-page T1 sample.**

---

## PHASE 4 — Form Registry + Calibration

Goals:

- flexible form profiles,
- multiple departments/forms,
- versioning,
- reference images,
- form geometry,
- registration preparation.

Status:

**IN PROGRESS.**

T1/v1 is the first profile.

The old detector showed that independently finding horizontal lines is not robust enough on every page.

New direction:

```text
form profile
   ↓
reference geometry
   ↓
registration/alignment
   ↓
apply profile geometry
```

---

## PHASE 5 — Generic Registration + Segmentation

Goals:

- register each page to its form profile,
- use profile geometry,
- create generic row/region/field crops,
- support multiple forms.

Status:

**NOT YET ACCEPTED / NOT STARTED AS FINAL GENERIC PHASE.**

---

## PHASE 6 — Qwen OCR

Goals:

- row-level OCR,
- selective field-level OCR,
- prompt tuning,
- image/pixel tuning,
- token tuning,
- raw/structured outputs.

Status:

**EXPERIMENTAL / NOT READY.**

Do not consolidate into `qwen_ocr.py` yet.

---

## PHASE 7 — Validation + Confidence

Goals:

- deterministic field validation,
- retry/re-OCR,
- disagreement detection,
- human-review routing.

Status:

**NOT STARTED.**

---

## PHASE 8 — Ground Truth + Accuracy

Goals:

- create manually verified ground truth,
- measure character/field/row/page accuracy,
- test representative writers/forms/pages.

Target:

```text
~95%
```

Status:

**NOT STARTED.**

---

## PHASE 9 — Excel Sheet 05

Goals:

- map extracted data into workbook,
- preserve formulas,
- populate intended manual/yellow cells automatically,
- keep blue formula cells formula-driven,
- create final workbook.

Status:

**NOT STARTED.**

Need the actual workbook as source of truth when implementing.

---

## PHASE 10 — Telegram QC

Goals:

- show OCR result,
- allow Telegram corrections,
- accept confirmation,
- store final approved values.

Status:

**NOT STARTED.**

---

## PHASE 11 — n8n Integration

Goals:

- plug local OCR engine into existing workflow,
- preserve Telegram/state/callback behavior,
- replace/augment current OCR step,
- robust error handling.

Status:

**NOT STARTED.**

---

## PHASE 12 — Production Hardening

Goals:

- logging,
- retries,
- queueing,
- model lifecycle,
- cleanup,
- monitoring,
- security,
- configuration/version control,
- deployment/recovery.

Status:

**NOT STARTED.**

---

# 28. CURRENT STATUS — EXACT HANDOFF

Completed:

```text
[✓] Python venv
[✓] Qwen model downloaded
[✓] Qwen 4B loads on RTX 4050 ~6 GB
[✓] 4-bit NF4 loading
[✓] GPU/CPU memory mapping
[✓] PDF → 7 page PNG
[✓] image preprocessing
[✓] full-page smoke inference without previous OOM after token/pixel cap
[✓] Python-generated JSON output architecture
[✓] initial row-level Qwen experiments
[✓] identified need for flexible form architecture
```

Current:

```text
[→] PHASE 4 — Form Registry + Template Registration / Calibration
```

Current T1 reference geometry is known and stored in a candidate profile.

---

# 29. IMMEDIATE NEXT STEP

Do **not** restart from Phase 1.

Continue from Phase 4 using the new flexible architecture.

The next concrete commands prepared are:

```powershell
python .\app\form_registry.py --form T1 --version v1
```

then:

```powershell
python .\app\test_template_registration.py --form T1 --version v1
```

Expected debug output should be under something like:

```text
data/preprocessed/registration_debug/
```

Important artifacts to inspect after running:

```text
registration_debug/contact_sheet.jpg
registration_debug/registration_report.json
```

The test must be reviewed on all 7 T1 pages.

Only after registration/alignment is verified should Phase 5 proceed.

---

# 30. HOW TO CONTINUE IN A NEW CHAT

When continuing this project:

1. Read this README first.
2. Assume Phases 0–3 are already done unless new evidence contradicts that.
3. Continue from Phase 4.
4. Keep experiments in `test_*.py` files.
5. Do not merge into `qwen_ocr.py` until the experimental logic is proven.
6. Keep the architecture configuration-driven and versioned.
7. Do not assume T1 is the only form.
8. Test against the actual 7-page T1 data before moving phases.
9. Treat the production i7-14700K + 32 GB + RTX 3060 6 GB machine as the deployment constraint.
10. Keep accuracy ahead of speed.

---

# 31. IMPORTANT “DO NOT” RULES

```text
DO NOT rewrite the whole project from scratch.

DO NOT assume T1 is the only future form.

DO NOT hard-code T1 row/column coordinates into generic engines.

DO NOT treat Intel UHD shared memory as additional RTX VRAM.

DO NOT interpret valid JSON as proof of OCR accuracy.

DO NOT rely solely on Qwen self-reported confidence.

DO NOT sacrifice handwriting detail just to make inference faster.

DO NOT change Transformers/PyTorch without a demonstrated reason.

DO NOT expose/reproduce any API key previously seen in n8n.

DO NOT prematurely consolidate experimental OCR code into qwen_ocr.py.
```

---

# 32. FINAL TARGET ARCHITECTURE

```text
Telegram
   │
   ▼
existing n8n workflow
   │
   ▼
Input handler
   │
   ├── PDF
   ├── JPG
   └── PNG
   │
   ▼
PDF/page processor
   │
   ▼
Image normalization
   │
   ▼
Form identification / registry
   │
   ▼
Load form profile + version
   │
   ▼
Template registration
   │
   ▼
Generic segmentation
   │
   ├── rows
   ├── regions
   └── fields
   │
   ▼
Qwen3-VL-4B OCR
   │
   ▼
Raw OCR
   │
   ▼
Deterministic validation
   │
   ├── accepted
   ├── re-OCR
   └── human review
   │
   ▼
Structured data
   │
   ▼
Sheet 05 mapping
   │
   ▼
Excel
   │
   ▼
Telegram QC / correction
   │
   ▼
Final approved output
```

---

# 33. FINAL ARCHITECTURAL SUMMARY

The central design principle is:

> **The model is reusable; the form definition is configurable.**

Adding a new department/form should generally mean:

```text
NEW FORM
    ↓
create/register form profile
    ↓
calibrate/reference
    ↓
define fields / validation / mapping
    ↓
reuse the same OCR engine
```

A form revision should generally mean:

```text
T1 v1
  ↓
T1 v2
```

with a new version/config/reference rather than generic-engine rewrites.

Qwen3-VL-4B remains the shared OCR model unless testing later proves that another model is necessary.

---

# 34. ONE-LINE HANDOFF

> **Continue the Production OCR project from PHASE 4: verify the new configuration-driven Form Registry + Template Registration implementation on the 7 preprocessed T1 pages, inspect alignment/report, and only after Phase 4 is accepted proceed to Phase 5 Generic Registration + Segmentation; keep experimentation in test files and do not consolidate into `qwen_ocr.py` until the behavior is proven.**
