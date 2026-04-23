"""Le Proxy Français — Navigateur (Playwright Firefox via WebSocket)"""
import os
from playwright.sync_api import sync_playwright

API_KEY = os.environ["LPF_API_KEY"]

pw = sync_playwright().start()
browser = pw.firefox.connect(f"ws://nav.prx.lv:80/ghost?api_key={API_KEY}")
page = browser.new_page()
page.goto("https://api.ipify.org")
print(f"IP: {page.inner_text('body')}")
browser.close()
pw.stop()
