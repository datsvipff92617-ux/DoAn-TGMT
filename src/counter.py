import cv2
import numpy as np

class VehicleCounter:
    def __init__(self, roi_points):
        self.roi_points = np.array(roi_points, np.int32)
        self.counted_ids = set() # Dùng 'set' để tra cứu nhanh hơn, chống lag khi xe quá đông
        self.counts = {"bus": 0, "car": 0, "motorbike": 0, "truck": 0}

    def count_vehicle(self, track_id, class_name, cx, cy):
        """Kiểm tra tâm xe nằm trong ROI và xử lý đếm"""
        is_counted = False
        inside_roi = cv2.pointPolygonTest(self.roi_points, (cx, cy), False) >= 0
        
        if inside_roi:
            if track_id not in self.counted_ids:
                self.counted_ids.add(track_id)
                
                # Cập nhật số lượng
                if class_name in self.counts:
                    self.counts[class_name] += 1
                else:
                    self.counts[class_name] = 1 # Bắt lỗi nếu lọt class lạ
                    
                is_counted = True
                
        return is_counted, inside_roi