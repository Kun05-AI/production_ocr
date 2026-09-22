# PRODUCTION OCR — PHASE DETAIL

## Version 3 — Baseline-first execution specification

> Roadmap thực thi mới sau khi điều chỉnh.
>
> Hai thay đổi chính:
> 1. Registration chỉ làm **baseline cho T1/v1**, chưa cố biến thành universal registration engine. Chỉ mở rộng/tune khi có form mới hoặc failure mode thực tế.
> 2. **Ground Truth đưa lên Phase 2** để bộ dữ liệu chuẩn tồn tại trước khi tối ưu OCR và trước khi đo accuracy.

---

# 0. PROJECT GOAL

Xây dựng hệ thống OCR chữ viết tay cho các biểu mẫu báo cáo sản xuất được scan.

### Supported input

```text
PDF
JPG
PNG
```

### Target end-to-end flow

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
baseline template registration
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

### Accuracy target

```text
~95%
```

Đo ở:

```text
1. Character Accuracy
2. Field Accuracy
3. Row Accuracy
4. Page Accuracy
```

JSON hợp lệ không được coi là bằng chứng OCR chính xác.

---

# 1. ARCHITECTURAL PRINCIPLES

## 1.1 Configuration-driven forms

Không hard-code một form vào generic engine.

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

Một form revision nên trở thành version mới:

```text
T1/v1
T1/v2
```

### Khái niệm quan trọng

```text
T1/v1 = FORM PROFILE / FORM DEFINITION
```

Không phải một file PDF duy nhất.

Một `T1/v1` có thể áp dụng cho nhiều **document instances**.

Ví dụ mỗi thành viên có 4 PDF:

```text
Member A
    ├── PDF 1
    ├── PDF 2
    ├── PDF 3
    └── PDF 4

Member B
    ├── PDF 1
    ├── PDF 2
    ├── PDF 3
    └── PDF 4

...
```

Vì vậy test và Ground Truth không được chỉ dùng một PDF của một thành viên để đại diện toàn bộ hệ thống.

## 1.2 Qwen là OCR/vision component

Qwen chủ yếu:

```text
see image
    ↓
read handwriting / visible text
    ↓
return raw OCR content
```

Python chịu trách nhiệm:

```text
JSON structuring
field mapping
validation
confidence/review routing
retry/re-OCR
form selection
coordinates
business lookup
Excel generation
```

Không giao deterministic business logic cho Qwen.

## 1.3 Accuracy over speed

Không giảm image detail chỉ để tăng throughput.

Chỉ tối ưu tốc độ sau khi recognition quality đã được hiểu, acceptance criteria đạt và production behavior ổn định.

## 1.4 Experiment → measure → freeze

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
move proven logic into production
```

Experiment không được làm production module phình lên không kiểm soát.

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

## Production

```text
CPU         Intel Core i7-14700K
RAM         32 GB DDR5
GPU         NVIDIA RTX 3060 6 GB
OS          Windows 11
```

Production Qwen target:

```text
GPU_MEMORY = "5GiB"
CPU_MEMORY = "24GiB"
```

---

# 3. MODEL BASELINE

```text
Qwen/Qwen3-VL-4B-Instruct
```

Local model:

```text
D:\production_ocr\models\Qwen3-VL-4B-Instruct
```

Quantization:

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
```

Runtime baseline hiện tại đã load/infer được.

---

# 4. PHASE MAP

```text
PHASE 0   Requirement Freeze
    ↓
PHASE 1   Runtime + Qwen
    ↓
PHASE 2   Ground Truth Dataset
    ↓
PHASE 3   Input Engine
    ↓
PHASE 4   Image Normalization
    ↓
PHASE 5   Form Registry + Baseline Registration
    ↓
PHASE 6   Generic Registration + Segmentation
    ↓
PHASE 7   Qwen OCR
    ↓
PHASE 8   Validation + Confidence
    ↓
PHASE 9   Accuracy Evaluation
    ↓
PHASE 10  Excel Sheet 05
    ↓
PHASE 11  Telegram QC
    ↓
PHASE 12  n8n Integration
    ↓
PHASE 13  Production Hardening
```

---

# 5. PHASE 0 — REQUIREMENT FREEZE

## Objective

Đóng contract nghiệp vụ và kỹ thuật trước khi implementation trở nên phức tạp.

## Inputs

```text
business requirements
production form samples
real Excel workbook
existing n8n workflow
field definitions
```

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

### Human review states

```text
accepted
re-OCR
human review
```

## Output

```text
stable specification
```

## Current status

**MOSTLY DEFINED CONCEPTUALLY**

Workbook/business details vẫn phải verify với workbook thực tế.

---

# 6. PHASE 1 — RUNTIME + QWEN

## Objective

Làm local AI runtime đáng tin cậy.

## Tasks

```text
create virtual environment
verify Python
verify PyTorch
verify CUDA
verify GPU / VRAM
load Qwen locally
enable 4-bit NF4
configure CPU/GPU memory
verify inference
```

## Acceptance

```text
CUDA available = True
Qwen loads
Qwen generates output
no unexplained dependency failure
```

## Current status

**DONE FOR DEVELOPMENT**

---

# 7. PHASE 2 — GROUND TRUTH DATASET

## Objective

Xây bộ dữ liệu chuẩn do con người xác nhận trước khi bước sâu vào OCR.

Ground Truth là:

```text
original image/document
        +
human verified transcription
```

## Vì sao Ground Truth đưa lên Phase 2?

Ground Truth phải tồn tại trước để:

```text
OCR experiment
      ↓
prediction
      ↓
compare against ground truth
      ↓
measure actual error
```

Không chờ tới cuối dự án mới tạo bộ đối chuẩn.

## Dataset phải đại diện cho

```text
nhiều thành viên / writers
nhiều file PDF trên mỗi thành viên
nhiều page
nhiều handwriting styles
numbers
technical codes
difficult handwriting
blank rows
filled rows
```

Không dùng một PDF của một thành viên để đại diện cho toàn bộ hệ thống.

## Directory

```text
evaluation/
├── ground_truth/
├── predictions/
└── reports/
```

Trong Phase 2:

```text
ground_truth/      ← xây và verify
predictions/      ← chưa cần prediction hoàn chỉnh
reports/          ← chưa cần accuracy report cuối
```

## Ground Truth record

Mỗi record phải có khả năng trace về nguồn:

```text
sample_id
member/document identifier
page
row
field (nếu có)
ground_truth value
source image reference
```

Schema cụ thể có thể khóa sau khi thống nhất với prediction schema.

## Acceptance

```text
ground truth manually verified
representative coverage achieved
schema stable
source traceability preserved
```

## Current status

**CHƯA HOÀN THÀNH**

Đây là phase cần làm trước.

---

# 8. PHASE 3 — INPUT ENGINE

## Objective

Chuyển user file thành page images deterministic.

## Flow

```text
input file
   ↓
detect extension
   ↓
PDF?
 ├── yes → render every page
 └── no  → use image
```

## Output

```text
data/input/

data/pages/
    T1_page_001.png
    T1_page_002.png
    ...
```

## Acceptance

```text
every PDF page is rendered
page ordering preserved
original file unchanged
images readable
```

## Current status

**DONE FOR BASIC PDF → PNG**

---

# 9. PHASE 4 — IMAGE NORMALIZATION

## Objective

Tạo representation ổn định cho Computer Vision.

## Tasks

```text
orientation normalization
page size normalization
conservative contrast normalization
preserve original
preview/contact sheet
preprocess report
```

## T1 baseline hiện tại

```text
3509 × 2481
```

## Output

```text
data/preprocessed/pages/

data/preprocessed/preview/contact_sheet.jpg

data/preprocessed/preprocess_report.json
```

## Important

Không sharpen hoặc threshold quá mạnh đến mức làm mất handwriting.

## Current status

**DONE trên bộ T1 7-page sample**

---

# 10. PHASE 5 — FORM REGISTRY + BASELINE REGISTRATION

## Objective

Đảm bảo `T1/v1` có profile ổn định và page scan được đưa về cùng coordinate system ở mức baseline.

### Tư duy

Không xây universal registration engine ở phase này.

Mục tiêu trước mắt:

```text
T1/v1
+
real document pages
+
known reference
    ↓
reliable baseline alignment
```

Khi có form mới hoặc failure mode mới:

```text
T2/v1
T1/v2
QC01/v1
new scan condition
    ↓
mở rộng / tune registration
```

## 10.1 Registry

```text
config/forms/registry.json
        ↓
T1/v1
        ↓
config/forms/T1/v1/form.json
        ↓
reference.png
```

## 10.2 Baseline registration

```text
preprocessed page
        ↓
T1/v1 profile
        ↓
reference
        ↓
ROI
        ↓
affine registration
        ↓
aligned page
```

Theo dõi:

```text
translation
rotation
scale
shear
quality
visual overlay
```

## 10.3 Không biến baseline thành hệ quá phức tạp

Chưa cần coi các yêu cầu sau là acceptance burden:

```text
universal registration
automatic ROI discovery
automatic geometry discovery
nhiều lớp fallback phức tạp
xử lý mọi loại scan distortion
support mọi loại form
```

Có thể giữ fallback trong code, nhưng baseline acceptance phải rõ ràng và dễ debug.

## 10.4 Reference image

Reference lý tưởng:

```text
clean blank production form
```

Reference T1/v1 hiện tại bắt nguồn từ một page có dữ liệu/handwriting, nên chỉ coi là:

```text
experimental reference
```

Nếu công ty cung cấp blank form, nên thay reference trước khi freeze production behavior.

## 10.5 Registration output integrity

Registration chỉ được phép biến đổi hình học.

Nó **không được copy pixel/content từ reference vào input page**.

Phải giữ:

```text
input page A
    ↓ geometric transform only
aligned page A

input page B
    ↓ geometric transform only
aligned page B
```

Không xảy ra:

```text
page A data
    ↓
page B output
```

Nếu output có biểu hiện dữ liệu của reference/page 1 xuất hiện trên page khác, đó là **registration/output pipeline bug** và phải reopen Phase 5.

## 10.6 Review output

Không được coi file trong `aligned/` là valid accepted alignment nếu registration status là `REVIEW`.

Phải phân biệt:

```text
PASS    → accepted aligned artifact
REVIEW  → diagnostic/review artifact
```

## 10.7 Current known result

Một lần chạy multi-start trước đó cho:

```text
7/7 PASS
0/7 REVIEW
0/7 ERROR
```

Nhưng sau khi kiểm tra lại output bằng mắt đã xuất hiện nghi vấn:

```text
some pages still visually misaligned
reference/page-1 content appears to propagate into later output
```

Do đó Phase 5 được xem là:

```text
REOPENED / NOT FROZEN
```

## 10.8 Acceptance

```text
registry resolves correctly
reference is valid
T1/v1 pages align visually
transform is physically plausible
each output preserves its own page content
no reference content is injected
review/error outputs are clearly separated
report is interpretable
```

## Current status

**BASELINE REGISTRATION CẦN KIỂM TRA LẠI TRƯỚC KHI FREEZE**

---

# 11. PHASE 6 — GENERIC REGISTRATION + SEGMENTATION

## Objective

Dùng geometry đã verified để tạo reusable row / region / field crops.

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

## T1/v1

```text
20 row slots
```

Nhưng engine phải đọc:

```text
form.json
    ↓
row_strategy.count
```

Không hard-code:

```text
T1 = 20
```

## row_detector.py

Nhiệm vụ:

```text
form geometry
    ↓
row crop
    ↓
mask/remove printed grid influence
    ↓
measure ink/text occupancy
    ↓
active rows
```

Không làm:

```text
form identification
OCR
Excel generation
```

## Acceptance

```text
row boxes come from form profile
empty rows are skipped
handwriting is not clipped
neighboring rows are not mixed
```

## Current status

**CHƯA LÀM**

---

# 12. PHASE 7 — QWEN OCR

## Objective

Nhận diện handwriting từ segmented images.

## Preferred flow

```text
row / field crop
    ↓
Qwen3-VL-4B
    ↓
raw OCR text
    ↓
Python
    ↓
structured JSON
```

## OCR levels

Bắt đầu:

```text
row-level OCR
```

Sau đó selective:

```text
field-level OCR
```

chỉ khi evidence cho thấy cần.

Không lập tức tạo quá nhiều model calls.

## Qwen không quyết định

```text
Excel formulas
master-data joins
business identity
final business semantics
field validity
```

## Raw outputs

Luôn giữ:

```text
*_qwen_raw.txt
*_qwen_result.json
```

## Current status

**CHƯA HOÀN THÀNH**

---

# 13. PHASE 8 — VALIDATION + CONFIDENCE

## Objective

Phân loại OCR result:

```text
accept
re-OCR
human review
```

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
accept / human review
```

Model self-reported confidence chỉ là một signal.

## Current status

**CHƯA HOÀN THÀNH**

---

# 14. PHASE 9 — ACCURACY EVALUATION

## Objective

Chứng minh accuracy thực tế bằng Ground Truth đã tạo từ Phase 2.

## Metrics

```text
Character Accuracy
Field Accuracy
Row Accuracy
Page Accuracy
```

Target:

```text
~95%
```

## Flow

```text
ground_truth/
      +
predictions/
      ↓
comparison
      ↓
metrics
      ↓
reports/
```

## Dataset coverage

```text
different writers
different documents
different pages
difficult handwriting
numbers / codes
blank / filled rows
```

## Important

Phase 2:

```text
create + verify Ground Truth
```

Phase 9:

```text
run predictions + compute accuracy
```

## Current status

**CHƯA HOÀN THÀNH**

---

# 15. PHASE 10 — EXCEL SHEET 05

## Objective

Map validated data vào workbook thật.

Real workbook là source of truth.

## Three field classes

### A. Direct OCR fields

Ví dụ:

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

### B. Lookup / normalization

Ví dụ:

```text
DM_NHAN_SU
DM_MAY
DM_CONG_DOAN
03_DON_HANG_BAN_VE
04_KE_HOACH_CD
```

### C. Derived / formula

Được tính bằng deterministic business rules hoặc workbook formula.

Không yêu cầu Qwen tự sinh.

## Mapping warning

Không map field chỉ vì tên nhìn giống nhau.

Ví dụ:

```text
SL NG
```

không được tự động coi là:

```text
SL chờ
```

nếu business meaning chưa được xác nhận.

## Current status

**CHƯA HOÀN THÀNH**

---

# 16. PHASE 11 — TELEGRAM QC

## Objective

Cho con người xác nhận trước khi final output.

```text
OCR result
 ↓
Telegram
 ↓
employee checks
 ↓
correction
 ↓
confirm
 ↓
approved record
```

Corrections phải được lưu để traceability.

## Current status

**CHƯA HOÀN THÀNH**

---

# 17. PHASE 12 — N8N INTEGRATION

## Objective

Đưa OCR engine đã được chứng minh vào workflow n8n hiện tại.

## Preferred flow

```text
Telegram
 ↓
n8n
 ↓
download
 ↓
local OCR service
 ↓
Qwen
 ↓
parse / state / callback
```

Giữ working state/callback/error handling.

Không expose API keys.

## Current status

**CHƯA HOÀN THÀNH**

---

# 18. PHASE 13 — PRODUCTION HARDENING

## Objective

Biến validated pipeline thành service vận hành ổn định.

## Areas

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

Production baseline:

```text
RTX 3060 6 GB
32 GB RAM
```

## Current status

**CHƯA HOÀN THÀNH**

---

# 19. DATA TRACEABILITY

Requirement xuyên suốt:

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
human correction
    ↓
Excel cell
```

Mọi final value phải có khả năng truy ngược về source image / OCR output / validation.

---

# 20. CURRENT PROJECT STRUCTURE

```text
D:\production_ocr\

├── .venv\
│
├── app\
│   ├── __init__.py
│   ├── api.py
│   ├── excel_writer.py
│   ├── form_registry.py
│   ├── form_template.py
│   ├── image_preprocess.py
│   ├── mapper.py
│   ├── pdf_processor.py
│   ├── qwen_ocr.py
│   ├── row_detector.py
│   ├── template_registration.py
│   └── validator.py
│
├── tests\
│   ├── __init__.py
│   ├── test_template_registration.py
│   └── test_qwen_4b_row.py
│
├── config\
│   ├── mapping.json
│   ├── settings.json
│   └── forms\
│       ├── registry.json
│       └── T1\
│           └── v1\
│               ├── form.json
│               ├── reference.png
│               └── REFERENCE_IMAGE_REQUIRED.txt
│
├── data\
│   ├── input\
│   │   └── T1.pdf
│   ├── pages\
│   ├── preprocessed\
│   │   ├── pages\
│   │   ├── preview\
│   │   ├── preprocess_report.json
│   │   ├── registration_debug\
│   │   │   ├── aligned\
│   │   │   ├── overlays\
│   │   │   ├── contact_sheet.jpg
│   │   │   └── registration_report.json
│   │   └── template_debug\
│   ├── crops\
│   ├── ocr\
│   ├── output\
│   ├── reviewed\
│   └── validated\
│
├── evaluation\
│   ├── README.md
│   ├── ground_truth\
│   ├── predictions\
│   └── reports\
│
├── gcck\
│   ├── BAO CAO\
│   │   ├── 1207. NGUYEN TRUONG NHAN\
│   │   ├── 1236. BUI MINH HOANG\
│   │   ├── 1263. NGUYEN HUU THUONG\
│   │   ├── 1570. THACH SANG DO\
│   │   └── 1575. DAO DUC THINH\
│   └── GCCK_Production_QCD_Master_V2.0.0.xlsx
│
├── models\
│   └── Qwen3-VL-4B-Instruct\
│
├── scripts\
│   ├── check_runtime.py
│   └── download_model.ps1
│
├── Lí thuyết readme\
│   ├── readme1.md
│   └── readme2.md
│
├── logs\
├── prompts\
│
├── N8N_INTEGRATION.md
├── PHASES_DETAILED.md
├── production_ocr_PROJECT_CONTEXT_README(file dùng để promt tiếp).md
├── requirements.txt
├── SETUP_HOME_WINDOWS.md
└── WF04_01_CoCongNo.json
```

---

# 21. CURRENT IMPLEMENTATION STATUS

## Completed / substantially completed

```text
Phase 0
    mostly defined conceptually

Phase 1
    DONE for development

Phase 3
    DONE for basic PDF → PNG

Phase 4
    DONE on current T1 7-page normalization sample

Phase 5
    baseline implementation exists
    BUT NOT FROZEN
    visual/output integrity must be re-verified
```

## Not completed

```text
Phase 2   Ground Truth Dataset
Phase 6   Generic Registration + Segmentation
Phase 7   Qwen OCR
Phase 8   Validation + Confidence
Phase 9   Accuracy Evaluation
Phase 10  Excel
Phase 11  Telegram QC
Phase 12  n8n
Phase 13  Production Hardening
```

---

# 22. CURRENT PROJECT-SPECIFIC CONTEXT

## T1/v1 is a form profile, not one PDF

The project has multiple members and each member can have four PDF files.

Therefore:

```text
T1/v1
```

must be understood as:

```text
versioned form definition
```

while:

```text
member + PDF
```

is a document instance.

Testing, Ground Truth and Accuracy must eventually cover document instances across members.

---

# 23. CURRENT REGISTRATION ISSUE

Một lần chạy multi-start cho:

```text
PASS   7 / 7
REVIEW 0 / 7
ERROR  0 / 7
```

Tuy nhiên sau đó kiểm tra output bằng mắt cho thấy vẫn có nghi vấn ở một số page, đặc biệt các page từng gặp vấn đề như 003, 005, 006.

Có thêm nghi vấn rằng output ở page sau dường như xuất hiện dữ liệu của reference/page 1.

Vì vậy:

```text
numerical 7/7 PASS
```

chưa được coi là final proof.

Cần kiểm tra trước khi freeze:

```text
1. each output contains its own source-page content
2. no reference pixels/content are injected
3. table geometry is actually aligned
4. accepted alignment is visually correct
5. REVIEW output is not mislabeled as accepted aligned output
```

Đây là **registration/output-integrity investigation**, không phải lý do để tiếp tục làm registration ngày càng phức tạp mà không có evidence.

---

# 24. CURRENT EXECUTION PLAN

## Bước 1 — Làm Phase 2 trước

Xây và verify Ground Truth trên nhiều member/document/page/row đại diện.

Không tạo Ground Truth từ một member duy nhất.

## Bước 2 — Giữ Phase 3 và Phase 4 hiện có

Input Engine và Image Normalization đã có baseline.

Không rewrite nếu không có evidence.

## Bước 3 — Reopen registration

Theo numbering mới, registration là **Phase 5**.

Sau Phase 2:

```text
Phase 2
   ↓
Phase 3/4 đã có baseline
   ↓
Phase 5 registration re-verification
```

Mục tiêu không phải làm thuật toán phức tạp hơn mà là chứng minh:

```text
current aligned outputs are truly correct
```

đặc biệt với page 003, 005, 006 và nghi vấn reference-content propagation.

## Bước 4 — Chỉ sau khi Phase 5 thực sự frozen

Chuyển sang:

```text
Phase 6 — Generic Registration + Segmentation
```

Sau đó:

```text
Phase 7 — Qwen OCR
```

---

# 25. ONE-LINE PROJECT STATUS

> **Current job: build the Ground Truth dataset first, then reopen and verify the T1/v1 baseline registration before freezing the coordinate system; after that, proceed to generic segmentation and only then deepen Qwen OCR.**
