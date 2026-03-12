import torch
from PIL import Image
from torchvision import transforms
import json
import requests

# 1. 加载预训练模型（第一次运行会自动下载权重）
model = torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True)
model.eval()  # 切换到评估模式

# 2. 下载ImageNet类别标签（1000类）
url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
class_names = requests.get(url).text.splitlines()

# 3. 图像预处理：MobileNetV2要求输入224x224，并做特定归一化
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),          # 模型要求的输入尺寸
    transforms.ToTensor(),
    transforms.Normalize(                 # ImageNet数据集的均值和标准差
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# 4. 加载并预处理图像
img = Image.open("your_image.jpg")        # 替换成你的图片路径
input_tensor = preprocess(img)
input_batch = input_tensor.unsqueeze(0)   # 增加batch维度 [1, 3, 224, 224]

# 5. 推理
with torch.no_grad():
    output = model(input_batch)

# 6. 解析结果
probabilities = torch.nn.functional.softmax(output[0], dim=0)
top5_prob, top5_indices = torch.topk(probabilities, 5)

print("Top-5预测结果：")
for i in range(5):
    idx = top5_indices[i].item()
    print(f"{class_names[idx]}: {top5_prob[i].item()*100:.2f}%")