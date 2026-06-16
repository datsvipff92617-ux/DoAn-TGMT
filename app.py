import streamlit as st
import cv2
import sys
import os
import time
import pandas as pd
import plotly.express as px
import tempfile
from collections import deque

# Thêm thư mục src vào đường dẫn để import
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from detector import VehicleDetector
from counter import VehicleCounter
from logger import Logger
import utils

# ================= CẤU HÌNH GIAO DIỆN =================
st.set_page_config(
    page_title="ITS Traffic Monitoring Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để làm đẹp giao diện
st.markdown("""
    <style>
    h1 {text-align: center; font-weight: 800;}
    </style>
""", unsafe_allow_html=True)

st.title("🚦 HỆ THỐNG GIÁM SÁT GIAO THÔNG THÔNG MINH (ITS)")
st.markdown("---")

# ================= SIDEBAR CÀI ĐẶT =================
with st.sidebar:
    st.header("⚙️ Cài đặt Hệ thống")
    
    # 1. Chọn Nguồn Video
    st.subheader("1. Nguồn Video")
    video_source = st.radio("Chọn nguồn:", ["Video Demo", "Tải video lên"])
    
    video_path = None
    if video_source == "Video Demo":
        base_dir = os.path.dirname(__file__)
        default_video = os.path.join(base_dir, "data", "video_test.mp4")
        flat_video = os.path.join(base_dir, "video_test.mp4")
        
        if os.path.exists(default_video):
            video_path = default_video
            st.success(f"Đã tải: {os.path.basename(default_video)}")
        elif os.path.exists(flat_video):
            video_path = flat_video
            st.success(f"Đã tải: {os.path.basename(flat_video)}")
        else:
            st.error("Không tìm thấy video demo!")
    else:
        uploaded_file = st.file_uploader("Tải lên file .mp4", type=['mp4', 'avi', 'mov'])
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False) 
            tfile.write(uploaded_file.read())
            video_path = tfile.name

    # 2. Chọn Mô hình
    st.subheader("2. Chọn Mô hình YOLO")
    # Hỗ trợ cả cấu trúc thư mục (Local) và cấu trúc phẳng (khi user kéo thả tất cả lên chung 1 chỗ trên GitHub)
    base_dir = os.path.dirname(__file__)
    
    default_model_v8 = os.path.join(base_dir, "models", "yolov8n_best.pt")
    if not os.path.exists(default_model_v8): default_model_v8 = os.path.join(base_dir, "yolov8n_best.pt")
        
    default_model_v11 = os.path.join(base_dir, "models", "yolov11n_best.pt")
    if not os.path.exists(default_model_v11): default_model_v11 = os.path.join(base_dir, "yolov11n_best.pt")
    
    model_choice = st.selectbox("Mô hình khả dụng:", [
        "YOLOv8n (Improved)",
        "YOLO11n (Improved)", 
        "Tùy chỉnh (Nhập đường dẫn)"
    ])
    
    model_path = ""
    if model_choice == "YOLOv8n (Improved)":
        model_path = default_model_v8
    elif model_choice == "YOLO11n (Improved)":
        model_path = default_model_v11
    else:
        model_path = st.text_input("Nhập đường dẫn file .pt:")

    # 3. Nút Bắt Đầu
    st.markdown("---")
    start_button = st.button("▶ BẮT ĐẦU CHẠY", use_container_width=True, type="primary")
    stop_button = st.button("⏹ DỪNG", use_container_width=True)

# ================= KHU VỰC CHÍNH (MAIN DASHBOARD) =================
# Khởi tạo các Session State để lưu dữ liệu
if 'counts' not in st.session_state:
    st.session_state.counts = {"bus": 0, "car": 0, "motorbike": 0, "truck": 0}
if 'log_history' not in st.session_state:
    st.session_state.log_history = deque(maxlen=50) # Lưu tối đa 50 log gần nhất
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = deque(maxlen=4) # Lưu 4 ảnh bằng chứng gần nhất
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

with st.sidebar:
    st.markdown("---")
    st.subheader("📥 Xuất Kết Quả")
    df_export = pd.DataFrame(list(st.session_state.log_history), columns=["Lịch sử sự kiện"])
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button("Tải File Export CSV", data=csv_data, file_name='ket_qua.csv', mime='text/csv')

if start_button:
    st.session_state.is_running = True
if stop_button:
    st.session_state.is_running = False

# Khu vực hiển thị KPI (3 cột)
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    fps_metric = st.empty()
with kpi2:
    total_metric = st.empty()
with kpi3:
    time_metric = st.empty()

st.markdown("---")

# Khu vực hiển thị Video & Bảng điều khiển phụ
col1, col2 = st.columns([7, 3])

with col1:
    st.subheader("📺 Camera Giám sát Real-time")
    video_placeholder = st.empty()

with col2:
    st.subheader("📊 Thống kê Phương tiện")
    chart_placeholder = st.empty()
    
    st.subheader("📋 Danh sách phương tiện")
    log_placeholder = st.empty()
    
    st.subheader("📸 Ảnh chụp phương tiện")
    snapshot_placeholder = st.empty()

# ================= LOGIC XỬ LÝ =================
if st.session_state.is_running and video_path and model_path:
    if not os.path.exists(model_path):
        st.sidebar.error(f"❌ Không tìm thấy mô hình: {model_path}")
    else:
        # Khởi tạo module
        detector = VehicleDetector(model_path)
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            st.error("❌ Không thể đọc luồng video!")
        else:
            w_orig = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h_orig = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Tự động xoay video nếu video gốc nằm ngang (như video_test.mp4)
            if w_orig > h_orig:
                w_new, h_new = h_orig, w_orig
                needs_rotation = True
            else:
                w_new, h_new = w_orig, h_orig
                needs_rotation = False
            
            # Khởi tạo Vùng đếm ROI
            ROI_POINTS = [
                (int(w_new * 0.02), int(h_new * 0.70)),
                (int(w_new * 0.98), int(h_new * 0.70)),
                (int(w_new * 0.98), int(h_new * 0.95)),
                (int(w_new * 0.02), int(h_new * 0.95))
            ]
            
            counter = VehicleCounter(ROI_POINTS)
            prev_time = time.time()
            
            # Vòng lặp xử lý video
            while cap.isOpened() and not stop_button:
                ret, frame = cap.read()
                if not ret:
                    st.info("Đã phát hết video.")
                    break
                
                # Cập nhật nút Stop
                if not st.session_state.is_running:
                    break
                
                start_time = time.time()
                
                
                # CHẠY Yolo: Tự động lật nếu video gốc bị ngang
                if needs_rotation:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    
                result = detector.track(frame)
                utils.draw_roi(frame, ROI_POINTS)
                
                new_logs = []
                
                if result.boxes.id is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    track_ids = result.boxes.id.int().cpu().tolist()
                    class_ids = result.boxes.cls.int().cpu().tolist()

                    for box, track_id, class_id in zip(boxes, track_ids, class_ids):
                        cls_name = detector.names[class_id]
                        x1, y1, x2, y2 = map(int, box)
                        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

                        # Đếm xe chuẩn
                        is_counted, in_roi = counter.count_vehicle(track_id, cls_name, cx, cy)

                        if is_counted: 
                            current_time_str = time.strftime("%H:%M:%S")
                            log_msg = f"[{current_time_str}] Phát hiện {cls_name.upper()} (ID: {track_id})"
                            st.session_state.log_history.appendleft(log_msg)
                            
                            # Cắt ảnh làm bằng chứng
                            try:
                                snap = frame_rgb[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
                                if snap.size > 0:
                                    st.session_state.snapshots.appendleft((log_msg, snap))
                            except Exception:
                                pass

                        box_color = (0, 0, 255) if in_roi else (0, 255, 0)
                        utils.draw_box(frame, box, color=box_color)
                        utils.draw_text_with_background(frame, f"ID:{track_id} {cls_name}", (x1, y1 - 10), bg_color=box_color)
                        cv2.circle(frame, (cx, cy), 5, box_color, -1)

                # Vẽ Text Thống kê góc trên (như code gốc)
                utils.draw_text_with_background(frame, "THONG KE TONG:", (20, 40), bg_color=(50, 50, 50))
                y_offset = 80
                total_current = 0
                for cls, cnt in counter.counts.items():
                    utils.draw_text_with_background(frame, f"{cls.upper()}: {cnt}", (20, y_offset), text_color=(0, 255, 255))
                    y_offset += 35
                    total_current += cnt
                
                # Convert frame từ BGR (OpenCV) sang RGB (Streamlit)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Tính FPS
                curr_time = time.time()
                process_time = curr_time - start_time
                fps = 1 / (curr_time - prev_time)
                prev_time = curr_time
                
                # Tối ưu hóa cực độ cho Streamlit Cloud: Chỉ cập nhật giao diện mỗi 5 frame
                if 'frame_count' not in locals():
                    frame_count = 0
                frame_count += 1
                
                # Cập nhật UI hình ảnh siêu mượt (30fps hoặc 15fps tùy máy)
                if frame_count % 2 == 0:
                    video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
                # Cập nhật Thống kê mỗi 10 frame để giao diện không bị treo
                if frame_count % 10 == 0:
                    fps_metric.metric("⚡ Tốc độ xử lý (FPS)", f"{fps:.1f}")
                    total_metric.metric("🚗 Tổng xe đi qua", f"{total_current}")
                    time_metric.metric("⏱️ Độ trễ (ms/frame)", f"{process_time*1000:.1f} ms")
                    
                    df_counts = pd.DataFrame(list(counter.counts.items()), columns=['Loại xe', 'Số lượng']).set_index('Loại xe')
                    chart_placeholder.bar_chart(df_counts, height=250)
                    df_logs = pd.DataFrame(list(st.session_state.log_history), columns=["Lịch sử sự kiện"])
                    log_placeholder.dataframe(df_logs, use_container_width=True, height=250)
                    
                    # Cập nhật Ảnh bằng chứng
                    if len(st.session_state.snapshots) > 0:
                        with snapshot_placeholder.container():
                            cols = st.columns(len(st.session_state.snapshots))
                            for i, (msg, snap) in enumerate(st.session_state.snapshots):
                                cols[i].image(snap, use_container_width=True)
            
            cap.release()

elif st.session_state.is_running and not video_path:
    st.sidebar.warning("Vui lòng chọn hoặc tải lên một video.")
