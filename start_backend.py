#!/usr/bin/env python
"""
水果成熟度检测系统 - 后端启动脚本
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import ultralytics
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ["uploads", "results", "experiments"]
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ 创建目录: {dir_name}")

def initialize_database():
    """初始化数据库"""
    try:
        from backend.database import engine, Base
        from backend.models import UserDB, DetectionHistory
        
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库初始化完成")
        
        # 创建演示用户
        from backend.auth import get_password_hash
        from sqlalchemy.orm import Session
        
        db = Session(bind=engine)
        try:
            # 检查演示用户是否存在
            demo_user = db.query(UserDB).filter(UserDB.username == "demo").first()
            if not demo_user:
                demo_user = UserDB(
                    id="demo-user",
                    username="demo",
                    email="demo@example.com",
                    hashed_password=get_password_hash("demo")
                )
                db.add(demo_user)
                db.commit()
                print("✅ 创建演示用户: demo/demo")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")

def start_server():
    """启动后端服务器"""
    print("🚀 启动后端服务器...")
    try:
        # 切换到backend目录
        os.chdir("backend")
        
        # 启动FastAPI服务器
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🍎 水果成熟度检测系统 - 后端服务")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("backend"):
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 检查依赖
    if not check_dependencies():
        print("\n尝试自动安装依赖...")
        if not install_dependencies():
            print("\n请手动安装依赖:")
            print("pip install -r backend/requirements.txt")
            return
    
    # 创建目录
    create_directories()
    
    # 初始化数据库
    initialize_database()
    
    print("\n" + "=" * 50)
    print("✅ 系统准备就绪")
    print("📊 API文档: http://localhost:8000/docs")
    print("🌐 后端服务: http://localhost:8000")
    print("=" * 50)
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()