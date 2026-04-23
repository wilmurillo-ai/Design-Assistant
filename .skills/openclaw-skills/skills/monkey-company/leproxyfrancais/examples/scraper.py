"""Le Proxy Français — Scraping e-commerce avec navigateur"""
import os
import json
from playwright.sync_api import sync_playwright

API_KEY = os.environ["LPF_API_KEY"]

pw = sync_playwright().start()
browser = pw.firefox.connect(f"ws://nav.prx.lv:80/ghost?api_key={API_KEY}")
page = browser.new_page()

page.goto("https://www.example-shop.fr/produits")
page.wait_for_selector(".product-card")

products = page.eval_on_selector_all(".product-card", """
  cards => cards.map(c => ({
    name: c.querySelector('.name')?.textContent,
    price: c.querySelector('.price')?.textContent,
    url: c.querySelector('a')?.href
  }))
""")

print(json.dumps(products, indent=2, ensure_ascii=False))
browser.close()
pw.stop()
