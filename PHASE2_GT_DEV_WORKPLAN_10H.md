phần 1 từ đây đến dòng 277
Đúng, nhưng tao chỉnh lại workflow cho **ít rối hơn**: **mày không bắt buộc phải chạy `normalize_dev_annotations.py` nữa**, vì tao đã tạo sẵn file đã normalize là `dev_annotations_qwen_schema.jsonl`.

### Bước 1 — Chuẩn hóa schema

Cách tao khuyên dùng:

Tải:

[dev_annotations_qwen_schema.jsonl](sandbox:/mnt/data/dev_annotations_qwen_schema.jsonl)

Rồi đặt nó đè vào:

```text
D:\production_ocr\evaluation\ground_truth\selection\dev_annotations.jsonl
```

Sau đó kiểm tra:

```powershell
python -c "import json; p=r'evaluation\ground_truth\selection\dev_annotations.jsonl'; x=[json.loads(l) for l in open(p,encoding='utf-8') if l.strip()]; print('pages=',len(x)); print('rows=',sum(len(r['rows']) for r in x)); print(x[0]['rows'][0]['ground_truth'].keys())"
```

Kỳ vọng:

```text
pages= 24
rows= 480
dict_keys(['stt', 'date', 'order_code', 'drawing_code', 'revision', 'work_code', 'target_time', 'start_time', 'end_time', 'processed_qty', 'good_qty', 'ng_qty', 'process_detail', 'note'])
```

**Không cần chạy `normalize_dev_annotations.py` nếu mày dùng file trên.**

Script `normalize_dev_annotations.py` chỉ để sau này tự động hóa bước này trong pipeline.

---

# Bước 2 — Chưa OCR. Label thử đúng 1 page

Đây mới là bước quan trọng.

Lấy:

```text
DEV GT 01/24
Member 1207
T1 page 003
sample_id = 1207_T1_p003
```

Trang này nằm trong:

```text
evaluation\ground_truth\selection\selected_pages\1207\
```

và cũng nằm ở page 1 của:

```text
ground_truth_dev_24pages.pdf
```

Mày mở **ảnh full resolution của page này**, không dùng thumbnail.

Trong `dev_annotations.jsonl`, tìm record:

```text
"sample_id": "1207_T1_p003"
```

rồi điền **chỉ record này**.

---

# Bước 3 — Rule annotation phải giữ cực chặt

Đây là phần tao cần mày quan sát.

### `active`

```text
active = true
```

khi row đó thực sự có dữ liệu viết tay.

```text
active = false
```

khi row trống.

**Không được lấy dữ liệu row trước rồi copy xuống row sau.**

Cái này đặc biệt quan trọng vì trước đó pipeline registration của mình đã từng xuất hiện hiện tượng dữ liệu page trước bị propagate sang page sau.

### Nội dung field

Phải chép **đúng những gì nhìn thấy**.

Ví dụ nhìn thấy:

```text
DH-123/01
```

thì GT:

```json
"order_code": "DH-123/01"
```

Không sửa thành thứ mày nghĩ là mã đúng.

Tương tự với:

```text
01/08/2026
08:15
1O0
100
A-12
```

thấy gì ghi nấy; **không normalize, không tự sửa typo của người viết**.

### Ô hoàn toàn trống

Để:

```json
null
```

Ví dụ:

```json
"revision": null
```

### Chữ có viết nhưng không thể đọc chắc chắn

**Không đoán.**

Tạm dùng:

```json
"[UNK]"
```

cho field đó.

Ví dụ:

```json
"process_detail": "[UNK]"
```

Tao sẽ xử lý riêng `[UNK]` trong evaluator để không biến một field con người cũng không đọc được thành lỗi OCR.

### Các field đặc biệt

Không tự suy diễn:

```text
work_code
target_time
revision
process_detail
note
```

Nhìn thế nào chép thế đó.

Đặc biệt:

```text
SL NG
```

thì Ground Truth vẫn là:

```json
"ng_qty": "..."
```

Không đổi nó thành `SL chờ`, vì mapping nghiệp vụ là chuyện khác.

---

# Bước 4 — Mày quan sát 1 page này để trả lời 5 thứ

Không cần đánh giá OCR model lúc này.

Chỉ cần xem:

**(1)** Có xác định được ranh giới 20 row bằng geometry hiện tại không?

**(2)** Những row nào thực sự `active=true`?

**(3)** Có field nào bị viết lệch sang cell bên cạnh khiến schema hiện tại khó biểu diễn không?

**(4)** Có trường hợp một giá trị nhìn như được dùng chung cho nhiều row không?

**(5)** Có field nào con người cũng không thể đọc chắc chắn, cần `[UNK]` không?

Đây chính là lúc chúng ta kiểm tra **annotation policy**, chứ chưa phải đo accuracy.

---

# Bước 5 — Gửi lại cho tao cái gì?

**Chỉ cần gửi lại `dev_annotations.jsonl` sau khi mày điền xong page đầu tiên.**

Tức là:

```text
24 pages
480 rows
```

nhưng chỉ:

```text
1207_T1_p003
```

được điền GT.

23 page còn lại vẫn `null`/chưa annotate.

Không cần gửi lại 143 ảnh.

Không cần gửi lại toàn bộ PDF 24 page.

Không cần chạy Qwen OCR.

---

# Sau khi tao kiểm tra page 1

Tao sẽ kiểm tra xem schema có biểu diễn được dữ liệu thực tế không, đặc biệt các case:

```text
row trống
row có dữ liệu
cell viết không rõ
text vượt cell
nhiều field trong một row
ký hiệu/số/mã
```

Nếu rule ổn, **lúc đó mới cho mày label tiếp 23 page còn lại**.

Như vậy tránh trường hợp mày mất công điền 480 row rồi mới phát hiện annotation schema/rule có vấn đề.

### Vì vậy ngay bây giờ

Không cần đụng `normalize_dev_annotations.py`.

Tải file này:

[dev_annotations_qwen_schema.jsonl](sandbox:/mnt/data/dev_annotations_qwen_schema.jsonl)

đặt vào đúng:

```text
D:\production_ocr\evaluation\ground_truth\selection\dev_annotations.jsonl
```

→ mở **1207 / T1 / page 003**
→ điền **một page duy nhất**
→ gửi lại `dev_annotations.jsonl` cho tao.

Đấy là bước tiếp theo chính xác.


-------------------------------------------------------------------------------
phần 2 từ đây tới dòng 447
Đúng, và chỗ này tao muốn **sửa một hiểu nhầm quan trọng** trước khi mày lên công ty.

File `dev_annotations.jsonl` hiện tại đang có:

```json
"active": null,
"ground_truth": {
    "stt": null,
    ...
}
```

`null` lúc này nghĩa là **CHƯA ANNOTATE**, chưa phải kết luận rằng ô đó trống.

Sau khi mày nhìn ảnh:

```text
row có dữ liệu       → active = true
row trống            → active = false
field có chữ         → ghi chữ
field trống          → giữ field = null
field có chữ nhưng
không đọc chắc được  → field = "[UNK]"
```

Đây là distinction rất quan trọng. Ví dụ:

```json
"active": false,
"ground_truth": {
    "stt": null,
    "date": null
}
```

có nghĩa:

> row này đã được con người kiểm tra và xác nhận là row trống.

Còn:

```json
"active": null
```

nghĩa:

> chưa kiểm tra row này.

---

## Còn geometry thì mày không cần hiểu toán học

Ngày mai **đừng ngồi tính tọa độ**.

Tao dùng từ “geometry” hơi kỹ thuật nên làm mày rối :v.

Mày chỉ cần hiểu:

> **Geometry = cách hệ thống chia cái bảng thành 20 hàng và 14 cột.**

Ví dụ trên ảnh:

```text
+----------------------------------+
|             row 1                |
+----------------------------------+
|             row 2                |
+----------------------------------+
|             row 3                |
+----------------------------------+
              ...
+----------------------------------+
|             row 20               |
+----------------------------------+
```

Việc của mày ngày mai chỉ là nhìn:

> “Cái `row_number: 7` trong JSON có thực sự trỏ đúng vùng hàng số 7 trên ảnh không?”

Nếu đúng hết → ghi:

```text
Geometry: PASS
```

Nếu thấy chẳng hạn dữ liệu của row 8 bị chia đôi, hoặc row 8 thực tế lại bị gộp vào row 9 → ghi:

```text
Geometry: ISSUE
```

**Không sửa code geometry ngay.**

---

## Còn “schema” cũng không phức tạp

Schema đơn giản là:

> **Một row được phép chứa những trường dữ liệu nào.**

Hiện tại một row có 14 field:

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

Nên câu:

> “schema có khó biểu diễn không?”

có nghĩa là:

> “Có tình huống thực tế nào trên giấy mà 14 field này không đủ để ghi lại chính xác không?”

Ví dụ người ta viết một thứ gì đó **vắt từ ô `process_detail` sang tận `note`**, thì phải xem đó là một giá trị hay hai giá trị. Đó mới là vấn đề schema.

Không phải cứ chữ viết xấu là schema issue.

---

## Một việc nữa tao khuyên mày làm ngày mai

**Đừng mở `dev_annotations.jsonl` rồi sửa một dòng JSON khổng lồ như screenshot mãi.** Nó rất dễ sửa nhầm.

Tốt nhất trong buổi sáng tao sẽ cho mày một workflow để:

```text
dev_annotations.jsonl
        ↓
extract riêng page 1207_T1_p003
        ↓
file dễ đọc
        ↓
mày annotate
        ↓
merge trở lại JSONL
```

Như vậy sẽ an toàn hơn nhiều.

---

## File kế hoạch 10 tiếng

Tao đã viết đầy đủ kế hoạch từ **08:00 → 19:00**, gồm mục tiêu từng giờ, command, quy tắc annotation, geometry, schema, review, validation và chính xác **cuối ngày phải gửi lại cho tao cái gì**.

[**Tải PHASE2_GT_DEV_WORKPLAN_10H.md**](sandbox:/mnt/data/PHASE2_GT_DEV_WORKPLAN_10H.md)

Bộ 24 page hiện tại vẫn giữ nguyên; metadata xác định đủ các document/member/page đã chọn, gồm 19 page coverage và 5 page challenge.  

**Ngày mai mày chỉ cần nhớ 1 câu:**
**Đừng cố “đọc OCR”; hãy làm người tạo Ground Truth — nhìn giấy, xác nhận row, xác nhận field, ghi đúng cái nhìn thấy, không đoán.**





------------------------------------------------------------------------------------------------------------------------





# Production OCR — Công việc ngày mai: Phase 2 Ground Truth DEV
## Kế hoạch làm việc 10 tiếng tại công ty

> **Mục tiêu của ngày mai:** hoàn thành và kiểm soát chặt **01 page Ground Truth đầu tiên** (`1207_T1_p003`), chốt rule annotation, rồi mới quyết định có mở rộng label 23 page còn lại hay không.
>
> **Không chạy Qwen OCR để đo accuracy trong ngày mai.**
>
> **Không quay lại sửa registration/segmentation trong ngày mai trừ khi phát hiện lỗi hình ảnh/geometry thật sự ảnh hưởng việc label.**

---

# PHẦN A — Trả lời 3 câu hỏi trước khi bắt đầu

## 1. “Bước 2 — Chưa OCR. Label thử đúng 1 page” có nghĩa là gì?

**Đúng.**

Ở bước này mày sẽ:

1. Mở ảnh full-resolution của **01 page được chọn**:
   - Member: `1207`
   - PDF/week: `T1`
   - Page: `003`
   - `sample_id = 1207_T1_p003`

2. Mở file:

```text
evaluation\ground_truth\selection\dev_annotations.jsonl
```

3. Tìm record có:

```json
"sample_id": "1207_T1_p003"
```

4. Trong record đó sẽ có khoảng:

```json
"rows": [
  {
    "row_number": 1,
    "active": null,
    "ground_truth": {
      "stt": null,
      "date": null,
      ...
    }
  },
  ...
]
```

5. Mày **nhìn trực tiếp vào hình** rồi điền giá trị Ground Truth vào các `null` thuộc `ground_truth`.

Ví dụ:

```json
{
  "row_number": 1,
  "active": true,
  "ground_truth": {
    "stt": "1",
    "date": "23/09/2026",
    "order_code": "DH001",
    "drawing_code": "BV-01",
    "revision": null,
    "work_code": "OP10",
    "target_time": "08:00",
    "start_time": "08:05",
    "end_time": "09:10",
    "processed_qty": "100",
    "good_qty": "98",
    "ng_qty": "2",
    "process_detail": "Tiện",
    "note": null
  }
}
```

**Quan trọng:** đây là ví dụ cấu trúc, không phải dữ liệu thật của page.

### Không phải tất cả `null` đều phải đổi thành text

Có 3 loại:

**A. Có chữ/số nhìn thấy rõ → điền nội dung nhìn thấy.**

**B. Ô có viết nhưng không thể đọc chắc chắn → điền `[UNK]`.**

**C. Ô hoàn toàn trống → giữ `null`.**

Ví dụ:

```json
"order_code": "DH001"
```

hoặc:

```json
"order_code": "[UNK]"
```

hoặc:

```json
"order_code": null
```

ba trường hợp này mang 3 ý nghĩa khác nhau.

---

# 2. `active` có tự động chuyển thành `true` không?

**Không. Mày phải tự điền.**

Trong file hiện tại:

```json
"active": null
```

đây là trạng thái **chưa annotate**.

Sau khi nhìn row trên ảnh:

### Row có dữ liệu sản xuất

```json
"active": true
```

### Row trống

```json
"active": false
```

Không có cơ chế tự động chuyển từ `null -> true`.

---

## Quan sát `active` ở đâu?

Quan sát **trên ảnh page**, không phải nhìn vào JSON để đoán.

Luồng là:

```text
Ảnh page
   ↓
Nhìn row #1
   ↓
Có dữ liệu viết trong row?
   ├── Có  → active=true
   └── Không → active=false
   ↓
Điền ground_truth tương ứng
```

Sau đó mở lại `dev_annotations.jsonl` để nhập kết quả.

### Quy tắc rất quan trọng

Không được làm:

> “Row này chắc có dữ liệu vì row phía trên có dữ liệu.”

Phải nhìn **đúng row đó**.

Không được tự copy giá trị từ row trước xuống row sau.

---

# 3. “Geometry là gì?”

## Geometry = thông tin tọa độ của form

Hiểu đơn giản:

> Geometry là **bản đồ vị trí** của cái bảng trên ảnh: bảng bắt đầu ở đâu, kết thúc ở đâu, các đường ngang ở đâu, các cột ở đâu.

Trong `config/forms/T1/v1/form.json`, hiện tại có thông tin kiểu:

```text
page: 3509 x 2481

table:
    x1 = ...
    x2 = ...
    y1 = ...
    y2 = ...

horizontal_lines:
    ... 21 giá trị ...

vertical_lines:
    ... 15 giá trị ...

columns = 14
```

### Vì sao có 21 horizontal lines?

Nếu có:

```text
21 đường ngang
```

thì chúng tạo ra:

```text
20 khoảng row
```

Tức là:

```text
line 1
   ↓
row 1
   ↓
line 2
   ↓
row 2
   ↓
...
   ↓
line 21
```

Đây chính là lý do annotation scaffold có:

```text
row_number = 1 ... 20
```

---

# 4. “Có phải geometry nghĩa là người ta viết tràn sang cell bên cạnh không?”

**Không.**

Đây là hai khái niệm khác nhau.

### Geometry

Là:

> “Biên của ô trên form nằm ở đâu?”

### Text overflow / writing spill

Là:

> “Người viết có viết chữ vượt qua biên của ô sang vùng kế bên không?”

Ví dụ:

```text
| order_code | drawing_code |
|   ABC123----------------> |
```

Nếu `ABC123` vượt khỏi đường biên của `order_code`, đó là **writing spill / overflow**.

---

# 5. “Schema là gì?”

**Schema = cấu trúc dữ liệu mà hệ thống dùng để biểu diễn 1 row OCR.**

Schema hiện tại của `app/qwen_ocr.py` là:

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

Tức là mỗi row sẽ có đúng các field này.

Ví dụ:

```json
{
  "stt": "1",
  "date": "23/09/2026",
  "order_code": "DH001",
  "drawing_code": "BV-01",
  "revision": null,
  "work_code": "OP10",
  "target_time": null,
  "start_time": "08:10",
  "end_time": "09:20",
  "processed_qty": "100",
  "good_qty": "98",
  "ng_qty": "2",
  "process_detail": "Tiện",
  "note": null
}
```

---

# 6. “Schema khó biểu diễn” nghĩa là gì?

Không phải là:

> “Chữ xấu.”

Mà là:

> “Cấu trúc form thực tế có trường hợp mà 14 field hiện tại không đủ để biểu diễn chính xác.”

Ví dụ:

### Case A — chữ tràn ô

Một nội dung thuộc `process_detail` chạy qua đường biên và sang vùng `note`.

Khi đó phải hỏi:

```text
Nội dung này vẫn là 1 field?
Hay thực tế người viết đang dùng cả 2 cell?
```

### Case B — một dòng nhưng có 2 giá trị cho cùng một field

Ví dụ một ô có:

```text
100 / 120
```

nhưng schema chỉ có 1:

```text
processed_qty
```

thì phải ghi nhận để xem rule xử lý như thế nào.

### Case C — một giá trị nằm ở giữa hai row

Có thể xảy ra khi người viết ghi lệch theo chiều dọc.

Lúc đó phải xác định:

```text
thuộc row trên?
thuộc row dưới?
hay thực tế là ghi chú ngoài bảng?
```

### Case D — thông tin dùng chung cho nhiều row

Ví dụ ngày chỉ ghi một lần ở đầu bảng nhưng ý nghĩa thực tế áp dụng cho nhiều row.

**Không được tự copy xuống Ground Truth.**

Phải ghi nhận trường hợp này để chốt annotation rule.

---

# PHẦN B — Việc ngày mai trong 10 tiếng

## 08:00–08:30 — Khởi động và kiểm tra môi trường

### Mục tiêu

Đảm bảo file và dataset không bị nhầm trước khi sửa.

Chạy:

```powershell
cd D:\production_ocr

python --version
```

Kiểm tra:

```powershell
python -c "import fitz; print('PyMuPDF OK')"
python -c "import reportlab; print('ReportLab OK')"
```

Kiểm tra selection:

```powershell
Get-ChildItem .\evaluation\ground_truth\selection\
```

Kiểm tra page:

```powershell
Get-ChildItem .\evaluation\ground_truth\selection\selected_pages\1207\
```

### Cần thấy

```text
dev_annotations.jsonl
dev_selection.json
dev_selection_index.csv
selected_pages\
ground_truth_dev_24pages.pdf
```

---

# 08:30–09:00 — Backup trước khi annotate

Không chỉnh trực tiếp mà không backup.

Chạy:

```powershell
Copy-Item `
  .\evaluation\ground_truth\selection\dev_annotations.jsonl `
  .\evaluation\ground_truth\selection\dev_annotations.before_page1.jsonl `
  -Force
```

Kiểm tra:

```powershell
Get-Item .\evaluation\ground_truth\selection\dev_annotations.before_page1.jsonl
```

Nếu có backup rồi thì mới bắt đầu.

---

# 09:00–09:30 — Mở đúng page đầu tiên

Mở:

```text
evaluation\ground_truth\selection\selected_pages\1207\
```

Tìm:

```text
1207_T1_page_003.png
```

Tên thực tế có thể khác một chút tùy output script.

Nếu không chắc, chạy:

```powershell
Get-ChildItem .\evaluation\ground_truth\selection\selected_pages\1207\ -Recurse
```

### Việc cần làm

Mở ảnh full-size.

**Không annotate bằng contact sheet.**

Contact sheet chỉ dùng để overview.

---

# 09:30–10:30 — Quan sát geometry và row boundary

Đây là bước quan trọng nhất để giải thích “geometry” bằng mắt.

## Không cần tính toán tọa độ bằng tay

Mày chỉ cần kiểm tra:

> 20 row mà hệ thống đang giả định có khớp với 20 vùng bảng trên ảnh hay không?

### Cách quan sát

Nhìn bảng từ trên xuống.

Với mỗi row:

```text
row 1
row 2
row 3
...
row 20
```

xem đường ngang thực tế có chia đúng từng vùng không.

### Câu hỏi cần trả lời

```text
Row 1 có đúng không?
Row 2 có đúng không?
...
Row 20 có đúng không?
```

### Dấu hiệu geometry SAI

Ví dụ:

```text
|------ row 1 ------|
|------ row 2 ------|
|--- row 3 ---------|
       ^
       chữ thuộc row 3 nhưng boundary lại cắt ở giữa
```

Hoặc:

```text
Một row thực tế bị chia thành 2 row.
```

Hoặc:

```text
2 row thực tế bị gom thành 1 row.
```

### Không cần sửa geometry ngay

Chỉ ghi nhận:

```text
PASS
```

hoặc:

```text
ISSUE
```

và mô tả row nào.

Ví dụ:

```text
Geometry observation:
- Rows 1–18: aligned
- Row 19: lower boundary slightly high
- Row 20: okay
```

---

# 10:30–12:00 — Annotate 5 row đầu tiên

**Chưa annotate cả page ngay.**

Làm row:

```text
1 → 5
```

Mỗi row:

### Bước A

Nhìn ảnh.

### Bước B

Set:

```json
"active": true
```

hoặc:

```json
"active": false
```

### Bước C

Điền field.

### Bước D

Kiểm tra lại trực tiếp trên ảnh.

### Quy tắc

**Visible text → exact text.**

**Không đọc được → `[UNK]`.**

**Trống → `null`.**

Không normalize.

Không đoán.

Không copy từ row trước.

---

# 12:00–13:00 — Nghỉ / review nhanh

Không tiếp tục sửa file trong lúc chưa kiểm tra.

Sau khi quay lại:

- mở ảnh;
- mở JSON;
- đối chiếu 5 row đầu.

Kiểm tra đặc biệt:

```text
active
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

---

# 13:00–14:30 — Annotate row 6–10

Lặp đúng quy trình:

```text
image
  ↓
row
  ↓
active
  ↓
field values
  ↓
visual verification
```

Đặc biệt chú ý:

### 1. Row rỗng

Không biến thành:

```json
"active": true
```

chỉ vì có nét bút ở vùng gần row.

### 2. `[UNK]`

Chỉ dùng khi **thực sự có nội dung nhưng không đọc được chắc chắn**.

### 3. Dấu gạch / ký hiệu

Không tự coi là:

```text
null
```

nếu đó là một mark có chủ đích.

Ghi nhận đúng cái nhìn thấy.

---

# 14:30–16:00 — Annotate row 11–20

Hoàn thành page.

Khi hoàn tất, record:

```text
sample_id = 1207_T1_p003
```

phải có:

```text
rows = 20
active đã xác định
ground_truth đã điền
```

---

# 16:00–16:30 — Kiểm tra tính hợp lệ JSON

Chạy:

```powershell
python -c "import json; p=r'evaluation\ground_truth\selection\dev_annotations.jsonl'; rows=[json.loads(l) for l in open(p,encoding='utf-8') if l.strip()]; print('pages=',len(rows)); print('page1 rows=',len(next(x for x in rows if x['sample_id']=='1207_T1_p003')['rows']))"
```

Kỳ vọng:

```text
pages=24
page1 rows=20
```

### Kiểm tra page khác không bị sửa

Chỉ record:

```text
1207_T1_p003
```

được điền.

23 record còn lại chưa annotate.

---

# 16:30–17:30 — Review annotation page 1

Đây là lúc phải **so ảnh và JSON từng row một lần cuối**.

Tạo checklist:

```text
Row 01  [ ] image ↔ JSON
Row 02  [ ] image ↔ JSON
Row 03  [ ] image ↔ JSON
Row 04  [ ] image ↔ JSON
Row 05  [ ] image ↔ JSON
Row 06  [ ] image ↔ JSON
Row 07  [ ] image ↔ JSON
Row 08  [ ] image ↔ JSON
Row 09  [ ] image ↔ JSON
Row 10  [ ] image ↔ JSON
Row 11  [ ] image ↔ JSON
Row 12  [ ] image ↔ JSON
Row 13  [ ] image ↔ JSON
Row 14  [ ] image ↔ JSON
Row 15  [ ] image ↔ JSON
Row 16  [ ] image ↔ JSON
Row 17  [ ] image ↔ JSON
Row 18  [ ] image ↔ JSON
Row 19  [ ] image ↔ JSON
Row 20  [ ] image ↔ JSON
```

---

# 17:30–18:00 — Tổng hợp các case đặc biệt

Tạo file:

```text
evaluation\ground_truth\selection\page1_observations.md
```

Ghi:

```markdown
# 1207_T1_p003 — Annotation Observations

## Geometry
- PASS / ISSUE

## Row boundary issues
- None / ...

## Overflow / spill
- None / ...

## Shared values
- None / ...

## Ambiguous handwriting
- None / ...

## Schema issues
- None / ...

## Annotation questions
- ...
```

### Đây là file cực kỳ quan trọng

Không cần dài.

Nhưng phải ghi lại những gì mày thật sự gặp.

---

# 18:00–18:30 — Chuẩn bị dữ liệu gửi lại

Trước tiên kiểm tra diff/thay đổi.

Có thể dùng Git nếu project có Git:

```powershell
git diff -- .\evaluation\ground_truth\selection\dev_annotations.jsonl
```

Nếu project chưa dùng Git, dùng backup:

```text
dev_annotations.before_page1.jsonl
```

để so sánh.

---

# 18:30–19:00 — Đóng gói kết quả ngày mai

Mày gửi lại cho tao **3 thứ**:

## 1. `dev_annotations.jsonl`

Đây là file chính.

Nó phải chứa:

```text
24 pages
480 rows
```

nhưng chỉ:

```text
1207_T1_p003
```

được annotate.

---

## 2. `page1_observations.md`

File này cho tao biết:

```text
geometry có ổn không
row boundary có ổn không
có overflow không
có ambiguity không
schema có đủ không
```

---

## 3. Nếu có vấn đề hình ảnh

Chỉ gửi thêm **ảnh crop/page cụ thể** có vấn đề.

Ví dụ:

```text
row 7 bị lệch
```

thì chụp/crop vùng row 7.

**Không cần gửi lại toàn bộ 143 page.**

---

# PHẦN C — Sau khi gửi lại cho tao

Tao sẽ không bắt mày label tiếp ngay.

Tao sẽ kiểm tra:

## Check 1 — Schema

Xem 14 field hiện tại có biểu diễn đúng page thực tế không.

## Check 2 — Annotation rule

Xem:

```text
null
[UNK]
active=false
active=true
```

đang được dùng đúng nghĩa không.

## Check 3 — Geometry

Xác định:

```text
20 rows
```

có hợp lý không.

## Check 4 — Overflow

Xem có cần thêm một rule đặc biệt cho chữ viết vượt cell không.

## Check 5 — Shared values

Xem có giá trị nào chỉ xuất hiện một lần nhưng đang có ý nghĩa cho nhiều row hay không.

---

# PHẦN D — Khi nào mới label 23 page còn lại?

Chỉ khi page đầu tiên được chốt.

Quy trình:

```text
PAGE 01
   ↓
annotation review
   ↓
rule freeze
   ↓
PAGE 02–05
   ↓
review
   ↓
PAGE 06–24
```

Không nên:

```text
label cả 24 page
   ↓
phát hiện rule sai
   ↓
sửa lại 24 page
```

Đó là cách dễ tốn thời gian nhất.

---

# PHẦN E — Những thứ TUYỆT ĐỐI chưa làm ngày mai

## Chưa chạy OCR

Không cần:

```powershell
python ...
qwen...
```

## Chưa tính accuracy

Phase accuracy đang ở sau.

## Chưa sửa registration algorithm

Trừ khi phát hiện:

```text
page/image thực sự sai
```

khiến annotation không thể làm được.

## Chưa mở rộng sang form khác

Hiện tại:

```text
form_id = T1
version = v1
```

vẫn giữ nguyên.

---

# PHẦN F — Checklist cuối ngày

```text
[ ] dev_annotations.jsonl đã backup
[ ] mở đúng 1207_T1_p003
[ ] hiểu 20 row
[ ] kiểm tra geometry bằng mắt
[ ] active được set true/false
[ ] field có dữ liệu được điền
[ ] field trống giữ null
[ ] field không đọc được dùng [UNK]
[ ] không tự suy diễn
[ ] không copy dữ liệu giữa row
[ ] không sửa 23 page còn lại
[ ] JSON vẫn parse được
[ ] tạo page1_observations.md
[ ] giữ lại backup
[ ] gửi dev_annotations.jsonl
[ ] gửi page1_observations.md
[ ] gửi crop ảnh nếu có issue
```

---

# PHẦN G — Tóm tắt cực ngắn để mở máy là làm được

```text
08:00
→ kiểm tra file + backup

09:00
→ mở 1207_T1_p003

09:30
→ hiểu 20 row / geometry

10:30
→ label row 1–5

13:00
→ label row 6–10

14:30
→ label row 11–20

16:00
→ review toàn page

17:30
→ ghi page1_observations.md

18:30
→ JSON validation

19:00
→ gửi lại cho GPT:
   1. dev_annotations.jsonl
   2. page1_observations.md
   3. crop issue nếu có
```

---

# PHỤ LỤC — Cách hiểu các khái niệm

## `null`

> Chưa có giá trị / ô trống / không có nội dung tùy ngữ cảnh annotation.

## `[UNK]`

> Có nội dung nhưng người annotate không đọc chắc chắn.

## `active`

> Row đó có đang chứa dữ liệu sản xuất hay không.

## geometry

> Bản đồ tọa độ của form: bảng nằm đâu, row nằm đâu, column nằm đâu.

## schema

> Cấu trúc dữ liệu mà OCR dùng để biểu diễn một row.

## overflow / spill

> Người viết ghi vượt qua biên của cell.

## Ground Truth

> Giá trị chuẩn do con người xác nhận từ ảnh, dùng làm mốc để kiểm tra OCR.

## DEV Ground Truth

> Bộ dữ liệu phục vụ phát triển/debug, chưa dùng làm validation cuối cùng.

---

# Mốc quyết định sau ngày mai

Không phụ thuộc vào việc “đã label xong page 1 hay chưa”.

Mốc đúng là:

```text
PAGE 1 ANNOTATION
       ↓
RULES UNDERSTOOD
       ↓
SCHEMA ACCEPTED
       ↓
GEOMETRY ACCEPTED
       ↓
ONLY THEN → CONTINUE 23 PAGES
```

