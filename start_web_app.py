#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
眼部健康大模型Web应用启动脚本
提供现代化的前端界面，整合所有眼部健康功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查Web应用依赖"""
    required_modules = [
        'flask',
        'flask_cors',
        'aiohttp',
        'pydantic'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少以下Web应用依赖模块: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_local_model():
    """检查本地模型服务"""
    import aiohttp
    import asyncio
    
    async def test_ollama():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags", timeout=5) as response:
                    if response.status == 200:
                        return True
        except:
            pass
        return False
    
    # 同步检查
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_ollama())
        loop.close()
        return result
    except:
        return False

def main():
    """主函数"""
    print("=== 眼部健康大模型Web应用 ===")
    print("正在检查系统环境...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    print("✅ Web应用依赖检查通过")
    
    # 检查本地模型
    if not check_local_model():
        print("❌ 本地Ollama服务未启动")
        print("请先启动Ollama服务:")
        print("1. 安装Ollama: https://ollama.ai/")
        print("2. 拉取DeepSeek模型: ollama pull deepseek-chat")
        print("3. 启动Ollama服务: ollama serve")
        print("\n或者使用其他启动方式:")
        print("- python run_eye_health_system.py (命令行版)")
        print("- python eye_health_agent_integrated.py (智能代理版)")
        sys.exit(1)
    print("✅ 本地模型服务正常")
    
    # 导入并启动Web应用
    try:
        from eye_health_web_app import main as run_web_app
        print("🚀 启动Web应用...")
        run_web_app()
    except ImportError as e:
        print(f"❌ 导入Web应用模块失败: {e}")
        print("请检查文件是否存在")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Web应用启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 