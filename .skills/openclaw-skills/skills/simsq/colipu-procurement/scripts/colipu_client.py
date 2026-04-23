# -*- coding: utf-8 -*-
"""Colipu API Client — CLI for the Colipu B2B procurement API."""
import argparse, hashlib, json, os, subprocess, sys, time, warnings
from pathlib import Path
from urllib.parse import urlencode

BASE_URL   = os.getenv('COLIPU_BASE_URL', 'https://api.ucip.colipu.com/cip').rstrip('/')
USERNAME   = os.getenv('COLIPU_USERNAME', '')
PASSWORD   = os.getenv('COLIPU_PASSWORD', '')
TOKEN_FILE_ENV = os.getenv('COLIPU_TOKEN_FILE', '').strip()
TOKEN_FILE = Path(TOKEN_FILE_ENV).expanduser() if TOKEN_FILE_ENV else None
TOKEN_PERSIST = os.getenv('COLIPU_TOKEN_PERSIST', '0').strip().lower() in ('1', 'true', 'yes', 'on')
_TOKEN_CACHE = None
if TOKEN_PERSIST and not TOKEN_FILE:
    warnings.warn('COLIPU_TOKEN_PERSIST=1 但未设置 COLIPU_TOKEN_FILE，token 将仅保存在内存中')

try:
    import requests
except ImportError:
    _venv_hint = (
        '  python -m venv .venv\n'
        '  .venv\\Scripts\\activate   (Windows)\n'
        '  source .venv/bin/activate  (Linux/macOS)\n'
        '  pip install requests==2.33.1'
    )
    sys.exit(f'Error: requests 库未安装。\n请在环境中运行:\n{_venv_hint}')


def _ts():
    return time.strftime('%Y%m%d', time.localtime())


def _sign(username, password, timestamp):
    raw = username + password + timestamp + password
    return hashlib.md5(raw.encode()).hexdigest().lower()


def _pj(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _load_json_file(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _err(msg):
    return {'success': False, 'errorcode': '-1', 'errormsg': str(msg), 'result': None}


# ── token file permission helpers ─────────────────────────────────────

def _secure_token_file(path: Path):
    """Restrict token file access to the current user only."""
    if sys.platform == 'win32':
        try:
            user = os.environ.get('USERNAME', '')
            if not user:
                warnings.warn(f'无法获取当前用户名，token 文件 {path} 的权限可能不安全')
                return
            subprocess.run(
                ['icacls', str(path), '/inheritance:r',
                 '/grant:r', f'{user}:(R,W)'],
                check=True, capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            warnings.warn(f'无法设置 token 文件权限 ({path}): {e}')
    else:
        try:
            os.chmod(path, 0o600)
        except OSError as e:
            warnings.warn(f'无法设置 token 文件权限 ({path}): {e}')


# ── token management ─────────────────────────────────────────────────

def _normalize_token_data(data):
    token_data = dict(data)
    expires = token_data.get('expires_at', '')
    try:
        ts = time.mktime(time.strptime(expires, '%Y-%m-%d %H:%M:%S'))
    except Exception:
        ts = time.time() + 43200
    token_data['expires_at_ts'] = ts
    return token_data

def load_token():
    global _TOKEN_CACHE
    data = _TOKEN_CACHE
    if data is None and TOKEN_PERSIST and TOKEN_FILE:
        if not TOKEN_FILE.exists():
            return None
        _secure_token_file(TOKEN_FILE)
        try:
            with open(TOKEN_FILE, encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            TOKEN_FILE.unlink(missing_ok=True)
            return None
        _TOKEN_CACHE = data
    if data is None:
        return None
    if time.time() > (data.get('expires_at_ts', 0) - 300):
        return refresh_token(data.get('refresh_token'))
    return data


def save_token(data):
    global _TOKEN_CACHE
    token_data = _normalize_token_data(data)
    _TOKEN_CACHE = token_data
    if not (TOKEN_PERSIST and TOKEN_FILE):
        return
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, ensure_ascii=False, indent=2)
    _secure_token_file(TOKEN_FILE)


def fetch_token():
    if not USERNAME or not PASSWORD:
        sys.exit('Error: set COLIPU_USERNAME and COLIPU_PASSWORD env vars.\n'
                 'To get credentials, contact: cip_tech@colipu.com')
    ts = _ts()
    s = _sign(USERNAME, PASSWORD, ts)
    resp = api_get(
        f'/api/restful/auth2/access_token?username={USERNAME}&timestamp={ts}&sign={s}',
    )
    if resp.get('success'):
        save_token(resp['result'])
        return resp['result']
    sys.exit(f'Failed to get token: {resp}')


def refresh_token(rt):
    resp = api_get(f'/api/restful/auth2/refresh_token?refresh_token={rt}')
    if resp.get('success'):
        save_token(resp['result'])
        return resp['result']
    return fetch_token()


def get_token():
    data = load_token()
    if data:
        return data['access_token']
    return fetch_token()['access_token']


# ── API transport ────────────────────────────────────────────────────

def api_get(path, token=None, params=None):
    headers = {'Colipu-Token': token} if token else {}
    url = BASE_URL + path
    if params:
        url += ('&' if '?' in url else '?') + urlencode(params)
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return _err(e)


def api_post(path, body, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Colipu-Token'] = token
    try:
        r = requests.post(BASE_URL + path, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return _err(e)


def api_patch(path, body, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Colipu-Token'] = token
    try:
        r = requests.patch(BASE_URL + path, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return _err(e)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='Colipu API Client')
    sub = p.add_subparsers(dest='cmd')

    # product
    sub.add_parser('categories', help='Get product categories')
    sp = sub.add_parser('product-detail', help='Get product detail')
    sp.add_argument('--sku', required=True)
    sp = sub.add_parser('product-price', help='Get product price')
    sp.add_argument('--skus', required=True)
    sp.add_argument('--customer-code')
    sp = sub.add_parser('product-stock', help='Get product stock')
    sp.add_argument('--skus', required=True)
    sp.add_argument('--area', default='*')
    sp.add_argument('--customer-code')

    # order
    sp = sub.add_parser('order-submit', help='Submit order')
    sp.add_argument('--data')
    sp.add_argument('--json', dest='json_str')
    sp = sub.add_parser('order-confirm', help='Confirm order')
    sp.add_argument('--order-id', required=True)
    sp.add_argument('--data')
    sp.add_argument('--json', dest='json_str')
    sp = sub.add_parser('order-cancel', help='Cancel order')
    sp.add_argument('--order-id', required=True)
    sp = sub.add_parser('order-info', help='Get order info')
    sp.add_argument('--order-id', required=True)
    sp = sub.add_parser('order-state', help='Get order state')
    sp.add_argument('--order-id', required=True)
    sp = sub.add_parser('order-signconfirm', help='Order sign confirm')
    sp.add_argument('--order-id', required=True)
    sp.add_argument('--delivery-code')

    # billing
    sp = sub.add_parser('bill-reconciliation', help='Bill reconciliation')
    sp.add_argument('--start-date', required=True)
    sp.add_argument('--end-date', required=True)
    sp.add_argument('--order-id')
    sp = sub.add_parser('bill-apply', help='Bill apply')
    sp.add_argument('--data', required=True)

    # aftersale
    sp = sub.add_parser('aftersale-apply', help='Aftersale apply')
    sp.add_argument('--data', required=True)
    sp = sub.add_parser('aftersale-info', help='Get aftersale info')
    sp.add_argument('--apply-code', required=True)
    sp.add_argument('--order-id')
    sp.add_argument('--delivery-code')
    sp = sub.add_parser('aftersale-cancel', help='Cancel aftersale')
    sp.add_argument('--apply-code', required=True)
    sp.add_argument('--order-id')

    # logistics
    sp = sub.add_parser('logistics', help='Query logistics')
    sp.add_argument('--order-id', required=True)
    sp = sub.add_parser('delivery-logistics', help='Query delivery logistics')
    sp.add_argument('--delivery-code', required=True)

    # messages
    sp = sub.add_parser('messages', help='Get messages')
    sp.add_argument('--type', default='302,303')
    sp.add_argument('--del', dest='delete', type=int, default=1)
    sp = sub.add_parser('message-delete', help='Delete messages')
    sp.add_argument('--ids', required=True)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return
    token = get_token()
    cmd = args.cmd

    if cmd == 'categories':
        _pj(api_get('/api/restful/categories', token))

    elif cmd == 'product-detail':
        _pj(api_get(f'/api/restful/product/{args.sku}/detail', token))

    elif cmd == 'product-price':
        params = {'skus': args.skus}
        if args.customer_code:
            params['customer_code'] = args.customer_code
        _pj(api_get('/api/restful/products/prices', token, params))

    elif cmd == 'product-stock':
        params = {'skus': args.skus, 'area': args.area}
        if args.customer_code:
            params['customer_code'] = args.customer_code
        _pj(api_get('/api/restful/products/areastocks', token, params))

    elif cmd == 'order-submit':
        body = _load_json_file(args.data) if args.data else json.loads(args.json_str or '{}')
        _pj(api_post('/api/restful/order', body, token))

    elif cmd == 'order-confirm':
        body = _load_json_file(args.data) if args.data else json.loads(args.json_str or '{}')
        _pj(api_patch(f'/api/restful/order/{args.order_id}/confirmation', body, token))

    elif cmd == 'order-cancel':
        _pj(api_patch(f'/api/restful/order/{args.order_id}/cancel', {}, token))

    elif cmd == 'order-info':
        _pj(api_get(f'/api/restful/order/{args.order_id}/query', token))

    elif cmd == 'order-state':
        _pj(api_get(f'/api/restful/order/{args.order_id}/state', token))

    elif cmd == 'order-signconfirm':
        body = {'delivery_code': args.delivery_code} if args.delivery_code else {}
        _pj(api_patch(f'/api/restful/order/{args.order_id}/signconfirm', body, token))

    elif cmd == 'bill-reconciliation':
        params = {'start_date': args.start_date, 'end_date': args.end_date}
        if args.order_id:
            params['order_id'] = args.order_id
        _pj(api_get('/api/restful/order/signstatus', token, params))

    elif cmd == 'bill-apply':
        _pj(api_post('/api/restful/apiBill', _load_json_file(args.data), token))

    elif cmd == 'aftersale-apply':
        _pj(api_post('/api/restful/refund/apply', _load_json_file(args.data), token))

    elif cmd == 'aftersale-info':
        params = {'apply_code': args.apply_code}
        if args.order_id:
            params['order_id'] = args.order_id
        if args.delivery_code:
            params['delivery_code'] = args.delivery_code
        _pj(api_get(f'/api/restful/refund/{args.apply_code}/query', token, params))

    elif cmd == 'aftersale-cancel':
        body = {'apply_code': args.apply_code}
        if args.order_id:
            body['order_id'] = args.order_id
        _pj(api_post('/api/restful/refund/cancel', body, token))

    elif cmd == 'logistics':
        _pj(api_get(f'/api/restful/order/{args.order_id}/logistics', token))

    elif cmd == 'delivery-logistics':
        _pj(api_get(f'/api/restful/order/delivery/{args.delivery_code}/logistics', token))

    elif cmd == 'messages':
        _pj(api_get('/api/restful/messages', token, {'type': args.type, 'del': args.delete}))

    elif cmd == 'message-delete':
        _pj(api_post('/api/restful/messages/batchdelete', {'ids': args.ids.split(',')}, token))


if __name__ == '__main__':
    main()
