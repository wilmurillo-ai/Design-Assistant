#!/usr/bin/env python3
"""setup_crons.py — self-improvement-loop v4.3: create cron jobs from payloads JSON."""
import json, subprocess, sys, os, urllib.request, urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAYLOADS_FILE = os.path.join(SCRIPT_DIR, 'cron-payloads.json')

# Auto-detect Telegram ID from openclaw.json
def detect_telegram_id():
    path = os.path.expanduser('~/.openclaw/openclaw.json')
    if not os.path.exists(path):
        return os.environ.get('TELEGRAM_ID', '')
    with open(path) as f:
        d = json.load(f)
    cfg = d.get('channels', {}).get('telegram', {})
    accounts = cfg.get('accounts', {})
    for account_name in ['default', 'code', 'moling']:
        if account_name in accounts:
            ids = accounts[account_name].get('allowFrom', [])
            if ids:
                return ids[0]
    ids = cfg.get('allowFrom', [])
    if ids:
        return ids[0]
    return os.environ.get('TELEGRAM_ID', '')

def read_payloads(telegram_id, channel, channel_account):
    """Read cron payloads and inject channel/account/telegram_id."""
    with open(PAYLOADS_FILE) as f:
        payloads = json.load(f)

    for name, job in payloads.items():
        # Inject auto-detected channel + account
        job.setdefault('delivery', {})['channel'] = channel
        if channel_account:
            job['delivery']['accountId'] = channel_account
        # Inject auto-detected Telegram ID
        if telegram_id:
            job.setdefault('delivery', {})['to'] = telegram_id
            msg = job['payload']['message']
            msg = msg.replace('<TELEGRAM_ID>', telegram_id)
            job['payload']['message'] = msg

        # Warn if sessionTarget=current but using CLI (CLI only supports main/isolated)
        if job.get('sessionTarget') == 'current':
            print(f"  ⚠ {name}: sessionTarget=current (requires API, not CLI)")
    return payloads

def create_via_api(name, job_config):
    """Create cron via gateway API (preferred — supports sessionTarget=current)."""
    gateway_url = os.environ.get('OPENCLAW_GATEWAY_URL', 'http://localhost:18789')
    token = os.environ.get('OPENCLAW_GATEWAY_TOKEN', '')

    api_payload = {
        'name': name,
        'schedule': job_config.get('schedule', {}),
        'sessionTarget': job_config.get('sessionTarget', 'isolated'),
        'payload': job_config.get('payload', {}),
        'delivery': job_config.get('delivery', {}),
        'enabled': job_config.get('enabled', True),
    }

    req = urllib.request.Request(
        f'{gateway_url}/api/cron/jobs',
        data=json.dumps(api_payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            print(f"  ✓ {name} created (API)")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"  ⚠ {name} API error {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  ⚠ {name} API error: {e}")
        return False

def create_via_cli(name, job_config):
    """Create cron via openclaw CLI (fallback — does NOT support sessionTarget=current)."""
    schedule = job_config.get('schedule', {})
    schedule_kind = schedule.get('kind', 'every')
    payload = job_config.get('payload', {})
    delivery = job_config.get('delivery', {})
    session_target = job_config.get('sessionTarget', 'isolated')

    # CLI only supports main|isolated — warn if current
    if session_target == 'current':
        print(f"  ⚠ {name}: CLI does not support sessionTarget=current, using isolated")
        session_target = 'isolated'

    cmd = [
        'openclaw', 'cron', 'add',
        '--name', name,
        '--payload-kind', payload.get('kind', 'agentTurn'),
        '--session', session_target,
    ]

    if schedule_kind == 'every':
        cmd += ['--every', str(schedule.get('everyMs', 1800000))]
    elif schedule_kind == 'cron':
        cmd += ['--cron', schedule.get('expr', '')]
        if 'tz' in schedule:
            cmd += ['--tz', schedule['tz']]

    cmd += ['--timeout-seconds', str(payload.get('timeoutSeconds', 300))]
    for tool in payload.get('toolsAllow', []):
        cmd += ['--tools', tool]

    # Delivery
    cmd += ['--deliver']
    cmd += ['--channel', delivery.get('channel', 'telegram')]
    if delivery.get('to'):
        cmd += ['--to', delivery['to']]

    proc = subprocess.run(
        cmd,
        input=payload.get('message', ''),
        text=True,
        capture_output=True,
        timeout=30
    )

    if proc.returncode == 0:
        print(f"  ✓ {name} created (CLI)")
        return True
    else:
        print(f"  ✗ {name} CLI failed: {proc.stderr[:200]}")
        return False

def job_exists(name):
    """Check if a cron job with this name already exists."""
    r = subprocess.run(
        ['openclaw', 'cron', 'list', '--json'],
        capture_output=True, text=True, timeout=15
    )
    if r.returncode != 0:
        return False
    try:
        data = json.loads(r.stdout)
        for job in data.get('jobs', []):
            if job.get('name') == name:
                return True
    except:
        pass
    return False

def main():
    print("Setting up cron jobs...")

    channel = os.environ.get('CHANNEL', 'telegram')
    channel_account = os.environ.get('CHANNEL_ACCOUNT', '')
    telegram_id = os.environ.get('TELEGRAM_ID', '') or detect_telegram_id()

    print(f"  ✓ Channel: {channel}" + (f" (account: {channel_account})" if channel_account else ""))
    if telegram_id:
        print(f"  ✓ Telegram ID detected: {telegram_id}")
    else:
        print("  ⚠ Telegram ID not detected — set TELEGRAM_ID env var or check openclaw.json")

    payloads = read_payloads(telegram_id, channel, channel_account)

    for name, job_config in payloads.items():
        if job_exists(name):
            print(f"  ✓ {name} already exists, skipping")
            continue

        # Try API first (supports sessionTarget=current)
        if not create_via_api(name, job_config):
            # Fallback to CLI
            print(f"  → Retrying via CLI...")
            create_via_cli(name, job_config)

    print("Cron setup complete.")

if __name__ == '__main__':
    main()
