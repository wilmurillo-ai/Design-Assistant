---
name: inline-asset-probe
version: 0.1.0
description: Fetch a URL with curl/wget, extract inline base64 data URIs, and best-effort decode any content to inspect embedded assets.
---

# Inline Asset Probe

Practical utility for quickly extracting inline assets from HTML or CSS and inspecting base64-encoded payloads.

## What It Does

- Fetches a target URL using curl or wget
- Scans for inline `data:*;base64,` assets and saves them as files
- Optionally base64-decodes the entire response as a best-effort probe

## Usage

PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -Url https://example.com
```

Save raw response and decode any content:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -Url https://example.com -SaveResponse -DecodeResponse
```

Limit extracted assets and choose output directory:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -Url https://example.com -OutDir probe_out -MaxAssets 20
```

## Output

- `probe_out/response.bin` when `-SaveResponse`
- `probe_out/assets/asset_*.ext` for extracted inline assets
- `probe_out/decoded.bin` when `-DecodeResponse`

## Notes

- `-DecodeResponse` performs a best-effort base64 decode of any content by stripping non-base64 characters and padding to a 4-byte boundary.
- Works best for HTML/CSS pages with inline data URIs.
