---
name: chaching-panel
description: Control a Chaching LED panel (64x32 HUB75 on ESP32-S3) over HTTP — display text, graphics, shapes, play sounds, and read status.
metadata: {"openclaw":{"emoji":"💡","requires":{"bins":["curl"],"env":["CHACHING_PANEL_IP"]},"primaryEnv":"CHACHING_PANEL_IP"}}
user-invocable: true
---

# Chaching Panel

Control a Chaching LED panel (64x32 pixels, RGB565) connected to your local network via HTTP.

## Connection

The panel runs an HTTP server on port 80. Base URL: `http://${CHACHING_PANEL_IP}`.
Use `curl -s` with `-H "Content-Type: application/json"` for all POST requests.

## Display specs

- Resolution: 64 wide x 32 tall pixels
- Color format: RGB565 as hex string (e.g. `"0xF800"`) or HTML hex (`"#FF0000"`)
- Coordinates: (0,0) is top-left, (63,31) is bottom-right
- Fonts (name → size): `arial_20` (largest), `arial_18`, `arial_16`, `mono_18`, `mono_12`, `5x7`, `4x6` (smallest)
- Common colors: `"0xF800"` red, `"0x07E0"` green, `"0x001F"` blue, `"0xFFE0"` yellow, `"0xFFFF"` white, `"0x0000"` black, `"#FF6600"` orange

## Endpoints

### Display drawing

**POST /api/display/text** — Show text.
```json
{"text": "Hello", "x": 0, "y": 16, "color": "0x07E0", "font": "arial_20", "align_right": false, "swap": true}
```
All fields except `text` are optional (defaults: x=0, y=0, color=white, font=mono_12, align_right=false, swap=true).

**POST /api/display/number** — Show a formatted number (large values auto-format: 1000000 → "1 M").
```json
{"value": 64770, "x": 0, "y": 20, "color": "0xFFFF", "font": "arial_20", "align_right": false, "swap": true}
```

**POST /api/display/clear** — Clear the display to black. No body needed.

**POST /api/display/pixel** — Draw pixels.
```json
{"pixels": [{"x": 10, "y": 5, "color": "0xF800"}, {"x": 11, "y": 5, "color": "0x07E0"}], "swap": true}
```

**POST /api/display/rect** — Draw a rectangle.
```json
{"x": 0, "y": 0, "w": 64, "h": 32, "color": "0x001F", "fill": true, "swap": true}
```
`fill` defaults to true. Set false for outline only.

**POST /api/display/circle** — Draw a circle.
```json
{"cx": 32, "cy": 16, "r": 10, "color": "0xFFE0", "fill": false, "swap": true}
```
`fill` defaults to false (outline). Set true for filled circle.

**POST /api/display/graph** — Draw a line graph.
```json
{"values": [1.0, 3.5, 2.0, 7.0, 5.5], "x": 0, "y": 8, "w": 64, "h": 24, "color_line": "0x07E0", "color_fill": "0x07E0", "fill": true, "swap": true}
```
Values are auto-scaled to fit the height. `fill` fills the area under the line.

**POST /api/display/panel** — Show a full dashboard panel (label + value + percentage + graph).
```json
{"label": "BTC", "value": 64770, "percent": 3.5, "values": [60000, 61000, 63000, 64770], "color_line": "0xFFE0", "color_fill": "0xFFE0", "fill": true, "dissolve": true}
```
This clears the screen and draws a complete panel. `dissolve` enables a fade transition.

**POST /api/display/gif** — Play the built-in animated GIF. No body needed.

**POST /api/display/brightness** — Set display brightness.
```json
{"value": 80}
```
Range: 0 (off) to 100 (max). Persists across reboots.

**GET /api/display/framebuffer** — Returns 4096 bytes of raw RGB565 binary data (64x32 pixels, row-major).

### Display control

**POST /api/display/lock** — Take exclusive control of the display. Pauses the normal panel timeline. No body needed. Auto-unlocks after 30 seconds of inactivity.

**POST /api/display/unlock** — Release control back to the normal timeline. No body needed.

**POST /api/view_panel** — Force a specific timeline panel to show.
```json
{"index": 0}
```
This also unlocks the display if it was locked.

### Sound

**POST /api/sound/play** — Play a built-in sound. Blocks until playback finishes.
```json
{"name": "coin"}
```
Available sounds: `order` (cash register), `coin` (Mario coin), `epicwin` (victory fanfare), `youwin` (short win).

**POST /api/sound/volume** — Set speaker volume. Persists across reboots.
```json
{"value": 50}
```
Range: 0 (mute) to 100 (max).

**GET /api/sound/status** — Returns current volume and mute state.
Response: `{"volume": 50, "muted": false}`

### Status

**GET /api/status** — Returns device info.
Response: `{"version": "1.6.4", "ip": "192.168.1.50", "brightness": 80, "volume": 50, "display": {"w": 64, "h": 32}, "ws_connected": true, "api_locked": false}`

## The `swap` parameter

Most draw endpoints accept `"swap": true|false` (default: true).
- `true`: the drawing appears on screen immediately after the call.
- `false`: the drawing is buffered but not shown yet. Use this to compose multiple elements before displaying them all at once. Send a final call with `"swap": true` to show everything.

## Workflow

1. **To show something temporarily**, use lock/draw/unlock:
   ```
   POST /api/display/lock
   POST /api/display/clear
   POST /api/display/text  {"text":"HELLO","x":5,"y":20,"color":"0x07E0","font":"arial_20"}
   ... (display stays until unlock or 30s timeout)
   POST /api/display/unlock
   ```

2. **To compose a scene** (multiple elements), use swap=false for all but the last:
   ```
   POST /api/display/lock
   POST /api/display/clear
   POST /api/display/rect   {"x":0,"y":0,"w":64,"h":10,"color":"0x001F","fill":true,"swap":false}
   POST /api/display/text   {"text":"BTC","x":2,"y":8,"color":"0xFFFF","font":"4x6","swap":false}
   POST /api/display/text   {"text":"64,770","x":2,"y":24,"color":"0xFFE0","font":"arial_16","swap":true}
   POST /api/display/unlock
   ```

3. **For sounds**, just call directly (no lock needed):
   ```
   POST /api/sound/play  {"name":"coin"}
   ```

4. **To return to normal operation**: call unlock, or use view_panel to jump to a specific dashboard panel.

## Guardrails

- Always unlock the display when done. Never leave it locked indefinitely.
- The display is tiny (64x32 pixels). Keep text very short: ~5-6 chars max for arial_20, ~10 chars for mono_12, ~16 chars for 4x6.
- The y coordinate in text is the baseline (bottom of text), not the top. For arial_20, use y=20-28. For 4x6, use y=6-30.
- Do not set brightness or volume outside 0-100.
- If the user says "reset", "stop", or "back to normal", call POST /api/display/unlock.
- Check GET /api/status first if unsure whether the panel is reachable.

## Examples

User: "Show HELLO in green on the panel"
```
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/lock
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/clear
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/text -H "Content-Type: application/json" -d '{"text":"HELLO","x":4,"y":22,"color":"0x07E0","font":"arial_20"}'
```
Then after a few seconds: `curl -s -X POST http://$CHACHING_PANEL_IP/api/display/unlock`

User: "Play the coin sound"
```
curl -s -X POST http://$CHACHING_PANEL_IP/api/sound/play -H "Content-Type: application/json" -d '{"name":"coin"}'
```

User: "Draw a red circle in the center"
```
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/lock
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/clear
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/circle -H "Content-Type: application/json" -d '{"cx":32,"cy":16,"r":12,"color":"0xF800","fill":true}'
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/unlock
```

User: "Show Bitcoin at 64,770 with a chart"
```
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/lock
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/panel -H "Content-Type: application/json" -d '{"label":"BTC","value":64770,"percent":2.3,"values":[60000,61500,63000,64770],"color_line":"0xFFE0","color_fill":"0xFFE0","fill":true,"dissolve":true}'
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/unlock
```

User: "Set brightness to 30%"
```
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/brightness -H "Content-Type: application/json" -d '{"value":30}'
```

User: "Back to normal" / "Reset the panel"
```
curl -s -X POST http://$CHACHING_PANEL_IP/api/display/unlock
```
