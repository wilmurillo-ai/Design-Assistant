# wttr Weather Skill

A lightweight CLI wrapper for the wttr.in weather service.

## Description

This skill provides easy access to weather forecasts for any location worldwide using the wttr.in API. No installation required - it uses `curl` to fetch weather data directly from the web service.

## Prerequisites

- `curl` installed (available on macOS, Linux, Windows with WSL)
- `wget` alternative available (optional)

## Installation

No installation needed. Just use the command directly:

```bash
curl wttr.in/CityName
```

Or add to your PATH as `wttr`:

```bash
alias wttr='curl wttr.in'
```

## Usage

### Basic Commands

```bash
# Current location weather
wttr

# Weather for a specific city
wttr Detroit
wttr New+York
wttr London

# One-line compact format
wttr Detroit/Compact

# Detailed forecast
wttr Detroit/Detailed
```

### Advanced Options

```bash
# Multi-day forecast
wttr Detroit/5d        # 5-day forecast
wttr Detroit/3d        # 3-day forecast

# JSON output for scripting
wttr Detroit?format=j1

# Airport weather
wttr JFK
wttr LHR

# Different languages
wttr Paris?lang=fr     # French
wttr Paris?lang=de     # German
```

## Command Reference

### Location Identifiers
- **City name**: `wttr Detroit`
- **City + Country**: `wttr Detroit+US`
- **Airport code**: `wttr JFK`
- **Latitude/Longitude**: `wttr 42.34,-83.05`

### Format Options
- `Compact` - One-line summary
- `Detailed` - Extended weather info
- `3d` - 3-day forecast
- `5d` - 5-day forecast
- `7d` - 7-day forecast
- `map` - ASCII map view
- `format=j1` - JSON output
- `format=csv` - CSV output
- `format=html` - HTML output

### Language Options
- `?lang=en` - English (default)
- `?lang=es` - Spanish
- `?lang=fr` - French
- `?lang=de` - German
- `?lang=pt` - Portuguese
- `?lang=ru` - Russian
- `?lang=zh` - Chinese
- `?lang=ja` - Japanese

## Examples

```bash
# Today's weather in Detroit
$ wttr Detroit
Weather report: detroit
  \o/   18°C
   / \  Partly Cloudy
 ──▲──  15 km/h
  /|\  0.0 mm

# 5-day forecast
$ wttr Detroit/5d
[forecast data for 5 days]

# JSON format for automation
$ wttr Detroit?format=j1
{"current_condition": [...], "forecast": [...]}

# Weather at airport
$ wttr JFK
Weather for JFK Airport
```

## Troubleshooting

### Common Issues

1. **Command not found**: Make sure `curl` is installed
   ```bash
   which curl
   ```

2. **Invalid location**: Use full city name or airport code
   ```bash
   # Instead of "wttr LA" try "wttr Los+Angeles" or "wttr LAX"
   ```

3. **Slow response**: wttr.in is free and may have delays during peak hours

4. **No data**: Check internet connection and try again

## Alternatives

- **Open-Meteo API**: `https://open-meteo.com/`
- **wttr-cli**: npm package for enhanced CLI features
- **term-icons**: Better ASCII weather icons

## Notes

- This skill requires no authentication
- Completely free to use
- No API key needed
- Works offline if you cache responses
- Data accuracy depends on wttr.in's sources

## Related

- [GitHub Repository](https://github.com/chubin/wttr.in)
- [wttr.in Help](https://wttr.in/:help)
- [Open-Meteo API](https://open-meteo.com/docs)

## License

MIT License - wttr.in is open source
