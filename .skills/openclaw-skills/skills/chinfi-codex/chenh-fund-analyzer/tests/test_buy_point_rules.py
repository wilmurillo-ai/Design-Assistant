import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))

from buy_point_rules import (
    analyze_buy_signals,
    detect_candlestick,
    process_market_data,
    process_nav_data,
    trading_days_between,
)


def test_trading_days_between_uses_index_distance():
    index = pd.bdate_range("2025-01-01", periods=10)
    assert trading_days_between(index, index[1], index[6]) == 5


def test_detect_candlestick_identifies_hammer():
    frame = pd.DataFrame(
        {
            "open": [100, 101, 100],
            "high": [102, 103, 101],
            "low": [99, 98, 90],
            "close": [101, 100, 100.5],
        },
        index=pd.bdate_range("2025-01-01", periods=3),
    )
    assert detect_candlestick(frame) == "锤子线"


def test_dual_mode_analysis_returns_structured_result():
    idx = pd.bdate_range("2024-01-01", periods=320)
    nav_values = [1.0 + i * 0.002 for i in range(280)]
    nav_values += [1.56, 1.58, 1.60, 1.62, 1.61, 1.60, 1.59, 1.58, 1.57, 1.56]
    nav_values += [1.55 - i * 0.0005 for i in range(30)]
    nav_df = pd.DataFrame({"nav": nav_values[:320]}, index=idx)

    market_close = pd.Series([3000 + i * 3 for i in range(320)], index=idx)
    market_df = pd.DataFrame(
        {
            "open": market_close.shift(1).fillna(market_close.iloc[0]),
            "high": market_close * 1.01,
            "low": market_close * 0.99,
            "close": market_close,
            "vol": pd.Series([4e8 - i * 1e5 for i in range(320)], index=idx),
        }
    )

    nav_data = process_nav_data(nav_df)
    market_data = process_market_data(market_df)
    signals = analyze_buy_signals(nav_data, market_data)

    assert "left_mode" in signals
    assert "right_mode" in signals
    assert "overall" in signals
    assert signals["left_mode"]["stage"] in {"条件不足", "左侧关注", "左侧观察", "左侧试仓"}
    assert signals["right_mode"]["stage"] in {"条件不足", "右侧跟踪", "右侧确认"}
