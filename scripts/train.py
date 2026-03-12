#!/usr/bin/env python
"""
YOLO11 训练脚本
用法: python scripts/train.py --config configs/train_config.yaml
"""
import argparse
from pathlib import Path
from ultralytics import YOLO
from src.utils.config import load_config, save_config

def main():
    parser = argparse.ArgumentParser(description="Train YOLO11 on fruit dataset")
    parser.add_argument('--config', type=str, default='configs/train_config.yaml',
                        help='Path to training config file')
    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)
    print("Loaded config:")
    print(config)

    # 初始化模型（自动下载预训练权重）
    model = YOLO(config['model'])

    # 开始训练
    results = model.train(
        data=config['data'],
        epochs=config['epochs'],
        imgsz=config['imgsz'],
        batch=config['batch'],
        device=config['device'],
        workers=config['workers'],
        project=config['project'],
        name=config['name'],
        exist_ok=config['exist_ok'],
        pretrained=config['pretrained'],
        optimizer=config['optimizer'],
        seed=config['seed'],
    )

    # 保存最终配置到实验目录（便于追溯）
    exp_dir = Path(config['project']) / config['name']
    save_config(config, exp_dir / 'train_config.yaml')
    print(f"Training completed. Results saved in {exp_dir}")

if __name__ == '__main__':
    main()