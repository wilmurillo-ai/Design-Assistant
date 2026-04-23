# Auth Command Reference

## Login

```bash
tronclass auth login <username>
tronclass auth login --fju <student_id>
```

**Generic API flow** (default): Works with any TronClass deployment. Prompts for the school's base URL and password. Session saved to `~/.tronclass-cli/`.

**FJU CAS flow** (`--fju`): Uses Fu Jen Catholic University's CAS. Supports interactive CAPTCHA — the CLI downloads the CAPTCHA image, opens it with the system image viewer, and prompts for input. If a valid session already exists for the same username, it is restored automatically.

## Check

```bash
tronclass auth check
```

Prints: authenticated username, student ID, base URL, school config, and whether session cookies are present.

## Logout

```bash
tronclass auth logout
```

Clears cookies and config from `~/.tronclass-cli/`.

## Session Storage

All session data lives in `~/.tronclass-cli/`:
- `config.json` — username, studentId, baseUrl, school
- `cookies.json` — session cookies (CookieJar format)
