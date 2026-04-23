---
name: locate-weather
version: 2.0.0
description: >
  定点天气预报 Skill。先通过 GPS、IP、WiFi、系统定位等多方法三角定位获取精确坐标，
  再获取该位置的天气预报。支持手动指定坐标/城市、时间感知定位策略（根据时段自动选择最优定位方法）。
  定位模块引用 multi-source-locate Skill，天气模块独立实现。
  用于："我这里的天气"、"定点天气预报"、"获取当前位置天气"。
---

# Locate-Weather Skill v2.0

**定点天气预报**：多方法定位 → 三角融合 → 精准天气。

## 何时使用

✅ 用户说以下内容时触发本 Skill：
- "我这里的天气"
- "定点天气预报"
- "获取当前位置天气"
- "我现在在哪，天气怎么样"
- "weather at my location"

❌ **不适用**：
- 指定城市名查天气 → 使用 `weather` Skill
- 历史天气数据查询
- 详细气象分析

## 工作流程

```
1. 定位探测（按优先级尝试）
   multi-source-locate →
     IP 定位 ──→ WiFi BSSID ──→ GPS 硬件 ──→ 系统定位 ──→ 默认位置

2. 多源三角定位
   multi-source-locate triangulate() → 逆方差加权质心算法 → 精度 ±Xm，置信度 Y%

3. wttr.in 定点天气查询（weather_at.py）
   坐标传入 → 当前天气 + 3天预报
```

## 命令行用法

```bash
# 自动定位 + 天气预报（默认使用时间感知策略）
python scripts/locate_weather.py

# 手动指定坐标查天气
python scripts/locate_weather.py --lat 30.558 --lon 114.317 --city 武汉

# 指定定位方法
python scripts/locate_weather.py --methods ip,gps

# 时间感知策略（根据时段自动选择最优方法）
python scripts/locate_weather.py --methods time_aware

# 输出 JSON（供 AI 后续处理）
python scripts/locate_weather.py --format json

# 模拟测试：虚拟时间 2:00，冬季
python scripts/locate_weather.py --methods time_aware --sim-hour 2 --sim-month 12
```

## 定位方法（来自 multi-source-locate）

| 方法 | 精度 | 依赖 | 说明 |
|------|------|------|------|
| GPS | 3-10m | GPS 硬件 / NMEA | 户外最高精度 |
| System | 10m–1km | OS 定位服务 | Win GeoCoordinateWatcher / macOS CoreLocation / Linux GeoClue2 |
| IP | 1-50km | 无 | 城市级定位，零依赖 |
| WiFi | 10-100m | Google/Unwired API Key | 室内/城市环境 |
| Cellular | 100m-3km | 基站可见性 | 户外备用方案 |

## 时间感知策略（time_aware）

| 时间段 | 方法优先级 | 理由 |
|--------|-----------|------|
| 0-5时（深夜） | ip→wifi→system→cellular→gps | 室内GPS信号弱，优先IP |
| 6-9时（清晨） | system→gps→cellular→wifi→ip | 通勤时段系统定位快速 |
| 10-16时（白天） | gps→system→wifi→cellular→ip | 户外GPS精度最高 |
| 17-20时（傍晚） | system→wifi→gps→cellular→ip | 通勤时段 |
| 21-23时（夜间） | ip→system→wifi→cellular→gps | 室内为主，IP/系统优先 |

## API Keys（可选）

```bash
export GOOGLE_GEOLOCATION_API_KEY="..."   # WiFi 精确定位
export UNWIRED_API_KEY="..."              # WiFi 备用
```

## 输出格式

### Text（默认）
```
═══════════════════════════════════════════════
  📍 定位结果
═══════════════════════════════════════════════
  坐标: 30.5580°N, 114.3169°E
  方法: triangulated
  精度: ±10000m
  置信度: 50%

═══════════════════════════════════════════════
  🌤️ 天气预报 — Wuhan, Hubei
═══════════════════════════════════════════════
  当前天气: Sunny
  气温: 26°C (体感 27°C)
  湿度: 70%
  风速: 6 km/h (NE)
  今日气温: 19°C ~ 27°C
```

### JSON（--format json）
```json
{
  "time_context": {
    "strategy": "time_aware",
    "hour": 12,
    "season": "spring",
    "month": 4,
    "gps_reliability": 0.9,
    "method_priority": ["gps", "system", "wifi", "cellular", "ip"]
  },
  "location": {
    "latitude": 30.558,
    "longitude": 114.317,
    "accuracy_meters": 150,
    "confidence": 0.85,
    "method": "triangulated",
    "sources": { "ip": {...}, "gps": {...} }
  },
  "weather": {
    "current": { "temp_c": 26, "condition": "Sunny", ... },
    "today": { "max_temp_c": 27, "min_temp_c": 19, ... },
    "forecast": [...]
  }
}
```

## 文件结构

```
locate-weather/
├── SKILL.md                        ← 本文件
├── scripts/
│   ├── locate_weather.py           ← Facade（导入 weather_at + multi-source-locate）
│   └── weather_at.py               ← 天气模块（含 time_aware 策略）
├── tests/
│   ├── double_blind_test.py
│   └── TEST_PLAN.md
└── references/
    └── api_endpoints.md            ← wttr.in API 格式参考
```

## 依赖关系

```
locate-weather
├── multi-source-locate (独立 Skill)
│   ├── scripts/locate.py          ← 定位核心（GPS/IP/WiFi/Cellular/System）
│   ├── scripts/gps_reader.py
│   ├── scripts/ip_lookup.py
│   ├── scripts/wifi_scanner.py
│   ├── scripts/cell_scanner.py
│   └── scripts/triangulate.py
└── scripts/weather_at.py           ← 天气模块 + time_aware 策略
```
