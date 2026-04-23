#!/usr/bin/env python3
"""
Quark OCR - 夸克扫描王 OCR 识别服务
支持公网 URL 和本地文件上传（通过阿里云 OSS 临时上传）
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import uuid
import socket
import ipaddress
import base64
from typing import Tuple, Dict, Any, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from requests.exceptions import Timeout, ConnectionError


# --- 配置常量 ---
API_URL = "https://scan-business.quark.cn/vision"
ALLOWED_TARGET_HOST = "scan-business.quark.cn"

# URL 安全配置
MAX_URL_LENGTH = 2048
ALLOWED_PROTOCOLS = {"http", "https"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
DANGEROUS_KEYWORDS = ["localhost", "internal", "intranet", "admin", "test"]


@dataclass
class OCRResult:
    """OCR 识别结果"""
    code: str
    message: Optional[str]
    text_list: List[str]

    def to_json(self) -> str:
        return json.dumps({
            "code": self.code,
            "message": self.message,
            "Text": self.text_list
        }, ensure_ascii=False, indent=2)


class URLValidator:
    """URL 安全验证器"""

    @staticmethod
    def validate(url: str) -> Tuple[bool, Optional[str]]:
        if not url or not isinstance(url, str):
            return False, "URL cannot be empty"

        url = url.strip()
        if len(url) > MAX_URL_LENGTH:
            return False, f"URL exceeds maximum length of {MAX_URL_LENGTH} characters"

        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"

        if parsed.scheme.lower() not in ALLOWED_PROTOCOLS:
            return False, f"Protocol '{parsed.scheme}' not allowed."

        hostname = parsed.hostname
        if not hostname:
            return False, "URL must contain a valid hostname"

        hostname_lower = hostname.lower()
        for keyword in DANGEROUS_KEYWORDS:
            if keyword in hostname_lower:
                return False, f"Hostname contains restricted keyword: {keyword}"

        is_safe, err_msg = URLValidator._validate_dns_resolution(hostname)
        if not is_safe:
            return False, err_msg

        path = parsed.path.lower()
        if path and "." in path:
            ext = os.path.splitext(path)[1]
            if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
                return False, f"File extension '{ext}' not allowed."

        return True, None

    @staticmethod
    def _validate_dns_resolution(hostname: str) -> Tuple[bool, str]:
        try:
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for family, socktype, proto, canonname, sockaddr in addr_info:
                ip = sockaddr[0]
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                        return False, f"Security Block: {hostname} resolves to private/internal IP {ip}"
                except ValueError:
                    continue
            return True, "OK"
        except socket.gaierror:
            return True, "OK"


class CredentialManager:
    @staticmethod
    def load() -> Tuple[str, str]:
        cid = os.getenv("QUARK_OCR_CLIENT_ID", "").strip()
        csec = os.getenv("QUARK_OCR_CLIENT_SECRET", "").strip()
        if cid and csec:
            return cid, csec
        raise ValueError("Credentials missing: QUARK_OCR_CLIENT_ID and QUARK_OCR_CLIENT_SECRET required")


class SignatureGenerator:
    SUPPORTED_METHODS = {
        "sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5,
        "sha3-256": hashlib.sha3_256, "sha3_256": hashlib.sha3_256,
    }

    @classmethod
    def generate(cls, client_id: str, client_secret: str, business: str,
                 sign_method: str, sign_nonce: str, timestamp: int) -> str:
        raw_str = f"{client_id}_{business}_{sign_method}_{sign_nonce}_{timestamp}_{client_secret}"
        method_lower = sign_method.lower()
        if method_lower not in cls.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported sign method: {sign_method}")
        return cls.SUPPORTED_METHODS[method_lower](raw_str.encode("utf-8")).hexdigest()


class QuarkOCRClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()

        parsed_api = urlparse(API_URL)
        if parsed_api.hostname != ALLOWED_TARGET_HOST and not parsed_api.hostname.endswith("." + ALLOWED_TARGET_HOST):
            raise RuntimeError(f"Security Configuration Error: API_URL hostname '{parsed_api.hostname}' is not allowed.")

    def recognize(self, image_url: str = None, image_path: str = None, base64_data: str = None) -> OCRResult:
        """
        识别图片内容
        - image_url: 公网图片 URL（推荐）
        - image_path: 本地文件路径（会先上传到阿里云 OSS 获取临时 URL）
        - base64_data: base64 data URL 或纯 base64 字符串
        """
        if base64_data:
            return self._recognize_base64(base64_data)
        elif image_path:
            return self._recognize_local_file(image_path)
        else:
            is_valid, error_msg = URLValidator.validate(image_url)
            if not is_valid:
                return OCRResult(code="URL_VALIDATION_ERROR", message=f"URL validation failed: {error_msg}", text_list=[])
            param = self._build_request_param(image_url)
            response = self._send_request(param)
            return self._parse_response(response)

    def _recognize_base64(self, base64_data: str) -> OCRResult:
        """
        处理 base64 data URL 或纯 base64 字符串
        """
        # 解析 base64 data URL
        if base64_data.startswith('data:'):
            # 格式: data:image/jpeg;base64,/9j/4AAQ...
            try:
                # 提取 base64 部分
                if ';base64,' in base64_data:
                    base64_content = base64_data.split(';base64,')[1]
                else:
                    return OCRResult(code="BASE64_FORMAT_ERROR", message="Invalid base64 data URL format", text_list=[])
            except Exception as e:
                return OCRResult(code="BASE64_PARSE_ERROR", message=f"Failed to parse base64 data URL: {str(e)}", text_list=[])
        else:
            # 纯 base64 字符串
            base64_content = base64_data.strip()

        # 验证 base64 格式
        try:
            # 尝试解码验证
            base64.b64decode(base64_content)
        except Exception as e:
            return OCRResult(code="BASE64_DECODE_ERROR", message=f"Invalid base64 string: {str(e)}", text_list=[])

        # 使用 base64 方式调用 OCR
        param = self._build_request_param(base64_data=base64_content)
        response = self._send_request(param)
        return self._parse_response(response)

    def _recognize_local_file(self, file_path: str) -> OCRResult:
        """
        处理本地文件：先上传到阿里云 OSS 获取临时公网 URL，再用 URL 方式调用 OCR
        """
        file_path = os.path.expanduser(file_path.strip())

        # 验证文件
        is_valid, error_msg = self._validate_local_file(file_path)
        if not is_valid:
            return OCRResult(code="FILE_ERROR", message=f"File validation failed: {error_msg}", text_list=[])

        # 读取文件并转为 base64
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            base64_content = base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            return OCRResult(code="FILE_READ_ERROR", message=f"Failed to read file: {str(e)}", text_list=[])

        # 尝试使用阿里云 OSS 上传获取临时 URL
        oss_url = self._upload_to_oss_temp(file_path, base64_content)

        if oss_url:
            # 上传成功，使用 URL 方式调用 OCR
            param = self._build_request_param(image_url=oss_url)
            response = self._send_request(param)
            return self._parse_response(response)
        else:
            # OSS 未配置，直接使用 dataBase64 参数调用 OCR
            param = self._build_request_param(base64_data=base64_content)
            response = self._send_request(param)
            return self._parse_response(response)

    def _validate_local_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        if not file_path or not isinstance(file_path, str):
            return False, "File path cannot be empty"

        file_path = os.path.expanduser(file_path.strip())

        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        if not os.path.isfile(file_path):
            return False, f"Not a file: {file_path}"

        max_size = 10 * 1024 * 1024
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return False, f"File size exceeds {max_size / 1024 / 1024}MB limit"

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return False, f"File extension '{ext}' not allowed"

        return True, None

    def _upload_to_oss_temp(self, file_path: str, base64_content: str) -> Optional[str]:
        """
        上传文件到阿里云 OSS 获取临时公网 URL
        需要配置：ALIYUN_OSS_ENDPOINT, ALIYUN_OSS_BUCKET, ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET
        如果未配置，返回 None
        """
        oss_endpoint = os.getenv("ALIYUN_OSS_ENDPOINT")
        oss_bucket = os.getenv("ALIYUN_OSS_BUCKET")
        access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")

        if not all([oss_endpoint, oss_bucket, access_key_id, access_key_secret]):
            return None  # 未配置 OSS，返回 None

        try:
            import oss2
            auth = oss2.Auth(access_key_id, access_key_secret)
            bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket)

            # 生成唯一文件名
            ext = os.path.splitext(file_path)[1].lower()
            object_key = f"ocr-temp/{uuid.uuid4().hex}{ext}"

            # 上传文件
            bucket.put_object(object_key, base64.b64decode(base64_content))

            # 生成临时 URL（有效期 1 小时）
            url = bucket.sign_url('GET', object_key, 3600)
            return url
        except Exception as e:
            print(f"OSS upload failed: {e}", file=sys.stderr)
            return None

    def _build_request_param(self, image_url: str = None, base64_data: str = None) -> Dict[str, Any]:
        business = "vision"
        sign_method = "SHA3-256"
        sign_nonce = uuid.uuid4().hex
        timestamp = int(time.time() * 1000)
        signature = SignatureGenerator.generate(
            self.client_id, self.client_secret, business, sign_method, sign_nonce, timestamp
        )

        param = {
            "dataType": "image", "serviceOption": "ocr",
            "inputConfigs": json.dumps({"function_option": "RecognizeGeneralDocument"}),
            "outputConfigs": json.dumps({"need_return_image": "True"}),
            "reqId": uuid.uuid4().hex, "clientId": self.client_id,
            "signMethod": sign_method, "signNonce": sign_nonce,
            "timestamp": timestamp, "signature": signature,
        }

        # 根据输入类型选择使用 dataUrl 或 dataBase64
        if base64_data:
            param["dataBase64"] = base64_data
        else:
            param["dataUrl"] = image_url

        return param

    def _send_request(self, param: Dict[str, Any]) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        response = self.session.post(
            API_URL,
            json=param,
            headers=headers,
            timeout=60,
            allow_redirects=True
        )
        return response

    def _parse_response(self, response: requests.Response) -> OCRResult:
        if response.status_code != 200:
            error_msg = response.text[:200] if response.text else "No error message"
            return OCRResult(code="HTTP_ERROR", message=f"HTTP {response.status_code}: {error_msg}", text_list=[])
        try:
            body = response.json()
        except json.JSONDecodeError as e:
            return OCRResult(code="JSON_PARSE_ERROR", message=f"Failed to parse JSON: {str(e)}", text_list=[])

        code = body.get("code", "unknown")
        message = body.get("message")
        text_list = self._extract_text_list(body.get("data", {}))
        return OCRResult(code=code, message=message, text_list=text_list)

    def _extract_text_list(self, data: Dict[str, Any]) -> List[str]:
        if not isinstance(data, dict): return []
        ocr_info_list = data.get("OcrInfo", [])
        if not isinstance(ocr_info_list, list): return []
        return [str(item["Text"]) for item in ocr_info_list if isinstance(item, dict) and "Text" in item]


def main():
    parser = argparse.ArgumentParser(description="Quark OCR - Secure JSON Output")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", help="图片 URL")
    group.add_argument("--path", "-p", help="本地图片文件路径")
    group.add_argument("--base64", "-b", help="base64 data URL 或纯 base64 字符串")
    args = parser.parse_args()

    try:
        client_id, client_secret = CredentialManager.load()
        client = QuarkOCRClient(client_id, client_secret)

        if args.base64:
            result = client.recognize(base64_data=args.base64)
        elif args.url:
            result = client.recognize(image_url=args.url)
        else:
            result = client.recognize(image_path=args.path)

        print(result.to_json())
    except ValueError as e:
        print(OCRResult(code="CONFIG_ERROR", message=str(e), text_list=[]).to_json())
        sys.exit(1)
    except Timeout:
        print(OCRResult(code="TIMEOUT", message="Request timed out", text_list=[]).to_json())
        sys.exit(1)
    except ConnectionError as e:
        print(OCRResult(code="NETWORK_ERROR", message=f"Network failed: {str(e)}", text_list=[]).to_json())
        sys.exit(1)
    except Exception as e:
        print(OCRResult(code="UNKNOWN_ERROR", message=f"Unexpected error: {str(e)}", text_list=[]).to_json())
        sys.exit(1)


if __name__ == "__main__":
    main()
