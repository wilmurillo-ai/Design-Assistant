from __future__ import annotations
from datetime import datetime
from typing import Dict, Optional
from ..utils.language import Translator, get_language_from_config


def build_report(
    results: list[dict], 
    weather_data: dict = None,
    config: Optional[Dict] = None,
    query_text: Optional[str] = None
) -> str:
    """Build irrigation report in multiple languages.
    
    Args:
        results: Irrigation decision results
        weather_data: Weather data
        config: System configuration
        query_text: Query text for language detection
        
    Returns:
        Report string in detected language
    """
    # Determine language
    if config is None:
        config = {}
    
    language = get_language_from_config(config, query_text)
    
    lines = [f"# {Translator.get_translation('daily_report', language)}", '']
    
    # Add generation time
    lines.append(f"*{Translator.get_translation('generated_at', language)}: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append('')
    
    # Add weather summary
    if weather_data:
        lines.append(f"## 🌤️ {Translator.get_translation('weather_summary', language)}")
        history = weather_data.get('history', {})
        forecast = weather_data.get('forecast', {})
        
        if history.get('daily') and forecast.get('daily'):
            # Recent rainfall
            recent_rain = sum(history['daily'].get('precipitation_sum', [])[-7:])
            today_rain = forecast['daily'].get('precipitation_sum', [0])[0]
            
            # Today's temperature
            today_temp_max = forecast['daily'].get('temperature_2m_max', [0])[0]
            today_temp_min = forecast['daily'].get('temperature_2m_min', [0])[0]
            
            lines.append(f"- {Translator.get_translation('recent_7day_rain', language)}: **{recent_rain:.1f}mm**")
            lines.append(f"- {Translator.get_translation('today_forecast_rain', language)}: **{today_rain:.1f}mm**")
            lines.append(f"- {Translator.get_translation('today_temperature', language)}: **{today_temp_min:.1f}°C ~ {today_temp_max:.1f}°C**")
            
            # Weather code to description
            weather_code = forecast['daily'].get('weathercode', [0])[0]
            weather_desc = Translator.translate_weather_code(weather_code, language)
            lines.append(f"- {Translator.get_translation('today_weather', language)}: **{weather_desc}** (code: {weather_code})")
        
        lines.append('')
    
    # Device status
    lines.append(f"## 📱 {Translator.get_translation('device_status', language)}")
    all_sensors = []
    for item in results:
        if 'sensors' in item:
            all_sensors.extend(item['sensors'])
    
    if all_sensors:
        online_count = sum(1 for s in all_sensors if s.get('online', False))
        lines.append(f"- {Translator.get_translation('online_devices', language)}: **{online_count}/{len(all_sensors)}**")
        lines.append('')
        
        for sensor in all_sensors:
            status_emoji = '🟢' if sensor.get('online', False) else '🔴'
            lines.append(f"### {status_emoji} {sensor.get('name', 'Unknown')}")
            lines.append(f"  - {Translator.get_translation('device_id', language)}: `{sensor.get('device_id', 'N/A')}`")
            
            status_text = Translator.get_translation('online', language) if sensor.get('online', False) else Translator.get_translation('offline', language)
            lines.append(f"  - {Translator.get_translation('status', language)}: {status_text}")
            
            if sensor.get('moisture') is not None:
                lines.append(f"  - {Translator.get_translation('soil_moisture', language)}: **{sensor['moisture']}%**")
            if sensor.get('temperature') is not None:
                lines.append(f"  - {Translator.get_translation('temperature', language)}: **{sensor['temperature']}°C**")
            if sensor.get('battery') is not None:
                battery = sensor['battery']
                battery_status = Translator.get_battery_status(battery, language)
                lines.append(f"  - {Translator.get_translation('battery', language)}: **{battery}%** ({battery_status})")
            if sensor.get('last_updated'):
                lines.append(f"  - {Translator.get_translation('last_updated', language)}: {sensor['last_updated']}")
            if sensor.get('error'):
                lines.append(f"  - {Translator.get_translation('error', language)}: {sensor['error']}")
            lines.append('')
    else:
        lines.append(f"- {Translator.get_translation('no_device_data', 'en')}")  # Fallback to English
        lines.append('')
    
    # Irrigation decisions
    lines.append(f"## 🌱 {Translator.get_translation('irrigation_decision', language)}")
    for item in results:
        lines.append(f"### {item['zone_name']}")
        
        yes_no = Translator.get_translation('yes', language) if item['decision']['should_irrigate'] else Translator.get_translation('no', language)
        lines.append(f"- {Translator.get_translation('should_irrigate', language)}: **{yes_no}**")
        
        lines.append(f"- {Translator.get_translation('watering_duration', language)}: **{item['decision']['minutes']} {Translator.get_translation('minutes', language)}**")
        lines.append(f"- {Translator.get_translation('decision_reason', language)}: {item['decision']['reason']}")
        lines.append('')
    
    return '\n'.join(lines)


def _weathercode_to_description(code: int) -> str:
    """Convert WMO weather code to description."""
    weather_codes = {
        0: "Clear",
        1: "Mostly clear",
        2: "Partly cloudy",
        3: "Cloudy",
        45: "Fog",
        48: "Fog",
        51: "Light rain",
        53: "Moderate rain",
        55: "Heavy rain",
        56: "Freezing drizzle",
        57: "Freezing drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Freezing rain",
        67: "Freezing rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Rain showers",
        81: "Rain showers",
        82: "Heavy rain showers",
        85: "Snow showers",
        86: "Snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Heavy thunderstorm with hail"
    }
    return weather_codes.get(code, f"Unknown weather (code {code})")
