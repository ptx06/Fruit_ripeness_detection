"""MobileNetV2分类模型封装模块"""
from typing import Dict, Any, Optional, List

import torch
import torch.nn as nn
from torchvision import models


class MobileNetV2Model:
    """
    MobileNetV2分类模型封装类
    提供统一的模型接口，支持训练、验证和推理
    """
    
    def __init__(
        self,
        num_classes: int = 3,
        pretrained: bool = True,
        model_name: str = "mobilenet_v2"
    ):
        """
        初始化MobileNetV2模型
        
        Args:
            num_classes: 类别数量
            pretrained: 是否使用预训练权重
            model_name: 模型名称
        """
        self.num_classes = num_classes
        self.pretrained = pretrained
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = self._build_model()
        self.model.to(self.device)
    
    def _build_model(self) -> nn.Module:
        """构建MobileNetV2模型"""
        if self.model_name == "mobilenet_v2":
            model = models.mobilenet_v2(pretrained=self.pretrained)
            
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_ftrs, self.num_classes)
        else:
            raise ValueError(f"不支持的模型: {self.model_name}")
        
        return model
    
    def train_model(
        self,
        train_loader: Any,
        val_loader: Any,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        scheduler: Any,
        epochs: int = 50,
        verbose: bool = True
    ) -> Dict[str, List[float]]:
        """
        训练模型
        
        Args:
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            criterion: 损失函数
            optimizer: 优化器
            scheduler: 学习率调度器
            epochs: 训练轮数
            verbose: 是否打印训练信息
            
        Returns:
            训练历史记录
        """
        history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
        
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for images, labels in train_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                optimizer.zero_grad()
                
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                train_correct += (preds == labels).sum().item()
                train_total += labels.size(0)
            
            if scheduler:
                scheduler.step()
            
            train_loss = train_loss / train_total
            train_acc = train_correct / train_total
            
            val_loss, val_acc = self.validate(val_loader, criterion)
            
            history["train_loss"].append(train_loss)
            history["train_acc"].append(train_acc)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)
            
            if verbose:
                print(f"Epoch [{epoch+1}/{epochs}]")
                print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
                print(f"  Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
                print("-" * 50)
        
        return history
    
    def validate(
        self,
        val_loader: Any,
        criterion: nn.Module
    ) -> Tuple[float, float]:
        """
        验证模型
        
        Args:
            val_loader: 验证数据加载器
            criterion: 损失函数
            
        Returns:
            (验证损失, 验证准确率)
        """
        self.model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
        
        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        
        return val_loss, val_acc
    
    def predict(
        self,
        image: torch.Tensor
    ) -> Dict[str, Any]:
        """
        推理预测
        
        Args:
            image: 输入图像张量 (C, H, W)
            
        Returns:
            预测结果字典
        """
        self.model.eval()
        
        if image.dim() == 3:
            image = image.unsqueeze(0)
        
        image = image.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
        
        return {
            "predicted_class": int(preds.item()),
            "probabilities": probs.cpu().numpy()[0].tolist()
        }
    
    def save(self, path: str) -> None:
        """
        保存模型权重
        
        Args:
            path: 保存路径
        """
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'num_classes': self.num_classes,
            'model_name': self.model_name
        }, path)
    
    @classmethod
    def load(cls, path: str) -> 'MobileNetV2Model':
        """
        加载模型权重
        
        Args:
            path: 模型权重路径
            
        Returns:
            加载后的模型实例
        """
        checkpoint = torch.load(path, map_location='cpu')
        
        model = cls(
            num_classes=checkpoint['num_classes'],
            pretrained=False,
            model_name=checkpoint['model_name']
        )
        model.model.load_state_dict(checkpoint['model_state_dict'])
        
        return model
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "num_classes": self.num_classes,
            "pretrained": self.pretrained,
            "device": str(self.device)
        }
    
    def set_device(self, device: str) -> None:
        """
        设置设备
        
        Args:
            device: 设备名称 ('cuda' 或 'cpu')
        """
        self.device = torch.device(device)
        self.model.to(self.device)