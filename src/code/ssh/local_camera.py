import cv2
import requests
import numpy as np

# 云端服务地址（因为做了端口转发，所以用本地地址）
SERVER_URL = "http://127.0.0.1:8000/predict"


def send_frame_to_cloud(frame):
    """发送一帧到云端推理"""
    # 压缩图片，减少传输量（质量80%）
    _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

    try:
        files = {'file': ('image.jpg', img_encoded.tobytes(), 'image/jpeg')}
        response = requests.post(SERVER_URL, files=files, timeout=1.0)
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None


# 打开本地摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("🚀 开始实时检测，按 'q' 退出")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 发送到云端
    result = send_frame_to_cloud(frame)

    # 如果有检测结果，画框
    if result and 'detections' in result:
        for det in result['detections']:
            x1, y1, x2, y2 = map(int, det['bbox'])
            label = f"{det['class']} {det['confidence']:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 显示画面
    cv2.imshow('Cloud YOLO Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()