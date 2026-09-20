Được. Với dự án của mày, tao sẽ thiết kế workflow theo hướng **không phải “Qwen OCR xong là đổ thẳng vào Excel”**, mà là một **pipeline OCR + validation \+ human review**. Cách này phù hợp hơn nhiều với mục tiêu accuracy ≥95%.

 # WORKFLOW TỔNG THỂ — QC\_OCR

```
                    ┌─────────────────────────┐
                    │       NHÂN VIÊN         │
                    │                          │
                    │ Gửi PDF / JPG / PNG     │
                    │ qua Telegram Bot         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     TELEGRAM BOT         │
                    │                          │
                    │ Nhận file               │
                    │ Tạo JobID                │
                    │ Lưu file gốc             │
                    │ Trả trạng thái           │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       INPUT MANAGER      │
                    │                          │
                    │ Kiểm tra file            │
                    │ PDF / JPG / PNG          │
                    │ Đặt tên / tạo Job        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
                 PDF                       IMAGE
                    │                         │
                    ▼                         │
          ┌───────────────────┐               │
          │ PDF PROCESSOR     │               │
          │                   │               │
          │ PDF → từng page   │               │
          │ 300 DPI           │               │
          └─────────┬─────────┘               │
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │      IMAGE PREPROCESS   │
                    │                          │
                    │ Deskew                   │
                    │ Crop / ROI               │
                    │ Contrast                 │
                    │ Noise reduction          │
                    │ Giữ bản gốc              │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       QWEN3-VL           │
                    │                          │
                    │   IMAGE → OCR JSON       │
                    │                          │
                    │ Chữ viết tay             │
                    │ Số                       │
                    │ Mã kỹ thuật              │
                    │ Tiếng Việt có dấu        │
                    │ Nhiều dòng               │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       VALIDATOR          │
                    │                          │
                    │ Kiểm tra format          │
                    │ Confidence               │
                    │ Số lượng                 │
                    │ Mã đơn hàng              │
                    │ Mã bản vẽ                │
                    │ Thời gian                │
                    │ Master data              │
                    └────────────┬────────────┘
                                 │
                         ┌───────┴────────┐
                         │                │
                         ▼                ▼
                  PASS / HIGH       LOW CONFIDENCE
                  CONFIDENCE             / ERROR
                         │                │
                         │                ▼
                         │      ┌─────────────────────┐
                         │      │    HUMAN REVIEW     │
                         │      │                     │
                         │      │ Nhân viên xem       │
                         │      │ dữ liệu OCR         │
                         │      │                     │
                         │      │ [ĐÚNG]              │
                         │      │ [SỬA]               │
                         │      │ [HUỶ]               │
                         │      └──────────┬──────────┘
                         │                 │
                         └────────┬────────┘
                                  ▼
                    ┌─────────────────────────┐
                    │         MAPPER          │
                    │                          │
                    │ OCR field               │
                    │       ↓                  │
                    │ Excel Sheet 05          │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      EXCEL WRITER        │
                    │                          │
                    │ Điền các cột có dữ liệu │
                    │ Giữ cột khác = blank    │
                    │ Không phá công thức      │
                    │ Giữ template production  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       OUTPUT            │
                    │                          │
                    │ Excel hoàn chỉnh         │
                    │                           │
                    │ Lưu server               │
                    │ + gửi lại Telegram       │
                    └─────────────────────────┘
```

---

 # 1. NHÂN VIÊN BẮT ĐẦU JOB

 Ví dụ nhân viên có:

```
T1.pdf
```

 gồm:

```
7 trang
```

 Nhân viên gửi:

```
📎 T1.pdf
```

 vào Telegram Bot.

 Hoặc gửi:

```
📷 page1.jpg
```

 hoặc:

```
📷 page1.png
```

 Hệ thống hỗ trợ:

```
PDF
JPG
JPEG
PNG
```

---

 # 2\. TELEGRAM BOT TẠO JOB

 Bot không xử lý OCR ngay trong Telegram.

 Nó gửi file về PC/server.

 Ví dụ:

```
JobID:
JOB_20260918_000123
```

 Cấu trúc:

```
data/
└── input/
    └── JOB_20260918_000123/
        └── T1.pdf
```

 Database/log có thể lưu:

```
JobID
User
FileName
UploadTime
Status
```

 Ban đầu:

```
RECEIVED
```

 Bot trả:

```
✅ Đã nhận file.

Job: JOB_20260918_000123
File: T1.pdf
Trạng thái: Đang xử lý...
```

---

 # 3\. PDF PROCESSOR

 Nếu input là:

```
T1.pdf
```

 thì:

```
T1.pdf
   │
   ├── page 1
   ├── page 2
   ├── page 3
   ├── page 4
   ├── page 5
   ├── page 6
   └── page 7
```

 render:

```
300 DPI
```

 thành:

```
data/pages/JOB_.../
    T1_p001.png
    T1_p002.png
    T1_p003.png
    T1_p004.png
    T1_p005.png
    T1_p006.png
    T1_p007.png
```

 **Luôn giữ PDF gốc.**

 Không bao giờ overwrite file gốc.

---

 # 4\. IMAGE PREPROCESSING

 Đây là tầng cực kỳ quan trọng đối với form của mày.

 Ảnh thực tế có thể:

```
✓ hơi nghiêng
✓ chữ đè lên line
✓ handwriting khác nhau
✓ ảnh sáng/tối khác nhau
```

 Pipeline có thể là:

```
Original
   ↓
Detect page
   ↓
Deskew
   ↓
Contrast
   ↓
Noise reduction
   ↓
ROI extraction
   ↓
OCR
```

 Nhưng **chưa chắc chúng ta sẽ làm toàn bộ ngay từ đầu**.

 Tao muốn benchmark Qwen trước.

---

 # 5\. FORM TEMPLATE

 Đây là một phần cực kỳ quan trọng vì mày nói:

 > Form luôn giống hệt nhau.

 Đó là lợi thế cực lớn.

 Ví dụ:

```
FORM V1

┌───────────────────────────────────────┐
│ Ngày: [...............]               │
│ Mã đơn hàng: [...............]        │
│ Mã bản vẽ: [...............]          │
│ Rev: [....]                           │
├───────────────────────────────────────┤
│ STT │ Công việc │ Bắt đầu │ Kết thúc │
├─────┼───────────┼─────────┼──────────┤
│  1  │ ........  │ ....... │ ........ │
│  2  │ ........  │ ....... │ ........ │
│  3  │ ........  │ ....... │ ........ │
└───────────────────────────────────────┘
```

 Ta sẽ định nghĩa trong:

```
config/form_v1.json
```

 Ví dụ sau này:

```
{
  "form_version": "v1",
  "regions": {
    "date": [100, 100, 500, 160],
    "order_code": [500, 100, 1000, 160],
    "drawing_code": [100, 180, 500, 240],
    "revision": [500, 180, 700, 240],
    "table": [100, 400, 2300, 3000]
  }
}
```

 **Đây chính là lý do tao chưa muốn phụ thuộc 100% vào việc Qwen tự tìm vị trí.**

 Form cố định → chúng ta có thể cho model biết:

 > "Đây là vùng Mã đơn hàng."

 thay vì:

 > "Hãy tìm Mã đơn hàng trong toàn bộ ảnh."

---

 # 6\. QWEN3-VL

 Đây là "não OCR".

 Input:

```
T1_p001.png
```

 Qwen nhìn ảnh.

 Output ban đầu:

```
{
  "document": {
    "date": "18/09/2026"
  },
  "rows": [
    {
      "order_code": "ABC123",
      "drawing_code": "DW-001",
      "revision": "B",
      "start_time": "08:15",
      "end_time": "10:20",
      "processed_qty": 100,
      "good_qty": 98,
      "ng_qty": 2,
      "note": "..."
    }
  ]
}
```

 Nhưng đây **chưa phải dữ liệu production**.

 Nó mới là:

```
RAW OCR
```

---

 # 7\. VALIDATOR

 Đây là tầng tao muốn làm rất mạnh.

 Ví dụ Qwen đọc:

```
Mã đơn hàng = ABC12O
```

 Trong master data lại có:

```
ABC120
```

 Validator phát hiện:

```
OCR:
ABC12O

MASTER:
ABC120
```

 và đánh dấu:

```
⚠ POSSIBLE OCR ERROR
```

 Không tự ý sửa ngay.

---

 # 8\. VALIDATOR KIỂM TRA NHIỀU LOẠI

 ### Kiểm tra format

 Ví dụ:

```
Ngày
```

 phải giống:

```
DD/MM/YYYY
```

---

 ### Kiểm tra thời gian

 Ví dụ:

```
Bắt đầu = 08:30
Kết thúc = 07:20
```

 → bất thường.

---

 ### Kiểm tra số lượng

 Ví dụ:

```
SL gia công = 100

SL đạt = 98

SL NG = 2
```

 → hợp lý.

 Nhưng:

```
SL gia công = 100
SL đạt = 98
SL NG = 7
```

 →

```
⚠ Quantity mismatch
```

---

 # 9\. MASTER DATA

 Mày đã có:

 > database/master list mã đơn hàng/mã bản vẽ

 Đây sẽ trở thành vũ khí rất mạnh.

 Ví dụ:

```
OCR:

Mã bản vẽ:
AB-102O
```

 Master:

```
AB-1020
```

 Validator có thể đưa:

```
OCR confidence: 0.71

Master match:
AB-1020

Possible correction:
AB-1020
```

 Nhưng **không tự sửa nếu confidence không đủ cao**.

---

 # 10\. CONFIDENCE ENGINE

 Đừng chỉ tin:

```
Qwen confidence = 0.95
```

 Ta nên tạo:

```
Final Confidence
```

 từ nhiều yếu tố.

 Ví dụ:

```
Qwen confidence       0.94
Format validation     1.00
Master match          1.00
Quantity validation   1.00
Image quality         0.90
--------------------------------
Final confidence      0.96
```

 Ngược lại:

```
Qwen confidence       0.68
Format validation     1.00
Master match          0.00
Quantity validation   0.50
Image quality         0.70
--------------------------------
Final confidence      0.57
```

 → bắt nhân viên review.

---

 # 11\. HUMAN REVIEW

 Đây là phần Telegram mà mày muốn.

 Ví dụ bot gửi:

```
⚠️ CẦN KIỂM TRA

Job: JOB_000123
Trang: 3

Mã đơn hàng:
ABC12O

Mã bản vẽ:
DW-102

Bắt đầu:
08:20

Kết thúc:
10:15

SL gia công:
100

SL đạt:
98

SL NG:
2
```

 Kèm:

```
[✅ ĐÚNG]
[✏️ SỬA]
[❌ HỦY]
```

---

 # 12\. NHÂN VIÊN BẤM "ĐÚNG"

 Nếu tất cả đúng:

```
Telegram
   ↓
[ĐÚNG]
   ↓
Review status = APPROVED
   ↓
Mapper
```

 Không cần nhập lại.

---

 # 13\. NHÂN VIÊN BẤM "SỬA"

 Bot hỏi:

```
Bạn muốn sửa trường nào?
```

 Ví dụ:

```
[Ngày]
[Mã đơn hàng]
[Mã bản vẽ]
[Rev]
[Bắt đầu]
[Kết thúc]
[SL gia công]
[SL đạt]
[SL NG]
[Ghi chú]
```

 Nhân viên chọn:

```
[Mã đơn hàng]
```

 Bot:

```
Giá trị OCR:

ABC12O

Vui lòng nhập giá trị đúng:
```

 Nhân viên:

```
ABC120
```

 Bot:

```
Đã sửa:

ABC120

[✅ Xác nhận]
[↩ Sửa lại]
```

---

 # 14\. ĐÂY LÀ CHỖ CỰC KỲ QUAN TRỌNG

 Mỗi lần nhân viên sửa:

```
OCR:
ABC12O

Human:
ABC120
```

 phải lưu lại.

 Ví dụ:

```
evaluation/
└── reviewed/
    └── corrections.json
```

 Sau một thời gian chúng ta sẽ có:

```
OCR output
+
Human correction
```

 Đây chính là **ground truth thực tế**.

 Ban đầu mày nói:

 > Không có Excel ground-truth cũ.

 Không sao.

 **Human review sẽ tạo ground truth mới.**

---

 # 15\. MAPPING

 Sau khi dữ liệu đã được xác nhận:

```
Validated JSON
        ↓
mapper.py
        ↓
Excel Sheet 05
```

 Mapping hiện tại:

 | Form | OCR | Excel Sheet 05 |
| --- | --- | --- |
| Ngày | `date` | Ngày |
| Mã đơn hàng | `order_code` | Mã đơn hàng |
| Mã bản vẽ | `drawing_code` | Mã bản vẽ |
| Rev | `revision` | Rev |
| Thời gian bắt đầu | `start_time` | Bắt đầu |
| Thời gian kết thúc | `end_time` | Kết thúc |
| SL gia công | `processed_qty` | SL xử lý |
| SL đạt | `good_qty` | SL đạt |
| SL NG | `ng_qty` | SL chờ |
| Ghi chú | `note` | Ghi chú |

---

 # 16\. CÁC CỘT KHÔNG CÓ TRÊN FORM

 Ví dụ:

```
RunID
Ca
Mã dòng hệ thống
OperationCode
OperationPlanID
Máy
ActivityType
Nghỉ
Setup TT
Downtime
Run TT
...
```

 hiện tại:

```
NULL / blank
```

 Không đoán.

 Không tự sinh.

 Không phá template.

---

 # 17\. CÁC Ô XANH

 Đây là điểm tao rất muốn giữ kiến trúc sạch.

 Nếu:

```
SL xử lý
SL đạt
SL chờ
```

 đã có dữ liệu.

 Các cột:

```
Cân đối SL
Earned Min
Labor Min
Hiệu suất
Chi phí LĐ
...
```

 có công thức Excel thì:

```
OCR
 ↓
điền INPUT CELLS
 ↓
Excel formula
 ↓
CALCULATED CELLS
```

 **Không để Qwen tính những thứ Excel đã có công thức.**

 Qwen chỉ nhập dữ liệu nguồn.

 Excel chịu trách nhiệm tính toán.

---

 # 18\. EXCEL WRITER

 Luồng:

```
Template production.xlsx
        ↓
Copy
        ↓
Job output.xlsx
        ↓
Điền dữ liệu
        ↓
Giữ nguyên formula
        ↓
Save
```

 Ví dụ:

```
data/output/
└── JOB_000123/
    └── T1_processed.xlsx
```

 Không sửa file template gốc.

---

 # 19\. TRẢ KẾT QUẢ VỀ TELEGRAM

 Sau khi Excel hoàn tất:

```
✅ Đã xử lý xong

Job: JOB_000123

Trang: 7/7
OCR: hoàn tất
Human review: hoàn tất

Số dòng: 21
Số trường cần sửa: 3

Excel:
T1_processed.xlsx
```

 Sau đó bot gửi file Excel.

---

 # 20\. ĐỒNG THỜI LƯU SERVER

 Server:

```
data/
└── output/
    └── JOB_000123/
        ├── T1_processed.xlsx
        └── metadata.json
```

---

 # 21\. TOÀN BỘ PIPELINE THỰC TẾ

 Nếu viết thành một đường thẳng:

```
NHÂN VIÊN
    │
    │ upload PDF/JPG/PNG
    ▼
TELEGRAM BOT
    │
    │ tạo JobID
    ▼
INPUT MANAGER
    │
    ├── PDF
    │     ↓
    │   PDF PROCESSOR
    │     ↓
    │   7 PNG pages
    │
    └── JPG/PNG
          ↓
        1 image
    │
    ▼
IMAGE PREPROCESSING
    │
    ▼
FORM TEMPLATE / ROI
    │
    ▼
QWEN3-VL
    │
    ▼
RAW OCR JSON
    │
    ▼
VALIDATOR
    │
    ├───────────────┐
    │               │
    ▼               ▼
HIGH CONFIDENCE   LOW CONFIDENCE
    │               │
    │               ▼
    │          TELEGRAM REVIEW
    │               │
    │          ┌────┴────┐
    │          ▼         ▼
    │        ĐÚNG       SỬA
    │          │         │
    │          └────┬────┘
    │               │
    └───────┬───────┘
            ▼
       VALIDATED JSON
            │
            ▼
          MAPPER
            │
            ▼
      EXCEL SHEET 05
            │
            ▼
       EXCEL FORMULA
            │
            ▼
       FINAL EXCEL
            │
       ┌────┴────┐
       ▼         ▼
    SERVER    TELEGRAM
```

---

 # 22\. CẤU TRÚC CODE CỦA MÌNH SẼ KHỚP WORKFLOW NÀY

 Cấu trúc mày đang có thực ra khá hợp:

```
QC_OCR/
│
├── app/
│   │
│   ├── pdf_processor.py
│   │       ↓
│   │   PDF → images
│   │
│   ├── image_preprocess.py
│   │       ↓
│   │   image cleaning / deskew / ROI
│   │
│   ├── form_template.py
│   │       ↓
│   │   biết form nằm ở đâu
│   │
│   ├── qwen_ocr.py
│   │       ↓
│   │   AI OCR
│   │
│   ├── validator.py
│   │       ↓
│   │   kiểm tra OCR
│   │
│   ├── mapper.py
│   │       ↓
│   │   OCR → Sheet 05
│   │
│   ├── excel_writer.py
│   │       ↓
│   │   ghi Excel
│   │
│   └── telegram_bot.py
│           ↓
│       human review
│
├── config/
│   │
│   ├── form_v1.json
│   │
│   ├── mapping.json
│   │
│   └── settings.json
│
├── data/
│   │
│   ├── input/
│   ├── pages/
│   ├── crops/
│   ├── results/
│   ├── reviewed/
│   └── output/
│
├── evaluation/
│   │
│   ├── ground_truth/
│   └── reports/
│
└── logs/
```

---

 # 23\. VÀ TAO MUỐN THÊM MỘT "VÒNG LẶP HỌC" SAU NÀY

 Đây mới là phần hay.

 Ban đầu:

```
Qwen
 ↓
OCR
 ↓
Human sửa
```

 Sau 300 ảnh:

```
OCR output
+
Human corrections
=
Ground Truth
```

 Ta bắt đầu thống kê:

```
Mã đơn hàng:
98.7%

Mã bản vẽ:
96.2%

Rev:
99.1%

Thời gian:
97.5%

Số lượng:
99.3%

Ghi chú:
91.4%
```

 Ta sẽ biết **chính xác Qwen đang yếu ở đâu**.

 Không phải đoán.

---

 # 24\. SAU ĐÓ MỚI TỐI ƯU MODEL

 Ví dụ phát hiện:

```
Mã bản vẽ rất tốt
Số lượng rất tốt
Thời gian khá tốt

Ghi chú rất tệ
```

 thì không cần thay cả hệ thống.

 Ta có thể chuyển:

```
FULL PAGE
```

 thành:

```
              PAGE
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
     Header    Table    Note
        │       │        │
      Qwen    Qwen     Qwen
```

 hoặc thậm chí:

```
Mã đơn hàng → crop riêng
Mã bản vẽ   → crop riêng
Rev         → crop riêng
Bắt đầu     → crop riêng
Kết thúc    → crop riêng
SL          → crop riêng
Ghi chú     → crop riêng
```

 Đây có thể là cách chúng ta đạt accuracy production cao hơn.

---

 # 25\. MỤC TIÊU CUỐI CÙNG

 Tao hình dung UX cuối cùng của nhân viên sẽ cực kỳ đơn giản:

```
Nhân viên
   │
   ▼
Gửi T1.pdf
   │
   ▼
Bot:
"Đã nhận. Đang xử lý..."
   │
   ▼
OCR + Validation
   │
   ▼
Bot:
"Đã đọc xong.
Có 2 trường cần kiểm tra."
   │
   ▼
Nhân viên
[ĐÚNG] [SỬA]
   │
   ▼
Excel tự sinh
   │
   ▼
Bot gửi:
"T1_processed.xlsx"
```

 Nhân viên **không cần mở Python, không cần mở Qwen, không cần biết OCR chạy thế nào**.

---

 ## Và quan trọng nhất: hệ thống này không chỉ là OCR

 Nó sẽ là:

```
                 ┌─────────────────┐
                 │      QWEN       │
                 │   Vision + OCR  │
                 └────────┬────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │      VALIDATOR        │
              │                       │
              │ Format               │
              │ Master data          │
              │ Quantity              │
              │ Time                  │
              │ Confidence            │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │     HUMAN REVIEW      │
              │                       │
              │ Telegram              │
              │ Đúng / Sửa            │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │       EXCEL           │
              │                       │
              │ Sheet 05              │
              │ Formula               │
              │ Production template   │
              └───────────────────────┘
```

 **Qwen không phải người quyết định cuối cùng.** Nó là tầng đọc dữ liệu; `validator + master data + human review` mới là lớp bảo vệ để biến OCR thành dữ liệu production.

 Và cái này cực kỳ hợp với mục tiêu **95% accuracy theo cả character/field/row**, vì sau này ta có thể đo từng tầng thay vì chỉ nói chung chung rằng "OCR đúng 95%".


 Đúng — **mày đang nhìn đúng vấn đề**. Và tao phải đính chính một chỗ ở câu trước: con số **5.03 GB** trên trang Hugging Face là kích thước được hiển thị cho Q4\_K\_M, nhưng file mà máy mày thực tế tải có thể hiển thị **6.19 GB** tùy cách Hugging Face/LM Studio hiển thị dung lượng. Trang Qwen hiện xác nhận Q4\_K\_M là 5.03 GB ở phần model metadata.  Hugging Face

 ### Còn `mmproj` thì: **ĐÚNG, nếu dùng GGUF Vision thì cần nó**

 Qwen chính thức nói GGUF của Qwen3-VL được chia thành **2 thành phần**:

```
1. Language model
   Qwen3-VL-8B-Instruct-Q4_K_M.gguf

2. Vision encoder / projector
   mmproj-Qwen3-VL-8B-Instruct-F16.gguf
```

 Qwen ghi rõ các file này là hai component riêng của model.  Hugging Face

 Với bài toán của mày là **OCR từ ảnh**, `mmproj` cực kỳ quan trọng. Nó là phần giúp model xử lý **image input**.

```
                    ẢNH
                     │
                     ▼
              ┌──────────────┐
              │    mmproj    │
              │ Vision part  │
              └──────┬───────┘
                     │
                     ▼
             Qwen3-VL 8B LLM
             Q4_K_M ~6GB
                     │
                     ▼
                   TEXT
```

 Nếu chỉ có:

```
Qwen3-VL-8B-Instruct-Q4_K_M.gguf
```

 thì **chưa đủ cho workflow vision của mình**.

 Qwen's own llama.cpp example cũng chạy model bằng cách chỉ định cả `-m` cho LLM và `--mmproj` cho vision projector.  Hugging Face

---

 ## Nhưng khoan tải `mmproj` ngay nếu mày dùng LM Studio

 Đây là điểm quan trọng.

 Trang chính thức của Qwen hiện liệt kê **LM Studio** trong các local apps hỗ trợ model này.  Hugging Face

 Vì vậy tao muốn mày **để LM Studio quản lý dependency trước**.

 Nếu LM Studio đã tải:

```
Qwen3-VL-8B-Instruct-Q4_K_M.gguf
```

 thì vào model details xem nó có tự nhận:

```
mmproj-Qwen3-VL-8B-Instruct-F16.gguf
```

 hay không.

 ### Nếu LM Studio báo thiếu vision/projector

 → lúc đó **tải thêm `mmproj`**.

 ### Nếu LM Studio tự tải/đã có projector

 → **không tải lần nữa**.

---

 # Còn chuyện 6.19 GB

 Cái này tao muốn mày **đừng hoảng**.

 Có hai con số khác nhau:

```
Qwen model card:
Q4_K_M = 5.03 GB
```

  Hugging Face  nhưng file/download UI của mày có thể hiển thị khoảng:

```
6.19 GB
```

 Điều quan trọng hơn là:

```
6.19 GB
    +
mmproj ~1.x GB
    +
KV cache
    +
runtime overhead
```

 **không có nghĩa toàn bộ 7\+ GB sẽ phải nằm trong VRAM.**

 LM Studio/llama.cpp có thể phân bổ một phần sang RAM tùy cấu hình GPU offload.

 Mày có **32 GB RAM**, nên đây chính là thứ ta sẽ thử.

---

 ## Và tao đổi chiến thuật một chút

 Đừng tự tải thủ công 2 file rồi mò cấu hình.

 ### Làm như này:

 **Bước 1**

 Trong LM Studio tải:

```
Qwen/Qwen3-VL-8B-Instruct-GGUF
Q4_K_M
```

 **Bước 2**

 Load model.

 **Bước 3**

 Nếu LM Studio hiện lỗi kiểu:

```
vision projector missing
```

 hoặc không cho đưa ảnh vào:

 → gửi screenshot cho tao.

 Tao sẽ hướng dẫn mày lấy đúng:

```
mmproj-Qwen3-VL-8B-Instruct-F16.gguf
```

 rồi đặt nó đúng chỗ.

 **Đừng tải Q6\_K. Đừng tải Q8\_0.**

 Với RTX 3050 6GB, **Q4\_K\_M vẫn là candidate đầu tiên**. Qwen hiện liệt kê Q4\_K\_M 5.03 GB, Q8\_0 8.71 GB và F16 16.4 GB.  Hugging Face

---

 ### Một chuyện nữa cực quan trọng

 Vì mày đang làm **OCR chữ viết tay**, tao muốn giữ:

```
8B GGUF
Q4_K_M
+
mmproj F16
```

 chứ **không giảm precision của vision projector ngay từ đầu**.

 Qwen cho phép vision encoder ở F16 hoặc Q8\_0.  Hugging Face

 Mình đang ưu tiên **accuracy \> speed**, nên giữ vision ở F16 trước. Sau khi benchmark xong mới cân nhắc Q8 nếu cần giảm RAM/VRAM.

 **=\> Tóm lại: Có, `mmproj` là thành phần cần thiết cho vision; nhưng chưa cần tải thủ công nếu LM Studio tự quản lý được.**

 https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct
Tôi đang cần một mô hình giúp quét qua chữ trên hình ảnh ( hình ảnh như trên ) và sau đó mapping các chữ viết bằng tay trong đó vào excel, dự định sử dụng mô hình trên: Qwen3-VL-4B-Instruct 
Hãy hỏi lại tôi những gì bạn muốn hỏi để hoàn thiện Dự án này !
A. Về dữ liệu
1. về dữ liệu, tôi có khoảng 300 ảnh như vậy, tuy nhiên nó là ảnh được lưu trong cùng 1 cái pdf, nhiều file pdf của nhiều người khác nhau, ví dụ như trên
2. Form luôn giống hệt nhau
3. Chữ viết tay có thể là Tiếng Việt có dấy, có thể là số, ký hiệu, mã kỹ thuật
B. Về handwriting
4. Những vùng phải đọc chính xác là tất cả các vùng
5. Chữ viết tay của nhiều người khác nhau, không đến cả trăm người nhưng cũng 15 người 16 người
D. Về hardware
9. Chạy model ở Window PC, i7-14700k, 32.0gb ddr5, 3060 6gb, win 11
10. về tốc độ không quan trọng, qtrong chất lượng là được
11. sai số được chấp nhận là 95%
12 dữ liệu này được phép gửi lên telegram, kiểu chạy trên tele rồi ra kết quả rồi nhân viên bấm xác nhận coi đúng hay sai
14. bắt tay vào làm luôn thôi, nhớ là xây dựng các phase chi tiết

Q1. 300 ảnh ở đây là sự ước lượng tự tao tính, mỗi ảnh 1 trang, 1 pdf vậy có 7 - 10 ảnh --> 7 - 10 trang, mỗi folder là của 1 người gồm 4 file pdf --> 28 - 40 ảnh cho 1 folder của 1 người 
Q2. đúng, phải được mapping vào chính các cột của sheet 05 đó, hiện tại có các cột:
RunID	Ngày	Ca	Mã đơn hàng	Mã bản vẽ	Rev	Dòng/Lô	Mã dòng hệ thống	Thứ tự CĐ	OperationCode	OperationPlanID	Nhân viên	Máy	ActivityType	Bắt đầu	Kết thúc	Nghỉ	Setup TT	Downtime	Run TT	SL xử lý	SL đạt	SL đạt lần đầu	SL cần sửa	SL phế	SL chờ	Cân đối SL	Earned Min	Labor Min	Hiệu suất	Chi phí LĐ	Chi phí máy	Chi phí chuyển đổi	Duyệt	Kiểm tra dữ liệu	Ghi chú
--> dễ thấy trong sheet 05 file excel có những cột mà trong ảnh không có, tạm thời có thể bỏ qua những cột không có, chỉ cần quan tâm đến việc quét hết cái ảnh rồi có dữ liệu nào mapping vô là ok

1. Như bạn đã thấy trong excel, mấy cái cột màu vàng là trước đó tui phải tự điền, nhưng mà sau khi hoàn thành mô hình thì mô hình điền há há, sau đó các ô màu xanh thì sẽ được tính từ công thức từ các cột trong cùng sheet mà ra hoặc có cả cột/ô trong sheet khác
Bảng mapping:
Trên form giấy	→	Excel Sheet 05
Ngày	→	Ngày
Mã đơn hàng	→	Mã đơn hàng
Mã bản vẽ	→	Mã bản vẽ
Rev	→	Rev
Thời gian bắt đầu	→	Bắt đầu
Thời gian kết thúc	→	Kết thúc
SL gia công	→	SL xử lý
SL đạt	→	SL đạt
SL NG -> SL chờ
Ghi chú -> Ghi chú
có thể có sai sót nên cũng cứ chủ động phân tích à để xuất mapping thêm nhé
3. một dòng trên giấy có tương ứng với 1 dòng trên excel
4. Các cột Excel không xuất hiện trên giấy xử lý thế nào: tạm thời cứ để trống đi rồi xử lí sau
7. ảnh trong pdf chất lượng y như tao gửi cho mày hồi nãy á 
12. telegram đang làm theo hướng nhân viên gửi ảnh lên xong bot đến server/pc ... luôn á dùng workflow đó đi, khi nhân viên bấm sửa thì sẽ sửa trên telegram luôn đi rồi sau cải tiến sau
15. cấu trúc thực tế giống v

Q1. PDF là scan ảnh hay PDF text/image?:
Q2. Tất cả page đều portrait?:
Q3. Ảnh có bị nghiêng/xoay không?:
Q4. Chữ có thường đè lên đường kẻ không?:
Q5. Ghi chú có thể nhiều dòng không?:

Q6. Có Excel ground-truth tương ứng với các page cũ không?:
    Có/Không:
    Nếu có: khoảng bao nhiêu page?

Q7. "95% accuracy" muốn tính theo:
    A. field
    B. page
    C. character
    D. cả 3

Q8. Ghi chú:
    A. phải đúng nguyên văn
    B. tương đối đúng cũng được

Q9. Phải giữ dấu tiếng Việt:
    Có/Không

Q10. Có database/master list mã đơn hàng/mã bản vẽ không?:
    Có/Không

Q11. File Excel trong screenshot có phải template production thật không?:
    Có/Không

Q12. Telegram:
    PDF / JPG / PNG / tất cả

Q13. PC chạy bot có IP/public domain không?:
    Có/Không/Chưa biết

Q14. Bạn muốn nhân viên:
    A. upload PDF
    B. upload từng ảnh
    C. cả hai

Q15. Khi xử lý xong, Excel:
    A. trả file Excel về Telegram
    B. lưu vào folder/server
    C. cả hai


QC_OCR/
│
├── app/
│   ├── pdf_processor.py
│   ├── image_preprocess.py
│   ├── form_template.py
│   ├── qwen_ocr.py
│   ├── validator.py
│   ├── mapper.py
│   ├── excel_writer.py
│   └── telegram_bot.py
│
├── config/
│   ├── form_v1.json
│   ├── mapping.json
│   └── settings.json
│
├── data/
│   ├── input/
│   ├── pages/
│   ├── crops/
│   ├── results/
│   ├── reviewed/
│   └── output/
│
├── evaluation/
│   ├── ground_truth/
│   └── reports/
│
├── logs/
│
├── requirements.txt
└── main.py


import sys
import json
import re
from pathlib import Path

import torch
from PIL import Image

from transformers import (
    AutoProcessor,
    Qwen3VLForConditionalGeneration,
    BitsAndBytesConfig,
)


MODEL_ID = "Qwen/Qwen3-VL-8B-Instruct"

# RTX 3050 6GB:
# Chừa VRAM cho Windows + vision + KV cache.
GPU_MEMORY = "5GiB"
CPU_MEMORY = "24GiB"


OCR_PROMPT = r"""
Bạn là hệ thống OCR chuyên đọc biểu mẫu sản xuất viết tay bằng tiếng Việt.

Hãy đọc TOÀN BỘ biểu mẫu trong ảnh.

Mục tiêu:
- Đọc chính xác chữ viết tay.
- Giữ nguyên số, mã kỹ thuật, ký hiệu.
- Không tự sửa mã kỹ thuật thành từ có nghĩa.
- Không tự suy đoán nếu không nhìn rõ.
- Với ô không có dữ liệu: trả về null.
- Với chữ không chắc chắn: ghi giá trị đọc được tốt nhất và đánh dấu confidence thấp.
- Phân biệt rõ từng dòng trên biểu mẫu.
- Một dòng trên giấy tương ứng với một record.

Các trường cần tìm:

1. Ngày
2. Mã đơn hàng
3. Mã bản vẽ
4. Rev
5. Thời gian bắt đầu
6. Thời gian kết thúc
7. SL gia công
8. SL đạt
9. SL NG
10. Ghi chú

Ngoài các trường trên, nếu biểu mẫu có thông tin có giá trị khác như:
- STT
- Mã công việc
- Ca
- Nhân viên
- Máy
- mã kỹ thuật
- số lượng
- thời gian
- nội dung công việc
- thông tin sản xuất khác

thì cũng phải đọc và đưa vào "additional_fields".

YÊU CẦU QUAN TRỌNG:

- Không bỏ qua bất kỳ dòng nào có dữ liệu.
- Không bỏ qua chữ viết tay.
- Không tự thêm dữ liệu không xuất hiện trong ảnh.
- Không chuyển đổi mã kỹ thuật sang dạng khác.
- Giữ nguyên dấu tiếng Việt nếu đọc được.
- Giữ nguyên format thời gian nếu có thể.
- Nếu có nhiều dòng, tạo nhiều record.

Chỉ trả về JSON hợp lệ.
Không markdown.
Không giải thích ngoài JSON.

Format:

{
  "document": {
    "date": null,
    "employee": null,
    "additional_fields": {}
  },
  "rows": [
    {
      "stt": null,
      "order_code": null,
      "drawing_code": null,
      "revision": null,
      "start_time": null,
      "end_time": null,
      "processed_qty": null,
      "good_qty": null,
      "ng_qty": null,
      "note": null,
      "additional_fields": {},
      "confidence": {
        "overall": 0.0,
        "order_code": 0.0,
        "drawing_code": 0.0,
        "revision": 0.0,
        "start_time": 0.0,
        "end_time": 0.0,
        "processed_qty": 0.0,
        "good_qty": 0.0,
        "ng_qty": 0.0,
        "note": 0.0
      }
    }
  ]
}
"""


def check_environment():
    print("=" * 70)
    print("QWEN OCR ENVIRONMENT")
    print("=" * 70)

    print(f"PyTorch       : {torch.__version__}")
    print(f"CUDA build    : {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if not torch.cuda.is_available():
        print()
        print("ERROR: PyTorch chưa nhận NVIDIA GPU.")
        print("Hãy cài CUDA-enabled PyTorch trước.")
        print()
        sys.exit(1)

    print(f"GPU           : {torch.cuda.get_device_name(0)}")
    print(
        f"VRAM          : "
        f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
    )
    print("=" * 70)
    print()


def load_model():
    print("Loading processor...")

    processor = AutoProcessor.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
    )

    print("Processor loaded.")
    print()

    print("Loading Qwen3-VL-8B-Instruct in 4-bit...")
    print("GPU memory limit:", GPU_MEMORY)
    print("CPU memory limit:", CPU_MEMORY)
    print()

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    max_memory = {
        0: GPU_MEMORY,
        "cpu": CPU_MEMORY,
    }

    model = Qwen3VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        quantization_config=quant_config,
        device_map="auto",
        max_memory=max_memory,
        torch_dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    print()
    print("MODEL LOADED")
    print()

    return processor, model


def clean_json_text(text):
    """
    Lấy JSON từ output của model trong trường hợp model
    vô tình thêm ```json ... ```
    """

    text = text.strip()

    # Remove markdown code fence
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Tìm JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end >= 0:
        text = text[start:end + 1]

    return text.strip()


def run_ocr(image_path, processor, model):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy image: {image_path}"
        )

    print("=" * 70)
    print("OCR IMAGE")
    print("=" * 70)
    print("Image:", image_path)

    image = Image.open(image_path).convert("RGB")

    print("Image size:", image.size)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": str(image_path),
                },
                {
                    "type": "text",
                    "text": OCR_PROMPT,
                },
            ],
        }
    ]

    print("Preparing inputs...")

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    )

    # Qwen official example moves processor output to model device.
    inputs = inputs.to(model.device)

    print("Running model...")
    print()

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=1800,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
        )

    generated_ids_trimmed = [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(
            inputs.input_ids,
            generated_ids
        )
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    print()
    print("=" * 70)
    print("RAW MODEL OUTPUT")
    print("=" * 70)
    print(output_text)
    print()

    return output_text


def save_result(image_path, raw_output):
    image_path = Path(image_path)

    result_dir = Path("data/results")
    result_dir.mkdir(parents=True, exist_ok=True)

    clean_text = clean_json_text(raw_output)

    output_json = result_dir / f"{image_path.stem}.json"

    try:
        parsed = json.loads(clean_text)

        with open(
            output_json,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                parsed,
                f,
                ensure_ascii=False,
                indent=2,
            )

        print("=" * 70)
        print("JSON RESULT")
        print("=" * 70)
        print(json.dumps(
            parsed,
            ensure_ascii=False,
            indent=2,
        ))

        print()
        print("Saved:", output_json)

    except json.JSONDecodeError as e:
        print()
        print("=" * 70)
        print("WARNING: MODEL OUTPUT IS NOT VALID JSON")
        print("=" * 70)
        print(e)

        raw_file = result_dir / f"{image_path.stem}_raw.txt"

        with open(
            raw_file,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(raw_output)

        print("Raw output saved:", raw_file)


def main():
    if len(sys.argv) != 2:
        print()
        print("Usage:")
        print(
            'python qwen_ocr.py "D:\\path\\to\\image.png"'
        )
        print()
        sys.exit(1)

    image_path = sys.argv[1]

    check_environment()

    processor, model = load_model()

    raw_output = run_ocr(
        image_path,
        processor,
        model,
    )

    save_result(
        image_path,
        raw_output,
    )


if __name__ == "__main__":
    main()

