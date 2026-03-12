import os

# 核心修改：获取项目根目录（脚本在任意位置执行，均以脚本所在目录的上一级为项目根）
# 若脚本放在 fruit_detection_yolo11/scripts/ 下，ROOT_DIR 即为项目根目录
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 定义 YOLO11 水果检测项目的目录/文件结构
structure = {
    # 根目录文件
    ".gitignore": "",
    "README.md": "",
    "requirements.txt": "",

    # 文件夹层级
    "configs": {
        "train_config.yaml": ""  # 训练配置文件
    },
    "data": {  # 数据目录
        "dataset": {  # YOLO格式数据集目录
            "images": {  # 图片目录
                "train": {},
                "val": {}
            },
            "labels": {  # 标签目录
                "train": {},
                "val": {}
            },
            "data.yaml": ""  # YOLO数据集配置文件
        }
    },
    "src": {  # 源代码模块
        "__init__.py": "",
        "data": {},  # 数据处理（预留空目录）
        "models": {},  # 模型相关（预留空目录）
        "training": {
            "trainer.py": ""  # 训练封装脚本
        },
        "utils": {
            "config.py": ""  # 配置加载器
        }
    },
    "scripts": {  # 可执行脚本目录
        "train.py": "",     # 训练入口
        "evaluate.py": "",  # 评估入口
        "predict.py": ""    # 单图预测脚本
    },
    "experiments": {  # 实验记录目录
        "exp_001": {  # 第一次实验目录
            "checkpoints": {},  # 模型权重保存目录
            "logs": {}          # 训练日志目录
        }
    },
    "deployments": {  # 部署相关目录
        "onnx": {}  # ONNX导出和推理脚本目录
    }
}


def create_structure(base_path, structure_dict):
    """
    递归创建文件夹和空文件，核心规则：
    1. 文件夹已存在 → 跳过（os.makedirs 的 exist_ok=True 实现）
    2. 文件已存在 → 跳过（先判断 os.path.exists）
    3. 空文件夹仅创建目录，不生成文件
    """
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # 处理文件夹：存在则跳过，不存在则创建
            os.makedirs(path, exist_ok=True)
            # 递归创建子目录/文件
            create_structure(path, content)
        else:
            # 处理文件：仅当文件不存在时创建空文件
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 创建空文件：{path}")
            else:
                print(f"ℹ️ 文件已存在，跳过：{path}")


if __name__ == "__main__":
    # 以项目根目录为基准创建结构
    print(f"📌 开始创建项目结构，基准路径：{ROOT_DIR}")
    create_structure(ROOT_DIR, structure)
    print("\n🎉 目录结构创建完成！已自动跳过所有已存在的文件夹/文件")