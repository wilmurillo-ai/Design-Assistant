#!/usr/bin/env python3
"""
Locate-Weather Skill v2.0  (Facade)
Delegates to:
  - multi-source-locate  → 定位模块 (GPS/IP/WiFi/Cellular/System)
  - weather_at.py         → 天气模块

本文件仅做前端分发，所有逻辑委托给上述模块。
旧 locate_weather.py 中的定位代码已移至 multi-source-locate。
旧 locate_weather.py 中的天气代码已移至 weather_at.py。
"""

import sys
import os

# ── Import delegation ──────────────────────────────────────────────────────────
# Re-export everything from weather_at (weather module) for backward compat
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from weather_at import (
    WeatherReport,
    get_time_aware_method_priority,
    get_season_factor,
    get_weather,
    main as _weather_main,
    MULTI_LOCATE_OK,
)

# Expose location models from multi-source-locate (via importlib inside weather_at)
from weather_at import (
    LocationSource,   # = multi-source-locate.LocationResult
    TriangulatedResult,  # = multi-source-locate.TriangulatedResult
    get_system_location,
    get_ip_location,
    get_wifi_location,
    get_cellular_location,
    get_gps_location,
    triangulate,
    validate_coordinates,
)

# Alias old name for locate_weather consumers
TriangulatedLocation = TriangulatedResult

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    _weather_main()
