from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlparse


VIDEO_URL_HINTS = (
    "http://",
    "https://",
    "www.",
    "youtu",
    "bilibili",
    "b23.tv",
    "tiktok",
    "douyin",
    "instagram",
    "twitter",
    "x.com",
    "weibo",
    "vimeo",
    "reddit",
)

ANIME_TERMS = (
    "\u52a8\u6f2b",
    "\u52a8\u753b",
    "\u756a\u5267",
    "\u65b0\u756a",
    "anime",
    "ova",
    "nyaa",
    "attack on titan",
    "one piece",
    "naruto",
    "demon slayer",
    "\u8fdb\u51fb",
    "\u5de8\u4eba",
    "\u6d77\u8d3c",
    "\u706b\u5f71",
)
TV_TERMS = (
    "season",
    "episode",
    "series",
    "\u7f8e\u5267",
    "\u82f1\u5267",
    "\u97e9\u5267",
    "\u65e5\u5267",
    "\u7b2c\u5b63",
    "\u7b2c\u96c6",
)
MUSIC_TERMS = (
    "\u97f3\u4e50",
    "\u4e13\u8f91",
    "\u5355\u66f2",
    "album",
    "single",
    "soundtrack",
    "ost",
    "flac",
    "mp3",
    "aac",
    "\u65e0\u635f",
)
SOFTWARE_TERMS = (
    "\u8f6f\u4ef6",
    "\u7a0b\u5e8f",
    "\u5de5\u5177",
    "\u5ba2\u6237\u7aef",
    "portable",
    "apk",
    "installer",
    ".exe",
    ".dmg",
    ".msi",
    "windows",
    "mac",
    "linux",
)
SOFTWARE_BRANDS = (
    "adobe",
    "photoshop",
    "illustrator",
    "premiere",
    "after effects",
    "windows",
    "office",
    "visual studio",
    "jetbrains",
    "pycharm",
    "intellij",
    "autocad",
)
BOOK_TERMS = (
    "epub",
    "pdf",
    "mobi",
    "azw3",
    "\u7535\u5b50\u4e66",
    "\u5c0f\u8bf4",
    "\u6f2b\u753b",
    "manga",
    "comic",
    "ebook",
)
SUBTITLE_TERMS = (
    "\u4e2d\u5b57",
    "\u5b57\u5e55",
    "subtitle",
    "subtitles",
    "subbed",
    "sub",
)
LOSSLESS_TERMS = ("flac", "\u65e0\u635f", "ape", "alac", "wav")

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "of",
    "to",
    "for",
    "in",
    "on",
    "with",
    "at",
}

DOMAIN_PROVIDER_MAP = {
    "aliyundrive.com": "aliyun",
    "alipan.com": "aliyun",
    "pan.quark.cn": "quark",
    "pan.baidu.com": "baidu",
    "115.com": "115",
    "115cdn.com": "115",
    "mypikpak.com": "pikpak",
    "pan.pikpak.com": "pikpak",
    "drive.uc.cn": "uc",
    "pan.xunlei.com": "xunlei",
    "123pan.com": "123",
    "123684.com": "123",
    "123865.com": "123",
    "123912.com": "123",
    "cloud.189.cn": "tianyi",
    "mega.nz": "mega",
    "mediafire.com": "mediafire",
    "drive.google.com": "gdrive",
    "onedrive.live.com": "onedrive",
    "cowtransfer.com": "cowtransfer",
    "lanzou": "lanzou",
    "lanzoux.com": "lanzou",
    "lanzouq.com": "lanzou",
}

PLATFORM_MAP = {
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "bilibili.com": "Bilibili",
    "b23.tv": "Bilibili",
    "tiktok.com": "TikTok",
    "douyin.com": "Douyin",
    "instagram.com": "Instagram",
    "twitter.com": "Twitter/X",
    "x.com": "Twitter/X",
    "weibo.com": "Weibo",
    "v.qq.com": "Tencent Video",
    "iqiyi.com": "iQIYI",
    "youku.com": "Youku",
    "acfun.cn": "AcFun",
    "nicovideo.jp": "NicoNico",
    "twitch.tv": "Twitch",
    "vimeo.com": "Vimeo",
    "facebook.com": "Facebook",
    "reddit.com": "Reddit",
}

RELEASE_NOISE_RE = re.compile(
    r"\b(?:"
    r"s\d{1,2}e\d{1,3}|season\s*\d{1,2}|episode\s*\d{1,3}|ep\s*\d{1,3}|"
    r"2160p|1440p|1080p|720p|480p|4k|uhd|"
    r"bluray|blu-ray|bdrip|brrip|web-dl|webdl|webrip|hdtv|dvdrip|"
    r"remux|hdr10\+?|hdr|dolby\s*vision|dovi|hevc|avc|x265|x264|h\.?265|h\.?264|"
    r"dts(?:-hd)?|truehd|atmos|aac|ac3|ddp|flac|mp3|"
    r"10bit|8bit|multi|dual\s*audio|subbed|subtitle|subtitles|"
    r"camrip|hdcam|hd-ts|hdts|telesync|telecine|ts"
    r")\b",
    re.I,
)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
SEASON_EPISODE_RE = re.compile(r"(?:s(?P<season>\d{1,2})[ ._-]*e(?P<episode>\d{1,3})|\b(?P<season2>\d{1,2})x(?P<episode2>\d{1,3})\b)", re.I)
QUALITY_RESOLUTION_RE = re.compile(r"\b(4320p|2160p|1440p|1080p|720p|480p)\b", re.I)
TOKEN_RE = re.compile(r"[\u4e00-\u9fff]+|[a-z0-9]+", re.I)
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")
EN_ALIAS_PAREN_RE = re.compile(r"[\(\uff08]([A-Za-z][^()\uff08\uff09]{1,100})[\)\uff09]")
EN_ALIAS_RE = re.compile(r"([A-Za-z][A-Za-z0-9\s\.\-:']{2,100})")
VERSION_RE = re.compile(r"\b(?:v(?:ersion)?\s*)?(\d+(?:\.\d+){0,3}|20\d{2})\b", re.I)
BOOK_FORMAT_RE = re.compile(r"\b(pdf|epub|mobi|azw3)\b", re.I)
BRACKET_RE = re.compile(r"[\[\]\(\)\{\}]")

SOURCE_PATTERNS = (
    (re.compile(r"\b(?:blu[- ]?ray|bdrip|brrip)\b", re.I), "bluray"),
    (re.compile(r"\b(?:web[- ]?dl|webdl)\b", re.I), "web-dl"),
    (re.compile(r"\b(?:webrip)\b", re.I), "webrip"),
    (re.compile(r"\b(?:hdtv)\b", re.I), "hdtv"),
    (re.compile(r"\b(?:dvdrip)\b", re.I), "dvdrip"),
    (re.compile(r"\b(?:hdcam|camrip|cam)\b", re.I), "cam"),
    (re.compile(r"\b(?:hdts|hd-ts|telesync|telecine)\b", re.I), "cam"),
    (re.compile(r"\b(?:remux)\b", re.I), "remux"),
)

AUDIO_CODEC_PATTERNS = (
    (re.compile(r"\b(?:dts[- ]?hd(?:\s*ma)?|dtshd)\b", re.I), "dts-hd"),
    (re.compile(r"\b(?:truehd|atmos)\b", re.I), "truehd"),
    (re.compile(r"\b(?:ddp|eac3)\b", re.I), "ddp"),
    (re.compile(r"\b(?:ac3)\b", re.I), "ac3"),
    (re.compile(r"\b(?:aac)\b", re.I), "aac"),
    (re.compile(r"\b(?:flac)\b", re.I), "flac"),
    (re.compile(r"\b(?:mp3)\b", re.I), "mp3"),
    (re.compile(r"\b(?:dts)\b", re.I), "dts"),
)

VIDEO_CODEC_PATTERNS = (
    (re.compile(r"\b(?:h\.?265|x265|hevc)\b", re.I), "hevc"),
    (re.compile(r"\b(?:h\.?264|x264|avc)\b", re.I), "avc"),
    (re.compile(r"\b(?:xvid)\b", re.I), "xvid"),
)

PACK_PATTERNS = (
    (re.compile(r"\b(?:remux)\b", re.I), "remux"),
    (re.compile(r"\b(?:repack)\b", re.I), "repack"),
    (re.compile(r"\b(?:proper)\b", re.I), "proper"),
)

HDR_PATTERNS = (
    (re.compile(r"\bhdr10\+?\b", re.I), "hdr10"),
    (re.compile(r"\bdovi\b|\bdolby\s*vision\b", re.I), "dolby-vision"),
    (re.compile(r"\bhdr\b", re.I), "hdr"),
)


def ensure_utf8_stdio() -> None:
    for handle_name in ("stdout", "stderr"):
        handle = getattr(sys, handle_name, None)
        if hasattr(handle, "reconfigure"):
            handle.reconfigure(encoding="utf-8", errors="replace")


def storage_root() -> Path:
    workspace = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
    root = workspace / "storage" / "resource-hunter"
    root.mkdir(parents=True, exist_ok=True)
    return root


def default_download_dir() -> Path:
    downloads = storage_root() / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads


def compact_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def dump_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def has_chinese(text: str) -> bool:
    return bool(CHINESE_RE.search(text or ""))


def has_latin(text: str) -> bool:
    return bool(LATIN_RE.search(text or ""))


def detect_language_mix(text: str) -> str:
    has_cn = has_chinese(text)
    has_en = has_latin(text)
    if has_cn and has_en:
        return "mixed"
    if has_cn:
        return "chinese"
    if has_en:
        return "latin"
    return "unknown"


def extract_year(text: str) -> str:
    match = YEAR_RE.search(text or "")
    return match.group(0) if match else ""


def extract_versions(text: str) -> list[str]:
    values = [item.group(1) for item in VERSION_RE.finditer(text or "")]
    return unique_preserve(values)


def extract_book_formats(text: str) -> list[str]:
    return unique_preserve([item.group(1).lower() for item in BOOK_FORMAT_RE.finditer(text or "")])


def extract_season_episode(text: str) -> tuple[int | None, int | None]:
    match = SEASON_EPISODE_RE.search(text or "")
    if match:
        season = match.group("season") or match.group("season2")
        episode = match.group("episode") or match.group("episode2")
        return (int(season) if season else None, int(episode) if episode else None)
    en_match = re.search(r"season\s*(\d{1,2}).{0,10}?episode\s*(\d{1,3})", text or "", re.I)
    if en_match:
        return int(en_match.group(1)), int(en_match.group(2))
    cn_match = re.search(r"\u7b2c\s*(\d{1,2})\s*\u5b63", text or "")
    ep_match = re.search(r"\u7b2c\s*(\d{1,3})\s*\u96c6", text or "")
    return (
        int(cn_match.group(1)) if cn_match else None,
        int(ep_match.group(1)) if ep_match else None,
    )


def is_video_url(text: str) -> bool:
    lowered = (text or "").lower()
    return any(hint in lowered for hint in VIDEO_URL_HINTS)


def _clean_alias(value: str) -> str:
    cleaned = compact_spaces(BRACKET_RE.sub(" ", value))
    cleaned = YEAR_RE.sub(" ", cleaned)
    cleaned = RELEASE_NOISE_RE.sub(" ", cleaned)
    cleaned = compact_spaces(cleaned)
    return cleaned.strip(" -_|")


def extract_english_alias(text: str) -> str:
    if is_video_url(text):
        return ""
    if has_chinese(text):
        match = EN_ALIAS_PAREN_RE.search(text or "")
        if match:
            return _clean_alias(match.group(1))
        match = EN_ALIAS_RE.search(text or "")
        if match:
            return _clean_alias(match.group(1))
        return ""
    if has_latin(text):
        return _clean_alias(text)
    return ""


def extract_chinese_alias(text: str) -> str:
    chunks = re.findall(r"[\u4e00-\u9fff0-9\uff1a:\u00b7\-\s]{2,80}", text or "")
    cleaned = [compact_spaces(chunk) for chunk in chunks if has_chinese(chunk)]
    return cleaned[0] if cleaned else ""


def _strip_title_noise(text: str) -> str:
    value = compact_spaces(unquote(text or "")).lower()
    value = YEAR_RE.sub(" ", value)
    value = RELEASE_NOISE_RE.sub(" ", value)
    value = re.sub(r"[-_.:,/\\]+", " ", value)
    value = BRACKET_RE.sub(" ", value)
    value = re.sub(r"\b(?:proper|repack|extended|limited|complete|dual|multi)\b", " ", value)
    return compact_spaces(value)


def title_tokens(text: str, keep_numeric: bool = False) -> list[str]:
    tokens: list[str] = []
    for token in TOKEN_RE.findall(_strip_title_noise(text)):
        lowered = token.lower()
        if lowered in STOPWORDS:
            continue
        if not keep_numeric and lowered.isdigit():
            continue
        if len(lowered) == 1 and not CHINESE_RE.search(lowered):
            continue
        tokens.append(lowered)
    return tokens


def title_core(text: str) -> str:
    return " ".join(title_tokens(text))


def unique_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def normalize_title(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    cleaned = unquote(cleaned)
    cleaned = compact_spaces(cleaned)
    return cleaned.strip(" -_|[]()")


def normalize_key(text: str) -> str:
    cleaned = normalize_title(text).lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", cleaned)


def detect_platform(url: str) -> str:
    lowered = (url or "").lower()
    for domain, name in PLATFORM_MAP.items():
        if domain in lowered:
            return name
    return "Unknown"


def detect_kind(text: str, explicit_kind: str | None = None) -> str:
    if explicit_kind:
        return explicit_kind
    lowered = (text or "").lower()
    if is_video_url(lowered):
        return "video"
    if lowered.startswith("magnet:") or lowered.endswith(".torrent"):
        return "torrent"
    season, episode = extract_season_episode(lowered)
    if season is not None or episode is not None:
        return "tv"
    if any(term in lowered for term in ANIME_TERMS):
        return "anime"
    if any(term in lowered for term in MUSIC_TERMS) or any(term in lowered for term in LOSSLESS_TERMS):
        return "music"
    if any(term in lowered for term in SOFTWARE_TERMS) or any(term in lowered for term in SOFTWARE_BRANDS):
        return "software"
    if any(term in lowered for term in BOOK_TERMS):
        return "book"
    if any(term in lowered for term in TV_TERMS):
        return "tv"
    if extract_year(lowered):
        return "movie"
    return "general"


def text_contains_any(text: str, terms: Iterable[str]) -> bool:
    lowered = (text or "").lower()
    return any(term.lower() in lowered for term in terms)


def _detect_source_type(lowered: str) -> str:
    for pattern, label in SOURCE_PATTERNS:
        if pattern.search(lowered):
            return label
    return ""


def _detect_codec(lowered: str, patterns: tuple[tuple[re.Pattern[str], str], ...]) -> str:
    for pattern, label in patterns:
        if pattern.search(lowered):
            return label
    return ""


def parse_release_tags(text: str) -> dict[str, Any]:
    lowered = (text or "").lower()
    resolution_match = QUALITY_RESOLUTION_RE.search(lowered)
    resolution = resolution_match.group(1).lower() if resolution_match else ""
    if not resolution and re.search(r"\b(?:4k|uhd)\b", lowered):
        resolution = "2160p"
    hdr_flags = [label for pattern, label in HDR_PATTERNS if pattern.search(lowered)]
    source_type = _detect_source_type(lowered)
    pack = _detect_codec(lowered, PACK_PATTERNS)
    subtitle = text_contains_any(text, SUBTITLE_TERMS)
    lossless = any(term in lowered for term in LOSSLESS_TERMS)
    book_format = next((item.lower() for item in extract_book_formats(lowered)), "")
    return {
        "resolution": resolution,
        "source_type": source_type,
        "audio_codec": _detect_codec(lowered, AUDIO_CODEC_PATTERNS),
        "video_codec": _detect_codec(lowered, VIDEO_CODEC_PATTERNS),
        "pack": pack,
        "hdr_flags": hdr_flags,
        "subtitle": subtitle,
        "lossless": lossless,
        "format": book_format,
        "book_format": book_format,
    }


def parse_quality_tags(text: str) -> dict[str, Any]:
    tags = parse_release_tags(text)
    return {
        "resolution": tags["resolution"],
        "source": tags["source_type"],
        "source_type": tags["source_type"],
        "audio_codec": tags["audio_codec"],
        "video_codec": tags["video_codec"],
        "pack": tags["pack"],
        "hdr_flags": tags["hdr_flags"],
        "subtitle": tags["subtitle"],
        "lossless": tags["lossless"],
        "format": tags["format"],
        "book_format": tags["book_format"],
    }


def quality_display_from_tags(tags: dict[str, Any]) -> str:
    bits: list[str] = []
    if tags.get("book_format"):
        bits.append(tags["book_format"])
    elif tags.get("lossless"):
        bits.append("lossless")
    elif tags.get("resolution"):
        bits.append(tags["resolution"])
    if tags.get("source_type") and tags["source_type"] not in {"cam"}:
        bits.append(tags["source_type"])
    if tags.get("pack"):
        bits.append(tags["pack"])
    return " ".join(unique_preserve(bits))


def infer_quality(text: str) -> str:
    return quality_display_from_tags(parse_quality_tags(text))


def infer_provider_from_url(url: str) -> str:
    parsed = urlparse(url or "")
    host = parsed.netloc.lower()
    for domain, provider in DOMAIN_PROVIDER_MAP.items():
        if domain in host:
            return provider
    if (url or "").startswith("magnet:"):
        return "magnet"
    if (url or "").startswith("ed2k://"):
        return "ed2k"
    return "other"


def extract_password(text: str) -> str:
    decoded = unquote(text or "")
    match = re.search(r"[?&](?:password|pwd|pass)=([^&#]+)", decoded, re.I)
    if match:
        return match.group(1).strip()
    match = re.search(r"(?:\u63d0\u53d6\u7801|\u63d0\u53d6\u78bc|\u5bc6\u7801)[:\uff1a ]*([A-Za-z0-9]{4,8})", decoded)
    if match:
        return match.group(1)
    match = re.search(r"\?([A-Za-z0-9]{4,8})$", decoded)
    if match:
        return match.group(1)
    return ""


def clean_share_url(url: str) -> str:
    decoded = unquote(url or "")
    decoded = re.sub(r"[?&](?:password|pwd|pass)=[^&#]*", "", decoded, flags=re.I)
    decoded = re.sub(r"(?:\u63d0\u53d6\u7801|\u63d0\u53d6\u78bc|\u5bc6\u7801)[:\uff1a ]*[A-Za-z0-9]{4,8}", "", decoded)
    return decoded.rstrip("?&#, ").strip()


def extract_share_id(url: str, provider_hint: str = "") -> str:
    cleaned = clean_share_url(url)
    parsed = urlparse(cleaned)
    path = parsed.path.rstrip("/")
    if cleaned.startswith("magnet:"):
        match = re.search(r"btih:([A-Fa-f0-9]+)", cleaned)
        return match.group(1).lower() if match else normalize_key(cleaned)[:32]
    if cleaned.startswith("ed2k://"):
        return normalize_key(cleaned)[:32]
    if provider_hint == "baidu":
        match = re.search(r"/s/([A-Za-z0-9_-]+)", path)
        if match:
            return match.group(1)
    parts = [part for part in path.split("/") if part]
    return parts[-1] if parts else parsed.netloc.lower()


def source_priority(source_name: str) -> int:
    priorities = {
        "2fun": 1,
        "hunhepan": 2,
        "pansou.vip": 3,
        "nyaa": 1,
        "eztv": 1,
        "tpb": 2,
        "yts": 2,
        "1337x": 3,
    }
    return priorities.get((source_name or "").lower(), 9)


def safe_filename(name: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip()
    return value or "download"


def token_overlap_score(query_tokens: list[str], title_tokens_: list[str]) -> float:
    if not query_tokens or not title_tokens_:
        return 0.0
    query_set = set(query_tokens)
    title_set = set(title_tokens_)
    shared = query_set & title_set
    if not shared:
        return 0.0
    return round(len(shared) / max(len(query_set), len(title_set)), 4)
