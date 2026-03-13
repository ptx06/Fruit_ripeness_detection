#!/usr/bin/env python
"""
水果成熟度检测系统 - 前端启动脚本
"""
import os
import sys
import subprocess
import time

def check_node_installed():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js未安装")
            return False
    except FileNotFoundError:
        print("❌ Node.js未安装")
        return False

def check_npm_installed():
    """检查npm是否安装"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ npm未安装")
            return False
    except FileNotFoundError:
        print("❌ npm未安装")
        return False

def install_dependencies():
    """安装前端依赖"""
    print("📦 正在安装前端依赖...")
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✅ 前端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_dev_server():
    """启动开发服务器"""
    print("🚀 启动前端开发服务器...")
    try:
        # 切换到frontend目录
        os.chdir("frontend")
        
        # 启动Vite开发服务器
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\n🛑 开发服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🍎 水果成熟度检测系统 - 前端服务")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("frontend"):
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 检查Node.js和npm
    if not check_node_installed():
        print("\n请先安装Node.js: https://nodejs.org/")
        return
    
    if not check_npm_installed():
        print("\nnpm未正确安装，请检查Node.js安装")
        return
    
    # 检查依赖是否已安装
    if not os.path.exists("frontend/node_modules"):
        print("\n检测到未安装依赖，开始安装...")
        if not install_dependencies():
            print("\n请手动安装依赖:")
            print("cd frontend && npm install")
            return
    else:
        print("✅ 依赖已安装")
    
    print("\n" + "=" * 50)
    print("✅ 前端准备就绪")
    print("🌐 前端地址: http://localhost:3000")
    print("📊 后端API: http://localhost:8000")
    print("=" * 50)
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 启动开发服务器
    start_dev_server()

if __name__ == "__main__":
    main()