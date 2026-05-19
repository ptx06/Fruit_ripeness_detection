"""训练器模块 - 同时支持目标检测和图片分类"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import json

import torch
import torch.nn as nn

from src.fruit_detection.models import YOLOModel, MobileNetV2Model
from src.fruit_detection.data import create_classification_data_loaders
from src.fruit_detection.utils import save_config


class DetectionTrainer:
    """
    目标检测训练器 (YOLO)
    封装完整的训练流程，提供统一的训练接口
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化训练器
        
        Args:
            config: 训练配置字典
        """
        self.config = config
        self.model = None
        self.results = None
        
        self.exp_dir = Path(config['project']) / config['name']
        self.exp_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            file_handler = logging.FileHandler(self.exp_dir / 'training.log')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def init_model(self) -> None:
        """初始化YOLO模型"""
        self.logger.info(f"初始化YOLO模型: {self.config['model']}")
        self.model = YOLOModel(self.config['model'])
        self.logger.info(f"模型信息: {self.model.get_model_info()}")
    
    def train(self) -> None:
        """执行训练"""
        if self.model is None:
            self.init_model()
        
        self.logger.info("开始目标检测训练...")
        self.logger.info(f"训练配置: {self.config}")
        
        self.results = self.model.train(
            data=self.config['data'],
            epochs=self.config['epochs'],
            imgsz=self.config['imgsz'],
            batch=self.config['batch'],
            device=self.config['device'],
            workers=self.config['workers'],
            project=self.config['project'],
            name=self.config['name'],
            exist_ok=self.config['exist_ok'],
            pretrained=self.config['pretrained'],
            optimizer=self.config['optimizer'],
            seed=self.config['seed'],
        )
        
        self.logger.info("训练完成")
    
    def validate(self) -> Optional[Any]:
        """执行验证"""
        if self.model is None:
            self.logger.error("模型未初始化，请先调用 init_model()")
            return None
        
        self.logger.info("开始验证...")
        results = self.model.validate(data=self.config['data'])
        self.logger.info("验证完成")
        
        return results
    
    def save_config(self) -> Path:
        """保存配置到实验目录"""
        config_path = self.exp_dir / 'train_config.yaml'
        save_config(self.config, config_path)
        self.logger.info(f"配置已保存: {config_path}")
        return self.exp_dir
    
    def get_results(self) -> Optional[Any]:
        """获取训练结果"""
        return self.results
    
    def run(self) -> Path:
        """执行完整的训练流程"""
        self.init_model()
        self.train()
        return self.save_config()


class ClassificationTrainer:
    """
    图片分类训练器 (MobileNetV2)
    封装完整的训练流程，提供统一的训练接口
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化训练器
        
        Args:
            config: 训练配置字典
        """
        self.config = config
        self.model = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        self.history = None
        
        self.exp_dir = Path(config['project']) / config['name']
        self.exp_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            file_handler = logging.FileHandler(self.exp_dir / 'training.log')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def init_data(self) -> None:
        """初始化数据加载器"""
        self.logger.info(f"初始化数据加载器: {self.config['data_path']}")
        
        self.train_loader, self.val_loader, self.test_loader = create_classification_data_loaders(
            data_dir=self.config['data_path'],
            batch_size=self.config['batch_size'],
            input_size=self.config['input_size'],
            workers=self.config['workers'],
            augmentation=self.config.get('augmentation'),
            class_names=self.config.get('class_names')
        )
        
        self.logger.info(f"训练集样本数: {len(self.train_loader.dataset)}")
        self.logger.info(f"验证集样本数: {len(self.val_loader.dataset)}")
        if self.test_loader:
            self.logger.info(f"测试集样本数: {len(self.test_loader.dataset)}")
        
        self.logger.info(f"类别列表: {self.train_loader.dataset.class_names}")
    
    def init_model(self) -> None:
        """初始化分类模型"""
        self.logger.info(f"初始化模型: {self.config['model_name']}")
        
        self.model = MobileNetV2Model(
            num_classes=self.config['num_classes'],
            pretrained=self.config['pretrained'],
            model_name=self.config['model_name']
        )
        
        self.model.set_device(self.config['device'])
        self.logger.info(f"模型信息: {self.model.get_model_info()}")
    
    def init_optimizer(self) -> None:
        """初始化优化器和学习率调度器"""
        self.logger.info(f"初始化优化器: {self.config['optimizer']}")
        
        params = self.model.model.parameters()
        
        if self.config['optimizer'] == 'adam':
            self.optimizer = torch.optim.Adam(
                params,
                lr=self.config['learning_rate'],
                weight_decay=self.config['weight_decay']
            )
        elif self.config['optimizer'] == 'sgd':
            self.optimizer = torch.optim.SGD(
                params,
                lr=self.config['learning_rate'],
                momentum=0.9,
                weight_decay=self.config['weight_decay']
            )
        else:
            raise ValueError(f"不支持的优化器: {self.config['optimizer']}")
        
        if self.config['scheduler'] == 'cosine':
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config['epochs']
            )
        elif self.config['scheduler'] == 'step':
            self.scheduler = torch.optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=10,
                gamma=0.1
            )
        elif self.config['scheduler'] == 'none':
            self.scheduler = None
        else:
            raise ValueError(f"不支持的调度器: {self.config['scheduler']}")
        
        self.criterion = nn.CrossEntropyLoss()
    
    def train(self) -> None:
        """执行训练"""
        if self.model is None:
            self.init_model()
        if self.train_loader is None:
            self.init_data()
        if self.optimizer is None:
            self.init_optimizer()
        
        self.logger.info("开始图片分类训练...")
        self.logger.info(f"训练配置: {self.config}")
        
        self.history = self.model.train_model(
            train_loader=self.train_loader,
            val_loader=self.val_loader,
            criterion=self.criterion,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            epochs=self.config['epochs'],
            verbose=True
        )
        
        self.logger.info("训练完成")
    
    def validate(self) -> Optional[Dict[str, float]]:
        """执行验证"""
        if self.model is None or self.val_loader is None:
            self.logger.error("模型或数据加载器未初始化")
            return None
        
        self.logger.info("开始验证...")
        loss, acc = self.model.validate(self.val_loader, self.criterion)
        self.logger.info(f"验证完成 - Loss: {loss:.4f}, Acc: {acc:.4f}")
        
        return {"loss": loss, "accuracy": acc}
    
    def test(self) -> Optional[Dict[str, float]]:
        """执行测试"""
        if self.model is None or self.test_loader is None:
            self.logger.error("模型或测试数据加载器未初始化")
            return None
        
        self.logger.info("开始测试...")
        loss, acc = self.model.validate(self.test_loader, self.criterion)
        self.logger.info(f"测试完成 - Loss: {loss:.4f}, Acc: {acc:.4f}")
        
        return {"loss": loss, "accuracy": acc}
    
    def save_model(self) -> Path:
        """保存模型权重"""
        model_path = self.exp_dir / 'best_model.pth'
        self.model.save(str(model_path))
        self.logger.info(f"模型已保存: {model_path}")
        return model_path
    
    def save_history(self) -> Path:
        """保存训练历史"""
        history_path = self.exp_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=4)
        self.logger.info(f"训练历史已保存: {history_path}")
        return history_path
    
    def save_config(self) -> Path:
        """保存配置到实验目录"""
        config_path = self.exp_dir / 'train_config.yaml'
        save_config(self.config, config_path)
        self.logger.info(f"配置已保存: {config_path}")
        return self.exp_dir
    
    def get_results(self) -> Optional[Dict[str, Any]]:
        """获取训练结果"""
        if self.history is None:
            return None
        
        final_train_acc = self.history['train_acc'][-1]
        final_val_acc = self.history['val_acc'][-1]
        final_train_loss = self.history['train_loss'][-1]
        final_val_loss = self.history['val_loss'][-1]
        
        return {
            "history": self.history,
            "final_train_acc": final_train_acc,
            "final_val_acc": final_val_acc,
            "final_train_loss": final_train_loss,
            "final_val_loss": final_val_loss,
            "best_val_acc": max(self.history['val_acc']),
            "best_val_loss": min(self.history['val_loss'])
        }
    
    def run(self) -> Path:
        """执行完整的训练流程"""
        self.init_data()
        self.init_model()
        self.init_optimizer()
        self.train()
        self.save_model()
        self.save_history()
        self.save_config()
        
        results = self.get_results()
        if results:
            self.logger.info(f"最佳验证准确率: {results['best_val_acc']:.4f}")
        
        return self.exp_dir


class CVTrainer:
    """
    计算机视觉通用训练器
    根据配置自动选择目标检测或图片分类训练器
    """
    
    def __new__(cls, config: Dict[str, Any]):
        """
        根据任务类型创建对应的训练器
        
        Args:
            config: 训练配置字典，必须包含 'task_type' 字段
        
        Returns:
            DetectionTrainer 或 ClassificationTrainer 实例
        """
        task_type = config.get('task_type', 'detection')
        
        if task_type == 'detection':
            return DetectionTrainer(config)
        elif task_type == 'classification':
            return ClassificationTrainer(config)
        else:
            raise ValueError(f"不支持的任务类型: {task_type}")