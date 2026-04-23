#!/usr/bin/env python3
import subprocess, json

with open('/Users/godspeed/.openclaw/agents/dawang/agents/dawang/auth-profiles.json') as f:
    key = json.load(f)['profiles']['minimax:default']['key']

url = 'https://api.minimax.io/anthropic/v1/messages'
data = json.dumps({'model': 'MiniMax-M2.7', 'messages': [{'role': 'user', 'content': 'say hello'}]})
r = subprocess.run(
    ['curl', '-s', '--noproxy', '*', '-X', 'POST', url,
     '-H', 'Authorization: Bearer ' + key,
     '-H', 'anthropic-version: 2023-06-01',
     '-H', 'Content-Type: application/json',
     '-d", data],
    capture_output=True, text=True, timeout=20)
print(r.stdout[:200])
