#!/usr/bin/env python3
"""Quark OCR - 夸克扫描王图片增强服务"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from common import run_ocr, save_image_from_result

if __name__ == "__main__":
    run_ocr(result_handler=save_image_from_result)
