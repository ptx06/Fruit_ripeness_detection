"""YOLO模型封装模块"""
from typing import Dict, Any, Optional
from ultralytics import YOLO


class YOLOModel:
    """
    YOLO11模型封装类
    提供统一的模型接口，支持训练、验证和推理
    """
    
    def __init__(self, model_path: str = "yolo11n.pt"):
        """
        初始化YOLO模型
        
        Args:
            model_path: 预训练模型路径或模型名称
        """
        self.model = YOLO(model_path)
        self.model_path = model_path
        self.class_names = self.model.names
    
    def train(
        self,
        data: str,
        epochs: int = 50,
        imgsz: int = 640,
        batch: int = 16,
        device: int = 0,
        workers: int = 8,
        project: str = "experiments",
        name: str = "train",
        exist_ok: bool = True,
        pretrained: bool = True,
        optimizer: str = "auto",
        seed: int = 42,
        **kwargs
    ) -> Any:
        """
        训练模型
        
        Args:
            data: 数据集配置文件路径
            epochs: 训练轮数
            imgsz: 输入图像尺寸
            batch: 批次大小
            device: GPU设备ID (-1表示CPU)
            workers: 数据加载线程数
            project: 实验保存目录
            name: 实验名称
            exist_ok: 是否允许覆盖已存在目录
            pretrained: 是否使用预训练权重
            optimizer: 优化器类型
            seed: 随机种子
            
        Returns:
            训练结果对象
        """
        results = self.model.train(
            data=data,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            workers=workers,
            project=project,
            name=name,
            exist_ok=exist_ok,
            pretrained=pretrained,
            optimizer=optimizer,
            seed=seed,
            **kwargs
        )
        return results
    
    def validate(self, data: str, **kwargs) -> Any:
        """
        验证模型
        
        Args:
            data: 数据集配置文件路径
            
        Returns:
            验证结果对象
        """
        results = self.model.val(data=data, **kwargs)
        return results
    
    def predict(
        self,
        source: Any,
        imgsz: int = 640,
        conf: float = 0.25,
        iou: float = 0.7,
        **kwargs
    ) -> Any:
        """
        推理预测
        
        Args:
            source: 输入源（图片路径、图片数组、视频路径等）
            imgsz: 输入图像尺寸
            conf: 置信度阈值
            iou: NMS IoU阈值
            
        Returns:
            预测结果对象
        """
        results = self.model.predict(
            source=source,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            **kwargs
        )
        return results
    
    def export(
        self,
        format: str = "onnx",
        **kwargs
    ) -> str:
        """
        导出模型
        
        Args:
            format: 导出格式 (onnx, torchscript, engine等)
            
        Returns:
            导出模型的路径
        """
        path = self.model.export(format=format, **kwargs)
        return str(path)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_path": self.model_path,
            "class_names": self.class_names,
            "num_classes": len(self.class_names) if self.class_names else 0,
            "model_type": self.model.task
        }
    
    def save(self, path: str) -> None:
        """
        保存模型权重
        
        Args:
            path: 保存路径
        """
        self.model.save(path)