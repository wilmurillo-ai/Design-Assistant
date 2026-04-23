#!/usr/bin/env python3
"""
授权码验证脚本 - 收费技能演示
- 演示模式：未配置 SKILL_LICENSE_VERIFY_URL 时，仅接受本地哈希校验（默认演示码 demo-license-123）
- 生产模式：设置 SKILL_LICENSE_VERIFY_URL 后，通过该 URL 进行服务端校验
"""

import argparse
import hashlib
import os
import sys
from typing import Tuple

# 公钥/盐值，实际部署请修改为你自己的值
SALT = "PaidSkillDemoClawHub2024"

# 演示用授权码（仅在不使用服务端验证时生效）
DEMO_LICENSE_KEY = "demo-license-123"


def hash_license(license_key: str, salt: str = SALT) -> str:
    """计算授权码哈希"""
    return hashlib.sha256((license_key + salt).encode()).hexdigest()


def get_encryption_key(license_key: str) -> bytes:
    """从授权码派生加密密钥"""
    return hashlib.sha256((license_key + SALT).encode()).digest()


def _verify_via_server(license_key: str, verify_url: str) -> Tuple[bool, str]:
    """通过服务端接口验证授权码。接口约定：POST JSON {"key": "xxx"}，返回 JSON {"valid": true/false, "message": "..."}"""
    try:
        import requests
        response = requests.post(
            verify_url.strip(),
            json={"key": license_key},
            timeout=10,
        )
        if response.status_code != 200:
            return False, f"验证服务返回 HTTP {response.status_code}"
        data = response.json()
        valid = data.get("valid", False)
        msg = data.get("message", "授权验证通过" if valid else "授权码无效")
        return bool(valid), str(msg)
    except Exception as e:
        return False, f"联网验证失败: {e}"


def check_license() -> Tuple[bool, str]:
    """
    检查授权码
    - 若设置了 SKILL_LICENSE_VERIFY_URL，则优先使用服务端验证（生产环境）
    - 否则使用本地哈希校验，仅接受 DEMO_LICENSE_KEY（演示用）
    返回: (是否有效, 消息)
    """
    license_key = os.environ.get("SKILL_LICENSE_KEY", "").strip()

    if not license_key:
        return False, "未配置授权码，请设置环境变量 SKILL_LICENSE_KEY"

    verify_url = os.environ.get("SKILL_LICENSE_VERIFY_URL", "").strip()
    if verify_url:
        return _verify_via_server(license_key, verify_url)

    # 演示模式：仅接受预设演示码
    expected_hash = hash_license(DEMO_LICENSE_KEY)
    user_hash = hash_license(license_key)
    if user_hash == expected_hash:
        return True, "授权验证通过（演示模式）"
    return False, "授权码无效，请检查 SKILL_LICENSE_KEY 配置。演示可用: " + DEMO_LICENSE_KEY


def main():
    parser = argparse.ArgumentParser(description="检查收费技能授权")
    args = parser.parse_args()

    valid, msg = check_license()

    if valid:
        print(f'{{"valid": true, "message": "{msg}"}}')
        sys.exit(0)
    else:
        print(f'{{"valid": false, "message": "{msg}"}}', file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()