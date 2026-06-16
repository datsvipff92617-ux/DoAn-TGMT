import cv2
import numpy as np

def draw_text_with_background(img, text, pos, text_color=(255, 255, 255), bg_color=(0, 0, 0), font_scale=0.7, thickness=2):
    """Vẽ chữ có nền mờ, có kiểm tra biên để không bị lỗi tọa độ"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    x, y = pos
    
    # 1. Kiểm tra tọa độ an toàn
    if y < 0 or x < 0: return

    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    
    # 2. Tính toán vùng cắt an toàn (không để bị âm)
    y1, y2 = max(0, y - text_height - 5), min(img.shape[0], y + 5)
    x1, x2 = max(0, x - 5), min(img.shape[1], x + text_width + 5)
    
    # 3. Chỉ vẽ nếu vùng cắt hợp lệ
    if y2 > y1 and x2 > x1:
        sub_img = img[y1:y2, x1:x2]
        white_rect = np.full(sub_img.shape, bg_color, dtype=np.uint8)
        res = cv2.addWeighted(sub_img, 0.5, white_rect, 0.5, 1.0)
        img[y1:y2, x1:x2] = res
    
    cv2.putText(img, text, pos, font, font_scale, text_color, thickness)

def draw_box(img, box, color=(0, 255, 0), thickness=2):
    """Vẽ khung bao quanh xe"""
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

def draw_roi(img, roi_points, color=(0, 200, 255), thickness=2):
    """Vẽ vùng đa giác ROI với hiệu ứng mờ bên trong"""
    pts = np.array(roi_points, np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts], isClosed=True, color=color, thickness=thickness)
    
    overlay = img.copy()
    cv2.fillPoly(overlay, [pts], color)
    cv2.addWeighted(overlay, 0.2, img, 0.8, 0, img)