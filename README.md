# 🚀 计算机视觉万能训练模板

一个**同时支持目标检测和图片分类**的通用计算机视觉训练框架，基于 YOLO11 和 MobileNetV2 模型，支持灵活的配置和扩展。

## ✨ 核心特性

- **双任务支持**: 同一框架同时支持目标检测(YOLO11)和图片分类(MobileNetV2)
- **一键切换**: 通过配置文件轻松切换任务类型
- **模块化设计**: 清晰的代码结构，易于扩展和维护
- **配置驱动**: 所有参数通过 YAML 配置文件管理，无需修改代码
- **实验可追溯**: 自动保存训练配置、权重和结果
- **跨平台**: 支持 Windows/Linux/macOS

## 🏗️ 项目结构

```
Fruit_ripeness_detection/
├── 📁 configs/                # 配置文件目录
│   └── train_config.yaml      # 训练配置（任务类型、参数等）
├── 📁 data/                   # 数据集目录
│   ├── Fruit_object_detection/ # 目标检测数据集（YOLO格式）
│   │   ├── images/            # 图片文件夹
│   │   │   ├── train/
│   │   │   └── val/
│   │   ├── labels/            # 标签文件夹
│   │   │   ├── train/
│   │   │   └── val/
│   │   └── data.yaml          # 数据集配置文件
│   └── apple_dataset/         # 图片分类数据集（按文件夹组织）
│       ├── train/
│       │   ├── class1/
│       │   ├── class2/
│       │   └── class3/
│       ├── val/
│       └── test/
├── 📁 scripts/                # 运行脚本
│   ├── train.py               # 训练脚本
│   ├── evaluate.py            # 评估脚本
│   └── predict.py             # 预测脚本
├── 📁 src/                    # 源代码目录
│   └── fruit_detection/       # 核心模块
│       ├── data/              # 数据集处理
│       │   ├── __init__.py
│       │   └── dataset.py     # 数据集类（检测+分类）
│       ├── models/            # 模型封装
│       │   ├── __init__.py
│       │   ├── yolo_wrapper.py      # YOLO11目标检测模型
│       │   └── mobilenet_wrapper.py # MobileNetV2分类模型
│       ├── training/           # 训练器
│       │   ├── __init__.py
│       │   └── trainer.py      # 训练器类（检测+分类）
│       └── utils/             # 工具函数
│           ├── __init__.py
│           └── config.py       # 配置管理
├── 📁 experiments/            # 实验结果目录
│   └── outputs/               # 训练输出（权重、日志、图表）
├── 📁 src/models/             # 预训练模型权重
├── .gitignore                 # Git忽略配置
├── requirements.txt           # Python依赖列表
└── README.md                  # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 准备数据集

#### 目标检测数据集（YOLO格式）
```
data/Fruit_object_detection/
├── images/
│   ├── train/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── val/
│       └── ...
├── labels/
│   ├── train/
│   │   ├── img1.txt
│   │   └── img2.txt
│   └── val/
│       └── ...
└── data.yaml
```

**data.yaml 格式**:
```yaml
path: ./data/Fruit_object_detection
train: images/train
val: images/val
names:
  0: apple
  1: banana
  2: orange
```

#### 图片分类数据集（按文件夹组织）
```
data/apple_dataset/
├── train/
│   ├── freshapples/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   ├── rottenapples/
│   └── unripeapples/
├── val/
│   └── ...
└── test/
    └── ...
```

### 3. 配置训练参数

编辑 `configs/train_config.yaml`:

```yaml
# 选择任务类型: detection 或 classification
task_type: detection

# 目标检测配置
data: ./data/Fruit_object_detection/data.yaml
model: ./src/models/yolo11n.pt
epochs: 50
batch: 16
imgsz: 640

# 图片分类配置（取消注释启用）
# task_type: classification
# data_path: "../data/apple_dataset"
# num_classes: 3
# class_names:
#   - freshapples
#   - rottenapples
#   - unripeapples
```

### 4. 训练模型

```bash
# 启动训练
python scripts/train.py --config configs/train_config.yaml
```

### 5. 评估模型

```bash
# 评估目标检测模型
python scripts/evaluate.py \
  --config configs/train_config.yaml \
  --weights experiments/train/weights/best.pt

# 评估分类模型
python scripts/evaluate.py \
  --config configs/train_config.yaml \
  --weights experiments/train/best_model.pth \
  --split val
```

### 6. 预测

```bash
# 目标检测预测
python scripts/predict.py \
  --weights experiments/train/weights/best.pt \
  --image test.jpg \
  --conf 0.25

# 分类预测
python scripts/predict.py \
  --weights experiments/train/best_model.pth \
  --image test.jpg
```

## ⚙️ 配置说明

### 目标检测配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `task_type` | 任务类型 | detection |
| `data` | 数据集配置文件路径 | ./data/Fruit_object_detection/data.yaml |
| `model` | 预训练模型路径 | ./src/models/yolo11n.pt |
| `epochs` | 训练轮数 | 50 |
| `batch` | 批次大小 | 16 |
| `imgsz` | 输入图像尺寸 | 640 |
| `device` | 训练设备 (0=cuda, -1=cpu) | 0 |
| `workers` | 数据加载线程数 | 8 |

### 图片分类配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `task_type` | 任务类型 | classification |
| `data_path` | 数据集路径 | ../data/apple_dataset |
| `num_classes` | 类别数量 | 3 |
| `class_names` | 类别名称列表 | - |
| `model_name` | 模型名称 | mobilenet_v2 |
| `input_size` | 输入图像尺寸 | 224 |
| `batch_size` | 批次大小 | 32 |
| `learning_rate` | 学习率 | 0.001 |
| `epochs` | 训练轮数 | 50 |
| `optimizer` | 优化器 | adam |
| `scheduler` | 学习率调度器 | cosine |

### 数据增强配置（分类任务）

```yaml
augmentation:
  horizontal_flip: True    # 水平翻转
  vertical_flip: False     # 垂直翻转
  rotation: 15             # 旋转角度
  brightness: 0.2          # 亮度调整
  contrast: 0.2            # 对比度调整
```

## 📊 实验输出

训练完成后，实验结果保存在 `experiments/<name>/` 目录：

```
experiments/train/
├── best_model.pth          # 最佳模型权重（分类）
├── training_history.json   # 训练历史记录
├── train_config.yaml       # 训练配置备份
├── training.log            # 训练日志
└── weights/                # YOLO模型权重（检测）
    ├── best.pt
    └── last.pt
```

## 🔄 任务切换示例

### 从目标检测切换到图片分类

1. 修改 `configs/train_config.yaml`:
```yaml
task_type: classification
data_path: "../data/apple_dataset"
num_classes: 3
class_names:
  - freshapples
  - rottenapples
  - unripeapples
```

2. 运行训练:
```bash
python scripts/train.py --config configs/train_config.yaml
```

## 🧠 支持的模型

| 任务类型 | 模型 | 说明 |
|---------|------|------|
| 目标检测 | YOLO11n | 轻量级，速度快 |
| 目标检测 | YOLO11m | 中等大小，精度高 |
| 图片分类 | MobileNetV2 | 轻量级，适合移动端 |

## 📋 系统要求

- **Python**: 3.8+
- **PyTorch**: 2.0+
- **torchvision**: 0.15+
- **ultralytics**: 8.0+ (YOLO11)
- **CUDA**: 可选（GPU加速）

## 🔧 开发指南

### 添加新模型

在 `src/fruit_detection/models/` 目录下创建新的模型封装类：

```python
class CustomModel:
    def __init__(self, num_classes, pretrained=True):
        self.model = self._build_model()
    
    def _build_model(self):
        # 构建模型逻辑
        pass
    
    def train(self, train_loader, val_loader, epochs):
        # 训练逻辑
        pass
    
    def predict(self, image):
        # 预测逻辑
        pass
```

### 添加新数据集格式

在 `src/fruit_detection/data/dataset.py` 中添加新的数据集类：

```python
class CustomDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        # 初始化逻辑
        pass
    
    def __getitem__(self, idx):
        # 获取样本逻辑
        pass
```

## 🐛 故障排除

### 常见问题

**Q: 数据集路径错误**
A: 检查配置文件中的 `data` 或 `data_path` 参数是否正确

**Q: CUDA 内存不足**
A: 减小 `batch` 或 `batch_size` 参数，或使用 CPU 训练 (`device: -1`)

**Q: 模型加载失败**
A: 确保预训练模型文件存在，或使用官方模型名称（如 `yolo11n.pt`）

**Q: 分类数据集找不到**
A: 确保数据集按照 `train/class_name/image.jpg` 结构组织

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 (Python)
- 添加适当的注释和文档
- 使用类型提示

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics) - 目标检测模型
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [torchvision](https://pytorch.org/vision/) - 计算机视觉工具库

---

**🚀 开始你的计算机视觉训练之旅！**