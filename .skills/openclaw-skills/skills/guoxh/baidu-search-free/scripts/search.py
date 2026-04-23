#!/home/guoxh/.openclaw/venv-clawd/bin/python3
# -*- coding: utf-8 -*-
import sys
import json
import requests
import time
import re
from urllib.parse import quote, urlparse, parse_qs
from bs4 import BeautifulSoup


# Baidu anti-scraping retry config
MAX_RETRIES = 2
RETRY_DELAY = 1
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


def get_real_url(baidu_link):
    """
    Resolve Baidu redirect link to get real destination URL
    """
    if not baidu_link.startswith('/link'):
        return baidu_link
    try:
        # First try to extract from URL parameters
        parsed = urlparse(baidu_link)
        query_params = parse_qs(parsed.query)
        if 'url' in query_params:
            return query_params['url'][0]
        # Then try to follow redirect to get real URL
        headers = {"User-Agent": USER_AGENT}
        resp = requests.head(f"https://www.baidu.com{baidu_link}", headers=headers, allow_redirects=True, timeout=3)
        return resp.url
    except:
        return f"https://www.baidu.com{baidu_link}"


def baidu_search(query, count=10, freshness=None):
    """
    Free Baidu web search, no API key required
    :param query: Search keywords
    :param count: Number of results to return, max 50
    :param freshness: Time range filter: pd(past day), pw(past week), pm(past month), py(past year), or YYYY-MM-DDtoYYYY-MM-DD
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # Build request parameters
    params = {
        "wd": query,
        "rn": min(count, 50),
        "ie": "utf-8",
        "cl": 3,
        "tn": "baiduadv"
    }
    
    # Handle time range filter
    if freshness:
        if freshness == "pd":
            params["gpc"] = "stf=" + str(int(time.time()) - 86400) + "," + str(int(time.time())) + "|stftype=1"
        elif freshness == "pw":
            params["gpc"] = "stf=" + str(int(time.time()) - 86400 * 7) + "," + str(int(time.time())) + "|stftype=1"
        elif freshness == "pm":
            params["gpc"] = "stf=" + str(int(time.time()) - 86400 * 30) + "," + str(int(time.time())) + "|stftype=1"
        elif freshness == "py":
            params["gpc"] = "stf=" + str(int(time.time()) - 86400 * 365) + "," + str(int(time.time())) + "|stftype=1"
        elif "to" in freshness:
            try:
                start_str, end_str = freshness.split("to")
                start_ts = int(time.mktime(time.strptime(start_str, "%Y-%m-%d")))
                end_ts = int(time.mktime(time.strptime(end_str, "%Y-%m-%d"))) + 86400
                params["gpc"] = f"stf={start_ts},{end_ts}|stftype=1"
            except:
                pass
    
    # Retry mechanism
    for retry in range(MAX_RETRIES):
        try:
            resp = requests.get("https://www.baidu.com/s", params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            
            # Detect anti-scraping verification
            if "验证码" in resp.text or "安全验证" in resp.text:
                if retry < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise RuntimeError("Baidu anti-scraping verification triggered, please try again later")
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []
            items = soup.select('.result') + soup.select('.c-container')
            items = items[:params["rn"]]
            
            for item in items:
                try:
                    # Get title
                    title_tag = item.select_one('h3') or item.select_one('.t a')
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    
                    # Get URL
                    url_tag = item.select_one('a[href]')
                    if not url_tag:
                        continue
                    baidu_link = url_tag['href']
                    real_url = get_real_url(baidu_link)
                    
                    # Get snippet
                    summary = ""
                    # Try multiple snippet selectors
                    for selector in ['.c-abstract', '.c-gap-top-small', '.content-right_8Zs40', '.op-stock-detail-sum', '.c-span-last']:
                        sum_tag = item.select_one(selector)
                        if sum_tag:
                            summary = sum_tag.get_text(strip=True)
                            break
                    if not summary:
                        # Fallback: extract all text
                        text = item.get_text(strip=True).replace(title, '').strip()
                        if len(text) > 20:
                            summary = text[:300] + "..."
                    
                    # Get publish time
                    time_str = ""
                    time_tag = item.select_one('.c-showurl') or item.select_one('.c-result-date')
                    if time_tag:
                        time_text = time_tag.get_text(strip=True)
                        time_match = re.search(r'(\d+天前|\d+小时前|\d+分钟前|\d{4}-\d{2}-\d{2})', time_text)
                        if time_match:
                            time_str = time_match.group(1)
                    
                    results.append({
                        "title": title,
                        "url": real_url,
                        "snippet": summary,
                        "time": time_str
                    })
                    
                except Exception as e:
                    continue
            return results
        
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise RuntimeError(f"Search failed: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py '{\"query\": \"keywords\", \"count\": 10, \"freshness\": \"pd/pw/pm/py/YYYY-MM-DDtoYYYY-MM-DD\"}'")
        sys.exit(1)
    
    try:
        params = json.loads(sys.argv[1])
        query = params.get('query')
        count = params.get('count', 10)
        freshness = params.get('freshness')
        
        if not query:
            print("Error: query parameter is required")
            sys.exit(1)
        
        results = baidu_search(query, count, freshness)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
