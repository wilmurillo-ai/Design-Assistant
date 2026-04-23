#!/usr/bin/env python3
"""
Weather-At Skill v2.0
定点天气预报 — 获取指定位置的实时天气和3天预报。

定位模块引用: multi-source-locate Skill (scripts/locate.py)
Weather module refactored out of locate_weather.py v2.0

Usage:
    python weather_at.py                          # 自动定位 + 天气
    python weather_at.py --lat 30.5 --lon 114.3 # 手动坐标
    python weather_at.py --city 武汉              # 城市名
    python weather_at.py --methods time_aware     # 时间感知定位策略
    python weather_at.py --format json            # JSON 输出
    python weather_at.py --sim-hour 2 --sim-month 12  # 模拟时间
"""

import argparse
import json
import sys
import os
import ssl
import math
import urllib.request
import urllib.error
import importlib.util
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WeatherReport:
    """Weather forecast report."""
    latitude: float
    longitude: float
    city: str
    region: str
    country: str
    current_temp: float
    current_feelslike: float
    current_condition: str
    current_humidity: int
    current_wind_speed: float
    current_wind_dir: str
    current_uv: float
    current_pressure: float
    current_visibility: float
    today_maxtemp: float
    today_mintemp: float
    forecast: List[Dict] = field(default_factory=list)
    sunrise: str = ""
    sunset: str = ""
    raw: Optional[Dict] = None


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-SOURCE LOCATE MODULE (dynamic import — handles hyphenated dir name)
# ═══════════════════════════════════════════════════════════════════════════════

def _load_multi_locate():
    """Dynamically load multi-source-locate locate.py module."""
    # Resolve paths
    _skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _multi_root = os.path.join(_skill_dir, "..", "multi-source-locate")
    _multi_root = os.path.normpath(_multi_root)
    _scripts_dir = os.path.join(_multi_root, "scripts")

    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)

    _spec = importlib.util.spec_from_file_location(
        "_msl", os.path.join(_scripts_dir, "locate.py")
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    return _mod

try:
    _msl = _load_multi_locate()
    get_system_location = _msl.get_system_location
    get_ip_location = _msl.get_ip_location
    get_wifi_location = _msl.get_wifi_location
    get_cellular_location = _msl.get_cellular_location
    get_gps_location = _msl.get_gps_location
    triangulate = _msl.triangulate
    validate_coordinates = _msl.validate_coordinates
    LocationSource = _msl.LocationResult  # multi-source-locate uses LocationResult
    TriangulatedResult = _msl.TriangulatedResult
    MULTI_LOCATE_OK = True
except Exception as e:
    get_system_location = get_ip_location = get_wifi_location = None
    get_cellular_location = get_gps_location = triangulate = None
    validate_coordinates = None
    LocationSource = TriangulatedResult = None
    MULTI_LOCATE_OK = False
    _msl_load_error = e


# ═══════════════════════════════════════════════════════════════════════════════
# TIME-AWARE STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════

def get_time_aware_method_priority(hour: Optional[int] = None) -> List[str]:
    """
    根据当前时间动态调整定位方法优先级。
    - 深夜 (0-5): IP优先，GPS信号弱，用户通常在室内
    - 清晨/傍晚 (6-9, 17-20): 系统定位优先，通勤时段
    - 白天 (10-16): GPS优先，户外可能性高
    - 夜间 (21-23): 混合策略，IP/系统优先
    """
    if hour is None:
        hour = datetime.now().hour
    if 0 <= hour < 6:
        return ["ip", "wifi", "system", "cellular", "gps"]
    elif 6 <= hour < 10:
        return ["system", "gps", "cellular", "wifi", "ip"]
    elif 10 <= hour < 17:
        return ["gps", "system", "wifi", "cellular", "ip"]
    elif 17 <= hour < 21:
        return ["system", "wifi", "gps", "cellular", "ip"]
    else:  # 21-23
        return ["ip", "system", "wifi", "cellular", "gps"]


def get_season_factor(
    month: Optional[int] = None,
    hour: Optional[int] = None
) -> Dict[str, Any]:
    """获取季节因素对定位的影响"""
    if month is None:
        month = datetime.now().month
    if hour is None:
        hour = datetime.now().hour
    if month in [3, 4, 5]:
        season = "spring"; gps_reliability = 0.9
    elif month in [6, 7, 8]:
        season = "summer"; gps_reliability = 0.85
    elif month in [9, 10, 11]:
        season = "autumn"; gps_reliability = 0.9
    else:
        season = "winter"; gps_reliability = 0.8
    return {"season": season, "month": month, "gps_reliability": gps_reliability, "hour": hour}


# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fetch_json(url: str, timeout: int = 10) -> Dict:
    """GET JSON with SSL/timeout handling."""
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            return json.loads(raw)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise ValueError(f"网络请求失败: {e}")


def get_weather(lat: float, lon: float, city_override: str = "") -> Optional[WeatherReport]:
    """Fetch weather for given coordinates using wttr.in."""
    try:
        url = f"https://wttr.in/{lat},{lon}?format=j1&lang=zh"
        data = _fetch_json(url)
        return _parse_weather_response(lat, lon, data, city_override)
    except Exception as e:
        print(f"[weather] 获取天气失败: {e}", file=sys.stderr)
        return None


def _parse_weather_response(
    lat: float, lon: float, data: Dict, city_override: str = ""
) -> WeatherReport:
    """Parse wttr.in JSON response."""
    current = data.get("current_condition", [{}])[0]
    today = data.get("weather", [{}])[0]

    if city_override:
        city = city_override
    else:
        area = data.get("nearest_area", [{}])[0]
        city = (area.get("areaName", [{}])[0].get("value") or
                area.get("region", [{}])[0].get("value") or
                area.get("country", [{}])[0].get("value") or "")

    region = country = ""
    try:
        nearest = data.get("nearest_area", [{}])[0]
        region = nearest.get("region", [{}])[0].get("value", "")
        country = nearest.get("country", [{}])[0].get("value", "")
    except Exception:
        pass

    forecast = []
    for day_data in data.get("weather", []):
        fc_day = day_data.get("hourly", [])
        maxt = float(day_data.get("maxtempC", "0"))
        mint = float(day_data.get("mintempC", "0"))
        desc = day_data.get("weatherDesc", [{}])[0].get("value", "")
        rain_prob = 0
        uv = 0.0
        for h in fc_day:
            try:
                rain_prob = max(rain_prob, int(h.get("chanceofrain", 0)))
                uv = max(uv, float(h.get("uvIndex", 0) or 0))
            except (ValueError, TypeError):
                pass
        astronomy = day_data.get("astronomy", [{}])[0]
        forecast.append({
            "date": day_data.get("date", ""),
            "maxtemp": maxt,
            "mintemp": mint,
            "avgtemp": float(day_data.get("avgtempC", "0")),
            "condition": desc,
            "rain_prob": rain_prob,
            "uv": uv,
            "sunrise": astronomy.get("sunrise", ""),
            "sunset": astronomy.get("sunset", ""),
        })

    astronomy0 = today.get("astronomy", [{}])[0]
    return WeatherReport(
        latitude=lat, longitude=lon, city=city, region=region, country=country,
        current_temp=float(current.get("temp_C", 0)),
        current_feelslike=float(current.get("FeelsLikeC", 0)),
        current_condition=current.get("weatherDesc", [{}])[0].get("value", ""),
        current_humidity=int(current.get("humidity", 0)),
        current_wind_speed=float(current.get("windspeedKmph", 0)),
        current_wind_dir=_norm_wind_dir(current.get("winddir16Point", "")),
        current_uv=float(current.get("uvIndex", 0)),
        current_pressure=float(current.get("pressure", 0)),
        current_visibility=float(current.get("visibility", 0)),
        today_maxtemp=float(today.get("maxtempC", 0)),
        today_mintemp=float(today.get("mintempC", 0)),
        forecast=forecast,
        sunrise=astronomy0.get("sunrise", ""),
        sunset=astronomy0.get("sunset", ""),
        raw=data,
    )


def _norm_wind_dir(abbr: str) -> str:
    """Normalize wind direction abbreviation."""
    mapping = {
        "N": "N", "NNE": "N", "NE": "NE", "ENE": "NE",
        "E": "E", "ESE": "E", "SE": "SE", "SSE": "SE",
        "S": "S", "SSW": "S", "SW": "SW", "WSW": "SW",
        "W": "W", "WNW": "W", "NW": "NW", "NNW": "NW",
    }
    return mapping.get(abbr.upper(), abbr)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

def _print_text(loc: Any, weather: Optional[WeatherReport], time_ctx: Optional[Dict] = None):
    """Human-readable output."""
    ns = getattr(loc, 'latitude', 0)
    ew = getattr(loc, 'longitude', 0)
    lat_str = f"{abs(ns):.4f}°{'N' if ns >= 0 else 'S'}"
    lon_str = f"{abs(ew):.4f}°{'E' if ew >= 0 else 'W'}"
    conf_str = f"{getattr(loc, 'confidence', 0):.0%}"
    acc_str = f"{getattr(loc, 'accuracy_meters', 0):.0f}"
    method_str = getattr(loc, 'method', '?')

    lines = [
        "",
        "═" * 55,
        "  📍 定位结果",
        "═" * 55,
        f"  坐标: {lat_str}, {lon_str}",
        f"  方法: {method_str}",
        f"  精度: ±{acc_str}m",
        f"  置信度: {conf_str}",
    ]
    if time_ctx:
        lines.append(
            f"  时间: {time_ctx.get('hour', '?')}时 | "
            f"{time_ctx.get('season', '?')} | "
            f"GPS可靠性 {time_ctx.get('gps_reliability', 0):.0%}"
        )
    if weather:
        lines += [
            "",
            "═" * 55,
            f"  🌤️ 天气预报 — {weather.city}" +
            (f", {weather.region}" if weather.region else "") +
            (f" ({weather.country})" if weather.country else ""),
            "═" * 55,
            f"  当前天气: {weather.current_condition}",
            f"  气温: {weather.current_temp:.0f}°C (体感 {weather.current_feelslike:.0f}°C)",
            f"  湿度: {weather.current_humidity}%",
            f"  风速: {weather.current_wind_speed:.0f} km/h ({weather.current_wind_dir})",
            f"  气压: {weather.current_pressure:.0f} hPa",
            f"  能见度: {weather.current_visibility:.0f} km",
            f"  今日气温: {weather.today_mintemp:.0f}°C ~ {weather.today_maxtemp:.0f}°C",
        ]
        if weather.sunrise:
            lines.append(f"  日出/日落: {weather.sunrise} / {weather.sunset}")
        if weather.forecast:
            lines.append("")
            lines.append("  ─── 天气预报 ───")
            for fc in weather.forecast[:4]:
                lines.append(
                    f"  {fc.get('date', '?')}: {fc.get('condition', '?')} "
                    f"{fc.get('mintemp', 0):.0f}°C ~ {fc.get('maxtemp', 0):.0f}°C "
                    f"🌧️ {fc.get('rain_prob', 0)}%"
                )
    print("\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    if not MULTI_LOCATE_OK:
        print(f"❌ 错误: multi-source-locate 不可用: {_msl_load_error}", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="定点天气预报 — 多方法定位 + wttr.in 天气"
    )
    parser.add_argument("--lat", type=float, default=None)
    parser.add_argument("--lon", type=float, default=None)
    parser.add_argument("--city", type=str, default="")
    parser.add_argument(
        "--methods", "-m", type=str, default="time_aware",
        help="定位方法: ip,gps,system,wifi,cellular,time_aware,all (逗号分隔)"
    )
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text")
    parser.add_argument("--gps-timeout", type=int, default=30)
    parser.add_argument("--sim-hour", type=int, default=None)
    parser.add_argument("--sim-month", type=int, default=None)
    args = parser.parse_args()

    # ── 1. 解析定位方法 ─────────────────────────────────────────────────────
    if args.methods == "all":
        methods = ["system", "gps", "ip", "wifi", "cellular"]
    elif args.methods == "time_aware":
        methods = get_time_aware_method_priority(hour=args.sim_hour)
        season = get_season_factor(month=args.sim_month, hour=args.sim_hour)
        hour_display = args.sim_hour if args.sim_hour is not None else season["hour"]
        print(f"🕐 时间感知策略: {hour_display}时 | {season['season']} | GPS可靠性 {season['gps_reliability']:.0%}", file=sys.stderr)
        print(f"   方法优先级: {' → '.join(methods)}", file=sys.stderr)
        time_context = {
            "strategy": "time_aware",
            "hour": args.sim_hour if args.sim_hour is not None else datetime.now().hour,
            "season": season["season"],
            "month": season["month"],
            "gps_reliability": season["gps_reliability"],
            "method_priority": methods,
        }
    else:
        methods = [m.strip().lower() for m in args.methods.split(",")]
        time_context = {"strategy": "manual", "method_priority": methods}

    # ── 2. 定位阶段 ─────────────────────────────────────────────────────────
    if args.lat is not None and args.lon is not None:
        lat, lon = validate_coordinates(args.lat, args.lon)
        if lat is None:
            print("❌ 无效坐标", file=sys.stderr)
            sys.exit(1)
        sources = [LocationSource(
            latitude=lat, longitude=lon,
            accuracy=10.0, method="manual", timestamp=_now()
        )]
        city = args.city or ""
    else:
        city = args.city or ""
        sources = []

        method_funcs = {
            "system":    lambda: get_system_location(args.gps_timeout or 20),
            "gps":       lambda: get_gps_location(args.gps_timeout),
            "ip":        lambda: get_ip_location(),
            "wifi":      lambda: get_wifi_location(),
            "cellular":  lambda: get_cellular_location(),
        }

        for method_name in methods:
            if method_name not in method_funcs:
                print(f"⚠️ 未知定位方法: {method_name}", file=sys.stderr)
                continue
            print(f"正在探测 [{method_name}]...", file=sys.stderr)
            try:
                result = method_funcs[method_name]()
                if result:
                    src = LocationSource(
                        latitude=result.latitude, longitude=result.longitude,
                        accuracy=result.accuracy, method=result.method,
                        timestamp=result.timestamp or _now(),
                    )
                    sources.append(src)
                    print(f"  ✓ {method_name}: {result.latitude:.4f}, {result.longitude:.4f} (±{result.accuracy:.0f}m)", file=sys.stderr)
                else:
                    print(f"  ✗ {method_name}: 不可用", file=sys.stderr)
            except Exception as e:
                print(f"  ✗ {method_name}: {e}", file=sys.stderr)

        if not sources:
            print("❌ 所有定位方法均失败，使用默认 IP 位置", file=sys.stderr)
            try:
                default = _fetch_json("https://wttr.in/?format=j1", timeout=10)
                area = default.get("nearest_area", [{}])[0]
                lat = float(area.get("latitude", 30))
                lon = float(area.get("longitude", 114))
                sources.append(LocationSource(
                    latitude=lat, longitude=lon,
                    accuracy=10000.0, method="default-ip", timestamp=_now()
                ))
            except Exception as e:
                print(f"默认位置也失败: {e}", file=sys.stderr)
                sys.exit(1)

    tri_loc = triangulate(sources)
    lat, lon = tri_loc.latitude, tri_loc.longitude

    # ── 3. 天气阶段 ─────────────────────────────────────────────────────────
    print(f"\n正在获取 ({lat:.4f}, {lon:.4f}) 的天气预报...", file=sys.stderr)
    weather = get_weather(lat, lon, city)

    if weather is None:
        print("⚠️ 天气获取失败，仅输出定位结果", file=sys.stderr)
        if args.format == "json":
            print(json.dumps({
                "time_context": time_context,
                "location": asdict(tri_loc),
                "weather": None,
            }, indent=2, ensure_ascii=False))
        else:
            _print_text(tri_loc, None, time_context)
        sys.exit(0)

    # ── 4. 输出 ──────────────────────────────────────────────────────────────
    if args.format == "json":
        print(json.dumps({
            "time_context": time_context,
            "location": asdict(tri_loc),
            "weather": {
                "current": {
                    "temp_c": weather.current_temp,
                    "feels_like": weather.current_feelslike,
                    "condition": weather.current_condition,
                    "humidity": weather.current_humidity,
                    "wind_kmh": weather.current_wind_speed,
                    "wind_dir": weather.current_wind_dir,
                    "uv_index": weather.current_uv,
                    "pressure_hpa": weather.current_pressure,
                    "visibility_km": weather.current_visibility,
                },
                "today": {
                    "max_temp_c": weather.today_maxtemp,
                    "min_temp_c": weather.today_mintemp,
                    "sunrise": weather.sunrise,
                    "sunset": weather.sunset,
                },
                "forecast": weather.forecast,
                "city": weather.city,
                "region": weather.region,
                "country": weather.country,
                "latitude": weather.latitude,
                "longitude": weather.longitude,
            }
        }, indent=2, ensure_ascii=False))
    else:
        _print_text(tri_loc, weather, time_context)
    sys.exit(0)


if __name__ == "__main__":
    main()
