"""计算机视觉数据集处理模块 - 同时支持目标检测和图片分类"""
import os
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

import cv2
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms


# ==================== 目标检测数据集 ====================

class DetectionDataset:
    """
    YOLO格式目标检测数据集类
    支持标准YOLO数据集格式:
    dataset/
        images/
            train/
                img1.jpg
                img2.jpg
            val/
                ...
            test/
                ...
        labels/
            train/
                img1.txt
                img2.txt
            val/
                ...
            test/
                ...
        data.yaml
    """
    
    def __init__(self, data_dir: str):
        """
        初始化数据集
        
        Args:
            data_dir: 数据集根目录路径
        """
        self.data_dir = Path(data_dir)
        self.image_dir = self.data_dir / "images"
        self.label_dir = self.data_dir / "labels"
        self.class_names = self._load_class_names()
    
    def _load_class_names(self) -> List[str]:
        """加载类别名称"""
        names_path = self.data_dir / "data.yaml"
        if names_path.exists():
            import yaml
            with open(names_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('names', [])
        return []
    
    def get_image_paths(self, split: str = "train") -> List[Path]:
        """
        获取指定分割集的图片路径
        
        Args:
            split: 数据集分割 (train/val/test)
            
        Returns:
            图片路径列表
        """
        split_dir = self.image_dir / split
        if not split_dir.exists():
            raise ValueError(f"分割目录不存在: {split_dir}")
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_paths = []
        
        for ext in image_extensions:
            image_paths.extend(split_dir.glob(f"*{ext}"))
            image_paths.extend(split_dir.glob(f"*{ext.upper()}"))
        
        return sorted(image_paths)
    
    def get_label_path(self, image_path: Path) -> Path:
        """
        获取图片对应的标签文件路径
        
        Args:
            image_path: 图片路径
            
        Returns:
            标签文件路径
        """
        label_name = image_path.stem + ".txt"
        return self.label_dir / image_path.parent.name / label_name
    
    def load_image(self, image_path: Path) -> np.ndarray:
        """
        加载图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片数组 (H, W, 3)
        """
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"无法加载图片: {image_path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    def load_labels(self, label_path: Path) -> List[List[float]]:
        """
        加载YOLO格式标签
        
        Args:
            label_path: 标签文件路径
            
        Returns:
            标签列表，每个标签为 [class_id, x_center, y_center, width, height]
        """
        labels = []
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = list(map(float, line.split()))
                        labels.append(parts)
        return labels
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取数据集统计信息
        
        Returns:
            统计字典
        """
        stats = {}
        
        for split in ["train", "val"]:
            try:
                images = self.get_image_paths(split)
                stats[f"{split}_images"] = len(images)
                
                total_labels = 0
                for img_path in images:
                    label_path = self.get_label_path(img_path)
                    labels = self.load_labels(label_path)
                    total_labels += len(labels)
                
                stats[f"{split}_labels"] = total_labels
            except ValueError:
                stats[f"{split}_images"] = 0
                stats[f"{split}_labels"] = 0
        
        stats["classes"] = len(self.class_names)
        
        return stats
    
    def __len__(self) -> int:
        """返回训练集图片数量"""
        try:
            return len(self.get_image_paths("train"))
        except ValueError:
            return 0


# ==================== 图片分类数据集 ====================

class ClassificationDataset(Dataset):
    """
    图片分类数据集类
    支持按文件夹组织的数据集:
    dataset/
        train/
            class1/
                img1.jpg
                img2.jpg
            class2/
                ...
        val/
            ...
        test/
            ...
    """
    
    def __init__(
        self,
        data_dir: str,
        split: str = "train",
        transform: Any = None,
        class_names: List[str] = None
    ):
        """
        初始化数据集
        
        Args:
            data_dir: 数据集根目录路径
            split: 数据集分割 (train/val/test)
            transform: 数据变换
            class_names: 类别名称列表（可选，自动从文件夹名推断）
        """
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform
        
        self.split_dir = self.data_dir / split
        if not self.split_dir.exists():
            raise ValueError(f"分割目录不存在: {self.split_dir}")
        
        if class_names is not None:
            self.class_names = class_names
        else:
            self.class_names = self._infer_class_names()
        
        self.class_to_idx = {name: idx for idx, name in enumerate(self.class_names)}
        self.samples = self._load_samples()
    
    def _infer_class_names(self) -> List[str]:
        """从文件夹名推断类别名称"""
        class_dirs = []
        for item in self.split_dir.iterdir():
            if item.is_dir():
                class_dirs.append(item.name)
        return sorted(class_dirs)
    
    def _load_samples(self) -> List[Tuple[Path, int]]:
        """加载所有样本路径和标签"""
        samples = []
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        
        for class_name in self.class_names:
            class_dir = self.split_dir / class_name
            if not class_dir.exists():
                continue
            
            for img_path in class_dir.glob('*'):
                if img_path.suffix.lower() in image_extensions:
                    class_idx = self.class_to_idx[class_name]
                    samples.append((img_path, class_idx))
        
        if not samples:
            raise ValueError(f"未找到任何图片文件在 {self.split_dir}")
        
        return samples
    
    def __len__(self) -> int:
        """返回样本数量"""
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[Any, int]:
        """
        获取单个样本
        
        Args:
            idx: 样本索引
            
        Returns:
            (图像, 标签)
        """
        img_path, label = self.samples[idx]
        img = cv2.imread(str(img_path))
        if img is None:
            raise ValueError(f"无法加载图片: {img_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        if self.transform is not None:
            img = self.transform(img)
        
        return img, label
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据集统计信息
        
        Returns:
            统计字典
        """
        stats = {
            "total_samples": len(self),
            "num_classes": len(self.class_names),
            "class_names": self.class_names,
            "class_distribution": {}
        }
        
        for class_name in self.class_names:
            count = sum(1 for _, label in self.samples if label == self.class_to_idx[class_name])
            stats["class_distribution"][class_name] = count
        
        return stats


def get_classification_transforms(split: str, input_size: int = 224, augmentation: Dict = None) -> transforms.Compose:
    """
    获取图片分类数据变换组合
    
    Args:
        split: 数据集分割 (train/val/test)
        input_size: 输入图像尺寸
        augmentation: 数据增强配置
        
    Returns:
        变换组合
    """
    base_transforms = [
        transforms.ToPILImage(),
        transforms.Resize((input_size, input_size)),
    ]
    
    if split == "train" and augmentation:
        aug_list = []
        if augmentation.get("horizontal_flip", False):
            aug_list.append(transforms.RandomHorizontalFlip())
        if augmentation.get("vertical_flip", False):
            aug_list.append(transforms.RandomVerticalFlip())
        if augmentation.get("rotation", 0) > 0:
            aug_list.append(transforms.RandomRotation(augmentation["rotation"]))
        if augmentation.get("brightness", 0) > 0 or augmentation.get("contrast", 0) > 0:
            aug_list.append(transforms.ColorJitter(
                brightness=augmentation.get("brightness", 0),
                contrast=augmentation.get("contrast", 0)
            ))
        base_transforms.extend(aug_list)
    
    base_transforms.extend([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    return transforms.Compose(base_transforms)


def create_classification_data_loaders(
    data_dir: str,
    batch_size: int = 32,
    input_size: int = 224,
    workers: int = 8,
    augmentation: Dict = None,
    class_names: List[str] = None
) -> Tuple[Any, Any, Any]:
    """
    创建图片分类数据加载器
    
    Args:
        data_dir: 数据集根目录
        batch_size: 批次大小
        input_size: 输入图像尺寸
        workers: 数据加载线程数
        augmentation: 数据增强配置
        class_names: 类别名称列表
        
    Returns:
        (训练加载器, 验证加载器, 测试加载器)
    """
    from torch.utils.data import DataLoader
    
    train_transform = get_classification_transforms("train", input_size, augmentation)
    val_transform = get_classification_transforms("val", input_size)
    test_transform = get_classification_transforms("test", input_size)
    
    train_dataset = ClassificationDataset(
        data_dir, split="train", transform=train_transform, class_names=class_names
    )
    val_dataset = ClassificationDataset(
        data_dir, split="val", transform=val_transform, class_names=class_names
    )
    
    test_dataset = None
    test_dir = Path(data_dir) / "test"
    if test_dir.exists():
        test_dataset = ClassificationDataset(
            data_dir, split="test", transform=test_transform, class_names=class_names
        )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=workers,
        pin_memory=True
    )
    
    test_loader = None
    if test_dataset:
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=workers,
            pin_memory=True
        )
    
    return train_loader, val_loader, test_loader