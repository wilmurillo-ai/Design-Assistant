# tgctl Installation Guide

## Dependencies

### macOS
```bash
brew install cmake gperf openssl go
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install cmake gperf libssl-dev zlib1g-dev build-essential golang
```

## Step 1: Build TDLib

```bash
mkdir -p ~/dev/tdlib-build && cd ~/dev/tdlib-build
git clone --depth 1 https://github.com/tdlib/td.git
cd td && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
  -DOPENSSL_ROOT_DIR=$(brew --prefix openssl@3 2>/dev/null || echo /usr) \
  -DCMAKE_INSTALL_PREFIX=$HOME/.local/tdlib \
  ..
cmake --build . --target tdjson -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
cmake --install .
```

If `cmake --install` reports a missing static lib error, ignore it — the dynamic lib is installed.

Copy headers if missing:
```bash
cp td/telegram/td_json_client.h $HOME/.local/tdlib/include/td/telegram/ 2>/dev/null
cp build/td/telegram/tdjson_export.h $HOME/.local/tdlib/include/td/telegram/ 2>/dev/null
```

## Step 2: Build tgctl

```bash
git clone https://github.com/youzixilan/go-tdlib.git
cd go-tdlib
CGO_CFLAGS="-I$HOME/.local/tdlib/include" \
CGO_LDFLAGS="-L$HOME/.local/tdlib/lib -ltdjson" \
go build -o ./bin/tgctl ./cmd/tgctl/
```

### Fix dynamic library path

macOS:
```bash
install_name_tool -add_rpath $HOME/.local/tdlib/lib ./bin/tgctl
```

Linux:
```bash
# Add to ~/.bashrc or ~/.zshrc:
export LD_LIBRARY_PATH=$HOME/.local/tdlib/lib:$LD_LIBRARY_PATH
```

## Step 3: Get Telegram API credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development"
4. Get `api_id` (number) and `api_hash` (string)

## Step 4: Login

```bash
TELEGRAM_API_ID=<your_id> TELEGRAM_API_HASH=<your_hash> ./bin/tgctl login
```

- Enter phone number when prompted
- Enter auth code (do NOT send it via Telegram — Telegram will block the login)
- Enter 2FA password if enabled

Session is saved in `~/.tgctl/` and persists across runs.

## Step 5: Record in TOOLS.md

Add to your workspace TOOLS.md:

```markdown
### tgctl
- Binary: /path/to/go-tdlib/bin/tgctl
- Env: TELEGRAM_API_ID=xxx TELEGRAM_API_HASH=xxx
```
