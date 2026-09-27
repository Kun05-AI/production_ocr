# PROMPT CHO AI AGENT — PRODUCTION OCR — LÀM VIỆC NGÀY MAI

Bạn đang tiếp quản dự án Windows local:

D:\production_ocr

Đây là một project Production OCR cho biểu mẫu báo cáo sản xuất viết tay tiếng Việt.

## 0. VAI TRÒ VÀ NGUYÊN TẮC LÀM VIỆC

Bạn là coding agent kỹ thuật. Mục tiêu của session ngày mai là TIẾP TỤC IMPLEMENT PHASE 6 của project, không phải thiết kế lại toàn bộ hệ thống.

QUY TẮC BẮT BUỘC:

1. INSPECT FIRST, MODIFY SECOND.
   - Không được giả định code hiện tại giống mô tả trong prompt.
   - Trước khi sửa bất kỳ file nào, phải inspect cây thư mục và đọc code thực tế liên quan.
   - Ưu tiên đọc:
     - app/form_template.py
     - app/row_detector.py
     - app/form_registry.py
     - app/template_registration.py
     - config/forms/T1/v1/form.json
     - evaluation/ground_truth/selection/dev_annotations.jsonl
     - PHASES_DETAILED.md
     - phase detail.md
     - PHASE2_GT_DEV_WORKPLAN_10H_UPDATED.md
   - Nếu code thực tế khác prompt, code thực tế + spec là source of truth.

2. KHÔNG tự ý refactor lớn.
   - Không đổi kiến trúc P0–P13.
   - Không sửa P5 registration nếu không có bằng chứng registration đang sai.
   - Không mở rộng sang form khác.
   - Không chạy OCR Qwen để "thử cho vui".
   - Không chuyển sang Excel/Telegram/n8n.

3. Mỗi thay đổi phải có test hoặc smoke test tương ứng.

4. Không tuyên bố PASS nếu chưa có bằng chứng.
   - Phân biệt rõ PASS / FAIL / CANDIDATE / BLOCKED.
   - Nếu chưa có Ground Truth thì không được nói active-row detector đã chính xác.

5. Không đoán dữ liệu nghiệp vụ.
   - Ground Truth phải là human-confirmed.
   - Không dùng detector để tự tạo Ground Truth.

6. Nếu có ambiguity hoặc conflict:
   - STOP tại điểm conflict.
   - Nêu file, dòng/chức năng, conflict là gì.
   - Đề xuất cách xử lý rồi chờ quyết định thay vì tự phá schema.

--------------------------------------------------
## 1. TRẠNG THÁI PROJECT HIỆN TẠI

### P0–P4
Đã hoàn thành ở mức hiện tại.

### P5 — Form Registry + Baseline Registration
Đã hoàn thành và FREEZE cho baseline hiện tại T1/v1.

Acceptance hiện tại của P5:
- registry resolves correctly
- reference valid
- T1/v1 pages visually align
- transform physically plausible
- page content preserved
- no reference content injection
- review/error outputs separated
- report interpretable

KHÔNG quay lại sửa registration trừ khi phát hiện lỗi hình ảnh/geometry thực sự ảnh hưởng P6.

### P2 — Ground Truth
ĐÃ có bộ DEV cố định 24 page:
- 19 coverage pages
- 5 challenge pages

Hiện tại mới có annotation đầy đủ cho ít nhất:
- sample_id = 1207_T1_p003

23 page còn lại chưa hoàn tất annotation.

QUAN TRỌNG:
- 7 page liên tục của 1207/T1 (page 1..7) đang được dùng như BASELINE/DEBUG CORPUS cho P5/P6.
- 7 page này KHÔNG được tự ý thêm vào dev_annotations.jsonl.
- DEV GT vẫn là bộ 24 page cố định.
- GT chưa phải blocker để implement P6.3/P6.4.

### Header metadata
Mẫu giấy có thông tin handwritten ở header như:
- Tổ/Nhóm
- Nhân viên
- Mã nhân viên
- Ngày
- Tuần

"Tổ/Nhóm" là handwritten metadata cấp page/header, KHÔNG phải row field.
Không nhét Tổ/Nhóm vào rows[*].ground_truth.
Không tự thay đổi canonical 14 row fields chỉ vì phát hiện header metadata này.
Header-level schema sẽ xử lý riêng về sau.

### Canonical row fields hiện tại
Dùng schema thực tế của project.
Hiện tại row fields gồm:
- stt
- date
- order_code
- drawing_code
- revision
- work_code
- target_time
- start_time
- end_time
- processed_qty
- good_qty
- ng_qty
- process_detail
- note

KHÔNG tự thêm field mới.

--------------------------------------------------
## 2. P6 — MỤC TIÊU SESSION NGÀY MAI

Mục tiêu chính:

### P6.1
Đã PASS.

### P6.2 — Active Row Detection
ĐANG OPEN / CANDIDATE.

Current `row_detector.py` đã được thử nhiều vòng.
Hiện tại candidate mới nhất là hướng geometry-aware masking (V4).

Quan sát đã có trên 7 baseline T1 pages:
- detector cũ đánh dấu 20/20 rows.
- nguyên nhân chính đã được xác định là printed grid/static content bị tính như ink.
- đã loại STT khỏi activity scoring.
- V4 dùng profile-anchored local search quanh known geometry để mask grid residual.
- V4 đã làm blank-row score giảm đáng kể.
- Nhưng threshold/active criterion CHƯA được freeze vì chưa có đủ DEV GT oracle.

DO NOT:
- không tuyên bố P6.2 PASS.
- không hard-code threshold mới chỉ dựa trên 7 debug pages.
- không tự dùng detector để sửa Ground Truth.

### P6.3/P6.4 — PHẦN CHÍNH CẦN LÀM NGÀY MAI

Implement segmentation thuần geometry:

aligned page
    ↓
FormTemplate
    ↓
20 row slots
    ↓
mỗi row
    ↓
14 field crops

Mục tiêu:
- crop row theo geometry profile
- crop field theo geometry profile
- không tự suy diễn tọa độ
- không làm form identification
- không OCR
- không Excel
- không active-row decision trong segmentation core

--------------------------------------------------
## 3. VIỆC PHẢI LÀM TRƯỚC KHI CODE

### Step 1 — Inspect tree

Chạy/đọc cây thư mục hiện tại.

Xác nhận:
- app/
- config/forms/T1/v1/
- data/preprocessed/registration_debug/aligned/
- data/crops/
- tests/
- evaluation/ground_truth/selection/

Không assume file đã tồn tại chỉ vì prompt nói.

### Step 2 — Read implementation

Đọc đầy đủ:
- app/form_template.py
- app/row_detector.py
- config/forms/T1/v1/form.json

Đặc biệt xác nhận:
- `FormTemplate.page_slots`
- `FormTemplate.table_bbox`
- `FormTemplate.horizontal_lines`
- `FormTemplate.vertical_lines`
- `FormTemplate.fields`
- `FormTemplate.row_bbox()`
- `FormTemplate.row_crop()`
- `FormTemplate.field_bbox()`
- `FormTemplate.field_crop()`

### Step 3 — Read P6 spec

Đọc P6 trong:
- PHASES_DETAILED.md
- phase detail.md

Không tự định nghĩa acceptance khác spec.

--------------------------------------------------
## 4. IMPLEMENT P6.3/P6.4

### File dự kiến

Nếu inspect xác nhận chưa có module tương đương:

Tạo:

D:\production_ocr\app\segmentation.py

Và test:

D:\production_ocr\tests\test_segmentation.py

Không tạo duplicate module nếu project đã có module tương đương.

### API mục tiêu

Thiết kế API đơn giản, deterministic, ví dụ:

segment_page(image_path, template)

Nhưng phải inspect style code hiện tại trước khi chốt signature.

Kết quả logic phải đại diện được:

{
  page / image metadata,
  rows: [
    {
      row_number: 1,
      bbox: (...),
      fields: {
        "stt": ...,
        "date": ...,
        "order_code": ...,
        ...
        "note": ...
      }
    }
  ]
}

LƯU Ý:
- Trong production artifact, không nhất thiết nhét PIL Image object trực tiếp vào JSON.
- Tách metadata/bbox khỏi việc ghi image file.
- Nếu cần lưu crops, dùng data/crops/.
- API phải rõ ràng và dễ test.

### Geometry rule

Row geometry PHẢI lấy từ FormTemplate.

Không:
- chia đều lại bằng toán riêng
- hard-code 20
- tự tính header_fraction
- đọc tọa độ từ ảnh bằng detector để redefine row geometry

Field geometry PHẢI lấy từ FormTemplate.

Không:
- hard-code x coordinates
- tự tính lại vertical lines
- thay đổi field order

--------------------------------------------------
## 5. SMOKE TEST BẮT BUỘC

Test đầu tiên trên:

D:\production_ocr\data\preprocessed\registration_debug\aligned\T1_page_003.png

Dùng:

config/forms/T1/v1/form.json

Expected:

- page size đúng profile
- 20 row slots
- mỗi row có bbox hợp lệ
- mỗi row có đủ 14 field crops
- field order khớp canonical fields
- không mix row
- row boundary đúng geometry profile

In ra report dạng:

========================================================
P6.3/P6.4 SEGMENTATION SMOKE TEST
========================================================
page:
image:
form:
rows:
fields_per_row:

row_001 bbox=...
  stt=...
  date=...
  ...
  note=...

...
row_020 bbox=...
========================================================
RESULT: PASS / FAIL
========================================================

Không cần in tất cả ảnh vào terminal nếu quá dài.
Có thể tạo JSON report.

--------------------------------------------------
## 6. VISUAL DEBUG ARTIFACTS

Nếu cần để xác minh mắt người, tạo artifact debug, ví dụ:

data/crops/debug/

hoặc thư mục phù hợp hiện có.

Nên có tối thiểu:
- contact sheet row crops
- một số field crops đại diện

Đặc biệt kiểm tra:
- row 1
- row 2
- một row giữa
- row cuối
- các field có width nhỏ
- field process_detail / note có width lớn

Không tạo hàng loạt artifact vô dụng.

--------------------------------------------------
## 7. BATCH TEST 7 BASELINE T1 PAGES

Chỉ sau khi smoke test page003 PASS.

Dùng:

data/preprocessed/registration_debug/aligned/T1_page_001.png
...
T1_page_007.png

Chạy segmentation.

Không cần active-row filtering.

Expected mỗi page:
- 20 row slots
- 14 fields / row

Tức:
7 pages × 20 rows × 14 fields

Nhưng KHÔNG cần gửi Qwen.

--------------------------------------------------
## 8. P6.2 — CHỈ DEBUG, CHƯA FREEZE

Sau khi P6.3/P6.4 hoạt động, có thể chạy row_detector V4 như một layer riêng:

segmentation
    ↓
row detector
    ↓
active row candidates

NHƯNG:
- Không gộp detector với segmentation geometry.
- Không để detector redefine bbox.
- Không thay đổi row bbox chỉ vì detector thấy khác.
- Không đóng P6.2 chỉ bằng 7 debug pages.

Nếu có thời gian:
- tạo diagnostic report score/candidate rows trên 7 baseline pages.
- giữ status = CANDIDATE.

Sau khi DEV GT hoàn thành:
- chạy detector trên 24 DEV pages
- compare predicted active vs GT active
- chỉ lúc đó mới tune/freeze P6.2.

--------------------------------------------------
## 9. GROUND TRUTH NGÀY MAI

GT có thể làm song song, không block segmentation.

Nếu có thời gian:
- tiếp tục annotation DEV GT
- ưu tiên đúng schema hiện tại
- `active=true` = row có report data
- `active=false` = row blank
- blank field = null
- unreadable but visible content = [UNK] theo current annotation policy
- không copy dữ liệu giữa row
- không normalize business meaning

Tổ/Nhóm:
- coi là header-level metadata
- chưa đưa vào row ground_truth

Nếu chưa đủ thời gian:
- không tự điền bằng detector
- để lại GT chưa annotate.

--------------------------------------------------
## 10. REGRESSION TESTS

Sau khi code xong:

1. py_compile / pytest relevant tests
2. test FormTemplate hiện tại không hỏng
3. test segmentation page003
4. test 7 baseline pages
5. nếu có existing tests, chạy test liên quan P5/P6

Không được thay đổi P5 outputs chỉ để làm test segmentation pass.

--------------------------------------------------
## 11. ACCEPTANCE CRITERIA CHO SESSION NGÀY MAI

### Có thể đánh PASS cho P6.3/P6.4 nếu:

- segmentation module tồn tại
- dùng FormTemplate làm source of truth
- không hard-code row count/field x coordinates
- 20 row bboxes đúng
- mỗi row có đúng 14 field crops
- row/field order deterministic
- page003 smoke test PASS
- 7 baseline T1 pages batch test PASS
- không có row mixing
- không có out-of-bounds crop
- tests chạy PASS

### P6.2 CHƯA được đánh PASS chỉ vì segmentation PASS.

P6.2 vẫn:
CANDIDATE / OPEN

cho đến khi có GT comparison.

--------------------------------------------------
## 12. TRẠNG THÁI CUỐI SESSION — BẮT BUỘC BÁO CÁO

Cuối session, tạo báo cáo ngắn:

# SESSION REPORT

## Done
- file nào đã tạo/sửa
- test nào PASS
- artifact nào đã tạo

## Not done
- P6.2 chưa freeze
- GT còn bao nhiêu page chưa annotate
- các task còn lại

## P6 status
- P6.1 = PASS
- P6.2 = CANDIDATE/OPEN
- P6.3 = PASS/FAIL
- P6.4 = PASS/FAIL

## Risks / Issues
- issue nào thực tế phát hiện
- file + location
- impact

## Next exact actions
Viết thành các task cụ thể, có file/command nếu có.

KHÔNG kết luận chung chung kiểu:
"segmentation seems good."

Phải viết:
"tests/test_segmentation.py: X tests passed"
"page003: 20/20 rows, 280/280 field crops valid"
v.v.

--------------------------------------------------
## 13. THỨ TUYỆT ĐỐI KHÔNG LÀM TRONG SESSION NÀY

- Không sửa form.json geometry nếu chưa có evidence.
- Không sửa reference.png.
- Không rerun/alter P5 registration algorithm nếu không cần.
- Không thêm form T2/T3/T4.
- Không chạy Qwen để đánh giá accuracy.
- Không làm Excel.
- Không làm Telegram.
- Không làm n8n.
- Không đưa Tổ/Nhóm vào row schema.
- Không đổi 14 canonical row fields.
- Không dùng detector để sinh Ground Truth.
- Không xóa artifacts cũ nếu chưa xác định chắc là obsolete.
- Không tạo script thử nghiệm rải rác trong evaluation/ root chỉ để test tạm thời; ưu tiên tests/ hoặc file debug có chủ đích.

--------------------------------------------------
## 14. MỤC TIÊU THỰC TẾ CỦA NGÀY MAI

Thứ tự ưu tiên:

P0. Inspect thật kỹ project + spec
P1. Hoàn thành P6.3/P6.4 geometry segmentation
P2. Test trên page003
P3. Batch test 7 T1 baseline pages
P4. Giữ P6.2 ở trạng thái candidate
P5. Nếu còn thời gian, annotate thêm DEV GT
P6. Cuối ngày ghi session report

Không cần cố "đóng" toàn bộ P6 trong một session.

Mục tiêu quan trọng nhất là:
SEGMENTATION GEOMETRY ĐÚNG, DETERMINISTIC, TESTABLE, VÀ KHÔNG PHỤ THUỘC VÀO ACTIVE-ROW DETECTION.

BẮT ĐẦU NGAY BẰNG INSPECT.
KHÔNG CODE TRƯỚC KHI ĐỌC CODE + SPEC THỰC TẾ.
