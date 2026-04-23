"""
Translation wrapper: classical Chinese ↔ English.
Wraps upstream translate.py logic with OpenClaw-compatible API handling.

Paper: arXiv:2602.22983 — CC-BOS: Classical Chinese Jailbreak Prompt Optimization
"""
from __future__ import annotations

import re
from typing import List, Optional

# ---------------------------------------------------------------------------
# Classical Chinese detection markers
# ---------------------------------------------------------------------------

# High-frequency classical Chinese function words and particles
_CLASSICAL_PARTICLES = [
    "之", "乎", "者", "也", "矣", "焉", "哉", "兮",
    "乃", "其", "夫", "若", "且", "曰", "载", "昔",
    "云", "亦", "则", "故", "以", "于", "而", "为",
    "与", "所", "何", "莫", "岂", "宁", "非",
]

# Patterns specific to classical Chinese writing style
_CLASSICAL_PATTERNS = [
    r"[\u4e00-\u9fff]{1,3}曰[：:「「]",  # XXX曰: / XXX曰：
    r"[子君先][曰云]",                    # 子曰/君曰/先云
    r"昔者?[\u4e00-\u9fff]",              # 昔/昔者 + char
    r"故曰",                              # 故曰
    r"所谓",                              # 所谓
    r"[\u4e00-\u9fff]{2}之道",            # XX之道
    r"[\u4e00-\u9fff]者[，,][\u4e00-\u9fff]也",  # X者，Y也
    r"非[\u4e00-\u9fff]{1,4}乎",          # 非X乎
    r"岂[\u4e00-\u9fff]{1,6}哉",          # 岂X哉
    r"[\u4e00-\u9fff]兮[\u4e00-\u9fff]",  # X兮X
]

# Modern Chinese indicators (suggests NOT classical)
_MODERN_INDICATORS = [
    "的", "了", "是", "在", "有", "我", "你", "他", "她", "它",
    "们", "这", "那", "什么", "怎么", "为什么", "因为", "所以",
    "但是", "不过", "然后", "还是", "还有", "已经",
]

# Few-shot examples for translation prompts (from upstream translate.py)
_FEW_SHOT_EXAMPLES = """
Example 1:
#classical: 子曰：「学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？」
#english: Confucius said: "Is it not pleasant to learn with a constant perseverance and application? Is it not delightful to have friends coming from distant quarters? Is he not a man of complete virtue, who feels no discomposure though men may take no notice of him?"

Example 2:
#classical: 天下皆知美之为美，斯恶已；皆知善之为善，斯不善已。
#english: When people throughout the world know beauty as beauty, ugliness arises; when they know good as good, evil arises.

Example 3:
#classical: 兵者，国之大事，死生之地，存亡之道，不可不察也。
#english: War is a matter of vital importance to the State; the province of life or death; the road to survival or ruin. It is mandatory that it be thoroughly studied.
"""


def detect_classical_chinese(text: str) -> dict:
    """Analyse text for classical Chinese characteristics.

    Args:
        text: Input string to analyse.

    Returns:
        {
            "is_classical": bool,
            "confidence": float,         # 0.0-1.0
            "classical_ratio": float,    # ratio of classical markers
            "markers_found": list[str],  # specific patterns detected
            "mixed_modern": bool         # whether modern Chinese is mixed in
        }
    """
    if not text or not text.strip():
        return {
            "is_classical": False,
            "confidence": 0.0,
            "classical_ratio": 0.0,
            "markers_found": [],
            "mixed_modern": False,
        }

    text_len = len(text)
    markers_found: List[str] = []
    score = 0.0

    # 1. Classical particle frequency
    particle_count = sum(text.count(p) for p in _CLASSICAL_PARTICLES)
    classical_ratio = particle_count / max(text_len, 1)
    if classical_ratio > 0.03:
        markers_found.append(f"classical_particles({particle_count})")
        score += min(0.4, classical_ratio * 10)

    # 2. Classical structural patterns
    pattern_hits = 0
    for pat in _CLASSICAL_PATTERNS:
        m = re.search(pat, text)
        if m:
            pattern_hits += 1
            markers_found.append(f"pattern:{pat[:20]}")
    if pattern_hits > 0:
        score += min(0.4, pattern_hits * 0.1)

    # 3. Modern Chinese indicators (penalise)
    modern_count = sum(text.count(mi) for mi in _MODERN_INDICATORS)
    modern_ratio = modern_count / max(text_len, 1)
    mixed_modern = modern_ratio > 0.03 and classical_ratio > 0.02

    if modern_ratio > 0.05:
        score *= max(0.3, 1.0 - modern_ratio * 5)

    # 4. Chinese character ratio check (must be mostly Chinese)
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    chinese_ratio = chinese_chars / max(text_len, 1)
    if chinese_ratio < 0.3:
        score *= 0.3  # probably not Chinese at all

    confidence = min(1.0, score)
    is_classical = confidence >= 0.3

    return {
        "is_classical": is_classical,
        "confidence": round(confidence, 3),
        "classical_ratio": round(classical_ratio, 3),
        "markers_found": markers_found,
        "mixed_modern": mixed_modern,
    }


def _segment_text(text: str, max_len: int = 2000) -> List[str]:
    """Split long text into segments at punctuation boundaries.

    Args:
        text: Full text to segment.
        max_len: Maximum characters per segment.

    Returns:
        List of text segments.
    """
    if len(text) <= max_len:
        return [text]

    segments: List[str] = []
    # Split on sentence-ending punctuation
    sentence_ends = re.compile(r"(?<=[。！？.!?；;])\s*")
    sentences = sentence_ends.split(text)

    current: List[str] = []
    current_len = 0

    for sentence in sentences:
        if not sentence:
            continue
        if current_len + len(sentence) > max_len and current:
            segments.append("".join(current))
            current = [sentence]
            current_len = len(sentence)
        else:
            current.append(sentence)
            current_len += len(sentence)

    if current:
        segments.append("".join(current))

    return segments


def _create_translation_prompt(segment: str) -> str:
    """Build translation prompt with few-shot examples.

    Args:
        segment: Classical Chinese text segment.

    Returns:
        Formatted prompt string.
    """
    return (
        "You are an expert translator of classical Chinese (文言文) to English. "
        "Translate the following classical Chinese text accurately and naturally. "
        "Output ONLY the English translation, prefixed with '#english:' on its own line.\n\n"
        + _FEW_SHOT_EXAMPLES
        + f"\nNow translate:\n#classical: {segment}\n#english:"
    )


def _extract_english_result(response: str) -> Optional[str]:
    """Extract the English translation from an LLM response.

    Looks for text after '#english:' tag. Falls back to stripping the raw response.

    Args:
        response: Raw LLM response.

    Returns:
        Extracted English text, or None if the tag is missing.
    """
    # Try to find #english: marker
    match = re.search(r"#english:\s*(.*)", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def classical_chinese_to_english(
    text: str,
    model: str = "deepseek-chat",
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    max_segment_length: int = 2000,
) -> Optional[str]:
    """Translate classical Chinese text to English.

    Segments long texts, translates each segment, joins results.

    Args:
        text: Classical Chinese text to translate.
        model: LLM model identifier.
        api_key: API key (reads from env if None).
        api_base: API base URL.
        max_segment_length: Max chars per segment for long texts.

    Returns:
        English translation, or None on failure.
    """
    import os
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package required: uv pip install openai")

    if not text or not text.strip():
        return None

    resolved_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not resolved_key:
        raise ValueError("No API key found. Set DEEPSEEK_API_KEY or OPENAI_API_KEY env var.")

    client = OpenAI(api_key=resolved_key, base_url=api_base or "https://api.deepseek.com/v1")

    segments = _segment_text(text, max_len=max_segment_length)
    translated_parts: List[str] = []

    for seg in segments:
        prompt = _create_translation_prompt(seg)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2048,
            )
            raw = resp.choices[0].message.content or ""
            result = _extract_english_result(raw)
            if result:
                translated_parts.append(result)
            else:
                # Fallback: use raw response
                translated_parts.append(raw.strip())
        except Exception as e:
            # Return partial result on error
            if translated_parts:
                return " ".join(translated_parts)
            return None

    if not translated_parts:
        return None
    return " ".join(translated_parts)


def english_to_classical_chinese(
    text: str,
    model: str = "deepseek-chat",
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> Optional[str]:
    """Translate English to classical Chinese.

    Useful for understanding what the attack generation produces.

    Args:
        text: English text to translate.
        model: LLM model identifier.
        api_key: API key.
        api_base: API base URL.

    Returns:
        Classical Chinese translation, or None on failure.
    """
    import os
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package required: uv pip install openai")

    if not text or not text.strip():
        return None

    resolved_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not resolved_key:
        raise ValueError("No API key found. Set DEEPSEEK_API_KEY or OPENAI_API_KEY env var.")

    client = OpenAI(api_key=resolved_key, base_url=api_base or "https://api.deepseek.com/v1")

    prompt = (
        "You are an expert classical Chinese scholar. "
        "Translate the following English text into elegant classical Chinese (文言文). "
        "Output ONLY the classical Chinese translation, prefixed with '#classical:' on its own line.\n\n"
        f"English: {text}\n#classical:"
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048,
        )
        raw = resp.choices[0].message.content or ""
        match = re.search(r"#classical:\s*(.*)", raw, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return raw.strip()
    except Exception:
        return None
