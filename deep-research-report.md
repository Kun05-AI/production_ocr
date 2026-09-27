```markdown
# Tài liệu Lộ Trình & Nghiên cứu Dự án OCR Production

## Tóm tắt  
Tài liệu này trình bày lộ trình chi tiết cho việc xây dựng **hệ thống OCR production** dựa trên mô hình Qwen3-VL-8B-Instruct (chạy cục bộ qua LM Studio) tại công ty. Từ Pha P0 (khởi tạo dự án) đến Pha P14 (chuẩn bị fine-tuning tương lai), mỗi pha được mô tả với: **mục tiêu**, **đầu vào**, **đầu ra**, **tiêu chí chấp nhận**, **kiểm thử/benchmark**, và **artifact cần lưu**. Bên cạnh đó có so sánh các chiến lược đầu vào (cả hàng, từng trường, hybrid) với các chỉ số đo lường (độ chính xác, độ trễ, VRAM, độ phức tạp), ví dụ **JSON schema** cho kết quả có cấu trúc, và **cấu trúc thư mục lưu artifact** (logs, data/ocr/raw, data/ocr/parsed, docs/HANDOFF). Các quy tắc quan trọng (như không đoán dữ liệu, sử dụng [UNK] với ký tự khó đọc, không hard-code endpoint/model ID, tách biệt metadata cấp trang và dữ liệu hàng) cũng được nhấn mạnh. Mục tiêu cuối cùng là một pipeline end-to-end tích hợp Telegram/n8n → tiền xử lý ảnh → đăng ký form → phân đoạn hàng và trường → Qwen OCR → xác nhận đầu ra → xuất Excel → Telegram QC.

## P0 – Thiết lập ban đầu  
- **Mục tiêu:** Đảm bảo repository sẵn sàng, cài đặt môi trường phù hợp. Xác định các phụ thuộc cần thiết (Python, thư viện, LM Studio, llama.cpp hoặc client Qwen).  
- **Đầu vào:** Code hiện tại trong `D:\production_ocr`, hướng dẫn của nhóm, danh sách phụ thuộc (nếu có).  
- **Đầu ra:** Môi trường Python/PowerShell có thể chạy script; phiên bản LM Studio hoạt động; kết nối đến Qwen3-VL-8B-Instruct sẵn sàng.  
- **Các file/modules:** Kiểm tra tồn tại `requirements.txt`/`pyproject.toml`; `app/form_template.py`, `row_detector.py`, `form_registry`, `pdf_processor`, `image_preprocessing`, `segmentation`, `ocr (Qwen)`, `validator`, `mapper`, `excel_writer`, `telegram_integration`, `n8n_integration`.  
- **Tiêu chí chấp nhận:** Môi trường khởi động mà không lỗi quan trọng; LM Studio server được xác định (địa chỉ, port); có thể xác nhận model ID Qwen3-VL-8B-Instruct đang sẵn sàng.  
- **Kiểm thử:** Chạy thử `python -V`; kiểm tra `pip install -r requirements.txt`; thử yêu cầu đơn giản đến LM Studio (ví dụ dùng `curl` hoặc client llama.cpp) để xác nhận model phản hồi.  
- **Không được:** Hard-code đường dẫn chưa xác định (như endpoint `localhost:1234` mà chưa kiểm tra).  
- **Artifact:** Ghi lại kết quả kiểm tra (log cài đặt, thông tin GPU/VRAM, endpoint, model id) để đưa vào báo cáo hiện trạng.

## P1 – Môi trường OCR Baseline  
- **Mục tiêu:** Thiết lập client kết nối với LM Studio và mô hình Qwen3-VL-8B-Instruct. Đảm bảo có thể gửi một ảnh mẫu (page ảnh đơn) và nhận được phản hồi text thô.  
- **Đầu vào:** Ảnh mẫu đơn giản (ví dụ ảnh văn bản có ký tự rõ); thông tin model (Qwen3-VL-8B-Instruct Q4_K_M); endpoint LM Studio.  
- **Đầu ra:** Kịch bản Python thử nghiệm thành công, ghi nhận đầu ra gốc (raw) của Qwen. Ví dụ, dùng thư viện `llama.cpp` hoặc `openai`-client để gọi completion.  
- **Các file/modules:** Tạo file thử nghiệm như `tests/test_lmstudio_connectivity.py`. Không cần thay đổi code chính.  
- **Tiêu chí chấp nhận:** LM Studio server phản hồi trạng thái OK; client Python có thể lấy mẫu văn bản từ hình ảnh; dữ liệu thô (text) được lưu vào `data/ocr/raw/` (hoặc log). Không có lỗi OOM.  
- **Kiểm thử:** Thực thi kịch bản Python với `llm = Llama.from_pretrained(...); llm.create_chat_completion(..."Đọc văn bản từ ảnh...")`; xác nhận output là chuỗi JSON/text. Đo thời gian phản hồi.  
- **Không được:** Xử lý dữ liệu đầu vào theo cách làm mất thông tin (ví dụ resize quá nhỏ). Không gọi API bên ngoài (dù laptop có Internet, nhưng cần offline).  
- **Artifact:** Lưu output thô (`data/ocr/raw/sample_page.json`), log chạy model, các thông số (prompt version, model ID, thời gian thực hiện, VRAM tiêu thụ). 

## P2 – Chuẩn bị Ground Truth (GT) Dev  
- **Mục tiêu:** Hoàn tất annotation (ground truth) cho bộ Dev (24 trang). GT gồm metadata đầu trang (`member_name`, `week_number`, `team_name`), và dòng dữ liệu sản xuất (14 cột canonical).  
- **Đầu vào:** Mẫu form có 24 trang cần GT; file hướng dẫn annotation.  
- **Đầu ra:** File `dev_annotations.jsonl` đã điền đầy đủ 24 trang (được kiểm tra xác nhận). Metadata và dữ liệu hàng được tách biệt.  
- **Các file/modules:** `dev_annotations.jsonl`, `ground_truth_dev_24pages.pdf`, hướng dẫn `DEV_ANNOTATION_GUIDE.md`.  
- **Tiêu chí chấp nhận:** GT phải bao gồm đủ 14 trường theo hàng (theo schema đã định) cho mỗi dòng có sản lượng, cũng như metadata trang (không ghi `team_name` vào các trường hàng). Đánh giá ngẫu nhiên để chắc chắn chất lượng annotation.  
- **Kiểm thử:** So sánh GT mới với phiếu gốc; kiểm tra tính nhất quán schema, kiểu dữ liệu (số/chuỗi), xử lý null khi không có giá trị.  
- **Không được:** Không điền nháp hoặc thêm trường ngoài quy định (ví dụ không tự thêm `Tổ/Nhóm` vào 14 trường).  
- **Artifact:** Cập nhật `dev_annotations.jsonl`, phiên bản mới, và file summary báo lỗi (nếu có).

## P3 – Xử lý đầu vào (PDF/PNG/JPG)  
- **Mục tiêu:** Xác định contract của input: định dạng đầu vào (PDF hoặc hình ảnh), biến đổi khi cần.  
- **Đầu vào:** File PDF hoặc hình ảnh chụp form. (Môi trường có sẵn module `pdf_processor`?).  
- **Đầu ra:** Hình ảnh trang đơn đã chuẩn hóa (ví dụ định DPI, chuyển sang grayscale nếu cần, loại bỏ méo, crop margin).  
- **Các file/modules:** `data/input/` chứa PDF/PNG; code xử lý PDF (nếu có) thành image; module `image_preprocessing`.  
- **Tiêu chí chấp nhận:** Ảnh ra đủ độ phân giải (ví dụ ≥300 DPI), tỷ lệ khung hình ổn định, ảnh cân chỉnh gần hoàn chỉnh (ví dụ phẳng, xoay chuẩn). Không làm mất các chi tiết viết tay (không nén mạnh).  
- **Kiểm thử:** Dùng một số PDF mẫu, kiểm tra ảnh xuất ra (qua `file checkimages`) để đảm bảo chữ không bị vỡ/pixel. Đo thông số như width×height, DPI.  
- **Không được:** Tự ý giảm DPI quá mạnh hoặc crop sai khiến mất chữ.  
- **Artifact:** Lưu ảnh trang đầu xử lý (`data/crops/page_example.png`) để kiểm thử sau.

## P4 – Tiền xử lý ảnh  
- **Mục tiêu:** Nâng cao chất lượng OCR: loại nhiễu, xóa phông, tăng tương phản, chỉnh quang.  
- **Đầu vào:** Ảnh đã chuẩn hoá từ P3.  
- **Đầu ra:** Ảnh sạch hơn (clean) cho OCR, trong thư mục `data/preprocessed/`.  
- **Các file/modules:** Sử dụng/viết các hàm trong `image_preprocessing.py` (ví dụ threshold, deskew).  
- **Tiêu chí chấp nhận:** Ảnh sau xử lý không mất chữ, ngưỡng sáng/tối ổn định. Đảm bảo không phát sinh artefact.  
- **Kiểm thử:** So sánh OCR kết quả trước/sau tiền xử lý (ví dụ trên một image test: dùng tỉ lệ correct characters). Đánh giá thủ công xem chữ viết tay rõ hơn.  
- **Không được:** Quá lạm dụng (ví dụ threshold quá cao làm mất nét nhạt, hay hủy thông tin màu cần thiết).  
- **Artifact:** Lưu lại ảnh đã xử lý (qua thư mục `data/preprocessed/`) và log các bước xử lý (nếu script có lưu).

## P5 – Đăng ký mẫu (Form Registration)  
- **Mục tiêu:** Định vị form mẫu để ánh xạ tọa độ:  Đăng ký form (gắn khung hoặc khớp template) cho bản mẫu T1.  
- **Đầu vào:** Ảnh preprocessed; mẫu form (template) nếu có.  
- **Đầu ra:** Hệ quy chiếu nhất quán về toạ độ (ví dụ warp perspective) cho tất cả trang T1.  
- **Các file/modules:** `form_registry.py`, `FormTemplate` (nếu tồn tại). Kiểm tra xem `form_template.py` đã chuẩn hóa profile T1 chưa.  
- **Tiêu chí chấp nhận:** Mọi trang T1 đều được căn chuẩn theo template: góc, tỷ lệ chính xác. Các hàng và cột sẽ thẳng hàng.  
- **Kiểm thử:** Áp dụng đăng ký vào một số trang, sau đó vẽ lưới hàng/cột kiểm tra bằng mắt (có thể dùng overlay). Đo sai số pixel.  
- **Không được:** Thay đổi schema cột/hàng (không move lưới). Không sử dụng deep learning nếu đã có `FormTemplate`. Không tự tạo template mới trừ khi thực sự cần.  
- **Artifact:** Ảnh đã đăng ký (`data/preprocessed/registered/`), tọa độ khung để kiểm thử.

## P6 – Phân đoạn (Segmentation)  
- **Mục tiêu:** Chia trang thành 20 khung hàng (row) * 14 khung cột (field).  
- **Đầu vào:** Ảnh đã đăng ký (aligned page).  
- **Đầu ra:** Các ảnh con: mỗi hàng là ảnh riêng (`data/crops/<page>/row_001.png`, …); trong mỗi hàng, từng cột nhỏ `field_<col>.png`.  
- **Các file/modules:** `app/segmentation.py` (mới) dùng `FormTemplate.row_crop()` và `FormTemplate.field_crop()` cho T1/v1 đã cấu hình geometry sẵn. Tạo test đơn trang (ví dụ `tests/test_segmentation.py`) để đảm bảo `20x14` crop đúng vị trí.  
- **Tiêu chí chấp nhận:** Có đúng **20 ảnh hàng** (ngang) và **14 ảnh cột** trong mỗi hàng, không lẫn dữ liệu giữa các hàng. Chữ trong mỗi field crop phải đầy đủ (không cắt mất). Tất cả bounding box đều nằm trong trang.  
- **Kiểm thử:** Tạo ảnh ví dụ, chạy segmentation, kiểm tra tổng số crop và mẫu ngẫu nhiên vài crops xem chữ có đúng hàng, cột. (Có thể dùng OCR dòng chữ tĩnh trong hàng để test vị trí).  
- **Không được:** Không bỏ sót hàng nào (ngay cả nếu trống) – vẫn crop ra để giữ thứ tự. Không thay đổi `FormTemplate`.  
- **Artifact:** Lưu toàn bộ crops dưới `data/crops/`, tên có cấu trúc dễ hiểu (như `row_001/col_01.png`). Lưu log ghi cấp số hàng/cột của từng crop.

## P7 – OCR Qwen Baseline  
- **Mục tiêu:** Thiết lập pipeline OCR sơ bộ: từ ảnh crop (có thể nguyên hàng hoặc từng ô) sang text. Định rõ chiến lược đầu vào (toàn hàng, từng ô, hay hybrid).  
- **Đầu vào:** Các ảnh crop từ P6. Ví dụ bắt đầu với ảnh hàng đầu tiên hoặc một vài ô tiêu biểu.  
- **Đầu ra:** Output văn bản thô hoặc JSON thô, chưa validate. Mỗi hàng/ô có kết quả text hoặc JSON tạm thời. Lưu kết quả vào `data/ocr/raw/`.  
- **Các file/modules:** Tạo prompt cho Qwen (ví dụ `prompts/qwen_row_v001.txt`, `prompts/qwen_field_v001.txt`). Sử dụng llama.cpp/LlamaCpp client để gọi Qwen3-VL-8B-Instruct. Test cả 2 chiến lược: (A) gửi nguyên ảnh hàng, (B) gửi từng ảnh trường một.  
- **Tiêu chí chấp nhận:** Kết quả không lỗi cú pháp JSON (nếu có) và có chứa hầu hết text. So sánh thử output với GT trên vài mẫu. Đầu ra lưu định dạng JSON tạm (`data/ocr/raw/<page>_<row>.json`).  
- **Kiểm thử:** Chạy OCR cho ít nhất 1 trang (ví dụ page003), chuyển kết quả JSON về Python, parse so sánh với GT: đo CER, xem có sai trường nào rõ. Đo độ trễ cho mỗi chiến lược.  
- **Không được:** Giả định kết quả hoàn hảo – luôn phải có bước kiểm tra (như validator). Tránh prompt quá dài/bền (nếu nhiều ảnh) do giới hạn VRAM. Không in ra các thông tin nội bộ.  
- **Artifact:** Lưu raw JSON, logs (prompt dùng, thời gian), JSON đã parse vào `data/ocr/parsed/`. Ghi chú chiến lược đã thử (Row vs Field) và hiệu năng.

## P8 – Đầu ra có cấu trúc & Xác thực  
- **Mục tiêu:** Thiết kế định dạng đầu ra cuối cùng theo **schema JSON canonical**. Chỉ giữ 14 trường đã định cho mỗi hàng. Tách metadata trang (như `member_name`, `week_number`, `team_name`) ra riêng.  
- **Đầu vào:** Output từ P7. Ví dụ JSON thô, văn bản thô.  
- **Đầu ra:** JSON chuẩn cho mỗi hàng, với 14 thuộc tính canonical: `stt`, `date`, `order_code`, `drawing_code`, `revision`, `work_code`, `target_time`, `start_time`, `end_time`, `processed_qty`, `good_qty`, `ng_qty`, `process_detail`, `note`. (Ví dụ JSON schema mẫu bên dưới.) Metadata trang có thể lưu ở phần riêng.  
- **Ví dụ JSON Schema:**  
  ```json
  {
    "type": "object",
    "properties": {
      "stt":            {"type": "integer"},
      "date":           {"type": "string", "format": "date"},
      "order_code":     {"type": "string"},
      "drawing_code":   {"type": "string"},
      "revision":       {"type": "string"},
      "work_code":      {"type": "string"},
      "target_time":    {"type": "integer"},
      "start_time":     {"type": "string", "format": "time"},
      "end_time":       {"type": "string", "format": "time"},
      "processed_qty":  {"type": "integer"},
      "good_qty":       {"type": "integer"},
      "ng_qty":         {"type": "integer"},
      "process_detail": {"type": "string"},
      "note":           {"type": "string"}
    },
    "required": ["stt","date","order_code","drawing_code","revision","work_code",
                 "target_time","start_time","end_time","processed_qty",
                 "good_qty","ng_qty","process_detail","note"]
  }
  ```  
- **Tiêu chí chấp nhận:** JSON hợp lệ theo schema (dùng `jsonschema` để kiểm tra). Không có trường dư/thiếu. Ký tự mờ thành `[UNK]` hoặc `null`.  
- **Kiểm thử:** Tạo hàm validator: kiểm tra từng JSON với schema, tìm lỗi (loại giá trị sai, trường thiếu). Đo tỉ lệ JSON hợp lệ/trên tổng mẫu (JSON validity rate).  
- **Không được:** Chuyển data từ hàng khác, sửa đổi giá trị theo "kiến thức riêng" (ví dụ không dùng logic nghiệp vụ để chỉnh lỗi OCR). Xuất trường mới ngoài 14 hoặc metadata trang (như `team_name`). Tất cả metadata trang không nên nằm trong output JSON mỗi hàng.  
- **Artifact:** Lưu JSON đã validate vào `data/ocr/validated/`. Tạo `validator_report.md` nếu cần ghi lại các lỗi. Ghi chú các giả định (ví dụ dùng `[UNK]`, `null`).

## P9 – Đánh giá độ chính xác (Benchmark)  
- **Mục tiêu:** Sử dụng GT để đo **độ chính xác** của hệ thống OCR. Xác định các metric: Độ lỗi ký tự (CER), lỗi từ (WER), độ chính xác trường (đúng giá trị), độ chính xác dòng (tất cả trường của dòng đúng), tốc độ xử lý, VRAM.  
- **Đầu vào:** Kết quả OCR (validated JSON), ground truth (`dev_annotations.jsonl`).  
- **Đầu ra:** Báo cáo số liệu (CSV hoặc Markdown) ghi rõ: Character Accuracy (1-CER), Field Accuracy (phần trăm trường đúng), Row Accuracy, Page Accuracy, JSON validity rate, Retry rate (nếu có), Time/row, Time/page.  
- **Các chỉ số đo lường:**  
  - *CER/WER:* Sai số ký tự/từ (dùng chuẩn thống kê, phân tách token giống Whisper/SpeechBrain).  
  - *Field accuracy:* % trường đúng giá trị (kiểm định kiểu dữ liệu).  
  - *Row accuracy:* % dòng hoàn toàn đúng.  
  - *JSON validity:* % kết quả hợp lệ JSON.  
  - *Latency:* bình quân giây/truy vấn (row hoặc page).  
  - *VRAM usage:* max trong thực thi.  
  - *Error categories:* phân tích nguyên nhân sai (sai định dạng, missing, [UNK],...).  
- **Tiêu chí chấp nhận:** Chưa định sẵn ngưỡng (cần test trước). Đạt độ ổn định (ví dụ ưu tiên CER thấp trên GT). Đảm bảo tất cả trường ít nhất xuất kết quả.  
- **Kiểm thử:** Thực thi benchmark script so sánh từng hàng với GT, ghi CSV. Thực hiện ít nhất 3 lần để lấy số ổn định. Báo cáo vào `evaluation/benchmark_results.csv`.  
- **Không được:** Đánh giá cảm tính. Không đặt target trước mà chưa đo. Dùng [22†L293-L301] làm tham khảo: ưu tiên CER/WER trước, sau đó mở rộng đánh giá nâng cao.

## P10 – Xuất Excel  
- **Mục tiêu:** Chuyển kết quả JSON đã validate thành file Excel (hoặc CSV) xuất cho business. Mỗi trang ➔ một sheet, hoặc nối vào CSV.  
- **Đầu vào:** JSON hợp lệ (phân theo trang), có thể metadata trang (tên NV, tổ, tuần).  
- **Đầu ra:** Tệp `output.xlsx` hoặc `output.csv` trên folder `data/output/`, với đầy đủ cột tương ứng (14 trường và metadata). Bảo đảm traceability (giữ link đến `source json raw`).  
- **Các file/modules:** `excel_writer.py`. Kiểm tra nếu đã có mẫu mã (liên quan đến `sheet`, `csv`).  
- **Tiêu chí chấp nhận:** File Excel mở được, đúng định dạng cột, dữ liệu trùng khớp JSON. Sheet hoặc file ghi chú ngày/ID.  
- **Kiểm thử:** Mở file bằng Excel hoặc pandas, so sánh vài dòng với JSON. So sánh cấu trúc (headers).  
- **Không được:** Ghi đè raw JSON. Không để lẫn data từ các trang khác.  

## P11 – Tích hợp Telegram (Giai đoạn đầu)  
- **Mục tiêu:** (Lên kế hoạch giai đoạn sau) Cho phép nhận tài liệu từ Telegram và gửi kết quả QA.  
- **Đầu vào/Đầu ra:** (Không cần làm ngay – để P12 và P13).  

## P12 – Tích hợp n8n (Pipeline End-to-End)  
- **Mục tiêu:** (Sau khi pipeline core ổn định) Tự động hóa: Telegram → n8n trigger → OCR pipeline → Excel → gửi trả kết quả.  
- **Đầu vào/Đầu ra:** Tài liệu mô tả n8n workflow, config, script cho call Python.  
- **Kiểm thử:** Tạo sample n8n để chạy pipeline end-to-end.  
- **Không được:** Không thực hiện trước khi OCR core ổn định.  

## P13 – Ổn định hệ thống (Harden)  
- **Mục tiêu:** Cải thiện độ tin cậy: xử lý lỗi, timeout, retry, logging, config tách biệt, caching, tài nguyên.  
- **Đầu ra:** Phiên bản cuối cùng của script, cấu hình rõ ràng, hệ thống test tích hợp.  
- **Kiểm thử:** Đóng gói, chạy test end-to-end, stress-test với nhiều ảnh/flows.  

## P14 – Lộ trình Fine-Tuning trong tương lai  
- **Mục tiêu:** Thu thập dữ liệu huấn luyện, đánh giá xem có cần fine-tune Qwen cho script đặc thù hay không.  
- **Đầu ra:** Chiến lược/đề xuất fine-tuning (nếu cần) dựa trên lỗi thực nghiệm (ví dụ LoRA với data viết tay).  
- **Lưu ý:** Chỉ thực hiện sau khi baseline đã được benchmark kỹ. Chỉ bắt đầu khi xác nhận bộ dữ liệu đủ chuẩn.

## So sánh chiến lược đầu vào (Bảng tổng hợp)

| Chiến lược         | Mô tả                                    | Độ chính xác (Ưu/Nhược)            | Độ trễ                   | VRAM                    | Độ phức tạp      |
|--------------------|------------------------------------------|-------------------------------------|--------------------------|-------------------------|------------------|
| **Nguyên hàng**    | Gửi cả ảnh hàng (20×~n chứ không cắt)    | Duy trì ngữ cảnh tốt, ít truy vấn    | Cao (một request lớn)    | Cao (model xử lý ảnh lớn)| Trung bình       |
| **Từng trường**    | Chia từng ô (14 hình/1 hàng)            | Chính xác cao cho mỗi ô riêng biệt  | Thấp/Middle (nhiều truy vấn nhỏ) | Thấp (ảnh nhỏ hơn) | Phức tạp (14 lần gọi) |
| **Hybrid (kết hợp)** | Kết hợp trên nhóm trường (n ví dụ)    | Cân bằng giữa độ chính xác và tốc độ | Trung bình              | Trung bình              | Trung bình cao   |

**Các chỉ số đo lường:** Sử dụng các metric: độ chính xác ký tự (CER), ký tự [UNK], từ bị thiếu; latency tính theo truy vấn; VRAM max; số lần gọi model (complexity). Mục tiêu so sánh: xác định trade-off giữa accuracy và hiệu năng.

## Các quy tắc chung

- Luôn **INSPECT FIRST** trước khi code. Đánh giá repository, version, endpoint, model.
- **REPORT TRƯỚC khi SỬA:** Ghi lại trạng thái hiện tại (module có/sẵn, thiếu).
- **Không tự ý thay đổi schema/chuyển logic lớn** (ví dụ thêm trường mới, thay đổi FormTemplate) mà chưa hỏi lại. Nếu cần, đánh dấu `DECISION REQUIRED`.
- **Không hard-code:** endpoint LM Studio, ID model, thông số chưa biết.
- **Prompt/logic Prompt:** Giữ rõ ràng theo ví dụ Alibaba: không suy diễn, blank→null, ký tự mờ→`?` hoặc `[UNK]`.
- **Không tin tưởng output mô hình:** Luôn validate JSON theo schema trước khi dùng.
- **Lưu trữ đầu ra thô:** Để phục vụ debug (thô và đã parse).
- **Tách metadata cấp trang và dữ liệu hàng:** Ví dụ `team_name`, `member_name`, `week_number` không nằm trong JSON mỗi hàng.
- **Kiểm tra mọi field/trường:** Không bỏ sót (nêu NULL nếu trống).
- **Cấu trúc thư mục:** Dùng `data/ocr/raw/`, `data/ocr/parsed/`, `logs/`, `docs/HANDOFF/`.

## Đề xuất cấu trúc thư mục lưu artifact

- `data/ocr/raw/`: Kết quả OCR thô (JSON từ model).  
- `data/ocr/parsed/`: Kết quả đã parse/validate.  
- `logs/`: File log các bước, thông tin model, alert.  
- `docs/HANDOFF/`: Báo cáo cuối mỗi ngày (ví dụ `YYYY-MM-DD_DAYn.md`).  
- `evaluation/`: Kết quả benchmark (.csv, .md).  
- `data/output/`: File Excel/CSV đầu ra.  

## Tóm lại

Pipeline end-to-end sẽ lần lượt là: **Telegram → n8n → Tiền xử lý hình ảnh → Đăng ký mẫu form → Phân đoạn hàng/trường → Gọi Qwen OCR (qua LM Studio) → Xác thực JSON → Xuất Excel → Telegram QC**. Các giai đoạn P0–P14 trên đảm bảo kiến trúc, kiểm thử, và khả năng nâng cấp (prompt version, fine-tuning) cho dự án hoàn thiện.  
```

```markdown
# PRODUCTION_OCR_AUTONOMOUS_EXECUTION_PROMPT.md

## Giới thiệu  
Bạn là AI engineer tự động, chịu trách nhiệm hoàn thiện hệ thống OCR production như đã mô tả trong **Tài liệu lộ trình** (`PRODUCTION_OCR_ROADMAP.md`). Nhiệm vụ của bạn là **tuân thủ quy trình**: inspect (kiểm tra) → báo cáo → lập kế hoạch → triển khai code → kiểm thử → đánh giá hiệu năng → lưu trữ kết quả → tự chuyển sang nhiệm vụ kế tiếp khi đạt tiêu chí. **Tuyệt đối** tuân thủ quy tắc: không làm gì ngoài nhiệm vụ, không giả định thiếu sót, không tự ý thay đổi kiến trúc hay schema.

### Quy trình tự động

1. **KIỂM TRA BAN ĐẦU**: Đọc kỹ *ROADMAP*. Chưa sửa code.  
   - **Mục tiêu:** Hiểu rõ trạng thái repository `D:\production_ocr`.  
   - **Công việc:** Liệt kê cây thư mục hiện tại, các module, môi trường (Python version, thư viện). Kiểm tra file config liên quan (endpoint LM Studio, model ID nếu có).  
   - **Kết quả yêu cầu:** Tạo file báo cáo `CURRENT_STATE.md` (hoặc tương đương) với các mục: (A) Cây thư mục hiện tại; (B) Module chức năng đã có/đang hoạt động; (C) Module còn thiếu/cần viết; (D) Có thể tái sử dụng module nào; (E) Module cũ của OCR (nếu có) cần giữ hoặc loại; (F) Phụ thuộc hiện có; (G) Phiên bản Python; (H) Địa chỉ LM Studio server (nếu tìm được); (I) Model ID (nếu biết); (J) Những khác biệt giữa repository và roadmap.  
   - **Tiêu chí:** Báo cáo phải đầy đủ (như trên). Nếu có thông tin chưa rõ, ghi thành `UNKNOWN: ...` hoặc tạo file `BLOCKERS.md` liệt kê các phần không rõ (không đoán).  

2. **XÁC ĐỊNH MÔI TRƯỜNG KẾT NỐI (P1)**: Sau khi inspect và báo cáo, tiến hành cài đặt/testing.  
   - **Mục tiêu:** Xác nhận kết nối tới LM Studio và model Qwen3-VL-8B-Instruct.  
   - **Công việc:**  
     - Tìm (hoặc khởi động) local LM Studio server (ví dụ `127.0.0.1:port`). Không tự đoán port; kiểm tra config hoặc chạy thử lệnh phổ biến (`llama serve`, `llama-cli`).  
     - Viết script Python thử: ví dụ sử dụng `llama_cpp` hoặc `openai` để gọi một yêu cầu đơn giản (chat completion) với một ảnh đơn giản.  
     - Ghi nhận đầu ra (store raw output).  
   - **Tiêu chí:** LM Studio phản hồi (không OOM). Python client nhận được response (text/JSON). Lưu response thô vào `data/ocr/raw/test_output.json`.  
   - **Kiểm thử:** Chạy lệnh sample, ví dụ:  
     ```powershell
     python - << 'EOF'
     from llama_cpp import Llama
     llm = Llama.from_pretrained("Qwen3-VL-8B-Instruct-Q4_K_M.gguf", n_ctx=2048)
     res = llm.create_chat_completion(messages=[{"role":"user","content":"Đọc chữ trên ảnh: Xin ch\u00e0o"}], max_tokens=10)
     print(res.choices[0].message.content)
     EOF
     ```  
     (hoặc dùng `curl` nếu model expose API). Xác nhận có output.  
   - **Không được:** Hard-code endpoint/model; cố định port mà chưa kiểm tra.

3. **PHÂN ĐOẠN HÌNH ẢNH (P6)**: Xây dựng mã cắt hàng/cột (segmentation).  
   - **Mục tiêu:** Tách mỗi trang thành 20 hàng và 14 cột như quy định.  
   - **Công việc:**  
     - Tạo file `app/segmentation.py`. Dùng `FormTemplate` có sẵn: gọi `row_crop()` để cắt 20 hàng, rồi `field_crop()` cho mỗi hàng (14 trường).  
     - Tạo test đơn trang (ví dụ `tests/test_segmentation.py`) kiểm tra số lượng ảnh crop.  
   - **Tiêu chí:** Có 20 ảnh hàng và 14 ảnh cột trong mỗi hàng. Kết quả crop lưu trong `data/crops/<page>/...`.  
   - **Kiểm thử:** Chạy test segmentation cho `1207/T1/page003`. Kiểm tra: đúng 20 rows × 14 fields, bounding boxes khớp, không lẫn dòng.  

4. **OCR QWEN CƠ BẢN (P7)**: Chạy Qwen trên crops.  
   - **Mục tiêu:** Lấy văn bản đầu ra cho mỗi crop.  
   - **Công việc:**  
     - Tạo prompt test (ví dụ `prompts/qwen_ocr.txt`) trong code.  
     - Thử cả hai chiến lược: (A) gửi ảnh cả hàng, (B) gửi ảnh từng trường.  
     - Lưu raw output JSON vào `data/ocr/raw/`.  
   - **Tiêu chí:** JSON output phải parse được. Lưu kết quả thô cho mỗi query.  
   - **Kiểm thử:** Chạy OCR cho page003: một bên output hàng, một bên output fields. Đảm bảo mỗi query thành công (mô hình không lỗi). 

5. **XÁC THỰC & ĐỘI HÌNH ĐẦU RA (P8)**: Xử lý text và chuyển thành JSON cấu trúc.  
   - **Mục tiêu:** Định dạng kết quả OCR thành JSON 14 trường canonical (như schema mẫu).  
   - **Công việc:**  
     - Viết code parse JSON thô từ Qwen, mapping vào schema.  
     - Thực hiện validate JSON bằng JSON Schema (dùng thư viện `jsonschema`).  
     - Xử lý ký tự không đọc được: thay bằng `[UNK]` hoặc `null` nếu blank. Theo gợi ý, prompt mẫu khuyến cáo thay ký tự mờ bằng `?`.  
   - **Tiêu chí:** Mọi kết quả phải hợp lệ JSON theo schema. Required keys có đủ. Blank values→`null`, ký tự mờ→đặc biệt (ví dụ `?`).  
   - **Kiểm thử:** Dùng `jsonschema` kiểm thử sample JSON output. Chạy script so khớp với GT để đánh giá. 

6. **ĐÁNH GIÁ (P9)**: Đo hiệu năng và độ chính xác.  
   - **Mục tiêu:** Tính CER/WER và accuracy các cấp (field, row, page). Theo khuyến nghị, CER/WER là cơ sở.  
   - **Công việc:**  
     - Viết script so sánh output với `dev_annotations.jsonl`. Ghi CSV kết quả.  
     - Tính tỉ lệ valid JSON, CER, field-accuracy, row-accuracy, thời gian/truy vấn.  
   - **Tiêu chí:** Nắm được baseline accuracy và performance.  
   - **Kiểm thử:** Kết quả benchmark file (`evaluation/benchmark_results.csv`). Đảm bảo metrics có ý nghĩa (vd: xác định score).  

7. **TÀI LIỆU CUỐI NGÀY (HANDOFF)**: Kết thúc ngày làm việc.  
   - **Mục tiêu:** Ghi báo cáo tổng kết (Handoff Report).  
   - **Công việc:**  
     - Tạo file `docs/HANDOFF/2026-09-<ngày>_DAY1.md` với nội dung: mục tiêu, kết quả đã làm, file tạo/sửa, test, lỗi, quyết định, công việc chưa hoàn thành, gợi ý task tiếp theo.  
     - Đưa tất cả artifact quan trọng (JSON, logs, benchmark) vào thư mục `docs/HANDOFF/`.  
   - **Tiêu chí:** Báo cáo rõ ràng, đầy đủ như mẫu yêu cầu.  

### Lịch trình ngày làm việc (10 giờ)

```mermaid
timeline
    title Ngày 1 (08:00–18:00)
    08:00: KHỞI ĐỘNG & KIỂM TRA MÔI TRƯỜNG
    09:00: THỬ KẾT NỐI LM STUDIO
    10:00: TEST CẮT ẢNH (P6)
    11:00: THỬ QWEN OCR (P7) trên sample
    12:00: GIẢI LAO
    13:00: XỬ LÝ KẾT QUẢ OCR (P8)
    14:00: XÁC THỰC & KIỂM TRA JSON
    15:00: CHẠY BENCHMARK & ĐO METRIC (P9)
    16:00: SÁNG TẠO VÀO BÁO CÁO (Handoff)
    17:00: BUFFER TIME / HOÀN THIỆN
    18:00: KẾT THÚC NGÀY 1
```

| Giờ        | Nội dung công việc chính                                 |
|------------|----------------------------------------------------------|
| 08:00–09:00 | Inspect repo & thiết lập môi trường, xác định endpoint    |
| 09:00–10:00 | Kiểm tra kết nối LM Studio (health check, test model)     |
| 10:00–11:00 | Xây test segmentation (20 row ×14 col)                    |
| 11:00–12:00 | Tạo prompt Qwen, thử OCR trên crops đầu tiên               |
| 12:00–13:00 | Nghỉ trưa                                                |
| 13:00–14:00 | Xử lý đầu ra OCR: parse, chuyển thành JSON cấu trúc        |
| 14:00–15:00 | Validate JSON, sửa lỗi nhỏ (đảm bảo theo schema)           |
| 15:00–16:00 | Chạy benchmark so sánh với GT (tính CER, accuracy)         |
| 16:00–17:00 | Ghi nhận kết quả, chuẩn bị báo cáo Handoff                 |
| 17:00–18:00 | Hoàn thiện báo cáo, buffer, sẵn sàng sang ngày tiếp theo    |

**Lưu ý:** Nếu hoàn thành mục tiêu sớm, tiếp tục sang mục tiêu kế tiếp trong lộ trình. Nếu gặp khó khăn hoặc thiếu thông tin, ghi lại **BLOCKERS.md** và dừng lại không đoán. Chỉ chuyển tiếp khi tiêu chí hiện tại đã đạt.

**Không được phép:**  
- Thêm trường mới vào JSON không theo hướng dẫn.  
- Sửa lỗi content (spellings) theo ý định riêng.  
- Đổi cấu trúc file hay xóa code cũ trước khi đảm bảo không ảnh hưởng.  
- Tự ý chỉnh sửa hệ thống Telegram/n8n nếu chưa xong OCR.  
- Tự tạo prompt thừa, chỉ làm theo yêu cầu.  

## Tiếp theo  

Sau khi hoàn thành Day 1, tiếp tục Day 2 theo lộ trình: tập trung vào cải thiện prompt (prompt engineering) và tích hợp sâu (validation, retry). Luôn cập nhật báo cáo cuối mỗi ngày. Chúc bạn thành công!  
```

