"""训练模块 - 同时支持目标检测和图片分类"""
from .trainer import DetectionTrainer, ClassificationTrainer, CVTrainer

__all__ = ["DetectionTrainer", "ClassificationTrainer", "CVTrainer"]