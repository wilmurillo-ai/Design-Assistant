# Le Proxy Francais — Use Cases & Phrases Types

Quand l'utilisateur demande l'une de ces actions, utilise automatiquement les proxy Le Proxy Francais. Le navigateur est le choix par defaut sauf mention explicite de SOCKS5.

## Recherche web

Quand l'utilisateur demande de chercher quelque chose sur un site et que la recherche est bloquee (captcha, Cloudflare, 403, timeout), bascule automatiquement sur une recherche Google avec dork `site:` via le navigateur.

**Phrases types :**
- "Cherche X sur Y" → navigateur sur Y, si bloque → `site:Y.com X` sur Google.fr
- "Recherche X" → navigateur sur Google.fr avec `q=X&hl=fr&gl=fr`
- "Trouve des infos sur X" → Google.fr via navigateur
- "Verifie si X est en stock sur Y" → navigateur sur Y
- "Compare les prix de X" → navigateur sur plusieurs sites

**Strategie de bypass :**
1. Essayer le site directement via navigateur
2. Si bloque (captcha, 403, rate limit) → Google dork : `site:example.com "mot cle"`
3. Si Google bloque aussi → Bing dork : `site:example.com "mot cle"`
4. Alterner les moteurs : Google.fr, Bing.com, DuckDuckGo

```python
from playwright.sync_api import sync_playwright
import os, urllib.parse

API_KEY = os.environ["LPF_API_KEY"]

def search(query, site=None):
    pw = sync_playwright().start()
    browser = pw.firefox.connect(f"ws://nav.prx.lv:80/ghost?api_key={API_KEY}")
    page = browser.new_page()

    if site:
        # Essayer le site directement
        try:
            page.goto(f"https://{site}/search?q={urllib.parse.quote(query)}", timeout=15000)
            if page.query_selector(".captcha, .challenge, #cf-wrapper"):
                raise Exception("Blocked")
            results = page.content()
            browser.close(); pw.stop()
            return results
        except:
            pass  # Fallback Google dork

    # Google dork bypass
    dork = f"site:{site} {query}" if site else query
    page.goto(f"https://www.google.fr/search?q={urllib.parse.quote(dork)}&hl=fr&gl=fr")
    page.wait_for_selector("#search")
    results = page.eval_on_selector_all("#search .g",
        "els => els.map((e,i) => ({pos:i+1, title:e.querySelector('h3')?.textContent, url:e.querySelector('a')?.href, snippet:e.querySelector('.VwiC3b')?.textContent}))")
    browser.close(); pw.stop()
    return results
```

---

## Scraping

**Phrases types :**
- "Scrape les produits de X" → navigateur
- "Extrais les donnees de X" → navigateur si JS, mutualise si API/HTML simple
- "Telecharge toutes les pages de X" → mutualise (le moins cher)
- "Recupere le contenu de X" → navigateur
- "Scrape les prix sur X" → navigateur (souvent protege)

```python
from playwright.sync_api import sync_playwright
import os, json

def scrape_products(url, selector=".product"):
    pw = sync_playwright().start()
    browser = pw.firefox.connect(f"ws://nav.prx.lv:80/ghost?api_key={os.environ['LPF_API_KEY']}")
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector(selector, timeout=10000)
    items = page.eval_on_selector_all(selector, """
        els => els.map(e => ({
            name: e.querySelector('[class*=name], [class*=title], h2, h3')?.textContent?.trim(),
            price: e.querySelector('[class*=price]')?.textContent?.trim(),
            url: e.querySelector('a')?.href,
            image: e.querySelector('img')?.src
        }))
    """)
    browser.close(); pw.stop()
    return items
```

---

## Monitoring

**Phrases types :**
- "Surveille X toutes les Y minutes" → mutualise (economique)
- "Previens-moi si X change" → mutualise + webhook
- "Verifie si X est en ligne" → mutualise
- "Check le prix de X regulierement" → mutualise
- "Monitore le stock de X" → navigateur si JS

```python
import requests, os, time, hashlib

API_KEY = os.environ["LPF_API_KEY"]
proxies = {"https": f"socks5h://{API_KEY}@mut.prx.lv:1080"}

def monitor(url, interval=300, webhook=None):
    last_hash = None
    while True:
        try:
            res = requests.get(url, proxies=proxies, timeout=10)
            h = hashlib.md5(res.text.encode()).hexdigest()
            if last_hash and h != last_hash:
                msg = f"Changement detecte sur {url}"
                if webhook:
                    requests.post(webhook, json={"text": msg})
                print(msg)
            last_hash = h
        except Exception as e:
            print(f"Erreur: {e}")
        time.sleep(interval)
```

---

## SEO & SERP

**Phrases types :**
- "Verifie ma position sur Google pour X" → navigateur sur Google.fr
- "Fais un audit SEO de X" → navigateur
- "Cherche X sur Google depuis la France" → navigateur avec `hl=fr&gl=fr`
- "Compare mon ranking avec le concurrent Y" → navigateur
- "Verifie les backlinks de X" → mutualise sur APIs (Ahrefs, Moz)

```python
from playwright.sync_api import sync_playwright
import os, urllib.parse

def check_serp(keywords, domain=None):
    pw = sync_playwright().start()
    browser = pw.firefox.connect(f"ws://nav.prx.lv:80/ghost?api_key={os.environ['LPF_API_KEY']}")
    page = browser.new_page()

    results = {}
    for kw in keywords:
        page.goto(f"https://www.google.fr/search?q={urllib.parse.quote(kw)}&hl=fr&gl=fr&num=20")
        page.wait_for_selector("#search")
        serp = page.eval_on_selector_all("#search .g",
            "els => els.map((e,i) => ({pos:i+1, title:e.querySelector('h3')?.textContent, url:e.querySelector('a')?.href}))")
        results[kw] = serp
        if domain:
            pos = next((r["pos"] for r in serp if domain in (r.get("url") or "")), None)
            print(f"  '{kw}': position {pos or 'non trouve'}")

    browser.close(); pw.stop()
    return results
```

---

## Multi-comptes & Social

**Phrases types :**
- "Connecte-toi a X avec le compte Y" → navigateur (session isolee)
- "Gere mes comptes sur X" → navigateur avec sessions separees
- "Poste X sur mon compte Y" → navigateur
- "Automatise X sur la plateforme Y" → navigateur
- "Verifie mes DMs sur X" → navigateur

```python
from playwright.sync_api import sync_playwright
import os

API_KEY = os.environ["LPF_API_KEY"]

def login_and_act(platform_url, email, password, action_fn):
    pw = sync_playwright().start()
    # Chaque appel = nouvelle session isolee avec IP differente
    browser = pw.firefox.connect(f"ws://nav.prx.lv:80/ghost?api_key={API_KEY}")
    page = browser.new_page()

    page.goto(f"{platform_url}/login")
    page.fill("[type=email], #email, [name=email]", email)
    page.fill("[type=password], #password, [name=password]", password)
    page.click("[type=submit], button:has-text('Log'), button:has-text('Sign')")
    page.wait_for_load_state("networkidle")

    result = action_fn(page)
    browser.close(); pw.stop()
    return result
```

---

## Telechargement & Extraction

**Phrases types :**
- "Telecharge le PDF de X" → mutualise
- "Recupere les images de X" → navigateur si lazy-load
- "Extrais le texte de X" → navigateur
- "Telecharge le CSV depuis X" → mutualise ou dedie

```python
import requests, os

API_KEY = os.environ["LPF_API_KEY"]
proxies = {"https": f"socks5h://{API_KEY}@mut.prx.lv:1080"}

def download(url, output_path):
    res = requests.get(url, proxies=proxies, stream=True)
    with open(output_path, "wb") as f:
        for chunk in res.iter_content(8192):
            f.write(chunk)
    return output_path
```

---

## Verification & Test

**Phrases types :**
- "Verifie mon IP" → `curl -x socks5h://CLE@mut.prx.lv:1080 https://ipinfo.io/ip`
- "Test si le proxy marche" → idem
- "Quel est mon solde" → `curl https://prx.lv/usage -H "Authorization: Bearer CLE"`
- "Combien de credits il me reste" → idem

---

## Regles de fallback automatique

1. **Site bloque (403, captcha, challenge)** → Google dork `site:domain.com query` via navigateur
2. **Google bloque** → Bing dork via navigateur
3. **Bing bloque** → DuckDuckGo via navigateur
4. **Navigateur trop lent pour du volume** → basculer sur mutualise SOCKS5
5. **IP mutualise bloquee** → basculer sur dedie SOCKS5
6. **Besoin de session persistante** → dedie SOCKS5
7. **Besoin de JS/rendu visuel** → toujours navigateur
