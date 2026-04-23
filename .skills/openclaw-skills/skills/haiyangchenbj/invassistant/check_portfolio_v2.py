#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓美股+港股信号检查 v2 — 模块化版本
调用 scripts/ 下的模块化引擎（redline_engine + exit_engine + data_fetcher）

保留原 check_portfolio.py 不动（作为回退），此文件是统一后的新入口。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from portfolio_checker import main

if __name__ == "__main__":
    main()
