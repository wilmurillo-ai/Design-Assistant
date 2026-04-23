import sys
import os
import json
from pathlib import Path

def get_directory_stats(target_dir: str) -> dict:
    try:
        target_path = Path(target_dir).resolve()
    except Exception as e:
        return {"error": f"无效的路径格式: {str(e)}"}

    if not target_path.exists():
        return {"error": f"找不到该目录: {target_path}"}
    if not target_path.is_dir():
        return {"error": f"提供的路径不是一个目录: {target_path}"}

    file_count = 0
    total_size = 0

    for root, _, files in os.walk(target_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_count += 1
                total_size += os.path.getsize(file_path)

    return {
        "status": "success",
        "directory": str(target_path),
        "file_count": file_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }

if __name__ == "__main__":
    dir_path = None

    # 1. 读取大模型通过 stdin 传来的原始参数
    raw_stdin = sys.stdin.read().strip()

    # 2. 暴力解析参数（防范大模型乱起参数名）
    try:
        if raw_stdin:
            args = json.loads(raw_stdin)
            if isinstance(args, dict):
                # 尝试大模型可能使用的各种键名
                dir_path = args.get("path") or args.get("dir") or args.get("directory") or args.get("target_dir")

                # 有些大模型会把参数包在 args 数组里，如 {"args":["C:\\..."]}
                if not dir_path and "args" in args and isinstance(args["args"], list) and len(args["args"]) > 0:
                    dir_path = args["args"][0]

                # 如果还是找不到，去字典的值里扫一遍，只要长得像路径就拿来用
                if not dir_path:
                    for val in args.values():
                        if isinstance(val, str) and (":" in val or "/" in val or "\\" in val):
                            dir_path = val
                            break
            elif isinstance(args, list) and len(args) > 0:
                dir_path = args[0]
            elif isinstance(args, str):
                dir_path = args
    except Exception:
        pass

    # 3. 兼容终端直接运行的测试场景
    if not dir_path and len(sys.argv) > 1:
        dir_path = sys.argv[1]

    # 4. 【核心机制】如果真的没拿到参数，返回 0 并附带 Debug 信息
    if not dir_path:
        error_msg = {
            "error": "工具执行失败：未收到有效的目录路径参数。",
            "debug_you_sent_stdin": raw_stdin,  # 把大模型传的错乱参数原样拍给它看
            "instruction": "请必须使用 JSON 格式通过工具参数传递路径，例如: {\"path\": \"你的目标路径\"}"
        }
        print(json.dumps(error_msg))
        # 必须使用 exit(0)！这样 LangChain 不会崩溃，大模型会读到这串 JSON 并自动醒悟重新调用
        sys.exit(0)

        # 5. 执行核心逻辑
    stats = get_directory_stats(dir_path)
    print(json.dumps(stats))
    sys.exit(0)
