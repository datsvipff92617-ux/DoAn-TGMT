import os
from ultralytics import YOLO

class VehicleDetector:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Không tìm thấy file mô hình tại: {model_path}")
            
        print("⏳ Đang tải mô hình YOLO...")
        self.model = YOLO(model_path)
        self.names = self.model.names

    def track(self, frame):
        """Chạy ByteTrack để gán ID không bị mất dấu"""
        results = self.model.track(
            frame, 
            persist=True, 
            tracker="bytetrack.yaml", 
            conf=0.45,  # Loại bỏ các vật thể tự tin dưới 45%
            iou=0.5, 
            verbose=False # Tắt log rác
        )
        return results[0]