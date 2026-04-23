# wttr - Weather CLI Tool

A simple wrapper for wttr.in weather service that provides weather forecasts for any location.

## Installation

```bash
curl wttr.in/Detroit
```

Or with more options:
```bash
curl wttr.in/Detroit/Detailed
```

## Usage

### Basic
```bash
# Current location (uses IP geolocation)
curl wttr.in

# Specific city
curl wttr.in/New+York
curl wttr.in/Detroit
curl wttr.in/London
```

### Options
```bash
# One-line compact output
curl wttr.in/Compact

# Detailed output
curl wttr.in/Detailed

# 3-day forecast
curl wttr.in/3d

# 5-day forecast
curl wttr.in/5d

# Map view (requires image viewer)
curl wttr.in/map?location=Detroit

# Airport code (e.g., JFK, LHR)
curl wttr.in/JFK
curl wttr.in/LHR
```

### Output Formats
```bash
# JSON format
curl wttr.in/Detroit?format=j1

# CSV format
curl wttr.in/Detroit?format=csv

# HTML format
curl wttr.in/Detroit?format=html
```

## Features

- 🌍 Supports cities, countries, airport codes
- 📅 1-day to 7-day forecasts
- 🌡️ Temperature in Celsius or Fahrenheit
- 💨 Wind speed and direction
- ☂️ Precipitation data
- 🌤️ Weather conditions with ASCII art
- 🌙 Moon phases
- 🌍 Map views

## Tips

1. **Spaces in city names**: Use `+` instead of spaces (e.g., `New+York` not `New York`)
2. **Country codes**: Add country abbreviation for clarity (e.g., `New+York+US`)
3. **Airport weather**: Use IATA codes for airport-specific weather
4. **Language**: Add `?lang=es` for Spanish, `?lang=de` for German, etc.

## Examples

```bash
# Today's weather in Detroit
curl wttr.in/Detroit

# 5-day forecast for London
curl wttr.in/London/5d

# Detailed hourly forecast for Tokyo
curl wttr.in/Tokyo/Detailed

# Weather at JFK Airport
curl wttr.in/JFK

# Compact format for script monitoring
curl wttr.in/Detroit?format=compact
```

## How it Works

wttr.in is a web-based weather service that returns ASCII-art formatted weather data. No installation required - just use curl, wget, or httpie to fetch the data.

## Related Tools

- [GitHub - chubin/wttr.in](https://github.com/chubin/wttr.in)
- [wttr.in Documentation](https://wttr.in/:help)
