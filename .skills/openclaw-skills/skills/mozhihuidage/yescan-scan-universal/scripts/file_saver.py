#!/usr/bin/env python3
"""
FileSaver - 简单的文件保存器
用于保存 OCR 结果到文件
"""
import os
import base64
import time
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

# 默认保存目录：yescan-scan-universal 技能目录下的 outputs 目录（支持环境变量覆盖）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SAVE_DIR = os.getenv("YESCAN_OUTPUT_DIR", os.path.join(SCRIPT_DIR, "outputs"))

# 成功响应码
SUCCESS_CODE = 0
ERROR_CODE = -1

class FileSaver:
    """简单的文件保存器，支持保存文本和二进制文件"""

    def __init__(self, default_dir: Optional[str] = None):
        """
        初始化文件保存器

        Args:
            default_dir: 默认保存目录，如果为 None 则使用环境变量或 /tmp
        """
        self.default_dir = default_dir or DEFAULT_SAVE_DIR
        # 确保默认目录存在
        Path(self.default_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"FileSaver initialized with default directory: {self.default_dir}")

    def _generate_filepath(self, extension: str) -> str:
        """
        生成带时间戳的随机文件路径

        Args:
            extension: 文件扩展名（如 .txt, .docx）

        Returns:
            完整的文件路径
        """
        filename = f"{int(time.time())}_{os.urandom(8).hex()}{extension}"
        return os.path.join(self.default_dir, filename)

    def save_text(self, content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        保存文本内容到文件

        Args:
            content: 要保存的文本内容
            filepath: 目标文件路径，如果为 None 则使用默认路径

        Returns:
            {"code": 0, "msg": "success", "data": {"path": "/path/to/file"}}
            或 {"code": -1, "msg": "error reason", "data": {}}
        """
        if not content:
            error_msg = "内容不能为空"
            logger.error(error_msg)
            return {"code": ERROR_CODE, "msg": error_msg, "data": {}}

        if filepath is None:
            filepath = self._generate_filepath(".txt")

        try:
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"文本保存成功: {filepath}")
            return {"code": SUCCESS_CODE, "msg": "success", "data": {"path": filepath}}
        except (IOError, OSError) as e:
            error_msg = f"保存文本失败: {str(e)}"
            logger.error(error_msg)
            return {"code": ERROR_CODE, "msg": error_msg, "data": {}}

    def _save_binary_from_base64(self, base64_content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        从 BASE64 保存二进制文件

        Args:
            base64_content: BASE64 编码的内容
            filepath: 目标文件路径，如果为 None 则使用默认路径

        Returns:
            {"code": 0, "msg": "success", "data": {"path": "/path/to/file"}}
            或 {"code": -1, "msg": "error reason", "data": {}}
        """
        if not base64_content:
            error_msg = "BASE64 内容不能为空"
            logger.error(error_msg)
            return {"code": ERROR_CODE, "msg": error_msg, "data": {}}

        if filepath is None:
            filepath = self._generate_filepath(".bin")

        try:
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(base64_content))
            logger.info(f"二进制文件保存成功: {filepath}")
            return {"code": SUCCESS_CODE, "msg": "success", "data": {"path": filepath}}
        except (IOError, OSError, base64.binascii.Error) as e:
            error_msg = f"保存二进制文件失败: {str(e)}"
            logger.error(error_msg)
            return {"code": ERROR_CODE, "msg": error_msg, "data": {}}

    def save_word_from_base64(self, base64_content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        从 BASE64 保存 Word 文档

        Args:
            base64_content: BASE64 编码的 Word 文档内容
            filepath: 目标文件路径，如果为 None 则使用默认路径

        Returns:
            {"code": 0, "msg": "success", "data": {"path": "/path/to/file"}}
            或 {"code": -1, "msg": "error reason", "data": {}}
        """
        if filepath is None:
            filepath = self._generate_filepath(".docx")
        return self._save_binary_from_base64(base64_content, filepath)

    def save_excel_from_base64(self, base64_content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        从 BASE64 保存 Excel 文档

        Args:
            base64_content: BASE64 编码的 Excel 文档内容
            filepath: 目标文件路径，如果为 None 则使用默认路径

        Returns:
            {"code": 0, "msg": "success", "data": {"path": "/path/to/file"}}
            或 {"code": -1, "msg": "error reason", "data": {}}
        """
        if filepath is None:
            filepath = self._generate_filepath(".xlsx")
        return self._save_binary_from_base64(base64_content, filepath)

    def save_image_from_base64(self, base64_content: str, image_format: str = "png") -> Dict[str, Any]:
        """
        从 BASE64 字符串保存图像，并返回标准响应结构。
        自动清理 data URL 前缀，支持 png/jpg/webp。

        Args:
            base64_content: BASE64 编码的图片内容
            image_format: 图片格式（png/jpg/webp），默认为 png

        Returns:
            {"code": 0, "msg": "success", "data": {"path": "/path/to/file"}}
            或 {"code": -1, "msg": "error reason", "data": {}}
        """
        # 清理 data:image/xxx;base64, 前缀
        if isinstance(base64_content, str) and base64_content.strip().startswith("data:"):
            try:
                base64_content = base64_content.split(",", 1)[1].strip()
            except (IndexError, ValueError):
                return {"code": ERROR_CODE, "msg": "Invalid data URL format", "data": {}}

        # 校验 Base64 合法性（长度、字符）
        try:
            if len(base64_content) % 4 != 0:
                raise ValueError("Base64 string length not multiple of 4")
            base64.b64decode(base64_content, validate=True)
        except Exception as e:
            return {"code": ERROR_CODE, "msg": f"Invalid Base64: {str(e)}", "data": {}}

        # 推导扩展名
        ext = "." + image_format.lower().replace("jpeg", "jpg")
        # 图片保存到 outputs/imgs/ 子目录
        imgs_dir = os.path.join(self.default_dir, "imgs")
        Path(imgs_dir).mkdir(parents=True, exist_ok=True)
        filename = f"{int(time.time())}_{os.urandom(8).hex()}{ext}"
        filepath = os.path.join(imgs_dir, filename)

        # 调用底层保存
        return self._save_binary_from_base64(base64_content, filepath)