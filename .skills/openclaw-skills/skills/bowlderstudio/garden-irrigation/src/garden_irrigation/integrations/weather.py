from __future__ import annotations

import json
import urllib.request


class WeatherClient:
    def history_and_forecast(self, latitude: float, longitude: float, timezone: str) -> dict:
        archive = (
            'https://archive-api.open-meteo.com/v1/archive'
            f'?latitude={latitude}&longitude={longitude}'
            '&start_date=2026-04-04&end_date=2026-04-10'
            '&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode'
            f'&timezone={timezone}'
        )
        forecast = (
            'https://api.open-meteo.com/v1/forecast'
            f'?latitude={latitude}&longitude={longitude}'
            '&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode'
            f'&timezone={timezone}&forecast_days=3'
        )
        with urllib.request.urlopen(archive) as r:
            history = json.loads(r.read().decode())
        with urllib.request.urlopen(forecast) as r:
            future = json.loads(r.read().decode())
        return {'history': history, 'forecast': future}
