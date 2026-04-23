#!/usr/bin/env python3
"""
Lota Football Skill - 脚本包装器

这个文件是 scripts/lota_football.py 的包装器，提供简单的命令行接口。
"""

import os
import sys
import subprocess

def main():
    """主函数：调用 scripts/lota_football.py"""
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'lota_football.py')

    if not os.path.exists(script_path):
        print(f"错误：找不到脚本文件 {script_path}")
        print("请确保 scripts/lota_football.py 存在")
        sys.exit(1)

    # 传递所有参数给底层脚本
    cmd = [sys.executable, script_path] + sys.argv[1:]

    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()