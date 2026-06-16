import csv
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="../logs", filename="traffic_log.csv"):
        os.makedirs(log_dir, exist_ok=True)
        self.filepath = os.path.join(log_dir, filename)
        
        # Khởi tạo file nếu chưa có
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Thời Gian", "Loại Phương Tiện", "ID Ghi Nhận"])

    def write_log(self, class_name, track_id):
        """Ghi dữ liệu ngay lập tức khi phát hiện xe qua ROI"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filepath, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([now, class_name.upper(), track_id])