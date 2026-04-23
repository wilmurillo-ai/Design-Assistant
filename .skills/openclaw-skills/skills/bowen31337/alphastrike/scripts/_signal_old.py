#!/usr/bin/env python3
"""AlphaStrike v2 Signal Generator - Technical Analysis & Rule-Based Trading Signals.

Generates trading signals for BTC/ETH/SOL on Hyperliquid using:
- RSI (14): Overbought > 70, Oversold < 30
- MACD: Trend direction and momentum
- EMA Crossover (9/21): Short-term trend
- Bollinger Bands (20, 2): Volatility breakout
- Volume Ratio: Confirmation (1.5x normal = strong signal)

Output format: JSON with symbol, signal, confidence, indicators, reasoning
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from decimal import Decimal
from typing import Literal

import httpx

# ── Configuration ─────────────────────────────────────────────────────────────

SIGNALS = Literal["LONG", "SHORT", "HOLD"]
ASSETS = ["BTC", "ETH", "SOL"]

HL_INFO_URL = "https://api.hyperliquid.xyz/info"
HL_EXCHANGE_URL = "https://api.hyperliquid.xyz/exchange"

# Technical indicator thresholds
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_BULL_THRESHOLD = 0
MACD_BEAR_THRESHOLD = 0
EMA_THRESHOLD = 0
BB_THRESHOLD = 0
VOLUME_CONFIRM = 1.5

# Signal confidence levels
CONFIDENCE_HIGH = 0.8
CONFIDENCE_MED = 0.6
CONFIDENCE_LOW = 0.4


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class Indicators:
    """Technical indicators for a trading signal."""
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    ema_9: float | None = None
    ema_21: float | None = None
    ema_cross: float | None = None  # positive = bullish crossover
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    bb_position: float | None = None  # 0-1, where 1 = at upper band
    atr_14: float | None = None
    volume_ratio: float | None = None


@dataclass
class TradingSignal:
    """Trading signal with metadata."""
    symbol: str
    signal: SIGNALS
    confidence: float  # 0.0-1.0
    price: float
    indicators: dict
    reasoning: str
    timestamp: str


# ── Market Data ──────────────────────────────────────────────────────────────

async def fetch_candles(asset: str, interval: str = "1h", limit: int = 100) -> list[dict]:
    """Fetch candlestick data from Hyperliquid.

    Args:
        asset: Asset symbol (BTC, ETH, SOL)
        interval: Timeframe (1h, 4h, 1d)
        limit: Number of candles (max 1000)

    Returns:
        List of candles with time, open, high, low, close, volume
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HL_INFO_URL,
            json={
                "type": "candleSnapshot",
                "req": {
                    "coin": asset,
                    "interval": interval,
                    "startTime": 0,  # fetch from beginning
                }
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

    # API returns array of [time, open, high, low, close, volume]
    candles = []
    for candle in data:
        candles.append({
            "time": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
        })

    # Return most recent N candles
    return candles[-limit:]


async def fetch_current_price(asset: str) -> float:
    """Fetch current mid price for an asset."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HL_INFO_URL,
            json={"type": "allMids"},
            timeout=10.0
        )
        response.raise_for_status()
        prices = response.json()

    return float(prices.get(asset, 0))


# ── Technical Indicators ─────────────────────────────────────────────────────

def calculate_rsi(closes: list[float], period: int = 14) -> float | None:
    """Calculate Relative Strength Index (RSI)."""
    if len(closes) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[float, float, float] | tuple[None, None, None]:
    """Calculate MACD (Moving Average Convergence Divergence).

    Returns:
        (macd_line, signal_line, histogram)
    """
    if len(closes) < slow + signal:
        return None, None, None

    # Calculate EMAs
    def ema(data: list[float], period: int) -> float:
        multiplier = 2 / (period + 1)
        ema_val = data[0]
        for price in data[1:]:
            ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
        return ema_val

    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line = ema_fast - ema_slow

    # For signal line, we'd need historical MACD values
    # Simplified: use recent MACD values
    macd_values = []
    for i in range(len(closes) - slow, len(closes)):
        slice_closes = closes[:i+1]
        if len(slice_closes) >= slow:
            ef = ema(slice_closes, fast)
            es = ema(slice_closes, slow)
            macd_values.append(ef - es)

    if len(macd_values) < signal:
        return macd_line, None, None

    signal_line = ema(macd_values[-signal:], signal)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_ema(closes: list[float], period: int) -> float | None:
    """Calculate Exponential Moving Average (EMA)."""
    if len(closes) < period:
        return None

    multiplier = 2 / (period + 1)
    ema_val = closes[0]

    for price in closes[1:]:
        ema_val = (price * multiplier) + (ema_val * (1 - multiplier))

    return ema_val


def calculate_bollinger_bands(closes: list[float], period: int = 20, std_dev: float = 2) -> tuple[float, float, float] | tuple[None, None, None]:
    """Calculate Bollinger Bands.

    Returns:
        (upper_band, middle_band, lower_band)
    """
    if len(closes) < period:
        return None, None, None

    recent = closes[-period:]
    sma = sum(recent) / period
    variance = sum((x - sma) ** 2 for x in recent) / period
    std = variance ** 0.5

    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)

    return upper, sma, lower


def calculate_atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float | None:
    """Calculate Average True Range (ATR)."""
    if len(closes) < period + 1:
        return None

    true_ranges = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        true_ranges.append(tr)

    atr = sum(true_ranges[-period:]) / period
    return atr


def calculate_indicators(candles: list[dict]) -> Indicators:
    """Calculate all technical indicators for a given candle history."""
    if len(candles) < 30:
        return Indicators()

    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    volumes = [c["volume"] for c in candles]

    # RSI
    rsi = calculate_rsi(closes, 14)

    # MACD
    macd, macd_sig, macd_h = calculate_macd(closes)

    # EMA crossover (9/21)
    ema_9 = calculate_ema(closes, 9)
    ema_21 = calculate_ema(closes, 21)
    ema_cross = None
    if ema_9 and ema_21:
        ema_cross = ema_9 - ema_21

    # Bollinger Bands
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(closes, 20, 2)
    bb_position = None
    if bb_upper and bb_lower:
        current_price = closes[-1]
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)

    # ATR
    atr = calculate_atr(highs, lows, closes, 14)

    # Volume ratio
    vol_ratio = None
    if len(volumes) >= 20:
        recent_vol = volumes[-1]
        avg_vol = sum(volumes[-20:-1]) / 19
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else None

    return Indicators(
        rsi_14=rsi,
        macd=macd,
        macd_signal=macd_sig,
        macd_hist=macd_h,
        ema_9=ema_9,
        ema_21=ema_21,
        ema_cross=ema_cross,
        bb_upper=bb_upper,
        bb_middle=bb_mid,
        bb_lower=bb_lower,
        bb_position=bb_position,
        atr_14=atr,
        volume_ratio=vol_ratio,
    )


# ── Signal Generation ─────────────────────────────────────────────────────────

def generate_signal(asset: str, indicators: Indicators, current_price: float) -> TradingSignal:
    """Generate a trading signal based on technical indicators.

    Rules:
    - LONG: RSI oversold + MACD bullish + EMA cross + volume confirmation
    - SHORT: RSI overbought + MACD bearish + EMA cross + volume confirmation
    - HOLD: No clear signal or conflicting signals
    """
    bullish_signals = 0
    bearish_signals = 0
    reasons = []

    # RSI signals
    if indicators.rsi_14:
        if indicators.rsi_14 < RSI_OVERSOLD:
            bullish_signals += 1
            reasons.append(f"RSI oversold ({indicators.rsi_14:.1f})")
        elif indicators.rsi_14 > RSI_OVERBOUGHT:
            bearish_signals += 1
            reasons.append(f"RSI overbought ({indicators.rsi_14:.1f})")

    # MACD signals
    if indicators.macd_hist:
        if indicators.macd_hist > 0:
            bullish_signals += 1
            reasons.append(f"MACD bullish (hist {indicators.macd_hist:.4f})")
        else:
            bearish_signals += 1
            reasons.append(f"MACD bearish (hist {indicators.macd_hist:.4f})")

    # EMA crossover
    if indicators.ema_cross:
        if indicators.ema_cross > 0:
            bullish_signals += 1
            reasons.append(f"EMA 9/21 bullish cross")
        else:
            bearish_signals += 1
            reasons.append(f"EMA 9/21 bearish cross")

    # Bollinger Bands
    if indicators.bb_position:
        if indicators.bb_position < 0.2:
            bullish_signals += 1
            reasons.append(f"Price near BB lower ({indicators.bb_position:.2f})")
        elif indicators.bb_position > 0.8:
            bearish_signals += 1
            reasons.append(f"Price near BB upper ({indicators.bb_position:.2f})")

    # Volume confirmation
    volume_confirmed = indicators.volume_ratio and indicators.volume_ratio > VOLUME_CONFIRM

    # Determine signal
    signal: SIGNALS = "HOLD"
    confidence = 0.0

    if bullish_signals >= 3 and volume_confirmed:
        signal = "LONG"
        confidence = CONFIDENCE_HIGH if bullish_signals >= 4 else CONFIDENCE_MED
    elif bearish_signals >= 3 and volume_confirmed:
        signal = "SHORT"
        confidence = CONFIDENCE_HIGH if bearish_signals >= 4 else CONFIDENCE_MED
    elif bullish_signals >= 2:
        signal = "LONG"
        confidence = CONFIDENCE_LOW
    elif bearish_signals >= 2:
        signal = "SHORT"
        confidence = CONFIDENCE_LOW

    reasoning = "; ".join(reasons) if reasons else "No clear signal"
    if volume_confirmed:
        reasoning += f"; volume confirmed ({indicators.volume_ratio:.1f}x)"

    return TradingSignal(
        symbol=asset,
        signal=signal,
        confidence=confidence,
        price=current_price,
        indicators=asdict(indicators),
        reasoning=reasoning,
        timestamp=datetime.now(UTC).isoformat(),
    )


# ── CLI ─────────────────────────────────────────────────────────────────────

async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate trading signals using technical analysis"
    )
    parser.add_argument(
        "--assets",
        nargs="+",
        default=ASSETS,
        help=f"Assets to analyze (default: {' '.join(ASSETS)})"
    )
    parser.add_argument(
        "--interval",
        default="1h",
        help="Candle interval (default: 1h)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of candles to fetch (default: 100)"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimum confidence to include in output (default: 0.3)"
    )
    parser.add_argument(
        "--output",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    results = []

    for asset in args.assets:
        try:
            # Fetch data
            candles = await fetch_candles(asset, args.interval, args.limit)
            current_price = await fetch_current_price(asset)

            if not candles:
                print(f"[WARN] No candles for {asset}", file=sys.stderr)
                continue

            # Calculate indicators
            indicators = calculate_indicators(candles)

            # Generate signal
            signal = generate_signal(asset, indicators, current_price)

            if signal.confidence >= args.min_confidence:
                results.append(signal)

        except Exception as e:
            print(f"[ERROR] {asset}: {e}", file=sys.stderr)

    # Output
    if args.output == "json":
        output = {
            "ok": True,
            "signals": [asdict(s) for s in results],
            "count": len(results),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        print(json.dumps(output, indent=2))
    else:
        # Summary format
        for s in results:
            print(f"{s.symbol}: {s.signal} (conf={s.confidence:.0%}) | {s.reasoning}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
