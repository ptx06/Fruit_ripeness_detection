# inference_server.py
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import cv2
import numpy as np
import uvicorn

app = FastAPI()

# 加载你训练好的模型（修改成你的模型路径）
model = YOLO("/root/autodl-tmp/coco128/runs/detect/train4/weights/best.pt")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 读取上传的图片
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 用YOLO推理
    results = model(img, imgsz=640)  # 保持640分辨率，又快又准

    # 提取检测结果（只返回必要信息，减少传输量）
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist()  # [x1,y1,x2,y2]
            })

    return {"detections": detections}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)