"""模型模块"""
from .yolo_wrapper import YOLOModel
from .mobilenet_wrapper import MobileNetV2Model

__all__ = ["YOLOModel", "MobileNetV2Model"]