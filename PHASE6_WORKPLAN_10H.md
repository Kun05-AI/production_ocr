# Production OCR — PHASE 6 WORKPLAN 10H
## P6.3/P6.4 Segmentation + P6.2 Calibration Follow-up

> **Mục đích:** Đây là workplan cho trạng thái hiện tại của project `D:\production_ocr`.
>
> **Không còn là kế hoạch Phase 2.**
>
> Phase 2 / DEV Ground Truth là một workstream song song còn dang dở; công việc chính của session này là **Phase 6**.

---

# 1. CURRENT PROJECT STATE

## 1.1 Roadmap cố định

Project vẫn theo roadmap:

```text
P0 Requirements
P1 Runtime + Qwen
P2 Ground Truth
P3 Input Engine
P4 Image Normalization
P5 Form Registry + Baseline Registration
P6 Generic Registration + Segmentation
P7 Qwen OCR
P8 Validation + Confidence
P9 Accuracy
P10 Excel
P11 Telegram
P12 n8n
P13 Hardening
```

---

# 2. WHAT IS ALREADY DONE

## P0
Requirements / architecture đã được xác định.

## P1
Runtime + Qwen environment đã được chuẩn bị và kiểm tra.

## P2 — Ground Truth
DEV set đã được chọn cố định:

```text
24 pages
19 coverage
5 challenge
```

Hiện tại:

```text
DEV GT = CHƯA COMPLETE
```

Đã có annotation hoàn chỉnh cho:

```text
1207_T1_p003
```

Các page còn lại vẫn cần annotate.

### Quan trọng

7 page liên tục:

```text
1207/T1/page001
...
1207/T1/page007
```

là **baseline/debug corpus của P5/P6**, không phải DEV GT selection.

Không tự ý thêm 6 page còn lại vào `dev_annotations.jsonl`.

---

## P3 — Input / PDF Rendering

Đã PASS ở baseline hiện tại.

## P4 — Image Normalization

Đã PASS ở baseline hiện tại.

## P5 — Registration

Đã FREEZE cho baseline:

```text
form = T1
version = v1
```

Acceptance đã kiểm tra:

- registry resolves
- reference hợp lệ
- T1/v1 pages align
- transform physically plausible
- page content được giữ nguyên
- không inject reference content
- output review/error tách biệt
- report đọc được

### Không quay lại P5

Chỉ quay lại registration nếu P6 phát hiện lỗi hình ảnh / geometry thực sự.

---

# 3. CURRENT P6 STATUS

## P6.1 — Form Geometry

### STATUS: PASS

`FormTemplate` hiện là canonical source of truth cho geometry.

Nó có:

```text
page_slots
table_bbox
horizontal_lines
vertical_lines
fields
row_bbox()
row_crop()
field_bbox()
field_crop()
```

T1/v1 hiện có:

```text
20 row slots
14 canonical row fields
21 horizontal lines
15 vertical lines
```

Không được hard-code lại các giá trị này trong module mới.

---

## P6.2 — Active Row Detection

### STATUS: OPEN / CANDIDATE

`row_detector.py` đã qua nhiều vòng debug.

Các nguyên nhân chính đã phát hiện:

```text
printed grid
static printed STT
residual registration / line displacement
```

V4 hiện tại dùng hướng:

```text
canonical geometry
    ↓
local search quanh geometry
    ↓
mask residual grid
    ↓
row ink score
```

Kết quả V4 đã cải thiện đáng kể blank-row score.

### Nhưng CHƯA FREEZE

Không được:

- tuyên bố P6.2 PASS
- tự chọn threshold chỉ dựa trên 7 baseline pages
- dùng detector để sinh Ground Truth

Sau khi DEV GT đủ, mới làm:

```text
GT active/blank
        vs
detector prediction
        ↓
calibrate
        ↓
freeze P6.2
```

---

# 4. P6.3 — ROW SEGMENTATION

## STATUS: CHƯA LÀM

Đây là việc chính.

Mục tiêu:

```text
aligned page
    ↓
FormTemplate
    ↓
20 exact row slots
```

Mỗi row phải có:

```text
row_number
bbox
crop
```

### Row geometry rule

PHẢI lấy từ:

```text
FormTemplate.row_bbox()
FormTemplate.row_crop()
```

Không được:

- chia đều lại bằng toán riêng
- hard-code 20
- dùng threshold để thay đổi row geometry
- dùng row detector để redefine bbox

P6.2 chỉ quyết định row nào active.

P6.3 quyết định row nằm ở đâu.

Hai việc này phải tách biệt.

---

# 5. P6.4 — FIELD SEGMENTATION

## STATUS: CHƯA LÀM

Mục tiêu:

```text
row crop
   ↓
14 field crops
```

Field geometry PHẢI lấy từ:

```text
FormTemplate.field_bbox()
FormTemplate.field_crop()
```

Không hard-code x coordinates.

Không tự tính lại vertical lines.

Canonical row fields hiện tại:

```text
stt
date
order_code
drawing_code
revision
work_code
target_time
start_time
end_time
processed_qty
good_qty
ng_qty
process_detail
note
```

Không tự ý thêm field mới trong session này.

---

# 6. HEADER METADATA — TỔ/NHÓM

Mẫu giấy có handwritten header metadata như:

```text
Tổ/Nhóm
Nhân viên
Mã nhân viên
Ngày
Tuần
```

Trong đó:

```text
Tổ/Nhóm = handwritten, có thể thay đổi giữa các page
```

Nhưng nó là:

```text
PAGE-LEVEL / HEADER-LEVEL METADATA
```

không phải một row field trong 20 production rows.

Vì vậy:

```text
KHÔNG thêm Tổ/Nhóm vào rows[*].ground_truth
KHÔNG thay đổi 14 canonical row fields chỉ vì field này tồn tại
```

Header schema sẽ được xử lý riêng sau.

---

# 7. ARCHITECTURE SAU P6.3/P6.4

Mục tiêu architecture:

```text
Aligned page
    ↓
FormTemplate
    ↓
Segmentation
    ├── row 1
    │     ├── stt
    │     ├── date
    │     ├── order_code
    │     ├── ...
    │     └── note
    │
    ├── row 2
    │     ├── ...
    │
    └── row 20
          └── ...

Row detector
    ↓
active row candidates
    ↓
later: only active rows → Qwen
```

Quan trọng:

```text
Segmentation = geometry
Row detector = activity
Qwen = OCR
```

Không trộn trách nhiệm.

---

# 8. FILES DỰ KIẾN

Trước khi tạo file, INSPECT xem project đã có implementation tương đương chưa.

Nếu chưa có:

```text
app/segmentation.py
tests/test_segmentation.py
```

Output crops nếu cần:

```text
data/crops/
```

Không tạo duplicate module nếu đã tồn tại.

Không tạo script test tạm rải rác trong project root.

---

# 9. API DỰ KIẾN

Có thể dùng API kiểu:

```python
segment_page(image_path, template)
```

Nhưng phải inspect coding style hiện tại trước khi chốt signature.

Logical output cần đại diện được:

```python
{
    "image": "...",
    "rows": [
        {
            "row_number": 1,
            "bbox": [x1, y1, x2, y2],
            "fields": {
                "stt": [x1, y1, x2, y2],
                "date": [x1, y1, x2, y2],
                ...
            }
        }
    ]
}
```

Metadata nên serializable.

Không cần nhét PIL Image object trực tiếp vào JSON.

Nếu ghi crop files:

```text
data/crops/<page>/row_001/...
```

hoặc cấu trúc hợp lý do implementation chọn.

---

# 10. TEST TARGET

## Test page đầu tiên

Dùng:

```text
data/preprocessed/registration_debug/aligned/T1_page_003.png
```

với:

```text
config/forms/T1/v1/form.json
```

Expected:

```text
20 row bboxes
14 field bboxes / row
```

Tổng:

```text
20 × 14 = 280 field crops
```

Kiểm tra:

- bbox hợp lệ
- không out-of-bounds
- row order 1 → 20
- field order đúng canonical schema
- không mix neighboring rows
- row geometry đúng profile
- field geometry đúng profile

---

# 11. VISUAL DEBUG

Sau smoke test, nên tạo một số artifact debug có mục đích.

Tối thiểu:

```text
row 1
row 2
row giữa
row 20
```

và các field tiêu biểu:

```text
stt
date
order_code
process_detail
note
```

Có thể tạo contact sheet.

Không tạo hàng loạt artifact nếu không dùng.

---

# 12. BATCH TEST 7 BASELINE T1 PAGES

Sau page003 PASS:

```text
T1_page_001
T1_page_002
T1_page_003
T1_page_004
T1_page_005
T1_page_006
T1_page_007
```

Expected mỗi page:

```text
20 rows
14 fields / row
```

Không active filtering.

Không OCR.

Không Qwen.

---

# 13. GT WORKSTREAM SONG SONG

GT không còn là blocker cho P6.3/P6.4.

Có thể làm song song:

```text
P6.3/P6.4 implementation
        +
DEV GT annotation
```

Khi GT hoàn thành:

```text
24 DEV pages
    ↓
active/blank oracle
    ↓
P6.2 calibration
```

Annotation rules:

```text
active=true
    → row có report data

active=false
    → row blank

visible text
    → chép đúng những gì thấy

blank field
    → null

có nội dung nhưng không đọc chắc chắn
    → [UNK]

không normalize business meaning
không copy giữa rows
không dùng detector để tạo GT
```

---

# 14. 10-HOUR WORKPLAN

## HOUR 1 — INSPECT

### Mục tiêu

Không code ngay.

Đọc:

```text
app/form_template.py
app/row_detector.py
app/form_registry.py
app/template_registration.py
config/forms/T1/v1/form.json
PHASES_DETAILED.md
phase detail.md
PHASE2_GT_DEV_WORKPLAN_10H_UPDATED.md (nếu còn tồn tại)
```

Xác nhận implementation thực tế.

### Deliverable

Một report ngắn:

```text
current state
files relevant
P6.1 status
P6.2 status
P6.3 missing?
P6.4 missing?
```

---

## HOUR 2 — IMPLEMENT P6.3

Tạo:

```text
app/segmentation.py
```

Chỉ làm row segmentation.

### Acceptance

```text
page003
20/20 row bboxes valid
```

---

## HOUR 3 — TEST P6.3

Tạo:

```text
tests/test_segmentation.py
```

Test:

```text
row count
bbox validity
row order
geometry consistency
```

Run test.

---

## HOUR 4 — IMPLEMENT P6.4

Thêm field segmentation.

Expected:

```text
20 rows × 14 fields
```

Không OCR.

---

## HOUR 5 — TEST P6.4

Page003:

```text
280 field bboxes valid
```

Kiểm tra field order.

---

## HOUR 6 — VISUAL DEBUG

Tạo artifact debug có mục đích.

Kiểm tra:

```text
row1
row2
row10
row20

stt
date
order_code
process_detail
note
```

Nếu có visual issue:

```text
STOP
→ report exact row/field
→ do not silently alter geometry
```

---

## HOUR 7 — BATCH 7 T1 PAGES

Chạy:

```text
page001 → page007
```

Expected:

```text
7 × 20 rows
7 × 20 × 14 fields
```

Report lỗi theo page/row/field nếu có.

---

## HOUR 8 — P6.2 DIAGNOSTIC

Có thể chạy V4 như candidate.

Không freeze.

Tạo diagnostic:

```text
page
row
score
candidate active
```

Nếu chưa chắc:

```text
CANDIDATE
```

---

## HOUR 9 — DEV GT SONG SONG

Nếu còn thời gian:

- annotate DEV GT
- bắt đầu / tiếp tục 24-page set
- không dùng detector để điền active

Nếu không đủ thời gian:

```text
leave GT incomplete
```

Không tự điền.

---

## HOUR 10 — REGRESSION + REPORT

Chạy:

```text
py_compile
pytest relevant tests
page003 smoke
7-page batch
```

Sau đó ghi:

```text
SESSION REPORT
```

---

# 15. ACCEPTANCE CRITERIA

## P6.3 PASS khi:

- segmentation module tồn tại
- FormTemplate là source of truth
- không hard-code 20
- 20/20 row bboxes valid
- row order deterministic
- no row mixing
- no out-of-bounds
- tests PASS

## P6.4 PASS khi:

- 14 fields / row
- field order canonical
- field bbox valid
- 280/280 field bboxes valid trên page003
- 7-page batch PASS
- tests PASS

## P6.2

Vẫn:

```text
OPEN / CANDIDATE
```

cho đến khi có GT comparison.

---

# 16. KHÔNG LÀM TRONG SESSION NÀY

Không:

```text
- sửa form.json nếu chưa có evidence
- sửa reference.png
- đổi registration algorithm
- mở rộng sang T2/T3/T4
- chạy Qwen accuracy benchmark
- làm Excel
- làm Telegram
- làm n8n
- thêm Tổ/Nhóm vào row schema
- dùng detector để sinh GT
- hard-code geometry vào segmentation
- xóa artifact cũ tùy tiện
- tạo script tạm rải rác ở root
```

---

# 17. SESSION END REPORT

Cuối session bắt buộc ghi:

## Done

- files created/modified
- tests run
- test result
- artifacts created

## Not done

- P6.2
- GT
- bất kỳ task nào còn lại

## P6 status

```text
P6.1 = PASS
P6.2 = OPEN / CANDIDATE
P6.3 = PASS / FAIL
P6.4 = PASS / FAIL
```

## Evidence

Ví dụ:

```text
page003:
20/20 row bboxes valid
280/280 field bboxes valid

7-page batch:
7/7 pages passed geometry checks
```

## Risks / Issues

Mỗi issue phải ghi:

```text
file
location
problem
impact
```

## Next action

Phải viết task cụ thể.

Không viết:

```text
"continue improving segmentation"
```

Mà viết:

```text
"review row 17 field process_detail bbox on T1_page_004"
```

---

# 18. MỤC TIÊU CUỐI CÙNG CỦA BUỔI 10 TIẾNG

Buổi này không cần đóng toàn bộ P6.

Mục tiêu đủ tốt là:

```text
P6.1  PASS
P6.2  OPEN / CANDIDATE
P6.3  PASS
P6.4  PASS
```

và có:

```text
deterministic geometry segmentation
20 rows
14 fields / row
testable
batch-tested trên 7 baseline T1 pages
```

DEV GT tiếp tục song song và sẽ được dùng để calibrate P6.2 sau.

---

# 19. START HERE

Thứ tự bắt buộc khi bắt đầu session:

```text
1. Inspect project tree
2. Read current code
3. Read P6 spec
4. Confirm P6.3/P6.4 do not already exist
5. Implement row segmentation
6. Test page003
7. Implement field segmentation
8. Test page003
9. Batch 7 pages
10. Report
```

**Không code trước bước 1–4.**

---

# 20. ONE-LINE SESSION GOAL

> **Tách geometry segmentation khỏi active-row detection và hoàn thành một segmentation layer deterministic, testable cho T1/v1: 20 rows × 14 fields, không phụ thuộc Ground Truth và không phụ thuộc Qwen.**
