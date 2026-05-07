#!/usr/bin/env python
"""
计算机视觉通用评估脚本
支持目标检测(YOLO)和图片分类(MobileNetV2)
用法: python scripts/evaluate.py --config configs/train_config.yaml --weights runs/train/weights/best.pt
"""
import argparse
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import torch.nn as nn

from src.fruit_detection.models import YOLOModel, MobileNetV2Model
from src.fruit_detection.data import create_classification_data_loaders
from src.fruit_detection.utils import load_config


def main():
    parser = argparse.ArgumentParser(description="Computer Vision Evaluation Script")
    parser.add_argument(
        '--config', 
        type=str, 
        default='configs/train_config.yaml',
        help='Path to training config file'
    )
    parser.add_argument(
        '--weights', 
        type=str, 
        required=True,
        help='Path to model weights file'
    )
    parser.add_argument(
        '--split',
        type=str,
        default='val',
        choices=['val', 'test'],
        help='Dataset split to evaluate on (for classification)'
    )
    args = parser.parse_args()

    # 加载配置
    print(f"📥 加载配置文件: {args.config}")
    config = load_config(args.config)
    
    task_type = config.get('task_type', 'detection')
    print(f"✅ 任务类型: {task_type}")
    
    # 加载模型
    print(f"\n📦 加载模型权重: {args.weights}")
    
    if task_type == 'detection':
        model = YOLOModel(args.weights)
        print(f"✅ 模型加载完成")
        
        # 执行评估
        print(f"\n🔬 开始评估...")
        results = model.validate(data=config['data'])
        
        print(f"\n🎉 评估完成!")
        print(f"📊 mAP@0.5: {results.box.map50:.4f}")
        print(f"📊 mAP@0.5:0.95: {results.box.map:.4f}")
    
    elif task_type == 'classification':
        model = MobileNetV2Model.load(args.weights)
        model.set_device(config.get('device', 'cpu'))
        print(f"✅ 模型加载完成")
        
        # 创建数据加载器
        print(f"\n📊 创建数据加载器...")
        _, val_loader, test_loader = create_classification_data_loaders(
            data_dir=config['data_path'],
            batch_size=config['batch_size'],
            input_size=config['input_size'],
            workers=config['workers'],
            class_names=config.get('class_names')
        )
        
        loader = val_loader if args.split == 'val' else test_loader
        if loader is None:
            print(f"❌ {args.split}数据集不存在")
            return
        
        # 执行评估
        print(f"\n🔬 开始评估 {args.split}集...")
        criterion = nn.CrossEntropyLoss()
        loss, acc = model.validate(loader, criterion)
        
        print(f"\n🎉 评估完成!")
        print(f"📊 {args.split} Loss: {loss:.4f}")
        print(f"📊 {args.split} Accuracy: {acc:.4f}")


if __name__ == '__main__':
    main()