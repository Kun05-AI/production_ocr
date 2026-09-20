# CÂY THƯ MỤC DỰ ÁN PRODUCTION OCR (CẬP NHẬT MỚI NHẤT)

Tài liệu này ghi nhận cấu trúc thư mục và toàn bộ tệp tin thực tế trong dự án `D:\production_ocr` sau khi đã được dọn dẹp, tái cấu trúc (tách riêng tầng `tests/`, gom `Lí thuyết readme/`, chuẩn hóa Form Registry và thêm phân vùng `evaluation/`).

---

## 1. Sơ Đồ Cây Thư Mục Tổng Quan

```text
D:\production_ocr\
│
├── .venv\                                  # Môi trường ảo Python (Virtual Environment)
│
├── app\                                    # Mã nguồn chính của Pipeline (Core Logic & Engines)
│   ├── __init__.py                         # Khai báo package Python
│   ├── api.py                              # FastAPI backend tiếp nhận file PDF/ảnh và trả kết quả JSON/Excel
│   ├── excel_writer.py                     # Ghi dữ liệu đã OCR và chuẩn hóa vào file Excel báo cáo
│   ├── form_registry.py                    # Quản lý danh mục biểu mẫu (Registry), nạp FormProfile & reference
│   ├── form_template.py                    # Định nghĩa cấu trúc khung biểu mẫu, tọa độ các cột ban đầu
│   ├── image_preprocess.py                 # Tiền xử lý ảnh: chuẩn hóa kích thước 3509x2481, xoay, cân bằng sáng
│   ├── mapper.py                           # Ánh xạ text OCR thô sang schema chuẩn theo mapping.json
│   ├── pdf_processor.py                    # Chuyển đổi PDF thành ảnh PNG phân giải cao (300 DPI)
│   ├── qwen_ocr.py                         # Module OCR tích hợp mô hình thị giác ngôn ngữ Qwen-VL
│   ├── row_detector.py                     # Nhận diện lưới hàng, xác định active rows và crop từng dòng
│   ├── template_registration.py            # Engine căn chỉnh ảnh hình học bằng thuật toán OpenCV ECC Affine
│   └── validator.py                        # Kiểm tra logic nghiệp vụ (tổng số lượng, định dạng ngày, mã công đoạn)
│
├── tests\                                  # Thư mục chứa toàn bộ các kịch bản kiểm thử độc lập
│   ├── __init__.py                         # Khai báo package test
│   ├── test_template_registration.py       # [Phase 4] Test runner căn chỉnh ảnh 7 trang T1 theo reference
│   └── test_qwen_4b_row.py                 # [Phase 6] Kiểm thử tốc độ và độ chính xác OCR Qwen trên từng hàng đã crop
│
├── config\                                 # Cấu hình hệ thống và Form Registry đa biểu mẫu
│   ├── mapping.json                        # Quy định ánh xạ trường dữ liệu trích xuất -> tên cột báo cáo Excel
│   ├── settings.json                       # Cấu hình tham số chung (đường dẫn, độ phân giải, runtime)
│   └── forms\                              # Danh mục định nghĩa form theo kiến trúc module hóa
│       ├── registry.json                   # Sổ đăng ký các form (T1, QC, ...) và phiên bản tương ứng
│       └── T1\
│           └── v1\
│               ├── form.json               # Cấu hình chi tiết form T1/v1 (kích thước, ROI, tham số ECC)
│               ├── reference.png           # Ảnh chuẩn gốc (calibration reference) dùng để căn chỉnh
│               └── REFERENCE_IMAGE_REQUIRED.txt # Tài liệu ghi chú yêu cầu về ảnh chuẩn
│
├── data\                                   # Dữ liệu phục vụ xử lý, dữ liệu trung gian và debug
│   ├── input\                              # Thư mục chứa file PDF tài liệu đầu vào
│   │   └── T1.pdf                          # File PDF báo cáo mẫu T1 dùng thử nghiệm
│   ├── pages\                              # Ảnh thô cắt ra từ PDF (chưa can thiệp xử lý)
│   │   ├── T1_page_001.png ... T1_page_007.png
│   ├── preprocessed\                       # Kết quả của bước tiền xử lý ảnh
│   │   ├── pages\                          # Ảnh đã chuẩn hóa kích thước 3509x2481, xoay đúng chiều
│   │   │   ├── T1_page_001.png ... T1_page_007.png
│   │   ├── preview\                        # Ảnh xem nhanh tổng hợp sau tiền xử lý
│   │   │   └── contact_sheet.jpg           # Ghép 7 trang sau tiền xử lý thành 1 ảnh preview
│   │   ├── preprocess_report.json          # Báo cáo JSON thông số kích thước, góc xoay của từng trang
│   │   ├── registration_debug\             # Kết quả kiểm thử căn chỉnh biểu mẫu (Phase 4)
│   │   │   ├── aligned\                    # Ảnh các trang sau khi căn chỉnh theo reference.png
│   │   │   ├── overlays\                   # Ảnh hòa trộn (overlay) để kiểm tra độ lệch quang học
│   │   │   ├── contact_sheet.jpg           # Bảng tổng hợp ảnh overlay 7 trang để kiểm tra bằng mắt
│   │   │   └── registration_report.json    # Báo cáo JSON kết quả ECC, độ lệch X, Y, góc xoay và độ co giãn
│   │   └── template_debug\                 # Kết quả lưu trữ của bộ căn chỉnh đường kẻ cũ
│   │       ├── overlays\                   # Ảnh overlay đường kẻ nhận diện được
│   │       ├── template_contact_sheet.jpg  # Contact sheet của bộ căn chỉnh cũ
│   │       └── template_calibration_report.json # Báo cáo tọa độ lưới kẻ ngang/dọc
│   ├── crops\                              # Ảnh cắt nhỏ từng dòng dữ liệu (Row crops) phục vụ OCR
│   │   └── T1_page_001_row_01.png ... row_04.png
│   ├── ocr\                                # Kết quả nhận diện chữ trung gian từ mô hình Qwen-VL
│   │   ├── T1_page_001_qwen_raw.txt        # Dữ liệu text thô trả về từ mô hình
│   │   ├── T1_page_001_qwen_result.json    # Dữ liệu parse JSON sau khi trích xuất
│   │   └── T1_page_001_row_0x_qwen_*       # Kết quả OCR chi tiết cho từng dòng crop
│   ├── output\                             # Nơi lưu file kết quả cuối cùng (Excel, JSON xuất xưởng)
│   ├── reviewed\                           # Dữ liệu chờ hoặc đã qua nhân viên rà soát thủ công
│   └── validated\                          # Dữ liệu đã vượt qua các bộ quy tắc kiểm tra logic nghiệp vụ
│
├── evaluation\                             # Đánh giá độ chính xác độc lập (Benchmark / Accuracy metrics)
│   ├── README.md                           # Hướng dẫn đánh giá độ chính xác (Char/Field/Row/Page accuracy)
│   ├── ground_truth\                       # Nơi lưu dữ liệu chuẩn con người gán nhãn (Ground Truth JSON)
│   ├── predictions\                        # Nơi lưu kết quả trích xuất tự động từ hệ thống
│   └── reports\                            # Nơi xuất báo cáo định lượng độ chính xác thực tế
│
├── gcck\                                   # Dữ liệu thực tế từ nhà máy (Gia Công Cơ Khí)
│   ├── BAO CAO\                            # Báo cáo sản xuất thực tế quét từ các công nhân/tổ đội
│   │   ├── 1207. NGUYEN TRUONG NHAN\       # Thư mục công nhân kèm các file scan T1.pdf -> T4.pdf
│   │   ├── 1236. BUI MINH HOANG\
│   │   ├── 1263. NGUYEN HUU THUONG\
│   │   ├── 1570. THACH SANG DO\
│   │   └── 1575. DAO DUC THINH\
│   └── GCCK_Production_QCD_Master_V2.0.0.xlsx # Bảng tính Excel Master quản lý QCD thực tế của nhà máy
│
├── models\                                 # Lưu trữ trọng số mô hình AI chạy Offline tại máy
│   └── Qwen3-VL-4B-Instruct\               # Mô hình Vision-Language Model cục bộ
│       ├── model-00001-of-00002.safetensors# Trọng số mô hình phần 1
│       ├── model-00002-of-00002.safetensors# Trọng số mô hình phần 2
│       ├── model.safetensors.index.json    # File chỉ mục trọng số
│       ├── config.json                     # Cấu hình kiến trúc mạng Qwen-VL
│       ├── tokenizer.json / vocab.json     # Bộ từ điển và tokenizer text
│       └── chat_template.json ...          # Cấu hình sinh prompt và tiền xử lý ảnh cho model
│
├── scripts\                                # Kịch bản tiện ích kiểm tra môi trường và vận hành
│   ├── check_runtime.py                    # Kiểm tra môi trường phần cứng: CUDA, VRAM GPU, PyTorch
│   └── download_model.ps1                  # Script PowerShell hỗ trợ tải mô hình từ HuggingFace về máy
│
├── Lí thuyết readme\                       # Tài liệu nghiên cứu lý thuyết và ghi chú ban đầu
│   ├── readme1.md                          # Tài liệu thiết kế hệ thống và luồng xử lý tổng thể ban đầu
│   └── readme2.md                          # Ghi chú kỹ thuật chi tiết về xử lý ảnh, OCR và mapping
│
├── logs\                                   # Thư mục lưu nhật ký vận hành hệ thống (trống / chờ ghi log)
├── prompts\                                # Thư mục chứa các file template prompt cho Qwen (trống / chờ nạp)
│
├── N8N_INTEGRATION.md                      # Hướng dẫn tích hợp hệ thống OCR với nền tảng tự động hóa n8n
├── PHASES_DETAILED.md                      # Đặc tả kỹ thuật chi tiết toàn bộ các Phase và tiêu chuẩn nghiệm thu
├── production_ocr_PROJECT_CONTEXT_README(file dùng để promt tiếp).md # Ngữ cảnh bàn giao kỹ thuật của dự án
├── requirements.txt                        # Danh sách thư viện Python phụ thuộc cần cài đặt
├── SETUP_HOME_WINDOWS.md                   # Hướng dẫn cấu hình môi trường máy tính Windows chạy CUDA
└── WF04_01_CoCongNo.json                   # Workflow mẫu định dạng JSON để import vào n8n
```

---

## 2. Chi Tiết Vai Trò Và Thay Đổi Của Từng Thành Phần

### 2.1. Thư mục `app/` (Chỉ chứa mã nguồn nghiệp vụ chạy chính)
- Đã được dọn dẹp sạch sẽ: toàn bộ các file kiểm thử `test_*.py` đã được chuyển sang thư mục riêng `tests/`.
- Không phụ thuộc vào script test khi đóng gói thành service chạy production.
- **`form_registry.py`**: Điểm nạp và quản lý hồ sơ biểu mẫu (`FormProfile`), liên kết giữa `registry.json`, `form.json` và ảnh chuẩn `reference.png`.
- **`template_registration.py`**: Module thuật toán ECC Affine Registration của OpenCV, tìm ma trận biến đổi 2x3 để căn ảnh về reference.
- **`row_detector.py`**: Cắt các dòng dữ liệu dựa theo geometry chuẩn của Form Profile sau khi trang đã được căn chỉnh.
- **`qwen_ocr.py`**: Thực hiện inference với mô hình Vision-Language để đọc dữ liệu chữ và số viết tay.

### 2.2. Thư mục `tests/` (Khu vực kiểm thử độc lập)
- **`test_template_registration.py`**: Kịch bản chạy căn chỉnh trên toàn bộ 7 trang của file T1, đo các chỉ số: hệ số tương quan ECC, độ lệch pixel $dx, dy$, góc xoay độ $\theta$, tỉ lệ scale/shear và xuất ảnh overlay.
- **`test_qwen_4b_row.py`**: Kịch bản kiểm tra khả năng nhận diện của Qwen trên từng ảnh dòng cắt mẫu trong `data/crops/`.

### 2.3. Thư mục `evaluation/` (Đánh giá chất lượng)
- Vừa được bổ sung nhằm phục vụ kiểm định khoa học ở các pha sau.
- Chứa hướng dẫn tại **`README.md`** về 4 chỉ số đo lường:
  1. **Character Accuracy**: Độ chính xác ở mức từng ký tự.
  2. **Field Accuracy**: Độ chính xác của từng ô/trường thông tin.
  3. **Row Accuracy**: Tỉ lệ cả hàng được trích xuất hoàn toàn chính xác.
  4. **Page Accuracy**: Tỉ lệ toàn bộ trang đạt chuẩn.
- Các thư mục con `ground_truth/`, `predictions/`, `reports/` sẵn sàng để lưu trữ bộ dữ liệu đối chuẩn thực tế.

### 2.4. Thư mục `Lí thuyết readme/`
- Gom các file tài liệu thiết kế ban đầu (`readme1.md`, `readme2.md`) vào một thư mục riêng biệt, giúp thư mục gốc của dự án gọn gàng và tập trung vào các tài liệu chỉ dẫn vận hành chính.

### 2.5. Thư mục `config/`
- Chuẩn hóa theo kiến trúc Form Registry (`config/forms/registry.json` và `config/forms/T1/v1/`).
- Đã loại bỏ các file cấu hình tạm cũ (`form_v1.json`, `form_v1_candidate.json`), chỉ giữ lại các cấu hình chuẩn hoá đang vận hành.
