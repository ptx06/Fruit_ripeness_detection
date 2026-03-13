import cv2
import numpy as np
from ultralytics import YOLO
from typing import List
import os
import uuid
from datetime import datetime

from models import FruitDetection, DetectionResult

class FruitDetectionService:
    def __init__(self, model_path: str = "best.pt"):
        """初始化水果检测服务"""
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载YOLO模型"""
        try:
            # 首先尝试加载训练好的模型
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"✅ 加载训练模型: {self.model_path}")
            else:
                # 如果没有训练好的模型，使用预训练模型
                self.model = YOLO("yolo11n.pt")
                print("⚠️ 使用预训练模型，建议先训练水果检测模型")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            # 使用预训练模型作为备用
            self.model = YOLO("yolo11n.pt")
    
    async def detect_fruit(self, image_path: str) -> DetectionResult:
        """检测水果成熟度"""
        if not self.model:
            raise Exception("模型未加载")
        
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise Exception("无法读取图像文件")
        
        # 使用YOLO进行检测
        results = self.model(image)
        
        # 解析检测结果
        detections = []
        result_image = image.copy()
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 获取检测信息
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # 创建检测结果
                    detection = FruitDetection(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=[x1, y1, x2, y2]
                    )
                    detections.append(detection)
                    
                    # 在图像上绘制检测结果
                    self._draw_detection(result_image, detection)
        
        # 保存结果图像
        result_filename = f"result_{uuid.uuid4()}.jpg"
        result_path = os.path.join("results", result_filename)
        cv2.imwrite(result_path, result_image)
        
        return DetectionResult(
            id=str(uuid.uuid4()),
            filename=os.path.basename(image_path),
            detections=detections,
            result_image_url=f"/results/{result_filename}",
            timestamp=datetime.now()
        )
    
    def _draw_detection(self, image: np.ndarray, detection: FruitDetection):
        """在图像上绘制检测结果"""
        x1, y1, x2, y2 = detection.bbox
        
        # 根据类别设置颜色
        color_map = {
            "fresh_apple": (0, 255, 0),      # 绿色 - 新鲜
            "ripe_apple": (255, 255, 0),     # 黄色 - 成熟
            "rotten_apple": (255, 0, 0),     # 红色 - 腐烂
        }
        
        color = color_map.get(detection.class_name, (255, 255, 255))
        
        # 绘制边界框
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        
        # 绘制标签
        label = f"{detection.class_name}: {detection.confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        
        # 标签背景
        cv2.rectangle(image, 
                     (int(x1), int(y1) - label_size[1] - 10),
                     (int(x1) + label_size[0], int(y1)),
                     color, -1)
        
        # 标签文字
        cv2.putText(image, label,
                   (int(x1), int(y1) - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    def get_model_info(self):
        """获取模型信息"""
        if not self.model:
            return {"status": "未加载"}
        
        return {
            "status": "已加载",
            "model_path": self.model_path,
            "classes": list(self.model.names.values()) if hasattr(self.model, 'names') else []
        }