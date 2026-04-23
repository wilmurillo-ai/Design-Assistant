# Install tgctl

## Pre-built binary (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/youzixilan/go-tdlib/main/scripts/install.sh | bash
```

Supports: macOS (arm64/amd64), Linux (amd64/arm64), Windows (amd64).

## Build from source

```bash
go install github.com/aqin/go-tdlib/cmd/tgctl@latest
```

No CGO, no external dependencies.
