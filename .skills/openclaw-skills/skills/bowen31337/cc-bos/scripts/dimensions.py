"""
Shared module: 8-dimension definitions from the CC-BOS framework.
Extracted from upstream gen.py for reuse across attack/defend/research modes.

Paper: arXiv:2602.22983 — CC-BOS: Classical Chinese Jailbreak Prompt Optimization
       via Bio-Inspired Search
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Core 8-dimension taxonomy (verbatim from upstream gen.py)
# Chinese keys map to integer indices (1-based)
# ---------------------------------------------------------------------------

DIMENSION_OPTIONS: Dict[str, Dict[str, int]] = {
    "role": {
        "学术身份": 1,    # academic identity
        "经典出处": 2,    # classic origin / canonical source
        "官职头衔": 3,    # official title
        "江湖人物": 4,    # jianghu figure
        "神话符号": 5,    # mythological symbol
        "文学流派": 6,    # literary school
    },
    "guidance": {
        "诱导生成": 1,    # induced generation
        "权威冒充": 2,    # authority impersonation
        "边界试探": 3,    # boundary probing
        "逻辑规避": 4,    # logic escape
        "情感操控": 5,    # emotional manipulation
        "认知混淆": 6,    # cognitive confusion
    },
    "mechanism": {
        "归谬推演": 1,    # reductio ad absurdum
        "墨家三表": 2,    # Mohist three-test (mozi sanbian)
        "易经卦象": 3,    # Yijing hexagram
        "公孙龙名辩": 4,  # Gongsun Long name-debate
        "孙子兵法虚实": 5, # Art of War feint (xu shi)
        "禅宗公案": 6,    # Zen koan
        "谶纬预言": 7,    # prophecy method (chen wei)
    },
    "metaphor": {
        "经典技术映射": 1,  # classic-technology mapping
        "自然系统映射": 2,  # nature-system mapping
        "器物机制映射": 3,  # artifact-mechanism mapping
        "历史事件隐喻": 4,  # historical event metaphor
        "兵法策略映射": 5,  # military strategy mapping
        "谶纬转换": 6,      # prophecy conversion
    },
    "expression": {
        "文学体裁": 1,    # literary style / genre
        "经典引用": 2,    # classic citation
        "结构组织": 3,    # structural organization
        "修辞手法": 4,    # rhetorical technique
        "互动节奏": 5,    # interactive rhythm
        "考证伪装": 6,    # verification disguise
    },
    "knowledge": {
        "符号解析": 1,    # symbol parsing
        "跨域推理": 2,    # cross-domain reasoning
        "因果推演": 3,    # causal deduction
        "规则建模": 4,    # rule modelling
        "知识重构": 5,    # knowledge reconstruction
    },
    "context": {
        "历史场景": 1,    # historical scenario
        "礼仪场景": 2,    # ritual scene
        "学术论辩": 3,    # academic debate
        "密折秘奏": 4,    # secret memorial
        "梦境预言": 5,    # dream prophecy
    },
    "trigger_pattern": {
        "单次触发": 1,    # one-shot trigger
        "渐进渗透": 2,    # progressive infiltration
        "延迟触发": 3,    # delayed trigger
        "周期探测": 4,    # periodic probing
    },
}

# English translations of all dimension option names
DIMENSION_OPTIONS_EN: Dict[str, Dict[str, int]] = {
    "role": {
        "academic identity": 1,
        "classic origin": 2,
        "official title": 3,
        "jianghu figure": 4,
        "mythological symbol": 5,
        "literary school": 6,
    },
    "guidance": {
        "induced generation": 1,
        "authority impersonation": 2,
        "boundary probing": 3,
        "logic escape": 4,
        "emotional manipulation": 5,
        "cognitive confusion": 6,
    },
    "mechanism": {
        "reductio ad absurdum": 1,
        "Mohist three-test": 2,
        "Yijing hexagram": 3,
        "Gongsun Long name-debate": 4,
        "Art of War feint": 5,
        "Zen koan": 6,
        "prophecy method": 7,
    },
    "metaphor": {
        "classic-technology mapping": 1,
        "nature-system mapping": 2,
        "artifact-mechanism mapping": 3,
        "historical event metaphor": 4,
        "military strategy mapping": 5,
        "prophecy conversion": 6,
    },
    "expression": {
        "literary style": 1,
        "classic citation": 2,
        "structural organization": 3,
        "rhetorical technique": 4,
        "interactive rhythm": 5,
        "verification disguise": 6,
    },
    "knowledge": {
        "symbol parsing": 1,
        "cross-domain reasoning": 2,
        "causal deduction": 3,
        "rule modelling": 4,
        "knowledge reconstruction": 5,
    },
    "context": {
        "historical scenario": 1,
        "ritual scene": 2,
        "academic debate": 3,
        "secret memorial": 4,
        "dream prophecy": 5,
    },
    "trigger_pattern": {
        "one-shot": 1,
        "progressive infiltration": 2,
        "delayed trigger": 3,
        "periodic probing": 4,
    },
}

# Sorted list of dimension key names (canonical order)
DIM_KEYS: List[str] = sorted(DIMENSION_OPTIONS.keys())

# Reverse lookup: (dim_key, value) -> Chinese name
_VALUE_TO_CN: Dict[str, Dict[int, str]] = {
    dim: {v: k for k, v in opts.items()}
    for dim, opts in DIMENSION_OPTIONS.items()
}

# Reverse lookup: (dim_key, value) -> English name
_VALUE_TO_EN: Dict[str, Dict[int, str]] = {
    dim: {v: k for k, v in opts.items()}
    for dim, opts in DIMENSION_OPTIONS_EN.items()
}

# Classical Chinese keyword markers used for detection
_CLASSICAL_MARKERS = [
    "之", "乎", "者", "也", "矣", "焉", "哉",
    "曰", "载", "昔", "今", "子", "典", "诗",
    "云", "兮", "乃", "其", "夫", "若", "且",
]

# Dimension-specific keyword patterns (Chinese text indicators)
_DIMENSION_KEYWORDS: Dict[str, List[str]] = {
    "role": ["学者", "先生", "夫子", "博士", "大夫", "侠客", "道士", "高僧",
             "神灵", "先贤", "圣人", "君子", "士大夫", "经典出处", "文人"],
    "guidance": ["请", "试", "以", "当", "须", "应", "宜", "可", "能",
                 "命", "令", "授", "传", "教", "示"],
    "mechanism": ["归谬", "三表", "卦象", "名辩", "虚实", "公案", "谶纬",
                  "阴阳", "五行", "八卦", "易", "兵法"],
    "metaphor": ["映射", "喻", "譬", "象", "符", "号", "化", "借",
                 "以...喻", "以...比", "比之于"],
    "expression": ["赋", "论", "书", "传", "辞", "颂", "铭", "序",
                   "注", "疏", "解", "释", "述"],
    "knowledge": ["解", "析", "论", "道", "理", "法", "义", "训",
                  "考", "证", "辨", "推", "演"],
    "context": ["朝堂", "学宫", "战场", "殿堂", "仪式", "辩场",
                "密折", "奏章", "梦境", "预言", "历史"],
    "trigger_pattern": ["其后", "渐次", "待", "延", "时机", "周而复始",
                        "一旦", "逐步", "缓缓", "循序"],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_dimension_name(dim_key: str, value: int) -> str:
    """Return the Chinese name for a dimension value.

    Args:
        dim_key: One of the 8 dimension keys (e.g. 'role').
        value: Integer value (1-based index).

    Returns:
        Chinese option name, or '<unknown>' if not found.
    """
    return _VALUE_TO_CN.get(dim_key, {}).get(value, "<unknown>")


def get_dimension_name_en(dim_key: str, value: int) -> str:
    """Return the English name for a dimension value.

    Args:
        dim_key: One of the 8 dimension keys (e.g. 'role').
        value: Integer value (1-based index).

    Returns:
        English option name, or '<unknown>' if not found.
    """
    return _VALUE_TO_EN.get(dim_key, {}).get(value, "<unknown>")


def fly_to_tuple(fly: dict) -> tuple:
    """Convert a fly dict to a hashable tuple (for deduplication).

    The tuple is sorted by DIM_KEYS order for determinism.

    Args:
        fly: Dict mapping dimension keys to integer values.

    Returns:
        Sorted tuple of (key, value) pairs.
    """
    return tuple(sorted((k, fly[k]) for k in DIM_KEYS if k in fly))


def convert_to_names(fly: dict) -> List[str]:
    """Convert a fly's numeric values to Chinese strategy names.

    Args:
        fly: Dict mapping dimension keys to integer values.

    Returns:
        List of Chinese strategy names in DIM_KEYS order.
    """
    return [get_dimension_name(dim, fly.get(dim, 1)) for dim in DIM_KEYS]


def convert_to_names_en(fly: dict) -> List[str]:
    """Convert a fly's numeric values to English strategy names.

    Args:
        fly: Dict mapping dimension keys to integer values.

    Returns:
        List of English strategy names in DIM_KEYS order.
    """
    return [get_dimension_name_en(dim, fly.get(dim, 1)) for dim in DIM_KEYS]


def detect_dimension_in_text(text: str) -> Dict[str, List[Tuple[str, float]]]:
    """Given a text string, detect which dimension patterns are present.

    Uses keyword matching and regex patterns for classical Chinese markers.

    Args:
        text: Input text to analyse.

    Returns:
        Dict mapping dim_key to list of (option_name, confidence_score) tuples
        for detected dimensions. Only dimensions with detected patterns are included.
    """
    if not text or not text.strip():
        return {}

    results: Dict[str, List[Tuple[str, float]]] = {}

    for dim_key, keywords in _DIMENSION_KEYWORDS.items():
        matches: List[Tuple[str, float]] = []
        for kw in keywords:
            pattern = re.compile(re.escape(kw))
            count = len(pattern.findall(text))
            if count > 0:
                # Normalise to 0-1 confidence (cap at 1.0)
                conf = min(1.0, count * 0.25)
                # Map keyword to closest dimension option name (use CN)
                option_names = list(DIMENSION_OPTIONS[dim_key].keys())
                # Pick first option as placeholder since keywords don't map 1:1
                if option_names:
                    matches.append((option_names[0], conf))

        if matches:
            # Deduplicate and keep highest confidence per option
            seen: Dict[str, float] = {}
            for name, conf in matches:
                if name not in seen or conf > seen[name]:
                    seen[name] = conf
            results[dim_key] = [(n, c) for n, c in seen.items()]

    # Also check for classical Chinese character frequency as a proxy for
    # structural markers (affects role, context, expression dims)
    classical_count = sum(text.count(m) for m in _CLASSICAL_MARKERS)
    classical_ratio = classical_count / max(len(text), 1)

    if classical_ratio > 0.05:  # >5% classical markers
        # Boost context detection
        if "context" not in results:
            results["context"] = [("历史场景", min(1.0, classical_ratio * 5))]
        if "expression" not in results:
            results["expression"] = [("文学体裁", min(1.0, classical_ratio * 4))]

    return results
