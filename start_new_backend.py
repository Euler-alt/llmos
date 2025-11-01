#!/usr/bin/env python3
"""
LLM OS 新式后端启动脚本
这个脚本会检查依赖并启动 NewVirtualEnd.py 后端服务器
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✓ {package_name} 已安装")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {package_name} 未安装")
    
    return missing_packages

def install_dependencies(missing_packages):
    """安装缺失的依赖"""
    if not missing_packages:
        return True
        
    print(f"\n正在安装缺失的依赖: {', '.join(missing_packages)}")
    
    try:
        # 使用 pip 安装依赖
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✓ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False

def check_context_program():
    """检查 context_program 模块是否存在"""
    context_program_path = Path('llmos_core/Program/context_program.py')
    if context_program_path.exists():
        print("✓ context_program.py 存在")
        return True
    else:
        print("⚠ context_program.py 不存在，但后端仍可启动（LLM调用功能可能受限）")
        return True

def start_backend():
    """启动后端服务器"""
    print("\n🚀 启动 LLM OS 新式后端服务器...")
    print("=" * 50)
    
    # 检查后端文件是否存在
    if not Path('NewVirtualEnd.py').exists():
        print("✗ NewVirtualEnd.py 不存在，请确保文件已创建")
        return False
    
    try:
        # 启动 uvicorn 服务器
        print("后端服务器启动中...")
        print("访问地址: http://localhost:3001")
        print("API 文档: http://localhost:3001/docs")
        print("\n支持的端点:")
        print("  - GET  /                   根路径信息")
        print("  - GET  /api/sse            SSE实时数据流")
        print("  - GET  /api/modules        获取模块数据（兼容）")
        print("  - GET  /api/windows/config 获取窗口配置")
        print("  - POST /api/modules/update 更新模块数据")
        print("  - POST /api/windows/config 更新窗口配置")
        print("  - POST /api/llm/call       LLM调用")
        print("\n按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 直接运行 NewVirtualEnd.py
        subprocess.run([sys.executable, 'NewVirtualEnd.py'])
        return True
        
    except KeyboardInterrupt:
        print("\n\n后端服务器已停止")
        return True
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("LLM OS 新式后端启动器")
    print("版本: 1.0.0")
    print()
    
    # 检查依赖
    missing_packages = check_dependencies()
    
    if missing_packages:
        if not install_dependencies(missing_packages):
            print("\n请手动安装依赖:")
            print(f"pip install {' '.join(missing_packages)}")
            return
    
    # 检查 context_program
    check_context_program()
    
    # 启动后端
    start_backend()

if __name__ == "__main__":
    main()