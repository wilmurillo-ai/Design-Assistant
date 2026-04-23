from __future__ import annotations

import re
import time
from typing import Any

from .cache import ResourceCache
from .common import (
    extract_season_episode,
    extract_versions,
    extract_year,
    normalize_key,
    parse_quality_tags,
    quality_display_from_tags,
    source_priority,
    title_core,
    title_tokens,
    token_overlap_score,
    unique_preserve,
)
from .models import SearchIntent, SearchResult
from .sources import profile_for


PAN_PROVIDER_SCORE = {
    "aliyun": 12,
    "quark": 11,
    "115": 10,
    "pikpak": 9,
    "uc": 8,
    "baidu": 7,
    "123": 6,
    "xunlei": 5,
    "tianyi": 4,
    "magnet": 3,
    "other": 1,
}

MATCH_BUCKET_ORDER = {
    "exact_title_episode": 0,
    "exact_title_family": 1,
    "title_family_match": 2,
    "episode_only_match": 3,
    "weak_context_match": 4,
}

TIER_ORDER = {"top": 0, "related": 1, "risky": 2}

BUCKET_LABELS = {
    "top": "Top matches",
    "related": "Related matches",
    "risky": "Risky recall",
}


def _target_title_cores(intent: SearchIntent) -> list[str]:
    cores = [
        intent.title_core,
        intent.english_title_core,
        intent.chinese_title_core,
    ]
    cores.extend([title_core(item) or item for item in intent.resolved_titles])
    return unique_preserve([core for core in cores if core])


def _title_signals(intent: SearchIntent, title: str) -> dict[str, Any]:
    candidate_core = title_core(title)
    candidate_tokens = title_tokens(candidate_core or title)
    target_cores = _target_title_cores(intent)
    target_token_sets = [title_tokens(core) for core in target_cores]
    candidate_key = normalize_key(candidate_core or title)
    target_keys = [normalize_key(core) for core in target_cores if normalize_key(core)]
    exact_core_match = bool(candidate_key and candidate_key in target_keys)
    phrase_match = any(
        core
        and (
            candidate_core == core
            or candidate_core.startswith(core + " ")
            or core.startswith(candidate_core + " ")
        )
        for core in target_cores
    )
    starts_with_target = any(tokens and candidate_tokens[: len(tokens)] == tokens for tokens in target_token_sets)
    overlap = max((token_overlap_score(tokens, candidate_tokens) for tokens in target_token_sets), default=0.0)
    season, episode = extract_season_episode(title)
    season_match = bool(intent.season is None or season == intent.season)
    episode_match = bool(intent.episode is None or episode == intent.episode)
    result_year = extract_year(title)
    year_match = bool(not intent.year or result_year == intent.year or (not result_year and intent.kind in {"tv", "anime"}))
    matched_core = next((core for core in target_cores if normalize_key(core) == candidate_key), target_cores[0] if target_cores else "")
    return {
        "candidate_core": candidate_core,
        "candidate_tokens": candidate_tokens,
        "exact_core_match": exact_core_match,
        "phrase_match": phrase_match,
        "starts_with_target": starts_with_target,
        "overlap": overlap,
        "season_match": season_match,
        "episode_match": episode_match,
        "result_season": season,
        "result_episode": episode,
        "result_year": result_year,
        "year_match": year_match,
        "matched_core": matched_core,
    }


def classify_result(result: SearchResult, intent: SearchIntent) -> tuple[str, float, list[str], list[str], dict[str, Any]]:
    signals = _title_signals(intent, result.title)
    reasons: list[str] = []
    penalties: list[str] = []

    if signals["exact_core_match"]:
        reasons.append("canonical title match")
    elif signals["phrase_match"]:
        reasons.append("phrase title match")
    elif signals["overlap"] >= 0.9:
        reasons.append("strong title-family match")
    elif signals["overlap"] >= 0.6:
        reasons.append("partial title-family match")
    elif signals["overlap"] > 0:
        reasons.append("weak context match")

    if signals["year_match"] and intent.year:
        reasons.append("year match")
    if intent.season is not None and signals["season_match"]:
        reasons.append("season match")
    if intent.episode is not None and signals["episode_match"]:
        reasons.append("episode match")

    strong_title = signals["exact_core_match"] or signals["phrase_match"] or (signals["overlap"] >= 0.82 and signals["starts_with_target"])
    related_title = strong_title or signals["overlap"] >= 0.62

    if intent.kind in {"tv", "anime"} and (intent.season is not None or intent.episode is not None):
        if strong_title and signals["season_match"] and signals["episode_match"]:
            return "exact_title_episode", 0.98, reasons, penalties, signals
        if related_title and signals["season_match"] and signals["episode_match"]:
            return "title_family_match", 0.78, reasons, penalties, signals
        if strong_title and signals["season_match"]:
            penalties.append("missing exact episode evidence")
            return "title_family_match", 0.62, reasons, penalties, signals
        if signals["season_match"] or signals["episode_match"]:
            penalties.append("episode without title-family match")
            return "episode_only_match", 0.26, reasons, penalties, signals
        penalties.append("weak context only")
        return "weak_context_match", 0.08, reasons, penalties, signals

    if strong_title and signals["year_match"]:
        return "exact_title_family", 0.95, reasons, penalties, signals
    if strong_title:
        penalties.append("year not confirmed")
        return "title_family_match", 0.74, reasons, penalties, signals
    if related_title and signals["year_match"]:
        return "title_family_match", 0.64, reasons, penalties, signals
    if signals["overlap"] >= 0.45:
        penalties.append("title-family weak")
        return "title_family_match", 0.48, reasons, penalties, signals
    penalties.append("weak context only")
    return "weak_context_match", 0.12, reasons, penalties, signals


def source_health(cache: ResourceCache | None, source_name: str) -> dict[str, Any]:
    profile = profile_for(source_name)
    if cache is None:
        return {
            "degraded": profile.default_degraded,
            "degraded_reason": "default_degraded" if profile.default_degraded else "",
            "recovery_state": "unknown",
            "last_success_epoch": None,
            "failure_kind": "",
        }
    latest = cache.latest_source_status(source_name)
    if not latest:
        return {
            "degraded": profile.default_degraded,
            "degraded_reason": "default_degraded" if profile.default_degraded else "",
            "recovery_state": "unknown",
            "last_success_epoch": None,
            "failure_kind": "",
        }
    last_success_epoch = latest.get("last_success_epoch")
    if latest.get("skipped") and latest.get("failure_kind") == "circuit_open":
        return {
            "degraded": True,
            "degraded_reason": "circuit_open",
            "recovery_state": "cooldown",
            "last_success_epoch": last_success_epoch,
            "failure_kind": latest.get("failure_kind", ""),
        }
    if profile.default_degraded:
        last_failure = cache.latest_failure_epoch(source_name, within_seconds=900)
        recovery_since = last_failure if last_failure is not None else (time.time() - 900)
        recovered = cache.count_real_successes_since(source_name, recovery_since, within_seconds=900) >= 2
        if latest.get("ok") and latest.get("failure_kind") == "probe_ok":
            recovered = True
        if recovered:
            return {
                "degraded": False,
                "degraded_reason": "",
                "recovery_state": "healthy",
                "last_success_epoch": last_success_epoch,
                "failure_kind": latest.get("failure_kind", ""),
            }
        return {
            "degraded": True,
            "degraded_reason": latest.get("degraded_reason") or latest.get("failure_kind") or "default_degraded",
            "recovery_state": "recovering" if last_success_epoch else "degraded",
            "last_success_epoch": last_success_epoch,
            "failure_kind": latest.get("failure_kind", ""),
        }
    return {
        "degraded": bool(latest.get("degraded")),
        "degraded_reason": latest.get("degraded_reason", ""),
        "recovery_state": latest.get("recovery_state", "healthy" if latest.get("ok") else "degraded"),
        "last_success_epoch": last_success_epoch,
        "failure_kind": latest.get("failure_kind", ""),
    }


def source_is_degraded(cache: ResourceCache | None, source_name: str) -> bool:
    return bool(source_health(cache, source_name).get("degraded"))


def _build_canonical_identity(result: SearchResult, intent: SearchIntent, signals: dict[str, Any]) -> str:
    strong_title = signals.get("exact_core_match") or signals.get("phrase_match") or signals.get("overlap", 0.0) >= 0.82
    base = (
        (signals.get("matched_core") if strong_title else "")
        or signals.get("candidate_core")
        or title_core(result.title)
        or title_core(intent.query)
        or normalize_key(result.title)
    )
    kind = intent.kind
    if kind == "movie":
        year = signals.get("result_year") or intent.resolved_year or intent.year or "na"
        return f"movie:{normalize_key(base)}:{year}"
    if kind in {"tv", "anime"}:
        season = signals.get("result_season") or intent.season or 0
        episode = signals.get("result_episode") or intent.episode or 0
        return f"{kind}:{normalize_key(base)}:s{int(season):02d}e{int(episode):03d}"
    if kind == "software":
        versions = extract_versions(result.title) or intent.version_hints or ["na"]
        return f"software:{normalize_key(base)}:{versions[0]}"
    if kind == "book":
        fmt = result.quality_tags.get("format") or result.quality_tags.get("book_format") or "na"
        return f"book:{normalize_key(base)}:{fmt}"
    if kind == "music":
        quality = "lossless" if result.quality_tags.get("lossless") else "na"
        return f"music:{normalize_key(base)}:{quality}"
    return f"{kind}:{normalize_key(base)}"


def _assign_tier(bucket: str, confidence: float) -> str:
    if bucket in {"exact_title_episode", "exact_title_family"}:
        return "top"
    if bucket == "title_family_match" and confidence >= 0.62:
        return "related"
    if bucket == "title_family_match" and confidence >= 0.48:
        return "related"
    return "risky"


def score_result(result: SearchResult, intent: SearchIntent, cache: ResourceCache | None = None) -> SearchResult:
    bucket, confidence, reasons, penalties, signals = classify_result(result, intent)
    result.match_bucket = bucket
    result.confidence = round(confidence, 3)
    result.reasons = unique_preserve(reasons)
    result.penalties = unique_preserve(penalties)

    tags = result.quality_tags or parse_quality_tags(result.title)
    result.quality_tags = tags
    result.quality = quality_display_from_tags(tags)

    score = {
        "exact_title_episode": 150,
        "exact_title_family": 140,
        "title_family_match": 92,
        "episode_only_match": 18,
        "weak_context_match": -8,
    }[bucket]

    if signals["exact_core_match"]:
        score += 30
    if signals["phrase_match"]:
        score += 16
    score += int(signals["overlap"] * 24)
    if signals["year_match"] and intent.year:
        score += 10
    if intent.season is not None and signals["season_match"]:
        score += 10
    if intent.episode is not None and signals["episode_match"]:
        score += 14

    resolution = tags.get("resolution")
    if resolution == "2160p":
        score += 18
        result.reasons.append("4k resolution")
    elif resolution == "1080p":
        score += 10
        result.reasons.append("1080p resolution")
    elif resolution == "720p":
        score += 4
        result.reasons.append("720p resolution")

    source_type = tags.get("source_type") or tags.get("source")
    if source_type == "bluray":
        score += 8
        result.reasons.append("bluray source")
    elif source_type == "web-dl":
        score += 5
        result.reasons.append("web-dl source")
    elif source_type in {"webrip", "hdtv"}:
        score += 2
        result.reasons.append(f"{source_type} source")
    elif source_type == "cam":
        score -= 28
        result.penalties.append("cam-quality release")
    if tags.get("pack") == "remux":
        score += 6
        result.reasons.append("remux pack")
    if tags.get("hdr_flags"):
        score += min(8, 4 * len(tags["hdr_flags"]))
        result.reasons.append("hdr flags")
    preference_mismatch = False

    if intent.wants_sub and tags.get("subtitle"):
        score += 12
        result.reasons.append("subtitle requested")
    if intent.wants_4k and resolution == "2160p":
        score += 20
        result.reasons.append("4k requested")
    if intent.kind == "music" and tags.get("lossless"):
        score += 16
        result.reasons.append("lossless audio")
    if intent.kind == "music":
        lowered_query = intent.original_query.lower()
        wants_lossless = any(term in lowered_query for term in ("flac", "lossless")) or "\u65e0\u635f" in intent.original_query
        if wants_lossless and not tags.get("lossless"):
            preference_mismatch = True
            score -= 28
            result.penalties.append("lossless preference mismatch")
    if intent.kind == "book" and tags.get("format"):
        score += 8
        result.reasons.append("book format match")
    if intent.kind == "book" and intent.format_hints:
        if tags.get("format") in intent.format_hints or tags.get("book_format") in intent.format_hints:
            score += 10
            result.reasons.append("requested format match")
        else:
            preference_mismatch = True
            score -= 18
            result.penalties.append("requested format mismatch")
    if intent.kind == "software":
        lowered_query = intent.original_query.lower()
        platform_hint = next((hint for hint in ("windows", "mac", "linux") if hint in lowered_query), "")
        if platform_hint:
            if platform_hint in result.title.lower():
                score += 10
                result.reasons.append("platform hint match")
            else:
                preference_mismatch = True
                score -= 18
                result.penalties.append("platform hint mismatch")

    if result.channel == "pan":
        score += PAN_PROVIDER_SCORE.get(result.provider, PAN_PROVIDER_SCORE["other"])
        if result.password:
            score += 6
            result.reasons.append("has extraction code")
    if result.channel == "torrent" and result.seeders:
        score += min(result.seeders, 240) // 6
        result.reasons.append("seeders")

    score += max(0, 12 - source_priority(result.source))
    result.reasons.append(f"source priority {source_priority(result.source)}")

    health = source_health(cache, result.source)
    result.source_health = health
    result.source_degraded = bool(health.get("degraded"))
    if result.source_degraded:
        penalty = profile_for(result.source).degraded_score_penalty
        if penalty:
            score -= penalty
            result.penalties.append(f"degraded source penalty ({penalty})")

    if bucket == "episode_only_match":
        score -= 48
        result.penalties.append("episode-only match penalty")
    elif bucket == "weak_context_match":
        score -= 32
        result.penalties.append("weak-context penalty")

    result.canonical_identity = _build_canonical_identity(result, intent, signals)
    result.evidence = {
        "title_core": signals["candidate_core"],
        "matched_core": signals["matched_core"],
        "exact_core_match": signals["exact_core_match"],
        "phrase_match": signals["phrase_match"],
        "starts_with_target": signals["starts_with_target"],
        "overlap": signals["overlap"],
        "year_match": signals["year_match"],
        "season_match": signals["season_match"],
        "episode_match": signals["episode_match"],
        "result_year": signals["result_year"],
        "result_season": signals["result_season"],
        "result_episode": signals["result_episode"],
        "preference_mismatch": preference_mismatch,
    }
    result.tier = "related" if preference_mismatch and _assign_tier(bucket, result.confidence) == "top" else _assign_tier(bucket, result.confidence)
    result.score = score
    result.reasons = unique_preserve(result.reasons)
    result.penalties = unique_preserve(result.penalties)
    return result


def _choice_tuple(result: SearchResult) -> tuple[int, int, int, int, int, int, int]:
    return (
        -MATCH_BUCKET_ORDER.get(result.match_bucket, 99),
        -TIER_ORDER.get(result.tier, 99),
        result.score,
        0 if not result.source_degraded else -1,
        result.seeders,
        1 if result.password else 0,
        len(result.title),
    )


def deduplicate_results(results: list[SearchResult]) -> list[SearchResult]:
    chosen: dict[str, SearchResult] = {}
    for result in results:
        key = result.canonical_identity or result.share_id_or_info_hash or normalize_key(result.title)[:96]
        current = chosen.get(key)
        if not current or _choice_tuple(result) > _choice_tuple(current):
            chosen[key] = result
    return list(chosen.values())


def sort_results(results: list[SearchResult]) -> list[SearchResult]:
    return sorted(
        results,
        key=lambda item: (
            TIER_ORDER.get(item.tier, 99),
            MATCH_BUCKET_ORDER.get(item.match_bucket, 99),
            -item.score,
            item.source_degraded,
            -item.seeders,
            item.title.lower(),
        ),
    )


def diversify_results(results: list[SearchResult], head_size: int = 8) -> list[SearchResult]:
    remaining = list(sort_results(results))
    selected: list[SearchResult] = []
    source_counts: dict[str, int] = {}
    provider_counts: dict[str, int] = {}
    quality_counts: dict[str, int] = {}
    while remaining:
        best_index = 0
        best_value: tuple[float, int] | None = None
        for index, item in enumerate(remaining):
            adjusted = float(item.score)
            if len(selected) < head_size:
                adjusted -= source_counts.get(item.source, 0) * 12
                adjusted -= provider_counts.get(item.provider, 0) * 6
                adjusted -= quality_counts.get(item.quality or "na", 0) * 4
            value = (adjusted, -index)
            if best_value is None or value > best_value:
                best_value = value
                best_index = index
        chosen = remaining.pop(best_index)
        selected.append(chosen)
        source_counts[chosen.source] = source_counts.get(chosen.source, 0) + 1
        provider_counts[chosen.provider] = provider_counts.get(chosen.provider, 0) + 1
        quality_counts[chosen.quality or "na"] = quality_counts.get(chosen.quality or "na", 0) + 1
    return selected


__all__ = [
    "BUCKET_LABELS",
    "MATCH_BUCKET_ORDER",
    "classify_result",
    "deduplicate_results",
    "diversify_results",
    "score_result",
    "sort_results",
    "source_health",
    "source_is_degraded",
]
