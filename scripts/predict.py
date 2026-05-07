#!/usr/bin/env python
"""
计算机视觉通用预测脚本
支持目标检测(YOLO)和图片分类(MobileNetV2)
用法: python scripts/predict.py --weights runs/train/weights/best.pt --image test.jpg
"""
import argparse
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import cv2
import torch
from torchvision import transforms

from src.fruit_detection.models import YOLOModel, MobileNetV2Model
from src.fruit_detection.utils import load_config


def main():
    parser = argparse.ArgumentParser(description="Computer Vision Prediction Script")
    parser.add_argument(
        '--weights', 
        type=str, 
        required=True,
        help='Path to model weights file'
    )
    parser.add_argument(
        '--image', 
        type=str, 
        required=True,
        help='Path to input image'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        default='configs/train_config.yaml',
        help='Path to config file'
    )
    parser.add_argument(
        '--conf', 
        type=float, 
        default=0.25,
        help='Confidence threshold (for detection)'
    )
    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)
    task_type = config.get('task_type', 'detection')
    
    # 加载模型
    print(f"📦 加载模型权重: {args.weights}")
    
    if task_type == 'detection':
        model = YOLOModel(args.weights)
        print(f"✅ 模型加载完成")
        print(f"📋 类别列表: {model.class_names}")
        
        # 执行预测
        print(f"\n🔍 检测图片: {args.image}")
        results = model.predict(source=args.image, conf=args.conf)
        
        # 解析结果
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                detections.append({
                    "class": model.class_names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy[0].tolist()
                })
        
        print(f"\n🎯 检测结果:")
        for i, det in enumerate(detections, 1):
            print(f"  {i}. {det['class']} - 置信度: {det['confidence']:.4f}")
        
        # 保存结果图片
        save_path = Path("prediction_result.jpg")
        results[0].save(str(save_path))
        print(f"\n💾 结果图片已保存: {save_path}")
    
    elif task_type == 'classification':
        model = MobileNetV2Model.load(args.weights)
        model.set_device('cuda' if torch.cuda.is_available() else 'cpu')
        
        class_names = config.get('class_names', ['class_0', 'class_1', 'class_2'])
        print(f"✅ 模型加载完成")
        print(f"📋 类别列表: {class_names}")
        
        # 加载并预处理图片
        print(f"\n📷 加载图片: {args.image}")
        img = cv2.imread(args.image)
        if img is None:
            print(f"❌ 无法加载图片: {args.image}")
            return
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((config['input_size'], config['input_size'])),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        img_tensor = transform(img)
        
        # 执行预测
        print(f"\n🔍 执行预测...")
        results = model.predict(img_tensor)
        
        # 解析结果
        predicted_class_idx = results['predicted_class']
        probabilities = results['probabilities']
        
        print(f"\n🎯 预测结果:")
        print(f"  预测类别: {class_names[predicted_class_idx]}")
        print(f"  置信度: {probabilities[predicted_class_idx]:.4f}")
        
        print(f"\n📊 各类别概率:")
        for idx, (class_name, prob) in enumerate(zip(class_names, probabilities)):
            print(f"  {class_name}: {prob:.4f}")


if __name__ == '__main__':
    main()