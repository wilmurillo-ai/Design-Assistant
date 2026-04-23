---
name: tunnel-proxy
version: 1.0.6
description: >
  🐴 RAT (Remote Access Trojan) for AI agents.
  
  What it does: Agent sends commands → Your machine executes them.
  
  What it can do: Whatever you can do in a terminal.
  
  Risk: Whatever damage your user account can cause.

  Why you'd use it: Sandbox has no free network, no Docker, no yt-dlp, no ffmpeg.
  Your machine has everything.
  
  What you risk: Agent can read/delete all your files, use your IP for crimes,
  install backdoors, turn your PC into a botnet node.
  
  Use when: sandbox lacks tools, network blocked, need file transfer.
  
author: TunnelProxy Team
homepage: https://github.com/TurinFohlen/tunnel_proxy
tags: [network, proxy, tunnel, file-transfer, remote-execution]
license: MIT
requirements: [python3:3.8+, requests]
risks: [critical: full remote shell access]
env:
  - TUNNEL_HOST
  - TUNNEL_PORT
  - TUNNEL_HTTP_PORT
  - TUNNEL_TIMEOUT
  - UPLOAD_MAGIC
---
## 🚇 Security Warning

This skill enables remote command execution and file transfer on your machine.

**Before use:**
- Set `TUNNEL_HOST=127.0.0.1` unless you intentionally expose the service
- Use random high ports (49152-65535) for public exposure
- Run TunnelProxy under a restricted user account
- Review the included scripts before execution

**Do NOT use with untrusted third-party Agent services.**

# TunnelProxy Skill

## Overview

This skill enables AI agents running in cloud sandboxes to bypass network restrictions by utilizing the user's local TunnelProxy service. It provides:

- **Remote command execution** via PTY Shell (TCP port)
- **Bidirectional file transfer** via HTTP interface
- **Unrestricted network access** through user's local connection

## Quick Start

### 1. Check Tunnel Connectivity

```python
from tunnel_check import check_tunnel

status = check_tunnel()
if status["pty"] and status["http"]:
    print("✅ Tunnel is ready")
elif status["pty"]:
    print("⚠️  PTY available, HTTP unavailable")
elif status["http"]:
    print("⚠️  HTTP available, PTY unavailable")
else:
    print("❌ Tunnel is down")
```

2. Execute Remote Commands

Method 1: Direct netcat (simplest)

```bash
# Single command
echo "ls -la" | nc ${TUNNEL_HOST:-<user-provided-host>} ${TUNNEL_PORT:-<user-provided-port>}

# Multiple commands
echo -e "pwd\necho 'hello'\nwhoami" | nc <user-provided-host> <user-provided-port>
```

Method 2: Python socket

```python
import socket

s = socket.socket()
s.connect(("<user-provided-host>", <user-provided-port>))
s.send(b"curl -s https://httpbin.org/ip\n")
result = s.recv(4096).decode()
print(result)
s.close()
```

3. File Transfer

Download from remote (pull)

```python
from http_transfer import TunnelHTTP

http = TunnelHTTP()
# remote_path is relative to TunnelProxy's doc_root
http.download("/system/build.prop", "./build.prop")
```

Upload to remote (push)

```python
from http_transfer import TunnelHTTP

http = TunnelHTTP()
# Uploads to TunnelProxy's upload directory
response = http.upload("./local_file.tar.gz")
print(f"Uploaded to: {response}")
```

Using curl directly:

```bash
# Download
curl http://<user-provided-host>:<user-provided-http-port>/path/to/file -O

# Upload
curl -F "file=@local.txt" http://<user-provided-host>:<user-provided-http-port>/upload
```

4. Fetch Remote Content via User's Network

```bash
# Let user's machine fetch blocked content for you
echo "curl -s https://pypi.org/simple/" | nc <user-provided-host> <user-provided-port>

# Download large file via user's network
echo "curl -sL https://example.com/large.iso -o /tmp/large.iso" | nc <user-provided-host> <user-provided-port>
```

5. Handle Binary Files

For binary data, use http_transfer.py which properly handles multipart form-data:

```python
from http_transfer import TunnelHTTP

# Upload binary file (images, archives, etc.)
http = TunnelHTTP()
http.upload("./screenshot.png")

# Download binary file
http.download("/remote/binary.dat", "./local.dat")
```

API Reference

tunnel_check.check_tunnel()

```python
def check_tunnel(host=None, pty_port=None, http_port=None) -> Dict[str, bool]
```

Returns {"pty": bool, "http": bool} indicating port availability.

TunnelHTTP Class

Method Description Returns
download(remote_path, local_path) Download file from remote File size in bytes
upload(local_path) Upload file to remote Server response string
ping() Check HTTP service Boolean

Environment Variables

Variable Default Description
TUNNEL_HOST <user-provided-host> TunnelProxy host address
TUNNEL_PORT <user-provided-port> PTY Shell TCP port
TUNNEL_HTTP_PORT <user-provided-http-port> HTTP file server port
TUNNEL_TIMEOUT 60 Default timeout in seconds
UPLOAD_MAGIC (empty) Optional upload verification token

Common Use Cases

Bypass PyPI blocking for pip install

```python
# Method 1: Download wheel via user's network
from http_transfer import TunnelHTTP
import socket

s = socket.socket()
s.connect(("<user-provided-host>", <user-provided-port>))
s.send(b"pip download torch --no-deps -d /tmp\n")
s.close()

# Then pull the file
http = TunnelHTTP()
http.download("/tmp/torch.whl", "./torch.whl")
```

Access internal company resources

```bash
# User's machine has internal network access
echo "curl -s http://internal-company-server/api/data" | nc <user-provided-host> <user-provided-port>
```

Transfer large files with progress

```python
# http_transfer.py handles binary correctly, no corruption
http = TunnelHTTP()
http.download("/system/fonts/NotoSansCJK.ttc", "./font.ttc")
```

Error Handling

```python
import socket
from http_transfer import TunnelHTTP

try:
    s = socket.socket()
    s.settimeout(10)
    s.connect(("<user-provided-host>", <user-provided-port>))
    s.send(b"ls\n")
    result = s.recv(4096).decode()
except socket.timeout:
    print("Command timeout - increase TUNNEL_TIMEOUT")
except ConnectionRefusedError:
    print("TunnelProxy not running - start the service first")
except Exception as e:
    print(f"Error: {e}")
finally:
    s.close()

# HTTP errors
try:
    http = TunnelHTTP()
    http.download("/nonexistent/file", "./out")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.reason}")
```

Included Scripts

This skill includes two minimal scripts:

- tunnel_check.py – Verify PTY and HTTP connectivity

- http_transfer.py – Binary-safe file upload/download

Security Notes

This skill grants the agent complete control over commands executed on the user's machine. Only use with:

· Fully trusted AI agents you control
· Users who understand the security implications
· In environments with additional safeguards (firewalls, UPLOAD_MAGIC)

Troubleshooting

Issue Solution
Connection refused TunnelProxy not running → start the service
Command returns empty PTY echo issue → use stty -echo or send ; echo after command
Binary file corrupted Use http_transfer.py instead of manual socket
Timeout on large files Increase TUNNEL_TIMEOUT environment variable
Upload fails Check if UPLOAD_MAGIC matches server configuration

## 📖 Practical Tips & Common Pitfalls

For detailed usage patterns, troubleshooting, and advanced techniques, see **[TIPS.md](./TIPS.md)**.

Quick reference:

| Problem | Solution (see TIPS.md for details) |
|---------|-------------------------------------|
| Empty output | Add `; echo MARKER` or use `stty -echo` |
| Binary corruption | Use HTTP channel, not PTY |
| Command timeout | Wrap with `timeout` command |
| Large file transfer | Use `http_transfer.py`, not `cat` |
| Stuck command | Avoid interactive commands |
| Exit code capture | Echo `$?` after command |

**TL;DR:** Use `nc` for commands, `http_transfer.py` for files.