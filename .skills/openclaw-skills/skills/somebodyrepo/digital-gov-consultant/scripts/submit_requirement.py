import json
import argparse
import subprocess
from urllib.parse import urlparse
from pathlib import Path


def _is_wsl():
    """检测是否在 WSL 环境中"""
    try:
        return 'microsoft' in Path('/proc/version').read_text().lower()
    except Exception:
        return False


def _curl_post(url, payload, proxy=None):
    """通过 Windows curl.exe 发起 POST 请求（WSL 下使用）"""
    args = [
        'curl.exe', '-s', url,
        '-X', 'POST',
        '-H', 'Content-Type: application/json',
        '--data-raw', json.dumps(payload, ensure_ascii=False),
    ]
    if proxy:
        args.extend(['--proxy', proxy])

    try:
        result = subprocess.run(
            args,
            capture_output=True, text=True, timeout=20
        )
        if result.stdout:
            try:
                return json.loads(result.stdout)
            except Exception:
                return {"raw": result.stdout}
        return {"error": result.stderr or "No response"}
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


def _requests_post(url, payload, proxy=None):
    """通过 Python requests 发起 POST 请求（非 WSL 环境使用）"""
    import requests
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
            proxies=proxies
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def submit_requirement(requirement, base_url="https://digital.somebody.icu", proxy=None):
    """
    提交需求到 API 并返回任务 ID
    WSL 环境下通过 Windows curl.exe 发起请求（解决 IPv6 不通问题）
    """
    parsed = urlparse(base_url)
    port = parsed.port or 80
    api_url = f"{base_url}/api/generate"
    payload = {"requirement": requirement}

    if _is_wsl():
        # WSL 下直接用 Windows curl，Windows 负责 DNS 解析
        return _curl_post(api_url, payload, proxy)
    else:
        return _requests_post(api_url, payload, proxy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit requirement to Digital Gov Consultant API")
    parser.add_argument("requirement", help="The requirement text to submit")
    parser.add_argument("base_url", nargs="?", default="https://digital.somebody.icu", help="API base URL")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:7890)")

    args = parser.parse_args()
    result = submit_requirement(args.requirement, args.base_url, args.proxy)
    print(json.dumps(result, ensure_ascii=False))
