import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import time
import copy

# -------------------- 1. 配置参数 --------------------
# 数据集路径（根据你的实际路径修改）
data_root = '../data'  # 假设当前目录包含 apple_dataset 和 val 文件夹
train_dir = os.path.join(data_root, 'orange_dataset', 'train')
test_dir = os.path.join(data_root, 'orange_dataset', 'test')
val_dir = os.path.join(data_root, 'orange_dataset', 'val')

# 模型保存路径
save_path = '../models/orange_best_model.pth'

# 训练超参数
batch_size = 32
num_epochs = 10
learning_rate = 0.001
momentum = 0.9
weight_decay = 1e-4
step_size = 7          # 学习率衰减步长
gamma = 0.1             # 学习率衰减因子

# 设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

# -------------------- 2. 数据预处理 --------------------
# ImageNet 归一化参数
mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]

# 训练集数据增强
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),       # 随机裁剪并缩放至224
    transforms.RandomHorizontalFlip(),        # 随机水平翻转
    transforms.RandomRotation(10),            # 随机旋转±10度
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),  # 颜色抖动
    transforms.ToTensor(),
    transforms.Normalize(mean, std)
])

# 验证/测试集只做基础变换
val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean, std)
])

# -------------------- 3. 加载数据集 --------------------
# 使用 ImageFolder 自动读取
train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
test_dataset = datasets.ImageFolder(test_dir, transform=val_transform)
val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)

# 获取类别名称和数量
class_names = train_dataset.classes
num_classes = len(class_names)
print(f'类别: {class_names}')
print(f'训练集样本数: {len(train_dataset)}')
print(f'测试集样本数: {len(test_dataset)}')
print(f'验证集样本数: {len(val_dataset)}')

# 创建 DataLoader
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

# -------------------- 4. 构建模型 --------------------
# 加载预训练的 MobileNetV2
model = models.mobilenet_v2(pretrained=True)

# 修改分类头
num_ftrs = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(0.2),
    nn.Linear(num_ftrs, num_classes)
)
model = model.to(device)

# -------------------- 5. 定义损失函数和优化器 --------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum, weight_decay=weight_decay)
# 学习率调度器：每 step_size 个 epoch 将学习率乘以 gamma
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)

# -------------------- 6. 训练函数 --------------------
def train_model(model, dataloaders, criterion, optimizer, scheduler, num_epochs):
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(1, num_epochs+1):
        print(f'Epoch {epoch}/{num_epochs}')
        print('-' * 30)

        # 每个 epoch 包含训练和验证阶段
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
                dataloader = dataloaders['train']
            else:
                model.eval()
                dataloader = dataloaders['val']

            running_loss = 0.0
            running_corrects = 0

            # 迭代数据
            for inputs, labels in dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # 梯度清零
                optimizer.zero_grad()

                # 前向传播
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # 训练阶段：反向传播 + 优化
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # 统计
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            if phase == 'train':
                scheduler.step()  # 更新学习率

            epoch_loss = running_loss / len(dataloader.dataset)
            epoch_acc = running_corrects.double() / len(dataloader.dataset)

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # 保存最佳模型（基于验证集准确率）
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())
                torch.save(model.state_dict(), save_path)
                print(f'已保存最佳模型，准确率: {best_acc:.4f}')

        print()

    time_elapsed = time.time() - since
    print(f'训练完成，耗时 {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'最佳验证准确率: {best_acc:.4f}')

    # 加载最佳模型权重
    model.load_state_dict(best_model_wts)
    return model

# -------------------- 7. 训练 --------------------
# 构建 dataloaders 字典
dataloaders = {'train': train_loader, 'val': val_loader}

model = train_model(model, dataloaders, criterion, optimizer, scheduler, num_epochs)

# -------------------- 8. 测试最终模型 --------------------
def test_model(model, test_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (preds == labels).sum().item()
    acc = 100.0 * correct / total
    print(f'测试集准确率: {acc:.2f}%')
    return acc

test_model(model, test_loader)

# -------------------- 9. 预测单张图片示例 --------------------
def predict_image(image_path, model, transform, class_names):
    from PIL import Image
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        outputs = model(image)
        _, pred = torch.max(outputs, 1)
    return class_names[pred.item()]

# 示例：预测验证集中的第一张图片（假设路径存在）
if val_dataset:
    sample_path, _ = val_dataset.samples[0]
    pred = predict_image(sample_path, model, val_transform, class_names)
    print(f'预测样本图片 {sample_path} 的类别为: {pred}')