#!/usr/bin/env python
"""
水果成熟度检测系统 - 完整系统启动脚本
"""
import os
import sys
import subprocess
import threading
import time
import signal
import webbrowser

def print_banner():
    """打印系统横幅"""
    banner = """
    🍎🍊🍌🍇🍓🍒🥭🍍
    ===========================================
        水果成熟度检测系统 v1.0.0
    ===========================================
    基于YOLO11的智能水果成熟度检测平台
    ===========================================
    """
    print(banner)

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查必要目录
    required_dirs = ["backend", "frontend"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 缺少目录: {dir_name}")
            return False
        print(f"✅ 目录存在: {dir_name}")
    
    return True

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")
    try:
        # 安装后端依赖
        print("📦 安装后端依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        # 创建必要目录
        for dir_name in ["uploads", "results", "experiments"]:
            os.makedirs(dir_name, exist_ok=True)
        
        # 启动后端服务器
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=os.getcwd()
        )
        
        # 等待后端启动
        time.sleep(5)
        
        # 检查后端是否正常启动
        import requests
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("✅ 后端服务启动成功")
                return backend_process
        except:
            pass
        
        print("❌ 后端服务启动失败")
        backend_process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("\n🚀 启动前端服务...")
    
    # 检查Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except:
        print("❌ 需要安装Node.js和npm")
        print("请访问: https://nodejs.org/")
        return None
    
    try:
        # 安装前端依赖
        print("📦 安装前端依赖...")
        subprocess.run(["npm", "install"], cwd="frontend", check=True, capture_output=True)
        
        # 启动前端开发服务器
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            shell=True
        )
        
        # 等待前端启动
        time.sleep(8)
        
        print("✅ 前端服务启动成功")
        return frontend_process
        
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None

def open_browser():
    """自动打开浏览器"""
    time.sleep(10)  # 等待服务完全启动
    print("\n🌐 正在打开浏览器...")
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:3000")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请检查上述问题")
        return
    
    print("\n✅ 环境检查通过")
    
    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ 后端服务启动失败，系统无法运行")
        return
    
    # 启动前端服务
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ 前端服务启动失败")
        backend_process.terminate()
        return
    
    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 打印系统信息
    print("\n" + "=" * 50)
    print("🎉 系统启动成功!")
    print("=" * 50)
    print("🌐 前端地址: http://localhost:3000")
    print("📊 后端API: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 50)
    print("\n📋 使用说明:")
    print("1. 系统会自动打开浏览器访问前端界面")
    print("2. 使用演示账号登录: demo / demo")
    print("3. 上传水果图片进行检测")
    print("4. 查看检测历史和统计信息")
    print("\n🛑 按 Ctrl+C 停止系统")
    print("=" * 50)
    
    # 信号处理
    def signal_handler(sig, frame):
        print("\n\n🛑 正在停止系统...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ 系统已停止")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 等待进程结束
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()