#!/usr/bin/env python3
"""
上传文件到七牛云存储（基础能力）

用途：获取七牛上传凭证 → 上传文件 → 返回下载地址

使用方式：
  python3 xgjk-base-skills/scripts/file_storage/qiniu_upload.py <file-path> [--file-key <key>] [--corp-id <id>]
  python3 xgjk-base-skills/scripts/file_storage/qiniu_upload.py <file-path> --context-json '{"access-token":"..."}'

环境变量：
  XG_USER_TOKEN   — access-token（优先）
  XG_BIZ_API_KEY  — 若无 token，则自动用 appKey 换取
  XG_CORP_ID      — 企业 ID（可选）

输出：
  成功时输出下载地址到 stdout

被其他脚本引用：
  from file_storage.qiniu_upload import get_qiniu_token, upload_file
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
import ssl
import io

# 七牛上传凭证接口
QINIU_AUTH_URL = "https://sg-cwork-api.mediportal.com.cn/ai-business/qiNiu/getSimpleUploadCredentials"

# 七牛上传地址（z2 区域）
QINIU_UPLOAD_URL = "https://up-z2.qiniup.com/"


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def get_qiniu_token(access_token: str, file_key: str, corp_id: str = "") -> dict:
    """
    获取七牛上传凭证，返回 {token, domain}。
    与前端逻辑一致：先 GET，GET 不支持则 fallback 到 POST。
    """
    ctx = _ssl_context()

    query_params = {"fileKey": file_key, "corpId": corp_id}
    get_url = f"{QINIU_AUTH_URL}?{urllib.parse.urlencode(query_params)}"

    headers = {
        "access-token": access_token,
        "Content-Type": "application/json",
    }

    # ── 尝试 GET ──
    try:
        req = urllib.request.Request(get_url, headers=headers, method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("data") and data["data"].get("token") and data["data"].get("domain"):
            return data["data"]
        msg = (data.get("resultMsg") or data.get("detailMsg") or "").lower()
        if "not supported" not in msg and "method not allowed" not in msg:
            raise RuntimeError(f"获取七牛凭证失败 (GET): {json.dumps(data, ensure_ascii=False)}")
    except urllib.error.HTTPError as e:
        if e.code != 405:
            raise

    # ── Fallback POST ──
    print("GET 方式不支持，尝试 POST ...", file=sys.stderr)
    post_body = {"fileKey": file_key, "corpId": corp_id}
    body_bytes = json.dumps(post_body).encode("utf-8")

    req = urllib.request.Request(QINIU_AUTH_URL, data=body_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if not data.get("data") or not data["data"].get("token"):
        raise RuntimeError(f"获取七牛凭证失败 (POST): {json.dumps(data, ensure_ascii=False)}")

    return data["data"]


def upload_file(qiniu_token: str, file_key: str, file_path: str) -> bool:
    """通过 multipart/form-data 上传文件到七牛"""
    import re

    boundary = f"----PythonBoundary{int(time.time() * 1000)}"
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_data = f.read()

    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode())
    body.write(b'Content-Disposition: form-data; name="token"\r\n\r\n')
    body.write(f"{qiniu_token}\r\n".encode())
    body.write(f"--{boundary}\r\n".encode())
    body.write(b'Content-Disposition: form-data; name="key"\r\n\r\n')
    body.write(f"{file_key}\r\n".encode())
    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode())
    body.write(b"Content-Type: application/octet-stream\r\n\r\n")
    body.write(file_data)
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())

    body_bytes = body.getvalue()
    ctx = _ssl_context()

    req = urllib.request.Request(
        QINIU_UPLOAD_URL,
        data=body_bytes,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body_bytes)),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
            if resp.getcode() != 200:
                raise RuntimeError(f"七牛上传失败 (HTTP {resp.getcode()})")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        region_match = re.search(r'please use\s+([a-z0-9.-]+)', error_body, re.IGNORECASE)
        if region_match:
            new_host = region_match.group(1)
            new_url = f"https://{new_host}/"
            print(f"区域重定向: {new_url}", file=sys.stderr)
            req2 = urllib.request.Request(
                new_url, data=body_bytes,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body_bytes))},
                method="POST",
            )
            with urllib.request.urlopen(req2, context=ctx, timeout=300) as resp2:
                if resp2.getcode() != 200:
                    raise RuntimeError(f"七牛上传失败（重定向后）")
        else:
            raise RuntimeError(f"七牛上传失败 (HTTP {e.code}): {error_body}")

    return True


def main():
    parser = argparse.ArgumentParser(description="上传文件到七牛云存储")
    parser.add_argument("file_path", help="要上传的文件路径")
    parser.add_argument("--file-key", default="", help="七牛文件 key（默认自动生成）")
    parser.add_argument("--corp-id", default="", help="企业 ID")
    parser.add_argument("--context-json", default="", help="显式传入上下文 JSON/文本")
    args = parser.parse_args()

    # 使用 build_auth_headers 自动处理 access-token 获取
    try:
        auth_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if auth_parent not in sys.path:
            sys.path.insert(0, auth_parent)
        from auth.login import build_auth_headers
    except ImportError as exc:
        print(f"错误: 无法加载鉴权模块: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        auth_headers = build_auth_headers("access-token", context=args.context_json)
        token = auth_headers["access-token"]
    except RuntimeError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)

    corp_id = args.corp_id or os.environ.get("XG_CORP_ID", "")
    file_path = os.path.abspath(args.file_path)
    if not os.path.isfile(file_path):
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    file_name = os.path.basename(file_path)
    file_key = args.file_key or f"{int(time.time() * 1000)}-{file_name}"

    print(f"[1/2] 获取七牛上传凭证 (fileKey={file_key}) ...", file=sys.stderr)
    creds = get_qiniu_token(token, file_key, corp_id)
    qiniu_token = creds["token"]
    domain = creds["domain"]
    print(f"[1/2] 凭证获取成功，domain={domain}", file=sys.stderr)

    size_kb = os.path.getsize(file_path) / 1024
    print(f"[2/2] 上传 {file_name} ({size_kb:.1f} KB) ...", file=sys.stderr)
    upload_file(qiniu_token, file_key, file_path)

    base_url = domain if domain.startswith("http") else f"https://{domain}"
    download_url = f"{base_url.rstrip('/')}/{file_key}"

    print(f"[2/2] 上传成功!", file=sys.stderr)
    print(f"下载地址: {download_url}", file=sys.stderr)
    print(download_url)


if __name__ == "__main__":
    main()
