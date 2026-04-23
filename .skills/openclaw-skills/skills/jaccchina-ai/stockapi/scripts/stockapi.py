#!/usr/bin/env python3
"""
StockAPI CLI - Query Chinese A-Stock market data via stockapi.com.cn
"""

import argparse
import json
import os
import sys
from urllib import request, parse, error
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "https://www.stockapi.com.cn"
TOKEN = os.environ.get("STOCKAPI_TOKEN", "")

def make_request(endpoint, params):
    """Make HTTP GET request to StockAPI"""
    if not TOKEN:
        print("Error: STOCKAPI_TOKEN not set. Please set environment variable.", file=sys.stderr)
        print("Example: export STOCKAPI_TOKEN='your_token_here'", file=sys.stderr)
        sys.exit(1)
    
    params["token"] = TOKEN
    query_string = parse.urlencode(params)
    url = f"{BASE_URL}{endpoint}?{query_string}"
    
    req = request.Request(url)
    req.add_header("User-Agent", "OpenClaw-StockAPI-Client/1.0")
    req.add_header("Accept", "application/json")
    
    try:
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
        try:
            error_body = e.read().decode("utf-8")
            print(f"Response: {error_body}", file=sys.stderr)
        except:
            pass
        sys.exit(1)
    except error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

def format_output(data, output_format="json"):
    """Format output data"""
    if output_format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif output_format == "table":
        if "data" in data and isinstance(data["data"], list):
            # Print first 10 rows as table
            rows = data["data"][:10]
            if rows:
                headers = list(rows[0].keys())
                # Print header
                print(" | ".join(str(h)[:15] for h in headers))
                print("-" * (15 * len(headers)))
                # Print rows
                for row in rows:
                    print(" | ".join(str(row.get(h, ""))[:15] for h in headers))
            print(f"\nTotal: {len(data['data'])} rows (showing first 10)")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))

def cmd_stock_daily(args):
    """Get daily stock data (K-line)"""
    params = {
        "code": args.code,
        "startDate": args.start_date,
        "endDate": args.end_date,
    }
    if args.cycle:
        params["calculationCycle"] = args.cycle
    
    data = make_request("/v1/base/day", params)
    format_output(data, args.format)

def cmd_stock_realtime(args):
    """Get real-time stock quote"""
    params = {"code": args.code}
    data = make_request("/v1/base/quote", params)
    format_output(data, args.format)

def cmd_index_daily(args):
    """Get index daily data"""
    params = {
        "code": args.code,
        "startDate": args.start_date,
        "endDate": args.end_date,
    }
    data = make_request("/v1/index/day", params)
    format_output(data, args.format)

def cmd_limit_up(args):
    """Get limit-up stocks (涨停池)"""
    params = {"date": args.date or datetime.now().strftime("%Y-%m-%d")}
    data = make_request("/v1/limit/limitUp", params)
    format_output(data, args.format)

def cmd_limit_down(args):
    """Get limit-down stocks (跌停池)"""
    params = {"date": args.date or datetime.now().strftime("%Y-%m-%d")}
    data = make_request("/v1/limit/limitDown", params)
    format_output(data, args.format)

def cmd_hot_money(args):
    """Get hot money data (游资数据)"""
    params = {"date": args.date or datetime.now().strftime("%Y-%m-%d")}
    data = make_request("/v1/hotmoney/list", params)
    format_output(data, args.format)

def cmd_dragon_tiger(args):
    """Get dragon-tiger list data (龙虎榜)"""
    params = {"date": args.date or datetime.now().strftime("%Y-%m-%d")}
    data = make_request("/v1/dragon/list", params)
    format_output(data, args.format)

def cmd_indicator_macd(args):
    """Get MACD indicator data"""
    params = {
        "code": args.code,
        "startDate": args.start_date,
        "endDate": args.end_date,
    }
    data = make_request("/v1/indicator/macd", params)
    format_output(data, args.format)

def cmd_indicator_kdj(args):
    """Get KDJ indicator data"""
    params = {
        "code": args.code,
        "startDate": args.start_date,
        "endDate": args.end_date,
    }
    data = make_request("/v1/indicator/kdj", params)
    format_output(data, args.format)

def cmd_test(args):
    """Test API connection"""
    if not TOKEN:
        print("Error: STOCKAPI_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    print(f"Testing connection to {BASE_URL}...")
    print(f"Token configured: {'Yes' : 'No'}")
    
    # Try a simple request
    params = {"code": "600004", "startDate": "2024-01-01", "endDate": "2024-01-05"}
    data = make_request("/v1/base/day", params)
    
    if "data" in data:
        print("✓ API connection successful!")
        print(f"  Token status: Valid")
    else:
        print("✗ API request failed")
        print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(
        description="StockAPI CLI - Query Chinese A-Stock market data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get daily K-line data for a stock
  python stockapi.py stock daily --code 600004 --start 2024-01-01 --end 2024-01-10
  
  # Get real-time quote
  python stockapi.py stock quote --code 000001
  
  # Get today's limit-up stocks
  python stockapi.py limit up
  
  # Get MACD indicator
  python stockapi.py indicator macd --code 600004 --start 2024-01-01 --end 2024-01-10
  
  # Test API connection
  python stockapi.py test

Environment Variables:
  STOCKAPI_TOKEN  - Your StockAPI access token (required)

For more API endpoints, visit: https://www.stockapi.com.cn/demo
        """
    )
    
    parser.add_argument("--format", "-f", choices=["json", "table"], default="json",
                       help="Output format (default: json)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Stock commands
    stock_parser = subparsers.add_parser("stock", help="Stock data commands")
    stock_sub = stock_parser.add_subparsers(dest="stock_cmd")
    
    # Stock daily K-line
    daily_parser = stock_sub.add_parser("daily", help="Get daily K-line data")
    daily_parser.add_argument("--code", "-c", required=True, help="Stock code (e.g., 600004)")
    daily_parser.add_argument("--start-date", "-s", required=True, help="Start date (YYYY-MM-DD)")
    daily_parser.add_argument("--end-date", "-e", required=True, help="End date (YYYY-MM-DD)")
    daily_parser.add_argument("--cycle", "-C", type=int, help="Calculation cycle")
    daily_parser.set_defaults(func=cmd_stock_daily)
    
    # Stock real-time quote
    quote_parser = stock_sub.add_parser("quote", help="Get real-time quote")
    quote_parser.add_argument("--code", "-c", required=True, help="Stock code")
    quote_parser.set_defaults(func=cmd_stock_realtime)
    
    # Index commands
    index_parser = subparsers.add_parser("index", help="Index data commands")
    index_sub = index_parser.add_subparsers(dest="index_cmd")
    
    index_daily_parser = index_sub.add_parser("daily", help="Get index daily data")
    index_daily_parser.add_argument("--code", "-c", required=True, help="Index code")
    index_daily_parser.add_argument("--start-date", "-s", required=True, help="Start date")
    index_daily_parser.add_argument("--end-date", "-e", required=True, help="End date")
    index_daily_parser.set_defaults(func=cmd_index_daily)
    
    # Limit commands
    limit_parser = subparsers.add_parser("limit", help="Limit up/down commands")
    limit_sub = limit_parser.add_subparsers(dest="limit_cmd")
    
    limit_up_parser = limit_sub.add_parser("up", help="Get limit-up stocks")
    limit_up_parser.add_argument("--date", "-d", help="Date (YYYY-MM-DD), default: today")
    limit_up_parser.set_defaults(func=cmd_limit_up)
    
    limit_down_parser = limit_sub.add_parser("down", help="Get limit-down stocks")
    limit_down_parser.add_argument("--date", "-d", help="Date (YYYY-MM-DD), default: today")
    limit_down_parser.set_defaults(func=cmd_limit_down)
    
    # Hot money command
    hotmoney_parser = subparsers.add_parser("hotmoney", help="Hot money data")
    hotmoney_parser.add_argument("--date", "-d", help="Date (YYYY-MM-DD), default: today")
    hotmoney_parser.set_defaults(func=cmd_hot_money)
    
    # Dragon-tiger list
    dragon_parser = subparsers.add_parser("dragon", help="Dragon-tiger list (龙虎榜)")
    dragon_parser.add_argument("--date", "-d", help="Date (YYYY-MM-DD), default: today")
    dragon_parser.set_defaults(func=cmd_dragon_tiger)
    
    # Indicator commands
    indicator_parser = subparsers.add_parser("indicator", help="Technical indicators")
    indicator_sub = indicator_parser.add_subparsers(dest="indicator_cmd")
    
    macd_parser = indicator_sub.add_parser("macd", help="MACD indicator")
    macd_parser.add_argument("--code", "-c", required=True, help="Stock code")
    macd_parser.add_argument("--start-date", "-s", required=True, help="Start date")
    macd_parser.add_argument("--end-date", "-e", required=True, help="End date")
    macd_parser.set_defaults(func=cmd_indicator_macd)
    
    kdj_parser = indicator_sub.add_parser("kdj", help="KDJ indicator")
    kdj_parser.add_argument("--code", "-c", required=True, help="Stock code")
    kdj_parser.add_argument("--start-date", "-s", required=True, help="Start date")
    kdj_parser.add_argument("--end-date", "-e", required=True, help="End date")
    kdj_parser.set_defaults(func=cmd_indicator_kdj)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test API connection")
    test_parser.set_defaults(func=cmd_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
