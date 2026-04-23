# http-status-checker

Check HTTP status codes for URLs. Supports bulk checking, redirects, and SSL verification.

## Usage

```
Check status of [URL]
Check multiple URLs: [list URLs]
Bulk check URLs from [file]
```

## What it does

- **Single URL** — Shows HTTP status code, response time, content-type, server
- **Redirect chain** — Follows all redirects and shows the full chain
- **SSL check** — Shows SSL certificate expiry, issuer, validity
- **Bulk** — Check up to 100 URLs from a text file

## Output

```
URL: https://example.com
Status: 200 OK
Response Time: 142ms
Content-Type: text/html
Server: ECS (sec/9393)
SSL: Valid until 2026-08-15 (DigiCert Inc)
```

## Notes

- No API key needed
- Rate limited to 50 requests/minute
- Shows full redirect chain for moved pages
