#!/usr/bin/env python3
"""
快速测试脚本 - 验证技能安装和基本功能

使用方法：
    python3 tests/quick_test.py
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """打印成功信息"""
    print(f"✅ {text}")

def print_error(text):
    """打印错误信息"""
    print(f"❌ {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"⚠️  {text}")

def test_python_version():
    """测试 Python 版本"""
    print_header("1. 检查 Python 版本")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python 版本：{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 版本过低：{version.major}.{version.minor}.{version.micro}")
        print_warning("需要 Python 3.8 或更高版本")
        return False

def test_dependencies():
    """测试依赖包"""
    print_header("2. 检查依赖包")
    
    deps = {
        "cv2": "opencv-python",
        "numpy": "numpy",
        "PIL": "pillow",
    }
    
    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print_success(f"{package} 已安装")
        except ImportError:
            print_error(f"{package} 未安装")
            print_warning(f"运行：pip install {package}")
            all_ok = False
    
    return all_ok

def test_scripts():
    """测试脚本文件"""
    print_header("3. 检查脚本文件")
    
    scripts = [
        "scripts/recognize_puzzle.py",
        "scripts/execute_drag.js",
    ]
    
    all_ok = True
    for script in scripts:
        script_path = Path(__file__).parent.parent / script
        if script_path.exists():
            print_success(f"{script} 存在")
        else:
            print_error(f"{script} 不存在")
            all_ok = False
    
    return all_ok

def test_recognize_help():
    """测试识别脚本帮助"""
    print_header("4. 测试识别脚本")
    
    try:
        result = subprocess.run(
            ["python3", "scripts/recognize_puzzle.py", "--help"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "拼图滑块验证码识别" in result.stdout:
            print_success("识别脚本正常运行")
            return True
        else:
            print_error("识别脚本运行异常")
            return False
    except Exception as e:
        print_error(f"识别脚本测试失败：{e}")
        return False

def test_test_suite():
    """测试单元测试"""
    print_header("5. 运行单元测试")
    
    try:
        result = subprocess.run(
            ["python3", "tests/test_recognize.py"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("所有测试通过")
            return True
        else:
            print_error("部分测试失败")
            print(result.stdout[-500:])  # 显示最后 500 字符
            return False
    except Exception as e:
        print_error(f"测试套件运行失败：{e}")
        return False

def main():
    """主函数"""
    print_header("🧩 Puzzle Captcha Solver - 快速测试")
    print("本测试将验证技能安装和基本功能\n")
    
    results = []
    
    # 运行各项测试
    results.append(("Python 版本", test_python_version()))
    results.append(("依赖包", test_dependencies()))
    results.append(("脚本文件", test_scripts()))
    results.append(("识别脚本", test_recognize_help()))
    results.append(("单元测试", test_test_suite()))
    
    # 汇总结果
    print_header("测试结果汇总")
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print_success("🎉 所有测试通过！技能已正确安装")
        print("\n下一步：")
        print("  1. 阅读文档：cat SKILL.md")
        print("  2. 运行示例：python3 scripts/recognize_puzzle.py --help")
        print("  3. 开始使用：参考 SKILL.md 中的使用示例")
        return 0
    else:
        print_error("部分测试失败，请根据上方提示修复")
        print("\n帮助：")
        print("  - 安装依赖：pip install -r requirements.txt")
        print("  - 查看文档：cat SKILL.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
