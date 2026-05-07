#!/usr/bin/env python
"""
计算机视觉通用训练脚本
支持目标检测(YOLO)和图片分类(MobileNetV2)
用法: python scripts/train.py --config configs/train_config.yaml
"""
import argparse
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.fruit_detection.training import CVTrainer
from src.fruit_detection.utils import load_config


def main():
    parser = argparse.ArgumentParser(description="Computer Vision Training Script")
    parser.add_argument(
        '--config', 
        type=str, 
        default='configs/train_config.yaml',
        help='Path to training config file'
    )
    args = parser.parse_args()

    # 加载配置
    print(f"📥 加载配置文件: {args.config}")
    config = load_config(args.config)
    
    task_type = config.get('task_type', 'detection')
    print(f"✅ 任务类型: {task_type}")
    print(f"✅ 配置加载完成")
    
    # 创建训练器并执行训练
    print(f"\n🚀 初始化训练器...")
    trainer = CVTrainer(config)
    
    print(f"\n🔬 开始训练...")
    exp_dir = trainer.run()
    
    print(f"\n🎉 训练完成!")
    print(f"📊 实验结果保存于: {exp_dir}")


if __name__ == '__main__':
    main()