#!/usr/bin/env python3
"""
性能基准测试脚本

测试不同模式下的识别速度和准确率

使用方法：
    python3 tests/benchmark.py
"""

import subprocess
import json
import time
from pathlib import Path
import sys

# 测试图片目录
TEST_IMAGES_DIR = Path(__file__).parent.parent / "tests" / "benchmark_images"

# 测试结果
results = []


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_result(name, success, time_cost, offset=None):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {name}: {time_cost:.3f}秒", end="")
    if offset:
        print(f" (offset={offset}px)", end="")
    print()


def run_test(image_path, mode="normal"):
    """运行单次测试"""
    cmd = [
        "python3",
        "scripts/recognize_puzzle.py",
        "--screenshot", str(image_path),
        "--benchmark"
    ]
    
    if mode != "normal":
        cmd.append(f"--{mode}")
    
    start = time.time()
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed = time.time() - start
    
    # 解析输出
    success = result.returncode == 0
    
    # 尝试从输出中提取 offset
    offset = None
    if "offset" in result.stdout:
        try:
            # 简单的字符串解析
            for line in result.stdout.split('\n'):
                if '"offset"' in line:
                    offset = line.split(':')[1].strip().rstrip(',')
                    break
        except:
            pass
    
    return {
        "success": success,
        "time": elapsed,
        "offset": offset,
        "mode": mode,
        "image": image_path.name
    }


def test_mode(image_path, mode, description):
    """测试特定模式"""
    print(f"\n测试：{description}")
    result = run_test(image_path, mode)
    print_result(
        f"{mode}模式",
        result["success"],
        result["time"],
        result["offset"]
    )
    return result


def create_test_image():
    """创建测试图片（如果不存在）"""
    if not TEST_IMAGES_DIR.exists():
        TEST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建测试目录：{TEST_IMAGES_DIR}")
    
    # 使用现有的测试图片
    test_image = Path(__file__).parent.parent.parent / "puzzle-captcha-solver" / "tests"
    if test_image.exists():
        # 复制一个测试图片
        import shutil
        test_files = list(test_image.glob("*.png"))
        if test_files:
            shutil.copy(test_files[0], TEST_IMAGES_DIR / "test_captcha.png")
            return TEST_IMAGES_DIR / "test_captcha.png"
    
    # 如果没有测试图片，创建一个简单的
    print("⚠️  未找到测试图片，请手动添加测试图片到 benchmark_images/ 目录")
    return None


def main():
    """主函数"""
    print_header("🧩 Puzzle Captcha Solver - 性能基准测试")
    
    # 创建测试图片
    test_image = create_test_image()
    if not test_image or not test_image.exists():
        print("\n❌ 无法找到或创建测试图片，退出测试")
        return 1
    
    print(f"\n📷 使用测试图片：{test_image.name}")
    
    # 测试不同模式
    print_header("测试不同识别模式")
    
    modes = [
        ("normal", "标准模式（平衡速度和精度）"),
        ("fast", "快速模式（速度优先）"),
        ("high-precision", "高精度模式（精度优先）"),
    ]
    
    all_results = []
    for mode, description in modes:
        result = test_mode(test_image, mode, description)
        all_results.append(result)
    
    # 汇总结果
    print_header("测试结果汇总")
    
    print(f"\n{'模式':<15} {'耗时 (秒)':<12} {'状态':<8} {'偏移量'}")
    print("-" * 50)
    
    for result in all_results:
        status = "✅ 成功" if result["success"] else "❌ 失败"
        offset = result["offset"] if result["offset"] else "-"
        print(f"{result['mode']:<15} {result['time']:<12.3f} {status:<8} {offset}")
    
    # 计算性能提升
    normal_time = next((r["time"] for r in all_results if r["mode"] == "normal"), None)
    fast_time = next((r["time"] for r in all_results if r["mode"] == "fast"), None)
    
    if normal_time and fast_time:
        improvement = ((normal_time - fast_time) / normal_time) * 100
        print(f"\n⚡ 快速模式性能提升：{improvement:.1f}%")
    
    # 保存结果
    results_file = Path(__file__).parent.parent / "benchmark_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "test_image": test_image.name,
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 结果已保存到：{results_file}")
    
    print("\n" + "=" * 60)
    print("✅ 基准测试完成！")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
