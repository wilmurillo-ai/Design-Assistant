#!/usr/bin/env python3
"""
Novada Search v2.0.0 — AI Agent Search Platform

Three-layer architecture:
  Layer 1: Full Engine Support (9 engines + Google 13 sub-types)
  Layer 2: Vertical Scenes (shopping, jobs, academic, local, video, news, travel)
  Layer 3: AI Agent Mode (auto, multi-engine, extract)

Designed to compete with Tavily as an AI-optimized search API.
"""

import argparse
import json
import math
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from typing import List, Dict, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

NOVADA_SEARCH_URL = "https://scraperapi.novada.com/search"

# ============================================================================
# Layer 1: Full Engine Registry
# ============================================================================

SUPPORTED_ENGINES = (
    "google", "bing", "yahoo", "duckduckgo",
    "yandex", "youtube", "ebay", "walmart", "yelp",
)

GOOGLE_TYPES = (
    "search", "shopping", "local", "videos", "news",
    "images", "flights", "jobs", "scholar", "finance",
    "patents", "play", "lens",
)

# Engine capabilities metadata — used by auto-search to pick the best engine
ENGINE_CAPABILITIES = {
    "google":      {"web": True, "local": True, "shopping": True, "news": True, "video": True, "images": True, "academic": True, "jobs": True, "travel": True, "finance": True},
    "bing":        {"web": True, "local": True, "shopping": True, "news": True, "video": True, "images": True},
    "yahoo":       {"web": True, "news": True, "finance": True},
    "duckduckgo":  {"web": True, "privacy": True},
    "yandex":      {"web": True, "local": True, "images": True},
    "youtube":     {"video": True},
    "ebay":        {"shopping": True, "ecommerce": True},
    "walmart":     {"shopping": True, "ecommerce": True},
    "yelp":        {"local": True, "reviews": True},
}

# ============================================================================
# Layer 2: Vertical Scene Definitions
# ============================================================================

SCENES = {
    "shopping": {
        "description": "Cross-platform price comparison",
        "engines": [
            {"engine": "google", "google_type": "shopping"},
            {"engine": "ebay"},
            {"engine": "walmart"},
        ],
        "merge_strategy": "price_compare",
    },
    "local": {
        "description": "Local business discovery with reviews",
        "engines": [
            {"engine": "google", "google_type": "local"},
            {"engine": "yelp"},
        ],
        "merge_strategy": "rating_merge",
    },
    "jobs": {
        "description": "Job search across platforms",
        "engines": [
            {"engine": "google", "google_type": "jobs"},
        ],
        "merge_strategy": "jobs_format",
    },
    "academic": {
        "description": "Academic paper and research search",
        "engines": [
            {"engine": "google", "google_type": "scholar"},
        ],
        "merge_strategy": "academic_format",
    },
    "video": {
        "description": "Video content across platforms",
        "engines": [
            {"engine": "youtube"},
            {"engine": "google", "google_type": "videos"},
        ],
        "merge_strategy": "video_merge",
    },
    "news": {
        "description": "Latest news from multiple sources",
        "engines": [
            {"engine": "google", "google_type": "news"},
            {"engine": "bing"},
        ],
        "merge_strategy": "recency_merge",
    },
    "travel": {
        "description": "Flights and travel planning",
        "engines": [
            {"engine": "google", "google_type": "flights"},
        ],
        "merge_strategy": "travel_format",
    },
    "images": {
        "description": "Image search across engines",
        "engines": [
            {"engine": "google", "google_type": "images"},
        ],
        "merge_strategy": "image_format",
    },
    "finance": {
        "description": "Financial data and stock info",
        "engines": [
            {"engine": "google", "google_type": "finance"},
            {"engine": "yahoo"},
        ],
        "merge_strategy": "finance_format",
    },
}

# ============================================================================
# Layer 3: Auto-Search Intent Detection
# ============================================================================

INTENT_KEYWORDS = {
    "shopping": ["buy", "price", "cheap", "deal", "discount", "cost", "purchase", "order", "shop", "store", "amazon", "ebay", "walmart", "aliexpress", "coupon", "sale", "offer", "compare price", "how much", "where to buy", "kaufen", "preis", "günstig", "bestellen"],
    "local":    ["near me", "nearby", "restaurant", "cafe", "café", "coffee", "bar", "hotel", "gym", "hospital", "dentist", "pharmacy", "gas station", "in der nähe", "restaurant", "kaffee"],
    "jobs":     ["job", "career", "hiring", "salary", "remote work", "position", "vacancy", "internship", "developer job", "engineer job", "arbeitsplatz", "stelle", "gehalt"],
    "academic": ["paper", "research", "study", "journal", "citation", "arxiv", "thesis", "dissertation", "peer review", "forschung", "studie"],
    "video":    ["video", "tutorial", "watch", "youtube", "how to", "demo", "walkthrough", "review video", "unboxing"],
    "news":     ["news", "latest", "breaking", "today", "update", "announcement", "headline", "nachrichten", "aktuell"],
    "travel":   ["flight", "fly", "airline", "airport", "travel", "booking", "ticket", "flug", "reise"],
    "images":   ["image", "photo", "picture", "wallpaper", "logo", "icon", "infographic", "bild", "foto"],
    "finance":  ["stock", "share price", "market cap", "trading", "invest", "dividend", "nasdaq", "aktie", "börse"],
}


def detect_intent(query: str) -> Optional[str]:
    """Detect search intent from query text to auto-select the best scene."""
    query_lower = query.lower()
    scores = {}
    for scene, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[scene] = score
    if scores:
        return max(scores, key=scores.get)
    return None


# ============================================================================
# Company Database
# ============================================================================

COMPANY_DB = {
    "Bright Data":  {"url": "https://brightdata.com",       "category": "Enterprise Proxy + Scraping",  "description": "World's largest proxy network",              "pricing": "Enterprise"},
    "Oxylabs":      {"url": "https://oxylabs.io",           "category": "Enterprise Proxy + Scraping",  "description": "Premium residential & ISP proxies",          "pricing": "Mid-Enterprise"},
    "Zyte":         {"url": "https://zyte.com",             "category": "Developer-focused API",        "description": "Smart proxy + Scrapy Cloud",                 "pricing": "Pay-as-you-go"},
    "ScrapingBee":  {"url": "https://www.scrapingbee.com",  "category": "Developer API",                "description": "Easy-to-use proxy API",                      "pricing": "Mid-range"},
    "Apify":        {"url": "https://apify.com",            "category": "Docker + Marketplace",         "description": "Custom scrapers in Docker",                  "pricing": "Freemium"},
    "Smartproxy":   {"url": "https://smartproxy.com",       "category": "Proxy Provider",               "description": "Cost-effective proxies",                     "pricing": "Budget-friendly"},
    "ScrapingAnt":  {"url": "https://scrapingant.com",      "category": "Lightweight API",              "description": "Simple proxy solution",                      "pricing": "Low-cost"},
    "ParseHub":     {"url": "https://parsehub.com",         "category": "No-code Tool",                 "description": "Point-and-click scraping",                   "pricing": "Free tier available"},
    "Diffbot":      {"url": "https://diffbot.com",          "category": "AI Data Extraction",           "description": "Structured data from web",                   "pricing": "Enterprise"},
    "NetNut":       {"url": "https://netnut.io",            "category": "Static Residential",           "description": "ISP proxy solutions",                        "pricing": "Enterprise"},
    "IPRoyal":      {"url": "https://iproyal.com",          "category": "Proxy Provider",               "description": "Transparent pricing",                        "pricing": "Budget-friendly"},
    "SOAX":         {"url": "https://soax.com",             "category": "Rotating Proxies",             "description": "Mobile & residential",                       "pricing": "Mid-range"},
    "Novada":       {"url": "https://novada.com",           "category": "Scraper API Platform",         "description": "Multi-engine web scraper with structured results", "pricing": "Developer-friendly"},
}


def match_companies_in_text(text: str) -> List[Tuple[str, Dict]]:
    """Find known companies in text."""
    found = []
    text_lower = text.lower()
    seen = set()
    for name, info in COMPANY_DB.items():
        patterns = [name.lower(), name.lower().replace(' ', ''), name.lower().replace(' ', '-')]
        if any(p in text_lower for p in patterns) and name not in seen:
            seen.add(name)
            found.append((name, info))
    return found


# ============================================================================
# API Key Loading
# ============================================================================

def load_key() -> Optional[str]:
    """Load NOVADA_API_KEY from env or ~/.openclaw/.env."""
    key = os.environ.get("NOVADA_API_KEY")
    if key:
        return key.strip()

    for env_dir in [".openclaw", ".claude"]:
        env_path = pathlib.Path.home() / env_dir / ".env"
        if env_path.exists():
            try:
                txt = env_path.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r'^\s*NOVADA_API_KEY\s*=\s*(.+?)\s*$', txt, re.M)
                if m:
                    v = m.group(1).strip().strip('"').strip("'")
                    if v:
                        return v
            except Exception:
                pass
    return None


# ============================================================================
# API Call — supports all engines + Google sub-types
# ============================================================================

def novada_search(query: str, engine: str, google_type: str = None,
                  max_results: int = 10, fetch_mode: str = "static") -> dict:
    """Call Novada search endpoint. Supports all 9 engines + Google sub-types."""
    key = load_key()
    if not key:
        raise SystemExit(
            "Missing NOVADA_API_KEY. Set env var or add to ~/.openclaw/.env or ~/.claude/.env"
        )

    params = {
        "engine": engine,
        "q": query,
        "api_key": key,
        "fetch_mode": fetch_mode,
    }

    # Add Google sub-type if applicable
    if engine == "google" and google_type and google_type != "search":
        params["google_type"] = google_type

    url = NOVADA_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "NovadaSearch/2.0"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        raise SystemExit(f"Novada API error (HTTP {e.code}): {body[:500]}")
    except Exception as e:
        raise SystemExit(f"Novada API request failed: {e}")

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise SystemExit(f"Novada returned non-JSON: {body[:500]}")


def novada_extract(url_to_extract: str, fetch_mode: str = "dynamic") -> dict:
    """Extract clean content from a URL using Novada API (Layer 3: Extract mode)."""
    key = load_key()
    if not key:
        raise SystemExit("Missing NOVADA_API_KEY.")

    params = {
        "engine": "google",
        "q": "",
        "url": url_to_extract,
        "api_key": key,
        "fetch_mode": fetch_mode,
        "extract_mode": "content",
    }

    url = NOVADA_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "NovadaSearch/2.0"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise SystemExit(f"Extract failed: {e}")

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"raw_content": body[:10000]}


# ============================================================================
# Multi-Engine Search (Layer 3)
# ============================================================================

def multi_engine_search(query: str, engines: List[Dict], max_results: int = 10,
                        fetch_mode: str = "static") -> List[Dict]:
    """
    Search across multiple engines concurrently and merge results.
    Each engine entry: {"engine": "google", "google_type": "shopping"} (google_type optional)
    """
    all_results = []

    def _search_one(eng_config):
        engine = eng_config["engine"]
        gtype = eng_config.get("google_type")
        try:
            raw = novada_search(query, engine, google_type=gtype,
                                max_results=max_results, fetch_mode=fetch_mode)
            data = raw.get("data") if isinstance(raw.get("data"), dict) else raw
            return {
                "engine": engine,
                "google_type": gtype,
                "raw": raw,
                "data": data,
                "local_results": parse_local_results(data.get("local_results", [])),
                "organic_results": extract_organic_results(data, max_results),
                "shopping_results": extract_shopping_results(data),
                "video_results": extract_video_results(data),
                "news_results": extract_news_results(data),
                "jobs_results": extract_jobs_results(data),
            }
        except SystemExit as e:
            return {"engine": engine, "google_type": gtype, "error": str(e),
                    "raw": {}, "data": {}, "local_results": [], "organic_results": [],
                    "shopping_results": [], "video_results": [], "news_results": [],
                    "jobs_results": []}

    with ThreadPoolExecutor(max_workers=min(len(engines), 5)) as pool:
        futures = {pool.submit(_search_one, eng): eng for eng in engines}
        for future in as_completed(futures):
            all_results.append(future.result())

    return all_results


def deduplicate_results(results: List[Dict], key_field: str = "url") -> List[Dict]:
    """Remove duplicate results based on URL similarity."""
    seen_urls = set()
    unique = []
    for r in results:
        url = r.get(key_field, "").strip().rstrip("/").lower()
        # Normalize URL for dedup
        url_clean = re.sub(r'[?#].*$', '', url)
        if url_clean and url_clean not in seen_urls:
            seen_urls.add(url_clean)
            unique.append(r)
    return unique


# ============================================================================
# URL Builders
# ============================================================================

def build_google_maps_url(name: str, address: str) -> str:
    search = f"{name} {address}".strip()
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(search)}"

def build_website_search_url(name: str) -> str:
    return f"https://www.google.com/search?q={urllib.parse.quote(name + ' official website')}"

def build_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""

def build_ebay_item_url(item_id: str) -> str:
    return f"https://www.ebay.com/itm/{item_id}" if item_id else ""


# ============================================================================
# Data Extraction — Local Results (Google Maps / Yelp)
# ============================================================================

def extract_rating_from_label(label: str) -> Tuple[Optional[float], Optional[int]]:
    if not label:
        return None, None
    match = re.search(r'(\d+\.?\d*)\(([^)]+)\)', label)
    if match:
        rating = float(match.group(1))
        count_str = match.group(2)
        if 'K' in count_str:
            count = int(float(count_str.replace('K', '')) * 1000)
        elif 'M' in count_str:
            count = int(float(count_str.replace('M', '')) * 1000000)
        else:
            try:
                count = int(count_str)
            except ValueError:
                count = None
        return rating, count
    return None, None

def extract_price_from_label(label: str) -> Optional[str]:
    if not label:
        return None
    match = re.search(r'([€$£¥]\d+[\s\-–]+\d+)', label)
    if match:
        return match.group(1).replace('–', '-').replace(' ', '')
    return None

def extract_business_type_from_label(label: str) -> str:
    if not label:
        return "Business"
    parts = [p.strip() for p in label.split('·')]
    for part in reversed(parts):
        if part and not any(c in part for c in '€$£¥()0123456789'):
            return part
    return "Business"


def parse_local_results(local_data: List[Dict]) -> List[Dict]:
    """Parse Google Maps / Yelp local results."""
    businesses = []
    for item in local_data:
        label = item.get("label", "")
        business = {
            "name": item.get("title", "Unknown"),
            "address": item.get("address", ""),
            "rating": None, "review_count": 0,
            "price_range": None, "business_type": "",
            "score": 0.0,
            "maps_url": "", "website_search_url": "",
            "source": item.get("origin_site", "google"),
        }
        if label:
            rating, count = extract_rating_from_label(label)
            business["rating"] = rating
            business["review_count"] = count
            business["price_range"] = extract_price_from_label(label)
            business["business_type"] = extract_business_type_from_label(label)
            if rating and count:
                business["score"] = round(rating * math.log(count + 1), 2)
            elif rating:
                business["score"] = rating
        business["maps_url"] = build_google_maps_url(business["name"], business["address"])
        business["website_search_url"] = build_website_search_url(business["name"])
        businesses.append(business)
    businesses.sort(key=lambda x: x["score"], reverse=True)
    return businesses


# ============================================================================
# Data Extraction — Shopping Results (eBay, Walmart, Google Shopping)
# ============================================================================

def extract_shopping_results(data: dict) -> List[Dict]:
    """Extract shopping/product results from any engine."""
    results = []
    # Try various keys that different engines may use
    candidates = (
        data.get("shopping_results") or data.get("product_results") or
        data.get("products") or data.get("inline_shopping") or []
    )
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", item.get("name", "")),
            "price": item.get("price", item.get("extracted_price", "")),
            "currency": item.get("currency", ""),
            "url": item.get("url", item.get("link", item.get("product_link", ""))),
            "image": item.get("thumbnail", item.get("image", "")),
            "seller": item.get("source", item.get("seller", item.get("merchant", ""))),
            "rating": item.get("rating"),
            "reviews": item.get("reviews", item.get("review_count")),
            "condition": item.get("condition", ""),
        })
    return results


# ============================================================================
# Data Extraction — Video Results (YouTube, Google Videos)
# ============================================================================

def extract_video_results(data: dict) -> List[Dict]:
    """Extract video results."""
    results = []
    candidates = data.get("video_results") or data.get("videos") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", item.get("link", "")),
            "duration": item.get("duration", item.get("length", "")),
            "views": item.get("views", ""),
            "channel": item.get("channel", item.get("author", item.get("source", ""))),
            "published": item.get("date", item.get("published_date", "")),
            "thumbnail": item.get("thumbnail", item.get("image", "")),
            "platform": item.get("platform", item.get("origin_site", "")),
        })
    return results


# ============================================================================
# Data Extraction — News Results
# ============================================================================

def extract_news_results(data: dict) -> List[Dict]:
    """Extract news results."""
    results = []
    candidates = data.get("news_results") or data.get("top_stories") or data.get("news") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", item.get("link", "")),
            "source": item.get("source", item.get("origin_site", "")),
            "date": item.get("date", item.get("published_date", "")),
            "snippet": item.get("snippet", item.get("description", "")),
            "thumbnail": item.get("thumbnail", item.get("image", "")),
        })
    return results


# ============================================================================
# Data Extraction — Jobs Results
# ============================================================================

def extract_jobs_results(data: dict) -> List[Dict]:
    """Extract job listing results."""
    results = []
    candidates = data.get("jobs_results") or data.get("jobs") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", ""),
            "company": item.get("company_name", item.get("company", "")),
            "location": item.get("location", ""),
            "url": item.get("url", item.get("link", item.get("apply_link", ""))),
            "salary": item.get("salary", ""),
            "date": item.get("date", item.get("posted_at", "")),
            "description": item.get("description", item.get("snippet", ""))[:300],
            "source": item.get("via", item.get("source", "")),
        })
    return results


# ============================================================================
# Data Extraction — Organic Results
# ============================================================================

def extract_organic_results(raw: dict, max_results: int) -> List[Dict]:
    """Extract web search results."""
    results = []
    candidates = raw.get("organic_results") or []
    if not candidates:
        candidates = raw.get("results") or []
    if not candidates:
        candidates = raw.get("search_results") or []
    if not candidates and isinstance(raw.get("data"), dict):
        candidates = raw["data"].get("organic_results") or raw["data"].get("results") or []
    if not candidates and isinstance(raw, list):
        candidates = raw

    for item in candidates[:max_results]:
        if not isinstance(item, dict):
            continue
        url = (item.get("url") or item.get("link") or item.get("href") or "").strip()
        if not url:
            continue
        results.append({
            "title": (item.get("title") or item.get("name") or "(no title)").strip(),
            "url": url,
            "snippet": (item.get("snippet") or item.get("description") or item.get("text") or "").strip(),
            "source": item.get("origin_site", item.get("displayed_link", ""))
        })
    return results


# ============================================================================
# Analysis & Recommendation
# ============================================================================

def analyze_businesses(businesses: List[Dict], max_recommendations: int = 5) -> Dict:
    if not businesses:
        return {"total_found": 0, "top_recommendations": [], "highest_rated": None,
                "most_reviewed": None, "average_rating": 0}
    top = businesses[:max_recommendations]
    ratings = [b["rating"] for b in businesses if b["rating"]]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
    return {
        "total_found": len(businesses),
        "top_recommendations": top,
        "highest_rated": max(businesses, key=lambda x: x["rating"] or 0),
        "most_reviewed": max(businesses, key=lambda x: x["review_count"] or 0),
        "average_rating": avg_rating,
    }


# ============================================================================
# Output Formatters — Agent-Friendly JSON (Tavily-compatible)
# ============================================================================

def to_agent_json(query: str, all_engine_results: List[Dict], scene: str = None) -> dict:
    """
    AI Agent optimized JSON output — designed to be consumed directly by LLMs.
    This is our answer to Tavily's search API format.
    """
    # Merge all results across engines
    all_organic = []
    all_local = []
    all_shopping = []
    all_video = []
    all_news = []
    all_jobs = []

    engines_used = []
    errors = []

    for er in all_engine_results:
        engine_label = er["engine"]
        if er.get("google_type"):
            engine_label += f":{er['google_type']}"
        engines_used.append(engine_label)

        if er.get("error"):
            errors.append({"engine": engine_label, "error": er["error"]})
            continue

        all_organic.extend(er.get("organic_results", []))
        all_local.extend(er.get("local_results", []))
        all_shopping.extend(er.get("shopping_results", []))
        all_video.extend(er.get("video_results", []))
        all_news.extend(er.get("news_results", []))
        all_jobs.extend(er.get("jobs_results", []))

    # Deduplicate
    all_organic = deduplicate_results(all_organic, "url")

    output = {
        "query": query,
        "scene": scene,
        "engines_used": engines_used,
        "result_counts": {
            "organic": len(all_organic),
            "local": len(all_local),
            "shopping": len(all_shopping),
            "video": len(all_video),
            "news": len(all_news),
            "jobs": len(all_jobs),
        },
    }

    # Include non-empty result sets
    if all_organic:
        output["organic_results"] = all_organic[:10]
    if all_local:
        analysis = analyze_businesses(all_local)
        output["local_results"] = {
            "businesses": all_local[:10],
            "average_rating": analysis["average_rating"],
            "highest_rated": analysis.get("highest_rated"),
        }
    if all_shopping:
        output["shopping_results"] = all_shopping[:10]
    if all_video:
        output["video_results"] = all_video[:10]
    if all_news:
        output["news_results"] = all_news[:10]
    if all_jobs:
        output["jobs_results"] = all_jobs[:10]

    if errors:
        output["errors"] = errors

    return output


# ============================================================================
# Output Formatters — Human-Readable
# ============================================================================

def to_ranked_markdown(query: str, all_engine_results: List[Dict], scene: str = None) -> str:
    """Readable ranked output, multi-engine aware."""
    all_organic = []
    all_local = []
    all_shopping = []
    all_video = []
    all_news = []
    all_jobs = []

    for er in all_engine_results:
        if er.get("error"):
            continue
        all_organic.extend(er.get("organic_results", []))
        all_local.extend(er.get("local_results", []))
        all_shopping.extend(er.get("shopping_results", []))
        all_video.extend(er.get("video_results", []))
        all_news.extend(er.get("news_results", []))
        all_jobs.extend(er.get("jobs_results", []))

    all_organic = deduplicate_results(all_organic, "url")
    analysis = analyze_businesses(all_local)

    # Detect companies
    all_text = query + " " + " ".join([o.get('title', '') + ' ' + o.get('snippet', '') for o in all_organic])
    companies_found = match_companies_in_text(all_text)

    scene_label = f" [{scene}]" if scene else ""
    engines_str = ", ".join(set(er["engine"] for er in all_engine_results if not er.get("error")))

    lines = [
        f"# Search Results: '{query}'{scene_label}",
        f"Engines: {engines_str}",
        "",
    ]

    # Company detection
    if companies_found:
        lines.append("## Detected Companies")
        lines.append("")
        for name, info in companies_found[:5]:
            lines.append(f"**{name}** — [{info['url']}]({info['url']})")
            lines.append(f"  {info['category']} · {info['description']} · {info['pricing']}")
            lines.append("")

    # Local businesses
    if all_local:
        lines.append(f"## Local Businesses ({analysis['total_found']} found, avg {analysis['average_rating']}/5)")
        lines.append("")
        for i, biz in enumerate(analysis["top_recommendations"][:5], 1):
            price_str = f" · {biz['price_range']}" if biz.get('price_range') else ""
            type_str = f" · {biz['business_type']}" if biz.get('business_type') else ""
            lines.append(f"### {i}. {biz['name']}")
            lines.append(f"  {biz['rating']}/5 ({biz['review_count']} reviews){price_str}{type_str}")
            lines.append(f"  {biz['address']}")
            lines.append(f"  [Maps]({biz.get('maps_url', '#')}) · [Website]({biz.get('website_search_url', '#')})")
            lines.append("")

    # Shopping results
    if all_shopping:
        lines.append("## Shopping Results")
        lines.append("")
        lines.append("| # | Product | Price | Seller | Rating |")
        lines.append("|---|---------|-------|--------|--------|")
        for i, item in enumerate(all_shopping[:10], 1):
            name = (item.get('title') or '')[:40]
            price = item.get('price', 'N/A')
            seller = (item.get('seller') or '')[:15]
            rating = f"{item['rating']}*" if item.get('rating') else '-'
            lines.append(f"| {i} | {name} | {price} | {seller} | {rating} |")
        lines.append("")

    # Video results
    if all_video:
        lines.append("## Video Results")
        lines.append("")
        for i, v in enumerate(all_video[:5], 1):
            dur = f" ({v['duration']})" if v.get('duration') else ""
            chan = f" — {v['channel']}" if v.get('channel') else ""
            lines.append(f"{i}. [{v['title']}]({v.get('url', '#')}){dur}{chan}")
        lines.append("")

    # News results
    if all_news:
        lines.append("## News")
        lines.append("")
        for i, n in enumerate(all_news[:5], 1):
            src = f" [{n['source']}]" if n.get('source') else ""
            dt = f" · {n['date']}" if n.get('date') else ""
            lines.append(f"{i}. [{n['title']}]({n.get('url', '#')}){src}{dt}")
        lines.append("")

    # Jobs results
    if all_jobs:
        lines.append("## Job Listings")
        lines.append("")
        for i, j in enumerate(all_jobs[:5], 1):
            company = f" at {j['company']}" if j.get('company') else ""
            loc = f" ({j['location']})" if j.get('location') else ""
            sal = f" · {j['salary']}" if j.get('salary') else ""
            lines.append(f"{i}. **{j['title']}**{company}{loc}{sal}")
            if j.get('url'):
                lines.append(f"   [Apply]({j['url']})")
        lines.append("")

    # Organic results
    if all_organic:
        lines.append("## Web Results")
        lines.append("")
        for i, item in enumerate(all_organic[:5], 1):
            lines.append(f"{i}. [{item['title']}]({item['url']})")
            if item.get('snippet'):
                lines.append(f"   {item['snippet'][:150]}")
        lines.append("")

    return "\n".join(lines)


def to_enhanced_markdown(query: str, all_engine_results: List[Dict], scene: str = None) -> str:
    """Enhanced markdown with clickable action links."""
    all_local = []
    all_organic = []
    for er in all_engine_results:
        if not er.get("error"):
            all_local.extend(er.get("local_results", []))
            all_organic.extend(er.get("organic_results", []))
    all_organic = deduplicate_results(all_organic, "url")
    analysis = analyze_businesses(all_local)

    lines = [
        f"# Actionable Results: '{query}'",
        "",
        f"**Found {analysis['total_found']} businesses with direct links**",
        "",
        "## Top Ranked (Click to open)",
        "",
    ]
    for i, biz in enumerate(analysis["top_recommendations"][:5], 1):
        price_str = f" · {biz['price_range']}" if biz.get('price_range') else ""
        type_str = f" · {biz['business_type']}" if biz.get('business_type') else ""
        lines.append(f"### {i}. {biz['name']}")
        lines.append(f"  {biz['rating']}/5 ({biz['review_count']} reviews){price_str}{type_str}")
        lines.append("")
        lines.append("**Quick Actions:**")
        lines.append(f"- [Open in Google Maps]({biz.get('maps_url', '#')})")
        lines.append(f"- [Search for website]({biz.get('website_search_url', '#')})")
        if biz.get('address'):
            lines.append(f"- Address: {biz['address']}")
        lines.append("")

    if all_organic:
        lines.append("---")
        lines.append("## Direct Links to Sources")
        lines.append("")
        for item in all_organic[:5]:
            lines.append(f"[{item['title']}]({item['url']})")
            if item.get('snippet'):
                lines.append(f"  {item['snippet'][:120]}")
            lines.append("")

    return "\n".join(lines)


def to_comparison_table(all_engine_results: List[Dict]) -> str:
    """Markdown table for side-by-side comparison."""
    all_local = []
    all_shopping = []
    for er in all_engine_results:
        if not er.get("error"):
            all_local.extend(er.get("local_results", []))
            all_shopping.extend(er.get("shopping_results", []))

    lines = []

    if all_local:
        lines.append("## Local Businesses")
        lines.append("")
        lines.append("| # | Name | Rating | Reviews | Price | Type |")
        lines.append("|---|------|--------|---------|-------|------|")
        for i, biz in enumerate(all_local[:10], 1):
            name = biz['name'][:25]
            rating = f"{biz['rating']}*" if biz['rating'] else "N/A"
            reviews = str(biz['review_count']) if biz['review_count'] else "N/A"
            price = biz.get('price_range') or "?"
            btype = biz.get('business_type', '?')[:12]
            lines.append(f"| {i} | {name} | {rating} | {reviews} | {price} | {btype} |")
        lines.append("")

    if all_shopping:
        lines.append("## Products")
        lines.append("")
        lines.append("| # | Product | Price | Seller | Rating |")
        lines.append("|---|---------|-------|--------|--------|")
        for i, item in enumerate(all_shopping[:10], 1):
            name = (item.get('title') or '')[:35]
            price = item.get('price', 'N/A')
            seller = (item.get('seller') or '')[:15]
            rating = f"{item['rating']}*" if item.get('rating') else '-'
            lines.append(f"| {i} | {name} | {price} | {seller} | {rating} |")
        lines.append("")

    if not lines:
        lines.append("No structured results found for table view.")

    return "\n".join(lines)


def to_action_links(query: str, all_engine_results: List[Dict]) -> str:
    """Shell commands to open results directly."""
    all_local = []
    all_organic = []
    for er in all_engine_results:
        if not er.get("error"):
            all_local.extend(er.get("local_results", []))
            all_organic.extend(er.get("organic_results", []))
    analysis = analyze_businesses(all_local)

    lines = [f"# Action Commands for: '{query}'", "", "Copy and run any command:", ""]
    if analysis.get("top_recommendations"):
        lines.append("## Local Businesses")
        lines.append("")
        for biz in analysis["top_recommendations"][:5]:
            lines.append(f"# {biz['name']}")
            lines.append(f"open \"{biz.get('maps_url', '')}\"")
            lines.append("")
    if all_organic:
        lines.append("## Web Sources")
        lines.append("")
        for item in all_organic[:5]:
            lines.append(f"# {item['title'][:50]}")
            lines.append(f"open \"{item['url']}\"")
            lines.append("")
    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Novada Search v2.0 — AI Agent Search Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
LAYER 1 — Direct engine search:
  %(prog)s --query "coffee Berlin" --engine google
  %(prog)s --query "iPhone 16" --engine ebay
  %(prog)s --query "ML tutorial" --engine youtube
  %(prog)s --query "python jobs" --engine google --google-type jobs
  %(prog)s --query "transformer paper" --engine google --google-type scholar

LAYER 2 — Vertical scenes (auto-selects best engines):
  %(prog)s --query "MacBook Pro" --scene shopping
  %(prog)s --query "ramen Tokyo" --scene local
  %(prog)s --query "react tutorial" --scene video
  %(prog)s --query "AI latest" --scene news
  %(prog)s --query "python developer Berlin" --scene jobs

LAYER 3 — AI Agent modes:
  %(prog)s --query "buy Nike shoes" --mode auto
  %(prog)s --query "coffee Berlin" --mode multi --engines google,yelp
  %(prog)s --url "https://example.com/article" --mode extract

Formats: ranked, enhanced, table, action-links, agent-json, brave, raw
        """
    )

    ap.add_argument("--query", help="Search query")
    ap.add_argument("--url", help="URL to extract content from (extract mode)")
    ap.add_argument(
        "--engine", default="google", choices=SUPPORTED_ENGINES,
        help="Search engine (default: google)",
    )
    ap.add_argument(
        "--google-type", default=None, choices=GOOGLE_TYPES,
        help="Google sub-type: shopping, news, scholar, jobs, videos, etc.",
    )
    ap.add_argument(
        "--scene", default=None, choices=list(SCENES.keys()),
        help="Vertical scene: shopping, local, jobs, academic, video, news, travel, images, finance",
    )
    ap.add_argument(
        "--mode", default=None, choices=["auto", "multi", "extract"],
        help="AI Agent mode: auto (smart engine selection), multi (parallel multi-engine), extract (URL content)",
    )
    ap.add_argument(
        "--engines", default=None,
        help="Comma-separated engines for multi mode (e.g., google,bing,yelp)",
    )
    ap.add_argument("--max-results", type=int, default=10, help="Max results (1-20)")
    ap.add_argument(
        "--fetch-mode", default="static", choices=["static", "dynamic"],
        help="static (fast) or dynamic (JS pages)",
    )
    ap.add_argument(
        "--format", default="enhanced",
        choices=["raw", "brave", "agent-json", "ranked", "table", "md", "enhanced", "action-links"],
        help="Output format (default: enhanced)",
    )
    args = ap.parse_args()

    max_results = max(1, min(args.max_results, 20))

    # ---- Mode: Extract ----
    if args.mode == "extract" or (args.url and not args.query):
        if not args.url:
            raise SystemExit("Extract mode requires --url")
        result = novada_extract(args.url, fetch_mode=args.fetch_mode)
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    if not args.query:
        raise SystemExit("--query is required (unless using --mode extract with --url)")

    # ---- Determine which engines to search ----
    engines_to_search = []
    scene = args.scene

    if args.mode == "auto":
        # Layer 3: Auto-detect intent and pick scene
        detected = detect_intent(args.query)
        if detected and detected in SCENES:
            scene = detected
            engines_to_search = SCENES[scene]["engines"]
        else:
            # Default: Google web search
            engines_to_search = [{"engine": "google"}]

    elif args.mode == "multi":
        # Layer 3: Multi-engine parallel search
        if args.engines:
            for eng in args.engines.split(","):
                eng = eng.strip()
                if ":" in eng:
                    engine, gtype = eng.split(":", 1)
                    engines_to_search.append({"engine": engine, "google_type": gtype})
                elif eng in SUPPORTED_ENGINES:
                    engines_to_search.append({"engine": eng})
        if not engines_to_search:
            engines_to_search = [{"engine": "google"}, {"engine": "bing"}, {"engine": "duckduckgo"}]

    elif scene:
        # Layer 2: Use scene's predefined engines
        engines_to_search = SCENES[scene]["engines"]

    else:
        # Layer 1: Direct single-engine search
        eng_config = {"engine": args.engine}
        if args.google_type:
            eng_config["google_type"] = args.google_type
        engines_to_search = [eng_config]

    # ---- Execute search ----
    all_engine_results = multi_engine_search(
        args.query, engines_to_search,
        max_results=max_results, fetch_mode=args.fetch_mode
    )

    # ---- Output ----
    if args.format == "raw":
        raw_output = {"engines": []}
        for er in all_engine_results:
            raw_output["engines"].append({
                "engine": er["engine"],
                "google_type": er.get("google_type"),
                "data": er.get("raw", {}),
            })
        json.dump(raw_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    elif args.format in ["brave", "agent-json"]:
        json.dump(
            to_agent_json(args.query, all_engine_results, scene=scene),
            sys.stdout, ensure_ascii=False, indent=2
        )
        sys.stdout.write("\n")

    elif args.format == "enhanced":
        sys.stdout.write(to_enhanced_markdown(args.query, all_engine_results, scene=scene))

    elif args.format == "action-links":
        sys.stdout.write(to_action_links(args.query, all_engine_results))

    elif args.format in ["ranked", "md"]:
        sys.stdout.write(to_ranked_markdown(args.query, all_engine_results, scene=scene))

    elif args.format == "table":
        sys.stdout.write(to_comparison_table(all_engine_results))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
