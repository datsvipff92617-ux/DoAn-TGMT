import cv2
import sys
from detector import VehicleDetector
from counter import VehicleCounter
from logger import Logger
import utils

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
MODEL_PATH = r"D:\DoAn TGMT\runs\detect\Ket_Qua_Huan_Luyen_ tối ưu YOLOv8n\improved_traffic_yolov8n\weights\best.pt" 
VIDEO_PATH = r"D:\DoAn TGMT\DoAn TGMT\traffic-monitoring-system\data\video_test.mp4"
OUTPUT_PATH = r"D:\DoAn TGMT\DoAn TGMT\traffic-monitoring-system\data\output3.mp4"

def main():
    print("\n🚀 KHỞI ĐỘNG HỆ THỐNG GIAO THÔNG (VIEW NGANG) 🚀")
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ LỖI: Không thể đọc video!")
        sys.exit()

    # 1. Đọc kích thước gốc
    w_orig = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h_orig = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # 2. XÁC ĐỊNH KÍCH THƯỚC MỚI SAU KHI XOAY 90 ĐỘ
    # Sau khi xoay 90 độ, Width mới = Height cũ, Height mới = Width cũ
    w_new, h_new = h_orig, w_orig
    
    # 3. Khởi tạo module
    detector = VehicleDetector(MODEL_PATH)
    
    # 4. ROI được tính trên kích thước đã xoay (w_new, h_new)
    # ROI_POINTS: Mở rộng tối đa chiều ngang để bắt xe sát lề
    ROI_POINTS = [
        (int(w_new * 0.02), int(h_new * 0.70)), # Top-Left: Lùi vào một chút để tránh nhiễu xa
        (int(w_new * 0.98), int(h_new * 0.70)), # Top-Right: Lùi vào một chút
        (int(w_new * 0.98), int(h_new * 0.95)), # Bottom-Right: Kéo sát mép phải
        (int(w_new * 0.02), int(h_new * 0.95))  # Bottom-Left: Kéo sát mép trái
    ]
        
    counter = VehicleCounter(ROI_POINTS)
    logger = Logger()
    
    # QUAN TRỌNG: Khởi tạo VideoWriter với (w_new, h_new)
    out = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w_new, h_new))

    print(f"🎥 Đang xử lý... Nhấn 'q' để dừng.")
    cv2.namedWindow("ITS Traffic Monitoring", cv2.WINDOW_NORMAL)

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break
            
            # Xoay ảnh để về view ngang
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE) 

            # Tracking & Vẽ ROI
            result = detector.track(frame)
            utils.draw_roi(frame, ROI_POINTS)

            if result.boxes.id is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                track_ids = result.boxes.id.int().cpu().tolist()
                class_ids = result.boxes.cls.int().cpu().tolist()

                for box, track_id, class_id in zip(boxes, track_ids, class_ids):
                    cls_name = detector.names[class_id]
                    x1, y1, x2, y2 = map(int, box)
                    cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

                    is_counted, in_roi = counter.count_vehicle(track_id, cls_name, cx, cy)
                    if is_counted: logger.write_log(cls_name, track_id)

                    box_color = (0, 0, 255) if in_roi else (0, 255, 0)
                    utils.draw_box(frame, box, color=box_color)
                    utils.draw_text_with_background(frame, f"ID:{track_id} {cls_name}", (x1, y1 - 10), bg_color=box_color)
                    cv2.circle(frame, (cx, cy), 5, box_color, -1)

            # Thống kê
            utils.draw_text_with_background(frame, "THONG KE", (20, 40), bg_color=(50, 50, 50))
            y_offset = 80
            for cls, count in counter.counts.items():
                utils.draw_text_with_background(frame, f"{cls.upper()}: {count}", (20, y_offset), text_color=(0, 255, 255))
                y_offset += 35

            out.write(frame) # Ghi frame đã xoay với kích thước đã chỉnh
            cv2.imshow("ITS Traffic Monitoring", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"\n🎉 HOÀN TẤT! Video tại: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()