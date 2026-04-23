"""Le Proxy Français — Proxy SOCKS5 (Mutualisé ou Dédié)"""
import os
import requests

API_KEY = os.environ["LPF_API_KEY"]

# Mutualisé (3 crédits/Go) — changer en ded.prx.lv:1081 pour Dédié (8 crédits/Go)
proxies = {"https": f"socks5h://{API_KEY}@mut.prx.lv:1080"}

res = requests.get("https://ipinfo.io/ip", proxies=proxies)
print(f"IP: {res.text.strip()}")
