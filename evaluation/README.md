# Evaluation

Mục tiêu benchmark: character accuracy, field accuracy, row accuracy và page accuracy.

Khuyến nghị lưu ground truth theo JSON cùng cấu trúc với OCR prediction. Sau đó chạy evaluator để tính cả 4 metric, không chỉ một điểm tổng.

Bộ dữ liệu hiện có 7 pages trong T1.pdf là sample để calibration layout; chưa coi nó là ground truth production.
