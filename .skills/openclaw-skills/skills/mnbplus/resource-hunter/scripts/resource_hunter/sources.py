from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree

from .common import (
    clean_share_url,
    compact_spaces,
    extract_password,
    extract_share_id,
    infer_provider_from_url,
    normalize_title,
    parse_quality_tags,
    quality_display_from_tags,
)
from .models import SearchIntent, SearchResult


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
}

TRACKERS = (
    "&tr=udp://tracker.openbittorrent.com:80"
    "&tr=udp://tracker.opentrackr.org:1337"
    "&tr=udp://open.demonii.com:1337"
    "&tr=udp://tracker.torrent.eu.org:451"
    "&tr=udp://tracker.cyberia.is:6969"
)


@dataclass(frozen=True)
class SourceRuntimeProfile:
    supported_kinds: tuple[str, ...]
    timeout: int
    retries: int
    degraded_score_penalty: int
    cooldown_seconds: int
    failure_threshold: int
    query_budget: int
    default_degraded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "supported_kinds": list(self.supported_kinds),
            "timeout": self.timeout,
            "retries": self.retries,
            "degraded_score_penalty": self.degraded_score_penalty,
            "cooldown_seconds": self.cooldown_seconds,
            "failure_threshold": self.failure_threshold,
            "query_budget": self.query_budget,
            "default_degraded": self.default_degraded,
        }


SOURCE_RUNTIME_PROFILES: dict[str, SourceRuntimeProfile] = {
    "2fun": SourceRuntimeProfile(
        supported_kinds=("movie", "tv", "anime", "music", "software", "book", "general"),
        timeout=10,
        retries=1,
        degraded_score_penalty=0,
        cooldown_seconds=180,
        failure_threshold=2,
        query_budget=3,
    ),
    "hunhepan": SourceRuntimeProfile(
        supported_kinds=("movie", "tv", "anime", "music", "software", "book", "general"),
        timeout=6,
        retries=0,
        degraded_score_penalty=18,
        cooldown_seconds=90,
        failure_threshold=1,
        query_budget=2,
        default_degraded=True,
    ),
    "pansou.vip": SourceRuntimeProfile(
        supported_kinds=("movie", "tv", "anime", "music", "software", "book", "general"),
        timeout=6,
        retries=0,
        degraded_score_penalty=20,
        cooldown_seconds=90,
        failure_threshold=1,
        query_budget=2,
        default_degraded=True,
    ),
    "nyaa": SourceRuntimeProfile(
        supported_kinds=("anime", "general"),
        timeout=8,
        retries=1,
        degraded_score_penalty=0,
        cooldown_seconds=180,
        failure_threshold=2,
        query_budget=3,
    ),
    "eztv": SourceRuntimeProfile(
        supported_kinds=("tv", "general"),
        timeout=10,
        retries=1,
        degraded_score_penalty=0,
        cooldown_seconds=180,
        failure_threshold=2,
        query_budget=3,
    ),
    "tpb": SourceRuntimeProfile(
        supported_kinds=("movie", "tv", "anime", "music", "software", "book", "general"),
        timeout=10,
        retries=1,
        degraded_score_penalty=0,
        cooldown_seconds=180,
        failure_threshold=2,
        query_budget=3,
    ),
    "yts": SourceRuntimeProfile(
        supported_kinds=("movie",),
        timeout=6,
        retries=0,
        degraded_score_penalty=16,
        cooldown_seconds=90,
        failure_threshold=1,
        query_budget=2,
        default_degraded=True,
    ),
    "1337x": SourceRuntimeProfile(
        supported_kinds=("movie", "tv", "anime", "software", "book", "general"),
        timeout=8,
        retries=0,
        degraded_score_penalty=4,
        cooldown_seconds=180,
        failure_threshold=2,
        query_budget=2,
    ),
}


def profile_for(source_name: str) -> SourceRuntimeProfile:
    return SOURCE_RUNTIME_PROFILES.get(
        source_name,
        SourceRuntimeProfile(
            supported_kinds=("general",),
            timeout=10,
            retries=1,
            degraded_score_penalty=0,
            cooldown_seconds=180,
            failure_threshold=2,
            query_budget=2,
        ),
    )


class HTTPClient:
    def __init__(self, retries: int = 1, default_timeout: int = 10) -> None:
        self.retries = retries
        self.default_timeout = default_timeout

    def _request(self, url: str, timeout: int | None = None) -> str:
        timeout = timeout or self.default_timeout
        last_error = ""
        for attempt in range(self.retries + 1):
            request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    charset = response.headers.get_content_charset() or "utf-8"
                    return response.read().decode(charset, errors="replace")
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}"
                if 400 <= exc.code < 500:
                    break
            except Exception as exc:  # pragma: no cover
                last_error = str(exc)
            if attempt < self.retries:
                time.sleep(0.2 * (attempt + 1))
        raise RuntimeError(last_error or "request failed")

    def get_text(self, url: str, timeout: int | None = None) -> str:
        return self._request(url, timeout=timeout)

    def get_json(self, url: str, timeout: int | None = None) -> dict[str, Any] | list[Any]:
        payload = self._request(url, timeout=timeout)
        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid json from {url}: {exc}") from exc


def _make_magnet(info_hash: str, name: str) -> str:
    return f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}{TRACKERS}"


def _clean_magnet(text: str) -> str:
    return html.unescape(text or "").strip()


def _format_size(size_bytes: int | str | None) -> str:
    if size_bytes in (None, "", 0, "0"):
        return ""
    try:
        numeric = float(size_bytes)
    except Exception:
        return str(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if numeric < 1024:
            return f"{numeric:.1f}{unit}"
        numeric /= 1024
    return f"{numeric:.1f}PB"


def _validate_pan_payload(payload: Any, source_name: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise RuntimeError(f"unexpected payload type from {source_name}")
    if "results" in payload and isinstance(payload["results"], list):
        return payload
    if "data" in payload and isinstance(payload["data"], (list, dict)):
        return payload
    raise RuntimeError(f"unexpected pan payload shape from {source_name}")


def _flatten_pan_payload(payload: dict[str, Any], source_name: str) -> list[SearchResult]:
    payload = _validate_pan_payload(payload, source_name)
    items: list[dict[str, Any]] = []
    if isinstance(payload.get("results"), list):
        items = payload["results"]
    elif isinstance(payload.get("data"), list):
        items = payload["data"]
    elif isinstance(payload.get("data"), dict):
        for provider, values in payload["data"].items():
            for value in values if isinstance(values, list) else []:
                entry = dict(value) if isinstance(value, dict) else {"url": value}
                entry.setdefault("cloud", provider)
                items.append(entry)

    results: list[SearchResult] = []
    for index, item in enumerate(items):
        raw_url = item.get("url") or item.get("link") or item.get("shareUrl") or ""
        cleaned_url = clean_share_url(raw_url)
        if not cleaned_url:
            continue
        provider = item.get("netdiskType") or item.get("cloud") or item.get("type") or infer_provider_from_url(cleaned_url)
        normalized_channel = "torrent" if (provider or "").lower() in {"magnet", "ed2k"} else "pan"
        title = normalize_title(item.get("title") or item.get("name") or "")
        password = item.get("pwd") or item.get("password") or extract_password(raw_url) or extract_password(title)
        quality_tags = parse_quality_tags(title)
        upstream_source = item.get("source") or source_name
        results.append(
            SearchResult(
                channel=normalized_channel,
                normalized_channel=normalized_channel,
                source=source_name,
                upstream_source=str(upstream_source),
                provider=(provider or infer_provider_from_url(cleaned_url)).lower(),
                title=title or cleaned_url,
                link_or_magnet=cleaned_url,
                password=password,
                share_id_or_info_hash=extract_share_id(cleaned_url, provider_hint=str(provider)),
                size=str(item.get("size") or ""),
                quality=quality_display_from_tags(quality_tags),
                quality_tags=quality_tags,
                raw={"index": index, **item},
            )
        )
    return results


class SourceAdapter:
    name = "base"
    channel = "both"
    priority = 9

    def search(
        self,
        query: str,
        intent: SearchIntent,
        limit: int,
        page: int,
        http_client: HTTPClient,
    ) -> list[SearchResult]:
        raise NotImplementedError

    def supports(self, intent: SearchIntent) -> bool:
        profile = profile_for(self.name)
        return intent.kind in profile.supported_kinds or "general" in profile.supported_kinds

    def capability_profile(self) -> dict[str, Any]:
        return profile_for(self.name).to_dict()

    def healthcheck(self, http_client: HTTPClient) -> tuple[bool, str]:
        probe_intent = SearchIntent(
            query="ubuntu",
            original_query="ubuntu",
            kind="general",
            channel=self.channel,
            title_core="ubuntu",
            title_tokens=["ubuntu"],
        )
        try:
            self.search("ubuntu", probe_intent, limit=1, page=1, http_client=http_client)
            return True, ""
        except Exception as exc:  # pragma: no cover
            return False, str(exc)


class TwoFunSource(SourceAdapter):
    name = "2fun"
    channel = "pan"
    priority = 1

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        url = "https://s.2fun.live/api/search?" + urllib.parse.urlencode(
            {"q": query, "page": page, "pageSize": max(limit * 3, 20)}
        )
        payload = http_client.get_json(url)
        assert isinstance(payload, dict)
        return _flatten_pan_payload(payload, self.name)


class HunhepanSource(SourceAdapter):
    name = "hunhepan"
    channel = "pan"
    priority = 2

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        url = "https://www.hunhepan.com/api/search?" + urllib.parse.urlencode({"q": query, "page": page})
        payload = http_client.get_json(url)
        assert isinstance(payload, dict)
        return _flatten_pan_payload(payload, self.name)


class PansouVipSource(SourceAdapter):
    name = "pansou.vip"
    channel = "pan"
    priority = 3

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        candidates = [
            "https://pansou.vip/api/search?" + urllib.parse.urlencode({"q": query, "page": page}),
            "https://pansou.vip/api/search?" + urllib.parse.urlencode({"keyword": query, "page": page}),
            "https://pansou.vip/api?" + urllib.parse.urlencode({"q": query, "page": page}),
        ]
        last_error = "no valid endpoint"
        for url in candidates:
            try:
                payload = http_client.get_json(url)
                if isinstance(payload, dict):
                    results = _flatten_pan_payload(payload, self.name)
                    if results:
                        return results
            except Exception as exc:  # pragma: no cover
                last_error = str(exc)
        raise RuntimeError(last_error)


class TPBSource(SourceAdapter):
    name = "tpb"
    channel = "torrent"
    priority = 2

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        url = f"https://apibay.org/q.php?q={urllib.parse.quote(query)}&cat=0"
        payload = http_client.get_json(url)
        if not isinstance(payload, list):
            return []
        results: list[SearchResult] = []
        for item in payload[: max(limit * 3, 12)]:
            name = normalize_title(item.get("name", ""))
            if not name or name == "No results returned":
                continue
            info_hash = (item.get("info_hash") or "").lower()
            quality_tags = parse_quality_tags(name)
            results.append(
                SearchResult(
                    channel="torrent",
                    normalized_channel="torrent",
                    source=self.name,
                    upstream_source=self.name,
                    provider="magnet",
                    title=name,
                    link_or_magnet=_make_magnet(info_hash, name),
                    share_id_or_info_hash=info_hash or hashlib.sha1(name.encode("utf-8")).hexdigest(),
                    size=_format_size(item.get("size", 0)),
                    seeders=int(item.get("seeders", 0)),
                    quality=quality_display_from_tags(quality_tags),
                    quality_tags=quality_tags,
                    raw=item,
                )
            )
        return results


class NyaaSource(SourceAdapter):
    name = "nyaa"
    channel = "torrent"
    priority = 1

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        category = "1_2" if intent.kind == "anime" else "0_0"
        url = f"https://nyaa.si/?f=0&c={category}&q={urllib.parse.quote(query)}&page=rss"
        payload = http_client.get_text(url)
        root = ElementTree.fromstring(payload)
        results: list[SearchResult] = []
        for item in root.findall("./channel/item")[: max(limit * 3, 12)]:
            title = normalize_title(item.findtext("title", ""))
            magnet = item.findtext("{https://nyaa.si/xmlns/nyaa}magnetUri", "")
            info_hash = extract_share_id(magnet, provider_hint="magnet")
            seeders = int(item.findtext("{https://nyaa.si/xmlns/nyaa}seeders", "0"))
            quality_tags = parse_quality_tags(title)
            results.append(
                SearchResult(
                    channel="torrent",
                    normalized_channel="torrent",
                    source=self.name,
                    upstream_source=self.name,
                    provider="magnet",
                    title=title,
                    link_or_magnet=_clean_magnet(magnet),
                    share_id_or_info_hash=info_hash,
                    size=item.findtext("{https://nyaa.si/xmlns/nyaa}size", ""),
                    seeders=seeders,
                    quality=quality_display_from_tags(quality_tags),
                    quality_tags=quality_tags,
                    raw={"title": title, "seeders": seeders},
                )
            )
        return results


class EZTVSource(SourceAdapter):
    name = "eztv"
    channel = "torrent"
    priority = 1

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        url = "https://eztv.re/api/get-torrents?" + urllib.parse.urlencode(
            {"imdb_id": 0, "limit": max(limit * 3, 20), "page": page, "keywords": query}
        )
        payload = http_client.get_json(url)
        if not isinstance(payload, dict):
            return []
        items = payload.get("torrents") or []
        results: list[SearchResult] = []
        for item in items[: max(limit * 3, 12)]:
            title = normalize_title(item.get("title", ""))
            magnet = item.get("magnet_url") or ""
            info_hash = (item.get("hash") or "").lower()
            if not magnet and info_hash:
                magnet = _make_magnet(info_hash, title)
            if not title or not magnet:
                continue
            quality_tags = parse_quality_tags(title)
            results.append(
                SearchResult(
                    channel="torrent",
                    normalized_channel="torrent",
                    source=self.name,
                    upstream_source=self.name,
                    provider="magnet",
                    title=title,
                    link_or_magnet=magnet,
                    share_id_or_info_hash=info_hash or extract_share_id(magnet, "magnet"),
                    size=_format_size(item.get("size_bytes", 0)),
                    seeders=int(item.get("seeds", 0)),
                    quality=quality_display_from_tags(quality_tags),
                    quality_tags=quality_tags,
                    raw=item,
                )
            )
        return results


class YTSSource(SourceAdapter):
    name = "yts"
    channel = "torrent"
    priority = 2

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        url = "https://yts.mx/api/v2/list_movies.json?" + urllib.parse.urlencode(
            {"query_term": query, "limit": max(limit * 3, 20), "sort_by": "seeds"}
        )
        payload = http_client.get_json(url)
        if not isinstance(payload, dict):
            return []
        movies = payload.get("data", {}).get("movies") or []
        results: list[SearchResult] = []
        for movie in movies[: max(limit * 2, 10)]:
            title = normalize_title(movie.get("title_long") or movie.get("title") or "")
            for torrent in movie.get("torrents", []):
                info_hash = (torrent.get("hash") or "").lower()
                full_title = compact_spaces(
                    f"{title} {torrent.get('quality', '')} {torrent.get('type', '')} {torrent.get('video_codec', '')}"
                )
                quality_tags = parse_quality_tags(full_title)
                results.append(
                    SearchResult(
                        channel="torrent",
                        normalized_channel="torrent",
                        source=self.name,
                        upstream_source=self.name,
                        provider="magnet",
                        title=full_title,
                        link_or_magnet=_make_magnet(info_hash, full_title),
                        share_id_or_info_hash=info_hash,
                        size=torrent.get("size", ""),
                        seeders=int(torrent.get("seeds", 0)),
                        quality=quality_display_from_tags(quality_tags),
                        quality_tags=quality_tags,
                        raw=torrent,
                    )
                )
        return results


class OneThreeThreeSevenXSource(SourceAdapter):
    name = "1337x"
    channel = "torrent"
    priority = 3

    SEARCH_ROW_RE = re.compile(
        r'<a href="(?P<detail>/torrent/[^"]+)"[^>]*>(?P<title>[^<]+)</a>.*?'
        r'class="coll-4[^"]*">(?P<size>.*?)</td>.*?'
        r'class="coll-2[^"]*">(?P<seeds>\d+)</td>.*?'
        r'class="coll-3[^"]*">(?P<leeches>\d+)</td>',
        re.S,
    )

    def search(self, query: str, intent: SearchIntent, limit: int, page: int, http_client: HTTPClient) -> list[SearchResult]:
        url = f"https://www.1377x.to/search/{urllib.parse.quote(query)}/{page}/"
        payload = http_client.get_text(url)
        results: list[SearchResult] = []
        for match in self.SEARCH_ROW_RE.finditer(payload):
            detail_path = html.unescape(match.group("detail"))
            detail_url = "https://www.1377x.to" + detail_path
            detail_payload = http_client.get_text(detail_url)
            magnet_match = re.search(r'href="(magnet:[^"]+)"', detail_payload)
            if not magnet_match:
                continue
            title = normalize_title(html.unescape(match.group("title")))
            magnet = _clean_magnet(magnet_match.group(1))
            info_hash = extract_share_id(magnet, provider_hint="magnet")
            quality_tags = parse_quality_tags(title)
            results.append(
                SearchResult(
                    channel="torrent",
                    normalized_channel="torrent",
                    source=self.name,
                    upstream_source=self.name,
                    provider="magnet",
                    title=title,
                    link_or_magnet=magnet,
                    share_id_or_info_hash=info_hash,
                    size=normalize_title(html.unescape(match.group("size"))),
                    seeders=int(match.group("seeds")),
                    quality=quality_display_from_tags(quality_tags),
                    quality_tags=quality_tags,
                    raw={"detail_url": detail_url},
                )
            )
            if len(results) >= max(limit * 2, 8):
                break
        return results


def default_adapters() -> tuple[list[SourceAdapter], list[SourceAdapter]]:
    return (
        [TwoFunSource(), HunhepanSource(), PansouVipSource()],
        [NyaaSource(), EZTVSource(), TPBSource(), YTSSource(), OneThreeThreeSevenXSource()],
    )


__all__ = [
    "HTTPClient",
    "SOURCE_RUNTIME_PROFILES",
    "SourceAdapter",
    "SourceRuntimeProfile",
    "TwoFunSource",
    "HunhepanSource",
    "PansouVipSource",
    "TPBSource",
    "NyaaSource",
    "EZTVSource",
    "YTSSource",
    "OneThreeThreeSevenXSource",
    "_flatten_pan_payload",
    "as_completed",
    "default_adapters",
    "profile_for",
    "ThreadPoolExecutor",
]
