# PRODUCTION OCR — PHASES DETAILED
## Version 2 — Architecture and execution specification

> This document is the current technical execution plan for the Production OCR project.
> It supersedes the older 8-phase planning documents.
>
> Current implementation checkpoint: **PHASE 4 — Form Registry + Template Registration / Calibration**.
>
> The project principle is:
>
> **One reusable OCR engine + many versioned form profiles/configurations.**

---

# 0. PROJECT GOAL

Build a handwriting OCR system for scanned production report forms.

Supported input:

- PDF
- JPG
- PNG

Target end-to-end flow:

```text
Telegram
   ↓
existing n8n workflow
   ↓
input handler
   ↓
PDF → pages / image normalization
   ↓
form identification
   ↓
versioned form profile
   ↓
template registration
   ↓
generic segmentation
   ├── rows
   ├── regions
   └── fields
   ↓
Qwen3-VL-4B OCR
   ↓
raw OCR text
   ↓
Python structuring
   ↓
deterministic validation
   ↓
re-OCR / human review when necessary
   ↓
business-data lookup / mapping
   ↓
Excel Sheet 05
   ↓
Telegram confirmation
   ↓
final approved workbook
```

The OCR system must preserve:

- Vietnamese diacritics
- numbers
- capitalization
- punctuation
- technical codes
- symbols
- handwritten content
- traceability from original image to final Excel

Accuracy target:

```text
~95%
```

Measured at:

```text
1. Character Accuracy
2. Field Accuracy
3. Row Accuracy
4. Page Accuracy
```

JSON validity alone is not an OCR acceptance criterion.

---

# 1. ARCHITECTURAL PRINCIPLES

## 1.1 Configuration-driven forms

Do not hard-code one form into the generic engine.

Bad:

```text
if form == "T1":
    rows = 20
    x1 = 94
    x2 = 3466
```

Preferred:

```text
Form Registry
    ↓
form_id
    ↓
version
    ↓
form.json
    ↓
reference.png
    ↓
generic engine
```

A new form should normally be added by adding configuration/reference assets.

A revision should normally become a new version:

```text
T1/v1
T1/v2
```

rather than rewriting the generic engine.

---

## 1.2 Qwen is an OCR/vision component, not the entire business engine

Qwen should primarily:

```text
see image
    ↓
read handwriting / visible text
    ↓
return raw OCR content
```

Python should handle:

- JSON structuring
- field mapping
- validation
- confidence/review routing
- retry/re-OCR
- form selection
- coordinates
- business lookup
- Excel generation

Do not ask Qwen to invent deterministic business logic.

---

## 1.3 Accuracy over speed

Do not reduce image detail only to improve throughput.

Optimization is allowed after:

1. recognition quality is understood,
2. acceptance criteria are met,
3. production behavior is stable.

---

## 1.4 Experiments stay separate from production modules

Development pattern:

```text
experiment
   ↓
measure
   ↓
inspect
   ↓
tune
   ↓
validate
   ↓
freeze
   ↓
move proven logic into production module
```

Do not prematurely fill `qwen_ocr.py` with experimental logic.

---

# 2. HARDWARE / RUNTIME BASELINE

## Development

```text
OS          Windows 11
Python      3.11.9
GPU         NVIDIA RTX 4050 Laptop GPU
VRAM        ~6 GB
PyTorch     CUDA-enabled build
```

## Production baseline

```text
CPU         Intel Core i7-14700K
RAM         32 GB DDR5
GPU         NVIDIA RTX 3060 6 GB
OS          Windows 11
```

Production Qwen memory target:

```text
GPU_MEMORY = "5GiB"
CPU_MEMORY = "24GiB"
```

The development machine may temporarily use more CPU memory during experimentation.

---

# 3. MODEL BASELINE

Model:

```text
Qwen/Qwen3-VL-4B-Instruct
```

Local model path:

```text
D:\production_ocr\models\Qwen3-VL-4B-Instruct
```

Current quantization:

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
```

The current Qwen setup already loads/infer successfully.

Do not change PyTorch / Transformers merely because the NVIDIA driver reports another CUDA compatibility version.

---

# 4. PHASE MAP

```text
PHASE 0   Requirement Freeze
    ↓
PHASE 1   Runtime + Qwen
    ↓
PHASE 2   Input Engine
    ↓
PHASE 3   Image Normalization
    ↓
PHASE 4   Form Registry + Calibration / Registration
    ↓
PHASE 5   Generic Registration + Segmentation
    ↓
PHASE 6   Qwen OCR
    ↓
PHASE 7   Validation + Confidence
    ↓
PHASE 8   Ground Truth + Accuracy
    ↓
PHASE 9   Excel Sheet 05
    ↓
PHASE 10  Telegram QC
    ↓
PHASE 11  n8n Integration
    ↓
PHASE 12  Production Hardening
```

---

# 5. PHASE 0 — REQUIREMENT FREEZE

## Objective

Freeze the contract before implementation becomes complicated.

## Inputs

- business requirements
- production form samples
- real Excel workbook
- existing n8n workflow
- field definitions

## Must define

### Supported input

```text
PDF
JPG
PNG
```

### Form handling

```text
form_id
version
department
reference image
geometry
fields
validation
Excel mapping
```

### OCR acceptance

```text
Character Accuracy
Field Accuracy
Row Accuracy
Page Accuracy
```

### Human review

Define when an item is:

```text
accepted
re-OCR
human review
```

## Output

Stable specification.

## Current status

Mostly defined conceptually.

Workbook details remain subject to verification against the real workbook during Phase 9.

---

# 6. PHASE 1 — RUNTIME + QWEN

## Objective

Make the local AI runtime reliable.

## Tasks

1. create virtual environment
2. verify Python
3. verify PyTorch
4. verify CUDA availability
5. verify GPU name / VRAM
6. load Qwen locally
7. enable 4-bit NF4
8. configure CPU/GPU memory
9. verify inference

## Acceptance

```text
CUDA available = True
Qwen model loads
Qwen generates output
no unexplained dependency failure
```

## Status

DONE for development.

---

# 7. PHASE 2 — INPUT ENGINE

## Objective

Convert user files into deterministic page images.

## Flow

```text
input file
   ↓
detect extension
   ↓
PDF?
 ├── yes → render each page
 └── no  → use image
```

PDF rendering must be deterministic.

Preserve the original file.

## Output example

```text
data/input/T1.pdf

data/pages/
    T1_page_001.png
    T1_page_002.png
    ...
```

## Acceptance

- every PDF page is rendered
- page ordering is preserved
- original file remains unchanged
- image files are readable

## Status

DONE for basic PDF → PNG.

---

# 8. PHASE 3 — IMAGE NORMALIZATION

## Objective

Produce a stable image representation for later CV processing.

## Tasks

- orientation normalization
- page size normalization
- conservative contrast normalization
- preserve original image
- generate preview/contact sheet
- generate preprocessing report

## Current T1 normalized size

```text
3509 × 2481
```

## Output

```text
data/preprocessed/pages/
```

plus:

```text
data/preprocessed/preview/contact_sheet.jpg
data/preprocessed/preprocess_report.json
```

## Important

Do not aggressively sharpen or threshold in a way that destroys handwriting.

## Status

DONE on the current 7-page T1 sample.

---

# 9. PHASE 4 — FORM REGISTRY + CALIBRATION / REGISTRATION

## Objective

This is the current phase.

The phase answers:

> Which versioned form definition should interpret this page, and how should the page be geometrically aligned to that definition?

## Core architecture

```text
page
 ↓
form profile
 ↓
reference image
 ↓
registration
 ↓
aligned page
 ↓
known profile geometry
```

## Why registration instead of independent line detection?

The old approach tried to independently detect every horizontal and vertical table line on every page.

That approach was not robust across all scanned T1 pages.

Observed behavior previously included:

```text
some pages: 21 horizontal + 15 vertical
some pages: 20 horizontal + 15 vertical
some pages: 0 horizontal + 15 vertical
```

Therefore independent line detection must not be the central assumption.

The form version contains known geometry.

Registration should bring each page into the reference coordinate system, then the profile geometry can be applied.

---

## 9.1 Phase 4 directory contract

Preferred form structure:

```text
config/
└── forms/
    ├── registry.json
    └── T1/
        └── v1/
            ├── form.json
            └── reference.png
```

Future:

```text
T1/
├── v1/
└── v2/

QC01/
└── v1/
```

---

## 9.2 `registry.json`

Responsibilities:

- list supported forms
- identify department
- identify version
- point to profile directory

Example:

```json
{
  "registry_version": 1,
  "forms": [
    {
      "form_id": "T1",
      "department": "SanXuat",
      "version": "v1",
      "config_path": "T1/v1"
    }
  ]
}
```

---

## 9.3 `form.json`

The profile may define:

```text
form_id
department
version

page
registration
row_strategy
geometry
fields
ocr
validation
mapping
```

Current T1 baseline:

```text
page:
    width = 3509
    height = 2481
    orientation = landscape

registration:
    reference image
    ROI
    registration method
    quality thresholds
    transform limits

row_strategy:
    fixed
    20 slots
```

---

## 9.4 Reference image

The reference is the coordinate origin for the form version.

Current T1 candidate:

```text
data/preprocessed/pages/T1_page_001.png
```

copied to:

```text
config/forms/T1/v1/reference.png
```

Important:

This is acceptable as an experimental reference.

A clean blank production form is preferable if the company provides one.

A reference page containing different handwriting should not be assumed to be an ideal production reference.

---

## 9.5 Registration problem

Input:

```text
preprocessed page
```

Reference:

```text
reference.png
```

Goal:

```text
find transform M
such that:

input page
    --M-->
reference coordinate system
```

Current initial model:

```text
affine
```

Allowed transform components:

- translation
- rotation
- scale
- shear

---

## 9.6 Registration quality signals

A page is not accepted only because OpenCV returns a matrix.

Required signals include:

```text
correlation
translation X
translation Y
rotation
scale X
scale Y
shear
visual overlay
```

A transform with:

```text
ECC = 0.03
translation = -138, -350
rotation = 6.18°
```

must be rejected even if the algorithm returned a matrix.

---

## 9.7 Phase 4 registration strategy

The current implementation is being strengthened to use:

```text
1. structural feature image
2. ECC with multiple initializations
3. transform-limit validation
4. SIFT/RANSAC fallback when ECC does not converge
5. final visual/report inspection
```

The fallback is not an admission that ECC is invalid.

It is a robustness mechanism for real scans where local optimization can fail.

---

## 9.8 Structural feature image

The registration image should emphasize printed/form geometry rather than handwriting.

Useful components:

```text
grayscale
blur
adaptive threshold
long horizontal structures
long vertical structures
edges
```

Avoid using Qwen or OCR for registration.

---

## 9.9 Multi-start ECC

Instead of:

```text
ECC(identity only)
```

try a small set of reasonable initial transforms:

```text
identity
small translation
small rotation
small translation + rotation
```

Select the candidate that:

1. converges,
2. has acceptable correlation,
3. satisfies transform limits.

This reduces sensitivity to the optimizer starting point.

---

## 9.10 SIFT / RANSAC fallback

When ECC fails to converge:

```text
reference image
      +
input image
      ↓
SIFT keypoints
      ↓
descriptor matching
      ↓
ratio filtering
      ↓
RANSAC affine estimation
      ↓
geometric validation
      ↓
accept / reject
```

The fallback must still be checked against:

```text
translation limits
rotation limits
scale limits
shear limits
inlier count
inlier ratio
structural similarity
```

A fallback transform is never accepted solely because RANSAC produced a matrix.

---

## 9.11 Current T1 Phase 4 result

Previous run:

```text
Page 1   PASS
Page 2   PASS
Page 3   REVIEW
Page 4   REVIEW
Page 5   REVIEW
Page 6   REVIEW
Page 7   PASS
```

Detailed issue:

```text
Page 3–5
ECC did not converge.

Page 6
ECC returned a clearly implausible transform:
    ECC ≈ 0.03
    translation ≈ (-138, -350)
    rotation ≈ 6.18°
    scale_y ≈ 1.068
    shear ≈ 0.054
```

Therefore:

```text
Phase 4 is NOT PASS yet.
```

---

## 9.12 Phase 4 outputs

For every test page:

```text
aligned/<page>.png
overlays/<page>.png
```

Aggregate:

```text
contact_sheet.jpg
registration_report.json
```

Each page result should include:

```text
status
method
correlation
translation
rotation
scale
shear
message
```

---

## 9.13 Phase 4 acceptance criteria

A page is geometrically acceptable when:

```text
image size correct
AND
registration succeeds
AND
quality score acceptable
AND
transform is physically plausible
AND
overlay looks aligned
```

The phase is accepted only when the complete representative test set is acceptable.

For the current T1 checkpoint:

```text
7/7 pages must be reviewed
```

Do not declare Phase 4 PASS merely because the script exits with code 0.

---

# 10. PHASE 5 — GENERIC REGISTRATION + SEGMENTATION

## Objective

Use the verified form geometry to produce reusable row/region/field crops.

## Input

```text
aligned page
+
form profile
```

## Output

```text
rows
regions
fields
```

## Row strategy

For T1/v1:

```text
20 row slots
```

The engine should not hard-code:

```text
T1 = 20
```

It should read:

```text
form.json → row_strategy.count
```

---

## `row_detector.py`

Purpose:

> determine which predefined row slots actually contain handwriting/data.

It does not:

- identify the form
- perform OCR
- create Excel

Its conceptual flow:

```text
form geometry
    ↓
row crop
    ↓
remove/mask printed grid influence
    ↓
measure remaining ink/text occupancy
    ↓
active rows
```

Example:

```text
20 slots
   ↓
[1,2,5,6,7]
```

Only those rows need OCR.

---

## Acceptance

- row boxes come from form profile
- active-row detection does not redefine template geometry
- empty rows are not unnecessarily sent to Qwen
- handwriting is not clipped
- neighboring rows are not mixed

---

# 11. PHASE 6 — QWEN OCR

## Objective

Recognize handwriting from segmented images.

## Preferred flow

```text
row/field crop
   ↓
Qwen
   ↓
raw OCR text
   ↓
Python
   ↓
structured JSON
```

## Qwen should not decide

- Excel formulas
- master-data joins
- final business semantics
- database identities
- field validity

---

## OCR levels

Start with:

```text
row-level OCR
```

Then selectively add:

```text
field-level OCR
```

Do not immediately make dozens of model calls per row.

Only difficult fields should be split further after evidence shows it is necessary.

---

## Raw output retention

Always keep:

```text
*_qwen_raw.txt
```

and structured result:

```text
*_qwen_result.json
```

This is necessary for debugging.

---

# 12. PHASE 7 — VALIDATION + CONFIDENCE

## Objective

Detect OCR results that should be accepted, re-read, or reviewed.

## Validation signals

```text
format validation
field-specific rules
required-field presence
numeric structure
date structure
time structure
cross-field consistency
pass-1/pass-2 agreement
```

## Flow

```text
OCR
 ↓
validation
 ↓
acceptable?
 ├── yes → accept
 └── no
       ↓
    smaller crop
       ↓
      re-OCR
       ↓
    compare
       ↓
 accept or human review
```

Model self-reported confidence is one signal only.

---

# 13. PHASE 8 — GROUND TRUTH + ACCURACY

## Objective

Prove real handwriting accuracy.

## Ground truth

Manually verify representative records.

Directory:

```text
evaluation/
└── ground_truth/
```

## Metrics

### Character Accuracy

Measures character-level correctness.

### Field Accuracy

Measures whether a field is completely correct.

### Row Accuracy

Measures whether the complete row is correct.

### Page Accuracy

Measures whether the page is correctly processed to the agreed standard.

## Acceptance target

```text
~95%
```

The test set must represent:

- different writers
- different pages
- different forms/versions
- difficult handwriting
- codes/numbers
- blank and filled rows

---

# 14. PHASE 9 — EXCEL SHEET 05

## Objective

Map validated data into the actual workbook.

The real workbook is the source of truth.

## Sheet 05 contains fields such as

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

## Important distinction

Not every Excel field comes directly from handwriting.

There are three classes:

### A. Direct OCR fields

Example:

```text
Ngày
Mã đơn hàng
Mã bản vẽ
Rev
Bắt đầu
Kết thúc
SL xử lý
SL đạt
Ghi chú
```

### B. Lookup / normalization fields

May require joining against master sheets such as:

```text
DM_NHAN_SU
DM_MAY
DM_CONG_DOAN
03_DON_HANG_BAN_VE
04_KE_HOACH_CD
```

### C. Derived/formula fields

Should be calculated using deterministic business rules and/or existing workbook formulas.

Do not ask Qwen to generate these.

---

## Mapping warning

A paper field such as:

```text
SL NG
```

must not automatically be mapped to:

```text
SL chờ
```

without confirming the company's actual business meaning.

The real workbook must determine the final mapping.

---

# 15. PHASE 10 — TELEGRAM QC

## Objective

Human confirmation before final output.

Flow:

```text
OCR result
 ↓
Telegram message
 ↓
employee checks
 ↓
correction if needed
 ↓
confirm
 ↓
approved record
```

Corrections should be preserved for traceability.

---

# 16. PHASE 11 — N8N INTEGRATION

## Objective

Integrate the proven local OCR engine into the existing workflow.

Existing workflow:

```text
Telegram
 ↓
n8n
 ↓
download
 ↓
OCR
 ↓
parse/state/callback
```

Preferred change:

```text
existing Telegram + n8n
          ↓
    local OCR service
          ↓
       Qwen OCR
```

Preserve working n8n state/callback/error handling.

Do not expose API keys in source code.

---

# 17. PHASE 12 — PRODUCTION HARDENING

## Objective

Make the system operationally reliable.

Areas:

```text
logging
retry
queue
model lifecycle
resource limits
cleanup
monitoring
security
configuration versioning
deployment
recovery
```

Production must remain within:

```text
RTX 3060 6 GB
32 GB RAM
```

---

# 18. DATA TRACEABILITY

Every final value should be traceable through:

```text
original input
 ↓
rendered page
 ↓
preprocessed page
 ↓
registered page
 ↓
row crop
 ↓
field crop (if used)
 ↓
raw Qwen output
 ↓
structured JSON
 ↓
validated result
 ↓
human correction (if any)
 ↓
Excel cell
```

This is required for debugging and production auditability.

---

# 19. CURRENT PROJECT FILE RESPONSIBILITIES

## `app/`

```text
pdf_processor.py
    PDF → page images

image_preprocess.py
    page normalization

form_registry.py
    form_id + version → form profile

form_template.py
    form geometry / crop utilities

template_registration.py
    registration engine

row_detector.py
    active-row detection

qwen_ocr.py
    Qwen inference wrapper

validator.py
    deterministic validation

mapper.py
    business/data mapping

excel_writer.py
    workbook output

api.py
    service interface
```

## `tests/`

```text
test_template_registration.py
    Phase 4 experiment / acceptance test

test_qwen_4b_row.py
    OCR experiment / benchmark
```

## `config/`

```text
forms/registry.json
forms/<FORM>/<VERSION>/form.json
forms/<FORM>/<VERSION>/reference.png

mapping.json
settings.json
```

---

# 20. WHAT NOT TO DO

Never:

```text
hard-code T1 geometry into generic engines
```

Never:

```text
assume every future form has 20 rows
```

Never:

```text
use JSON validity as OCR accuracy
```

Never:

```text
trust Qwen confidence alone
```

Never:

```text
sacrifice handwriting detail for speed
```

Never:

```text
duplicate Qwen model-loading code across many production files
```

Never:

```text
put the same configuration in multiple files
```

Never:

```text
map business fields merely because two names look similar
```

Never:

```text
expose API keys
```

---

# 21. CURRENT EXECUTION PLAN

Current checkpoint:

```text
PHASE 4
```

Immediate sequence:

```text
1. clean source tree
2. verify T1/v1 profile
3. verify reference.png
4. run improved registration
5. inspect report
6. inspect all aligned overlays
7. tune registration only when evidence requires it
8. test another real document set such as T2
9. freeze registration behavior
10. move to Phase 5
```

---

# 22. PHASE 4 — TASK BREAKDOWN

## Task 4.1 — Registry validation

Must prove:

```text
registry.json
    ↓
T1/v1
    ↓
form.json
    ↓
reference.png
```

PASS when profile resolves correctly.

---

## Task 4.2 — Reference validation

Must prove:

```text
reference size == form page size
```

For T1:

```text
3509 × 2481
```

PASS when reference is readable and visually represents the intended form.

---

## Task 4.3 — Structural registration

Must align each page to reference coordinates.

PASS when a valid transform is produced.

---

## Task 4.4 — Registration robustness

Must handle pages where the first ECC optimization fails.

Strategy:

```text
structural features
      ↓
multi-start ECC
      ↓
RANSAC fallback
```

PASS when difficult pages either:

```text
register correctly
```

or are explicitly rejected for review.

A mathematically returned but physically implausible transform is NOT PASS.

---

## Task 4.5 — Visual acceptance

Inspect:

```text
contact_sheet.jpg
```

and individual overlays.

Printed table geometry should visually coincide with the reference coordinate system.

---

## Task 4.6 — Report acceptance

`registration_report.json` should make it obvious:

```text
which method was used
which page passed
which page failed
why it failed
what transform was found
```

---

## Task 4.7 — Representative-document check

After T1 pages are stable, run the same generic registration engine on a different real document set such as T2.

Important:

```text
T2.pdf
```

is a document instance.

It must not automatically become:

```text
form_id = T2
```

Form identity must come from layout/profile identification.

---

# 23. WHEN PHASE 4 IS CONSIDERED COMPLETE

Phase 4 is complete only when:

```text
registry works
AND
reference works
AND
registration is robust
AND
all representative pages are reviewed
AND
reports are interpretable
AND
overlays are acceptable
AND
geometry can be handed to Phase 5
```

Then the next state is:

```text
PHASE 5 — Generic Segmentation
```

Not Qwen tuning.

Not Excel mapping.

Not n8n integration.

---

# 24. ONE-LINE STATUS

> **Current job: finish Phase 4 by making registration robust and verifiable across real pages, then freeze the aligned coordinate system so Phase 5 can consume it generically.**