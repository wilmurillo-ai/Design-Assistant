---
name: telegram-cli
description: Manage Telegram via TDLib - login, send messages, create bots, list chats, search, view history, manage contacts. Use when user asks to interact with Telegram as a user account (not bot API), create Telegram bots, send messages via Telegram, list Telegram chats, or search Telegram.
---

# Telegram CLI (TDLib)

User-account-level Telegram management via TDLib.

## Prerequisites

- `tgctl` binary built and on PATH (see `references/install.md`)
- `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` env vars set
- Logged in (`tgctl login`, session persists in `~/.tgctl/`)
- Binary path and env recorded in TOOLS.md

## Commands

```bash
TELEGRAM_API_ID=<id> TELEGRAM_API_HASH=<hash> tgctl [--profile <name>] <command>
```

| Command | Description |
|---------|-------------|
| `me` | Current user info |
| `send <chat> <msg>` | Send message (ID or @username) |
| `chats [limit]` | List chats |
| `create-bot <name> <username>` | Create bot via BotFather, returns token |
| `history <chat> [limit]` | Chat history |
| `search <query>` | Search public chats |
| `contacts` | List contacts |
| `logout` | Logout |

## Multi-Account (--profile)

```bash
tgctl --profile work login     # login with work account
tgctl --profile personal login # login with personal account
tgctl --profile work me        # use work account
tgctl me                       # uses "default" profile
```

Each profile stores its own session in `~/.tgctl/<profile>/`.

## Chat ID Format

- **Private chat**: Use user ID directly (e.g. `8568316820`). tgctl auto-creates the private chat via `createPrivateChat`.
- **Group/Channel**: Add `-100` prefix to the peer ID. E.g. peer ID `3805592010` → chat ID `-1003805592010`.
- **@username**: Use directly (e.g. `@BotFather`).

## Security

- Credentials in env vars only, never hardcode
- `~/.tgctl/` contains auth session — protect it
- Auth codes must not be sent via Telegram (will be blocked by Telegram's security)
