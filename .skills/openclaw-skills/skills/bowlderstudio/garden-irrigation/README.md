# garden-irrigation

Automated garden irrigation skill — reads soil sensors, checks weather, and decides when and how long to water each zone.

## Dependencies

This skill requires the **[tuya-cloud](https://clawhub.ai/minshi-veyt/tuya-cloud)** skill to communicate with Tuya IoT devices (soil sensors and water valves). Install and configure it before using this skill.

## What it does
- loads zone and system config
- reads Tuya soil sensors via `tuya-cloud`
- fetches weather history + forecast from Open-Meteo
- computes a basic irrigation decision per zone
- writes local JSONL history under `data/`
- generates a markdown daily report

## Valve model

This skill expects valve configuration in this shape:

```json
"valve": {
  "device_id": "...",
  "switch_code": "switch_1",
  "countdown_code": "countdown_1",
  "supports_countdown": true
}
```

This matches the `tuya-cloud` guidance for water valves:
- open valve: `switch_X = true`
- timed watering: send `switch_X = true` and `countdown_X = <minutes>` in the same call
- close valve: `switch_X = false`

For **dual-channel valves**, use `switch_1`/`countdown_1` for the left outlet and `switch_2`/`countdown_2` for the right outlet. Each channel is controlled independently.

## Run
```bash
cd skills/garden-irrigation
python3 scripts/run_once.py
```

## Configuration

This skill uses **JSON configuration only**. The configuration files are located in the `config/` directory:

- `config/zones.json` — zone definitions with soil sensors and valve devices
- `config/system.json` — system-wide settings (location, timezone, reporting)

### Important Notes
- Device IDs in `config/zones.json` are placeholders — replace them with your actual Tuya device IDs
- Tuya credentials (`TUYA_ACCESS_ID`, `TUYA_ACCESS_SECRET`, `TUYA_API_ENDPOINT`) must be set in `.env` at the project root (see [tuya-cloud](https://clawhub.ai/minshi-veyt/tuya-cloud) for setup)
