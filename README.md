# 🍎 水果成熟度检测系统

基于YOLO11深度学习模型的水果成熟度智能检测系统，提供现代化的Web界面和完整的API服务。

## ✨ 系统特性

- **智能检测**: 基于YOLO11深度学习模型，准确识别水果成熟度
- **现代化界面**: React + TypeScript + Tailwind CSS 前端界面
- **RESTful API**: FastAPI 提供完整的后端服务
- **用户管理**: 支持用户注册、登录、检测历史记录
- **实时检测**: 支持图片上传和实时检测结果展示
- **数据统计**: 检测历史统计和可视化
- **易于部署**: 一键启动脚本，支持Windows/Linux/macOS

## 🏗️ 系统架构

```
水果成熟度检测系统
├── 📁 backend/          # 后端服务 (FastAPI)
│   ├── main.py          # 主应用入口
│   ├── models.py        # 数据模型
│   ├── database.py      # 数据库配置
│   ├── auth.py          # 认证模块
│   ├── detection_service.py  # 检测服务
│   └── requirements.txt # Python依赖
├── 📁 frontend/         # 前端应用 (React)
│   ├── src/
│   │   ├── components/  # React组件
│   │   ├── pages/       # 页面组件
│   │   ├── services/    # API服务
│   │   └── contexts/    # React上下文
│   ├── package.json     # Node.js依赖
│   └── vite.config.js   # Vite配置
├── 📁 data/             # 数据集目录
├── 📁 configs/          # 配置文件
├── 📁 experiments/      # 实验记录
├── start_system.py      # 完整系统启动脚本
├── start_backend.py     # 后端启动脚本
├── start_frontend.py    # 前端启动脚本
└── README.md           # 说明文档
```

## 🚀 快速开始

### 方式一：一键启动（推荐）

```bash
# 克隆或下载项目后，在项目根目录执行：
python start_system.py
```

系统将自动：
- 检查环境依赖
- 安装必要的Python包和Node.js依赖
- 启动后端服务 (端口8000)
- 启动前端服务 (端口3000)
- 自动打开浏览器访问系统

### 方式二：分别启动

#### 启动后端服务
```bash
# 终端1：启动后端
python start_backend.py
```

#### 启动前端服务
```bash
# 终端2：启动前端
python start_frontend.py
```

## 📋 系统要求

### 环境要求
- **Python**: 3.8+
- **Node.js**: 16+
- **npm**: 8+

### 硬件要求
- **内存**: 至少4GB RAM
- **存储**: 至少2GB可用空间
- **GPU**: 可选（支持CUDA加速）

## 🔧 安装配置

### 1. 环境准备

确保已安装Python和Node.js：

```bash
# 检查Python版本
python --version

# 检查Node.js版本
node --version

# 检查npm版本
npm --version
```

### 2. 手动安装依赖

如果自动安装失败，可以手动安装：

```bash
# 安装Python依赖
pip install -r backend/requirements.txt

# 安装Node.js依赖
cd frontend
npm install
```

### 3. 模型准备

系统支持两种模式：

1. **预训练模式**: 使用YOLO11预训练模型（默认）
2. **自定义训练**: 将训练好的模型保存为 `best.pt` 放在项目根目录

## 🎯 使用指南

### 1. 系统登录
- 访问 http://localhost:3000
- 使用演示账号：**demo / demo**

### 2. 水果检测
1. 点击"选择水果图片"按钮
2. 上传包含水果的图片
3. 点击"开始检测"按钮
4. 查看检测结果和成熟度分析

### 3. 查看历史
- 在"检测历史"页面查看所有检测记录
- 查看统计信息和检测趋势

### 4. API使用
后端API文档：http://localhost:8000/docs

## 🔌 API接口

### 主要端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/detect` | 水果检测 |
| GET | `/api/history` | 获取检测历史 |
| GET | `/api/stats` | 获取统计信息 |
| POST | `/api/auth/login` | 用户登录 |

### 检测请求示例

```bash
curl -X POST "http://localhost:8000/api/detect" \
  -H "Authorization: Bearer <token>" \
  -F "file=@fruit.jpg"
```

## 🎨 界面预览

### 主界面
- 图片上传区域
- 实时检测结果显示
- 检测历史统计

### 检测结果
- 边界框标注
- 成熟度分类（新鲜/成熟/腐烂）
- 置信度显示
- 检测时间记录

## 🔧 开发指南

### 后端开发

```python
# 添加新的API端点
@app.post("/api/custom")
async def custom_endpoint():
    return {"message": "自定义端点"}
```

### 前端开发

```javascript
// 添加新的React组件
function NewComponent() {
    return <div>新组件</div>
}
```

### 模型训练

1. 准备YOLO格式的数据集
2. 配置训练参数
3. 运行训练脚本
4. 导出训练好的模型

## 🐛 故障排除

### 常见问题

**Q: 启动脚本报错**
A: 检查Python和Node.js版本，确保满足要求

**Q: 前端无法访问**
A: 检查端口3000是否被占用，或手动访问 http://localhost:3000

**Q: 检测失败**
A: 检查图片格式，确保上传的是有效图片文件

**Q: 内存不足**
A: 减小批量大小或使用更小的模型

### 日志查看

```bash
# 查看后端日志
python start_backend.py

# 查看前端日志  
cd frontend && npm run dev
```

## 📈 性能优化

### 模型优化
- 使用量化模型减小内存占用
- 启用GPU加速提高检测速度
- 优化图像预处理流程

### 系统优化
- 启用缓存机制
- 优化数据库查询
- 使用CDN加速静态资源

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8 (Python)
- 使用ESLint (JavaScript)
- 添加适当的注释和文档

## 📄 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - 目标检测模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [React](https://reactjs.org/) - 用户界面库
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-repo/issues)
- 发送邮件: 304941600@qq.com

---

**🍎 享受智能水果检测的乐趣！**