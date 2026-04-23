#!/usr/bin/env python3
"""配置模块 - 统一读取USER.md中的配置"""

import os
import re

CONFIG = None


def load_config():
    """Load all API config from USER.md"""
    global CONFIG
    if CONFIG:
        return CONFIG

    user_md = os.path.expanduser("~/.openclaw/workspace/USER.md")
    try:
        with open(user_md, "r") as f:
            content = f.read()

        config = {
            'binance': {},
            'astock': {}
        }
        lines = content.split('\n')
        current_section = None

        for line in lines:
            stripped = line.strip()

            # Detect section change
            if stripped.startswith('##'):
                section_name = stripped.lstrip('#').strip().lower()
                if '币安' in section_name or 'binance' in section_name:
                    current_section = 'binance'
                elif '股票' in section_name or 'astock' in section_name:
                    current_section = 'astock'
                else:
                    current_section = None
                continue

            if current_section == 'binance':
                # API URL
                if 'API地址' in line or 'base_url' in line.lower():
                    url_match = re.search(r'https?://[^\s]+', line)
                    if url_match:
                        config['binance']['base_url'] = url_match.group(0).rstrip('/')

                # API Key (64 char alphanumeric)
                elif 'API Key' in line or 'api_key' in line.lower():
                    key_match = re.search(r'([A-Za-z0-9]{64})', line)
                    if key_match:
                        config['binance']['api_key'] = key_match.group(1)

                # Secret Key (64 char alphanumeric)
                elif 'Secret' in line:
                    secret_match = re.search(r'([A-Za-z0-9]{64})', line)
                    if secret_match:
                        config['binance']['secret_key'] = secret_match.group(1)

            elif current_section == 'astock':
                # A股相关配置
                if '雪球token' in line or 'xueqiu' in line.lower():
                    token_match = re.search(r'["\']?([A-Za-z0-9_]+)["\']?', line)
                    if token_match:
                        config['astock']['xueqiu_token'] = token_match.group(1)

        # Default values
        if 'base_url' not in config['binance']:
            config['binance']['base_url'] = 'https://api.binance.com'
        if 'api_key' not in config['binance']:
            print("[CONFIG] Warning: Binance API credentials not found in USER.md")
        if 'secret_key' not in config['binance']:
            print("[CONFIG] Warning: Binance Secret Key not found in USER.md")

        CONFIG = config
        return config

    except Exception as e:
        print(f"[CONFIG] Error reading USER.md: {e}")
        return {'binance': {}, 'astock': {}}


def get_signature(query_string, secret_key):
    """Generate HMAC SHA256 signature"""
    import hmac
    import hashlib
    return hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def save_positions(positions):
    """保存持仓到JSON文件"""
    import json
    from pathlib import Path
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    pos_file = data_dir / 'positions.json'
    with open(pos_file, 'w') as f:
        json.dump(positions, f, indent=2, ensure_ascii=False)


def load_positions():
    """读取持仓JSON文件"""
    import json
    from pathlib import Path
    pos_file = Path(__file__).parent.parent / 'data' / 'positions.json'
    if pos_file.exists():
        with open(pos_file, 'r') as f:
            return json.load(f)
    return {'binance': {}, 'astock': {}}


def log_trade(trade_info):
    """记录交易到日志"""
    import json
    from pathlib import Path
    from datetime import datetime
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    log_file = data_dir / 'trade_log.json'
    
    logs = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            logs = json.load(f)
    
    logs.append({
        'timestamp': datetime.now().isoformat(),
        **trade_info
    })
    
    # Keep last 1000 trades
    logs = logs[-1000:]
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    config = load_config()
    print("[CONFIG] Loaded:", config)
