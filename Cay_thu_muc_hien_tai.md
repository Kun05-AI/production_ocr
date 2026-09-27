# CÂY THƯ MỤC DỰ ÁN PRODUCTION OCR (CẬP NHẬT MỚI NHẤT)

Tài liệu này ghi nhận cấu trúc thư mục và toàn bộ tệp tin thực tế trong dự án `D:\production_ocr` theo thời gian thực hiện tại (Cuối tháng 9/2026). Dự án đã mở rộng đáng kể phần đánh giá (Evaluation) và chuẩn bị Ground Truth cho Dev Set.

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
│   ├── template_registration.py.back       # Bản sao lưu code của template registration
│   └── validator.py                        # Kiểm tra logic nghiệp vụ (tổng số lượng, định dạng ngày, mã công đoạn)
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
│   ├── pages\                              # Ảnh thô cắt ra từ PDF (chưa can thiệp xử lý)
│   ├── preprocessed\                       # Kết quả của bước tiền xử lý ảnh và gỡ lỗi (debug) căn chỉnh
│   ├── crops\                              # Ảnh cắt nhỏ từng dòng dữ liệu (Row crops) phục vụ OCR
│   ├── ocr\                                # Kết quả nhận diện chữ trung gian từ mô hình Qwen-VL
│   ├── output\                             # Nơi lưu file kết quả cuối cùng (Excel, JSON xuất xưởng)
│   ├── reviewed\                           # Dữ liệu chờ hoặc đã qua nhân viên rà soát thủ công
│   └── validated\                          # Dữ liệu đã vượt qua các bộ quy tắc kiểm tra logic nghiệp vụ
│
├── evaluation\                             # KHU VỰC ĐÁNH GIÁ CHẤT LƯỢNG & GROUND TRUTH
│   ├── README.md                           # Hướng dẫn đánh giá độ chính xác (Char/Field/Row/Page accuracy)
│   ├── build_ground_truth.py               # Script tổng hợp dữ liệu ground truth từ nhiều nguồn
│   ├── make_ground_truth_contact_sheets.py # Script tạo ảnh tổng hợp (contact sheets) cho tập GT
│   ├── normalize_dev_annotations.py        # Kịch bản chuẩn hóa dữ liệu gán nhãn thủ công (dev annotations)
│   ├── render_dev_annotation_300dpi.py     # Chuyển đổi dữ liệu chú thích sang độ phân giải 300DPI
│   ├── select_ground_truth_dev.py          # Lọc chọn dữ liệu tập Dev để làm Ground Truth
│   ├── verify_phase3_phase4.py             # Script kiểm tra chéo độ ổn định giữa Phase 3 và 4
│   ├── ground_truth\                       # Dữ liệu chuẩn do con người gán nhãn
│   │   ├── manifest.json / page_annotations.jsonl # Bảng kê và nội dung gán nhãn toàn bộ trang
│   │   ├── contact_sheets\                 # Ảnh PDF/JPG overview các bộ trang gán nhãn theo từng nhân viên
│   │   ├── selection\                      # Dev set (Tập dữ liệu dùng để phát triển, 24 trang)
│   │   │   ├── dev_annotations.jsonl       # Dữ liệu Ground Truth chuẩn cho Dev Set
│   │   │   ├── dev_selection_index.csv     # Bảng tra cứu các trang được chọn
│   │   │   ├── DEV_ANNOTATION_GUIDE.md     # Hướng dẫn gán nhãn chuẩn
│   │   │   └── ground_truth_dev_24pages.pdf# File PDF nối 24 trang dev set
│   │   └── source_pages\                   # Hàng ngàn file ảnh gốc trích xuất của từng công nhân (1207, 1263,...)
│   ├── predictions\                        # Nơi lưu kết quả trích xuất tự động từ hệ thống để so sánh với GT
│   └── reports\                            # Nơi xuất báo cáo định lượng độ chính xác thực tế
│
├── gcck\                                   # Dữ liệu thực tế từ nhà máy (Gia Công Cơ Khí)
│   ├── BAO CAO\                            # Báo cáo sản xuất quét từ các công nhân/tổ đội (1207, 1236, 1263...)
│   └── GCCK_Production_QCD_Master_V2.0.0.xlsx # Bảng tính Excel Master quản lý QCD thực tế của nhà máy
│
├── Lí thuyết readme\                       # Tài liệu nghiên cứu lý thuyết và ghi chú hệ thống
│   ├── readme1.md                          # Tài liệu thiết kế hệ thống và luồng xử lý tổng thể ban đầu
│   └── readme2.md                          # Ghi chú kỹ thuật chi tiết về xử lý ảnh, OCR và mapping
│
├── models\                                 # Lưu trữ trọng số mô hình AI chạy Offline tại máy
│   └── Qwen3-VL-4B-Instruct\               # Mô hình Vision-Language Model cục bộ (Trọng số safetensors, config)
│
├── scripts\                                # Kịch bản tiện ích kiểm tra môi trường và vận hành
│   ├── check_runtime.py                    # Kiểm tra môi trường phần cứng: CUDA, VRAM GPU, PyTorch
│   └── download_model.ps1                  # Script PowerShell hỗ trợ tải mô hình từ HuggingFace về máy
│
├── tests\                                  # Thư mục chứa toàn bộ các kịch bản kiểm thử độc lập
│   ├── test_template_registration.py       # Kiểm thử thuật toán căn chỉnh mẫu biểu
│   └── test_qwen_4b_row.py                 # Kiểm thử tốc độ và độ chính xác OCR Qwen
│
├── logs\                                   # Thư mục lưu nhật ký vận hành hệ thống
├── prompts\                                # Thư mục chứa các file template prompt
│
├── Cây thư mục hiện tại.md                 # TÀI LIỆU NÀY (Cấu trúc dự án)
├── Cay_thu_muc_hien_tai.md                 # Bản sao của cây thư mục (để tránh lỗi font ký tự)
├── CLAUDE.md / CLAUDE.txt                  # Ghi chú nội bộ dành cho AI Assistant (Claude/Gemini)
├── N8N_INTEGRATION.md                      # Hướng dẫn tích hợp hệ thống OCR với nền tảng n8n
├── PHASES_DETAILED.md                      # Đặc tả kỹ thuật chi tiết toàn bộ các Phase và tiêu chuẩn nghiệm thu
├── phase detail.md                         # Bản sao tài liệu phân kỳ dự án
├── PHASE2_GT_DEV_WORKPLAN_10H.md           # Kế hoạch công việc phát triển Ground Truth cho Dev Set
├── production_ocr_PROJECT_CONTEXT_README(file dùng để promt tiếp).md # Ngữ cảnh bàn giao kỹ thuật của dự án
├── requirements.txt / requirements-lock.txt# Danh sách thư viện Python phụ thuộc cần cài đặt
├── SETUP_HOME_WINDOWS.md                   # Hướng dẫn cấu hình môi trường máy tính Windows chạy CUDA
├── WF04_01_CoCongNo.json                   # Workflow mẫu định dạng JSON để import vào n8n
│
└── Các script phụ trợ ở gốc (Verifiers):   # Scripts dọn dẹp và xác minh dữ liệu đánh giá
    ├── cleanup_gt_schema_metadata.py       # Dọn dẹp metadata/schema bị lỗi trong file jsonl GT
    ├── verify_content_match.py             # So khớp nội dung giữa các lần chuyển đổi
    ├── verify_gt_after_migration.py        # Kiểm tra tính toàn vẹn GT sau khi chuyển đổi schema
    ├── verify_gt_before_migration.py       # Kiểm tra GT trước khi di chuyển schema
    └── verify_identity.py                  # Xác minh tính đồng nhất định dạng
```

---

## 2. Điểm Nhấn Đáng Chú Ý Của Lần Cập Nhật Này

1. **Phân hệ Đánh Giá (Evaluation) Cực Kỳ Đồ Sộ**: 
   - Đã hình thành một quy trình đánh giá chuẩn mực tại thư mục `evaluation/`.
   - Có kịch bản tự động (`select_ground_truth_dev.py`, `render_dev_annotation_300dpi.py`) để sinh ra **Tập Dữ Liệu Phát Triển (Dev Set - 24 trang)**.
   - Thư mục `evaluation/ground_truth/` đã được bổ sung đầy đủ ảnh gốc của 5 người công nhân (1207, 1236, 1263, 1570, 1575) cùng nhãn gán thủ công JSONL (`dev_annotations.jsonl`).

2. **Bổ Sung Nhiều Script Verifiers Tại Gốc**: 
   - Xuất hiện loạt file `verify_*.py` và `cleanup_*.py` ở root, chuyên thực hiện validate JSONL và migration script. Chức năng chính là kiểm chứng dữ liệu nhãn `ground_truth` không bị hỏng trong quá trình chuẩn hóa.

3. **Context Chuyên Sâu Cho AI (CLAUDE / Prompt context)**:
   - File `CLAUDE.md`, `CLAUDE.txt` và `PHASE2_GT_DEV_WORKPLAN_10H.md` được bổ sung làm tài liệu "Instruction & Goal" (Chỉ dẫn và mục tiêu) cho các session hỗ trợ lập trình tự động.
   - Các file khóa phiên bản như `requirements-lock.txt` xuất hiện để cô lập môi trường phụ thuộc chặt chẽ hơn.
