# 🚦 Hệ Thống Giám Sát Giao Thông Thông Minh (ITS)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Streamlit-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/YOLO-v8-yellow.svg" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Tracking-ByteTrack-green.svg" alt="ByteTrack">
</div>

## 📖 Giới thiệu (Overview)
Đây là dự án Đồ án chuyên ngành **Thị giác máy tính**. Hệ thống có khả năng tự động nhận diện, bám vết (tracking) và đếm lưu lượng phương tiện giao thông (Xe máy, Ô tô, Xe tải, Xe buýt) thông qua camera giao thông theo thời gian thực (Real-time).

Dự án áp dụng mô hình phát hiện vật thể tiên tiến nhất **YOLOv8** kết hợp với thuật toán tracking đa mục tiêu **ByteTrack** để giải quyết triệt để bài toán chồng lấn phương tiện và mất dấu (occlusion) trong điều kiện giao thông đông đúc.

## 🚀 Hướng Dẫn Khởi Chạy (1-Click Run)

Để hệ thống thân thiện nhất với người dùng cuối, dự án đã được đóng gói dưới dạng tự động hóa trên môi trường Windows.

**BƯỚC 1:** Tải mã nguồn hoặc giải nén đồ án ra một thư mục.
**BƯỚC 2:** Click đúp chuột vào file **`START_DO_AN.bat`**.

Hệ thống sẽ tự động cấu hình môi trường, cài đặt các thư viện phụ thuộc (nếu chưa có) và khởi động trực tiếp giao diện Web Dashboard trên trình duyệt mặc định của bạn. Bạn không cần phải mở Terminal hay gõ bất kỳ dòng lệnh nào.

> **Lưu ý:** Máy tính của bạn cần cài đặt sẵn Python 3.8 trở lên.

## 📁 Cấu trúc Thư Mục (Project Structure)
Dự án được tổ chức theo chuẩn kiến trúc phần mềm AI chuyên nghiệp:

```text
Project_ITS/
│
├── START_DO_AN.bat            # File khởi chạy nhanh (Dành cho Windows)
├── app.py                     # File chính khởi động giao diện Web Streamlit
├── requirements.txt           # Danh sách các thư viện cần thiết
├── README.md                  # Tài liệu hướng dẫn sử dụng
│
├── config/                    # Thư mục chứa các cấu hình hệ thống
│   ├── hyperparameters.yaml   # (Tùy chọn) Cấu hình tham số mô hình
│   └── lanes_config.json      # (Tùy chọn) Tọa độ ROI thiết lập vùng đếm xe
│
├── data/                      # Thư mục chứa dữ liệu video và hình ảnh
│   ├── showcase_h264.mp4      # Video nén H.264 dùng cho chế độ Demo Replay
│   └── video_test.mp4         # Video mẫu để chạy thử thuật toán
│
├── models/                    # Thư mục chứa trọng số mô hình
│   ├── yolov8n_best.pt        # Trọng số YOLOv8 đã được tối ưu
│   └── yolov11n_best.pt       # (Mở rộng) Trọng số YOLOv11
│
├── pages/                     # Các trang con của Web App
│   └── 1_Phan_Tich.py         # Màn hình Phân tích Báo cáo Động (Dynamic Dashboard)
│
├── src/                       # Các module xử lý lõi (Core logic)
│   ├── __init__.py            
│   ├── counter.py             # Logic kiểm tra vùng ROI và chống đếm trùng lặp
│   ├── detector.py            # Khởi tạo mô hình YOLO và cấu hình Tracking
│   ├── logger.py              # Xử lý log dữ liệu xuất ra CSV
│   └── utils.py               # Các hàm phụ trợ (vẽ box, render text)
│
└── weights/                   # Thư mục lưu trữ định dạng mô hình export (TensorRT, ONNX...)
    └── best.engine            # (Tùy chọn) Model TensorRT tối ưu tốc độ
```

## ✨ Tính Năng Nổi Bật (Key Features)

1. **Giao Diện Web Đa Trang (Multi-page Web App):**
   - Không chạy qua màn hình đen Console mộc mạc, hệ thống được trang bị giao diện Web hiện đại, tương tác trực quan.
2. **AI Real-time Tracking:**
   - Sử dụng YOLOv8n kết hợp ByteTrack, nhận diện tốc độ cao với độ chính xác đếm xe đạt trên 98% ngay cả trong điều kiện ánh sáng phức tạp.
3. **Báo Cáo Động (Dynamic Analytics Dashboard):**
   - Trang phân tích sẽ tự động "lắng nghe" và cập nhật các biểu đồ tròn, biểu đồ cột dựa trên chính xác dữ liệu từ luồng AI vừa chạy. Tích hợp tính năng AI tự động viết nhận xét, xuất báo cáo (Insights).
4. **Trích Xuất Bằng Chứng (Snapshot Logging):**
   - Chụp lại và lưu trữ khung hình của từng xe ngay tại thời điểm đi qua vạch đếm, phục vụ đối soát và xuất file CSV dễ dàng.

---
*Đồ án được thực hiện nhằm đáp ứng trọn vẹn yêu cầu chuyên môn của môn học Thị giác máy tính.*
