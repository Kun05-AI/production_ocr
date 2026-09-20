# Tích hợp với workflow n8n hiện tại

Workflow hiện tại đã có Telegram Trigger, tải media từ Telegram và pipeline Gemini OCR/rescue. File workflow hiện chứa hard-coded API key; cần rotate/revoke key đó và chuyển sang credential/secret trước khi đưa production.

## Nhánh mới

### PHOTO / JPG / PNG

Giữ:

`TG - Main Trigger -> ... -> Telegram - Download Image`

Sau `Telegram - Download Image`, thay đoạn Gemini OCR bằng HTTP Request tới local service:

`POST http://127.0.0.1:8000/ocr`

Body: multipart form-data, field `file`, binary data tải từ Telegram.

### DOCUMENT / PDF

Tạo nhánh riêng sau switch `PHOTO / DOCUMENT`:

`DOCUMENT -> Download Telegram File -> HTTP Local OCR -> Parse OCR JSON`

Không đưa PDF trực tiếp vào model. API local tự render từng page ở 300 DPI.

## Parse

API trả:

```json
{
  "filename": "...",
  "pages": [
    {
      "page": "...",
      "rows": [
        {
          "row_index": 1,
          "date": "...",
          "order_code": "..."
        }
      ],
      "validation": {
        "active_row_count": 4,
        "min_review_score": 72,
        "needs_review": true
      }
    }
  ]
}
```

n8n chỉ chịu trách nhiệm orchestration/Telegram/Google Sheets; không nhúng model Python trực tiếp vào workflow.

## QC Telegram

Đối với page/row có `needs_review=true`, n8n gửi kết quả + ảnh crop. Nút sửa nên thao tác trên một `review_id` duy nhất, lưu trạng thái vào Sheet/DB trước khi ghi Sheet 05.

## Excel

Tất cả file gửi vào đều ghi chung một workbook. Sheet 05 production phải được cung cấp ở Phase Excel Integration; các column không có trên giấy giữ nguyên blank. Formula/công thức của workbook gốc tuyệt đối không được phá khi append.
