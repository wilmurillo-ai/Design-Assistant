# API Endpoints Reference

## Weather: wttr.in

### Coordinate-based query
```
https://wttr.in/{lat}:{lon}?format=j1
```
Returns JSON with:
- `current_condition`: current weather
- `weather[]`: 3-day forecast
- `nearest_area[]`: closest city info

### Format codes
```
%l  Location
%c  Condition emoji
%t  Temperature
%f  Feels like
%w  Wind
%h  Humidity
%p  Precipitation
```

### JSON format
```bash
curl "wttr.in/30.558:114.317?format=j1"
```

## IP Geolocation

### ip-api.com (free, 45 req/min)
```
http://ip-api.com/json/
```
Response: `{ status, lat, lon, city, region, country, isp, accuracy }`

### ipinfo.io
```
https://ipinfo.io/json
```
Response: `{ ip, city, region, country, loc: "lat,lon", org, timezone }`

## WiFi: Google Geolocation API

```
POST https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}
Content-Type: application/json

{
  "wifiAccessPoints": [
    { "macAddress": "XX:XX:XX:XX:XX:XX", "signalStrength": -60 }
  ]
}
```
Returns: `{ location: { lat, lng }, accuracy }`

Requires: `GOOGLE_GEOLOCATION_API_KEY` env var
