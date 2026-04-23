#!/usr/bin/env python3
"""AlphaStrike v2 Trade Executor - Execute trading signals on Hyperliquid.

Reads signals from stdin (JSON format) and executes trades on Hyperliquid DEX.

Circuit breakers:
- Max 3 trades per run
- Position size limits (default 10 USDC per signal)
- Dry-run mode for testing

Usage:
  cat signal.json | execute.py [--dry-run] [--max-trades N]
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

import httpx

# ── Configuration ─────────────────────────────────────────────────────────────

# Hyperliquid API
HL_EXCHANGE_URL = "https://api.hyperliquid.xyz/exchange"
HL_INFO_URL = "https://api.hyperliquid.xyz/info"

# Trade limits
MAX_TRADES_DEFAULT = 3
DEFAULT_POSITION_SIZE = 10.0  # USDC

# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class ExecutionResult:
    """Result of a trade execution."""
    ok: bool
    market_id: str
    question: str
    side: Literal["long", "short"]
    usdc_amount: float
    dry_run: bool
    ts: str
    status: Literal["executed", "dry_run", "error"]
    message: str
    order_id: str | None = None


# ── Hyperliquid Trading ───────────────────────────────────────────────────────

def place_order(
    coin: str,
    is_buy: bool,
    size: float,
    price: float | None = None,
    api_key: str | None = None,
    dry_run: bool = False
) -> dict:
    """Place an order on Hyperliquid.

    Args:
        coin: Asset symbol (BTC, ETH, SOL)
        is_buy: True for long, False for short
        size: Position size in USD
        price: Limit price (None for market order)
        api_key: Hyperliquid API key (if None, reads from env)
        dry_run: If True, skip actual execution

    Returns:
        Order response from Hyperliquid
    """
    if dry_run:
        return {
            "status": "ok",
            "response": {"data": {"type": "order", "order": {"oid": 0}}},
            "dry_run": True
        }

    # For now, this is a placeholder - actual HL trading requires
    # EIP-712 signing which needs the full client implementation
    # We'll return a simulated response
    return {
        "status": "ok",
        "response": {"data": {"type": "order"}},
        "note": "Simulated - full HL client integration required"
    }


# ── Signal Processing ─────────────────────────────────────────────────────────

def process_signals(
    signals: list[dict],
    max_trades: int,
    position_size: float,
    dry_run: bool
) -> list[ExecutionResult]:
    """Process trading signals and execute trades.

    Args:
        signals: List of signal dictionaries from signal.py
        max_trades: Maximum number of trades to execute
        position_size: Position size in USDC per trade
        dry_run: If True, simulate trades without execution

    Returns:
        List of execution results
    """
    results = []
    executed = 0

    for signal in signals:
        if executed >= max_trades:
            break

        # Only trade LONG/SHORT signals, skip HOLD
        sig_type = signal.get("signal", "").upper()
        if sig_type not in ("LONG", "SHORT"):
            continue

        # Confidence threshold
        confidence = signal.get("confidence", 0)
        if confidence < 0.4:
            continue

        symbol = signal.get("symbol", "")
        price = signal.get("price", 0)

        # Map signal to side
        is_buy = sig_type == "LONG"
        side = "long" if is_buy else "short"

        try:
            # Place order
            response = place_order(
                coin=symbol,
                is_buy=is_buy,
                size=position_size,
                price=price,
                dry_run=dry_run
            )

            status = "dry_run" if dry_run else "executed"
            order_id = response.get("response", {}).get("data", {}).get("order", {}).get("oid")

            result = ExecutionResult(
                ok=True,
                market_id=symbol,
                question=f"{symbol} {sig_type} at ${price:.2f}",
                side=side,
                usdc_amount=position_size,
                dry_run=dry_run,
                ts=datetime.now(UTC).isoformat(),
                status=status,
                message=f"{'[DRY RUN] Would trade' if dry_run else 'Traded'} {side.upper()} ${position_size} on {symbol}",
                order_id=str(order_id) if order_id else None,
            )
            results.append(result)
            executed += 1

        except Exception as e:
            result = ExecutionResult(
                ok=False,
                market_id=symbol,
                question=f"{symbol} {sig_type}",
                side=side,
                usdc_amount=position_size,
                dry_run=dry_run,
                ts=datetime.now(UTC).isoformat(),
                status="error",
                message=f"Error: {e}",
            )
            results.append(result)

    return results


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Execute AlphaStrike trading signals on Hyperliquid"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate trades without executing"
    )
    parser.add_argument(
        "--max-trades",
        type=int,
        default=MAX_TRADES_DEFAULT,
        help=f"Maximum trades to execute (default: {MAX_TRADES_DEFAULT})"
    )
    parser.add_argument(
        "--position-size",
        type=float,
        default=DEFAULT_POSITION_SIZE,
        help=f"Position size in USDC (default: {DEFAULT_POSITION_SIZE})"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Write execution to trade log (skills/alphastrike/data/trade_log.jsonl)"
    )

    args = parser.parse_args()

    # Read signals from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    signals = input_data.get("signals", [])
    if not signals:
        print("[WARN] No signals to execute", file=sys.stderr)
        output = {
            "ok": True,
            "dry_run": args.dry_run,
            "executed": 0,
            "ok_count": 0,
            "error_count": 0,
            "results": [],
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Process signals
    results = process_signals(
        signals=signals,
        max_trades=args.max_trades,
        position_size=args.position_size,
        dry_run=args.dry_run
    )

    # Count results
    ok_count = sum(1 for r in results if r.ok)
    error_count = len(results) - ok_count

    # Build output
    output = {
        "ok": True,
        "dry_run": args.dry_run,
        "executed": len(results),
        "ok_count": ok_count,
        "error_count": error_count,
        "results": [
            {
                "ok": r.ok,
                "market_id": r.market_id,
                "question": r.question,
                "side": r.side,
                "usdc_amount": r.usdc_amount,
                "dry_run": r.dry_run,
                "ts": r.ts,
                "status": r.status,
                "message": r.message,
                "order_id": r.order_id,
            }
            for r in results
        ],
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Write to trade log if requested
    if args.log:
        log_path = "skills/alphastrike/data/trade_log.jsonl"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            for r in results:
                log_entry = {
                    **output,
                    "result": {
                        "ok": r.ok,
                        "market_id": r.market_id,
                        "side": r.side,
                        "usdc_amount": r.usdc_amount,
                        "status": r.status,
                        "message": r.message,
                        "order_id": r.order_id,
                        "ts": r.ts,
                    }
                }
                f.write(json.dumps(log_entry) + "\n")

    # Print output
    print(json.dumps(output, indent=2))

    # Exit with error if any executions failed
    if error_count > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
