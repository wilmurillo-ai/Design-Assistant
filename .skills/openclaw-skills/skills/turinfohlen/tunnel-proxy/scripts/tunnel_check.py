#!/usr/bin/env python3
"""
tunnel_check.py — 隧道连通性快速检测工具

用法：
    export TUNNEL_HOST="<用户提供的地址>"
    export TUNNEL_PORT="<用户提供的PTY端口>"
    export TUNNEL_HTTP_PORT="<用户提供的HTTP端口>"
    python3 tunnel_check.py

在脚本中调用：
    from tunnel_check import check_tunnel
    status = check_tunnel()
    if status["pty"] and status["http"]:
        print("隧道正常，可以操作")
"""

import os
import socket
import requests
from typing import Dict

HOST = os.environ.get("TUNNEL_HOST", "127.0.0.1")
PTY_PORT = int(os.environ.get("TUNNEL_PORT", "27417"))
HTTP_PORT = int(os.environ.get("TUNNEL_HTTP_PORT", "8080"))


def check_tunnel(host: str = HOST, pty_port: int = PTY_PORT, http_port: int = HTTP_PORT) -> Dict[str, bool]:
    result = {"http": False, "pty": False}
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, pty_port))
        sock.close()
        result["pty"] = True
    except Exception:
        pass
    
    try:
        r = requests.get(f"http://{host}:{http_port}/", timeout=5)
        result["http"] = (r.status_code == 200)
    except Exception:
        pass
    
    return result


def main():
    status = check_tunnel()
    
    print(f"PTY 端口 ({PTY_PORT}):  {'✓ 可达' if status['pty'] else '✗ 不可达'}")
    print(f"HTTP 端口 ({HTTP_PORT}): {'✓ 可达' if status['http'] else '✗ 不可达'}")
    
    if status["pty"] and status["http"]:
        print("\n✅ 隧道完全正常")
        return 0
    elif status["pty"] or status["http"]:
        print("\n⚠️  隧道部分可用")
        return 1
    else:
        print("\n❌ 隧道不可用")
        return 2


if __name__ == "__main__":
    exit(main())