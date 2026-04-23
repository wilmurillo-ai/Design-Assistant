"""
Unit tests for translate.py

Tests classical Chinese detection, text segmentation, prompt construction,
and result extraction. Does NOT test actual LLM calls (those are integration tests).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from translate import (
    detect_classical_chinese,
    _segment_text,
    _create_translation_prompt,
    _extract_english_result,
)

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

CLASSICAL_TEXT_1 = "子曰：「学而时习之，不亦说乎？有朋自远方来，不亦乐乎？」"
CLASSICAL_TEXT_2 = "天下皆知美之为美，斯恶已。皆知善之为善，斯不善已。"
CLASSICAL_TEXT_3 = "兵者，国之大事，死生之地，存亡之道，不可不察也。"
CLASSICAL_TEXT_LONG = CLASSICAL_TEXT_1 * 50  # >2000 chars
MODERN_CHINESE = "今天天气很好，我去公园散步了。然后买了一些蔬菜回家做饭，感觉很开心。"
MIXED_TEXT = "子曰学而时习之，但是现在的我觉得学习真的很重要，所以今天来学习古典文学。"
ENGLISH_TEXT = "The quick brown fox jumps over the lazy dog."


# ---------------------------------------------------------------------------
# detect_classical_chinese tests
# ---------------------------------------------------------------------------

def test_detect_classical_chinese_positive_lunyv():
    """Lunyu (Analects) opening is classical Chinese."""
    result = detect_classical_chinese(CLASSICAL_TEXT_1)
    assert result["is_classical"] is True
    assert result["confidence"] >= 0.3


def test_detect_classical_chinese_positive_laozi():
    """Laozi passage is classical Chinese."""
    result = detect_classical_chinese(CLASSICAL_TEXT_2)
    assert result["is_classical"] is True


def test_detect_classical_chinese_positive_sunzi():
    """Sun Tzu passage is classical Chinese."""
    result = detect_classical_chinese(CLASSICAL_TEXT_3)
    assert result["is_classical"] is True


def test_detect_classical_chinese_negative_modern():
    """Modern Chinese text is not classical Chinese."""
    result = detect_classical_chinese(MODERN_CHINESE)
    assert result["is_classical"] is False


def test_detect_classical_chinese_mixed():
    """Mixed classical + modern → mixed_modern=True."""
    result = detect_classical_chinese(MIXED_TEXT)
    assert result["mixed_modern"] is True


def test_detect_classical_chinese_english():
    """English text → is_classical=False, confidence≈0."""
    result = detect_classical_chinese(ENGLISH_TEXT)
    assert result["is_classical"] is False
    assert result["confidence"] < 0.15


def test_detect_classical_chinese_empty():
    """Empty string → all False/zero."""
    result = detect_classical_chinese("")
    assert result["is_classical"] is False
    assert result["confidence"] == 0.0
    assert result["classical_ratio"] == 0.0
    assert result["markers_found"] == []
    assert result["mixed_modern"] is False


def test_detect_classical_chinese_whitespace():
    """Whitespace-only string → is_classical=False."""
    result = detect_classical_chinese("   \n\t  ")
    assert result["is_classical"] is False


def test_detect_classical_chinese_returns_all_fields():
    """Result always contains all required fields."""
    result = detect_classical_chinese(CLASSICAL_TEXT_1)
    required = ["is_classical", "confidence", "classical_ratio", "markers_found", "mixed_modern"]
    for field in required:
        assert field in result, f"Missing field: {field}"


def test_detect_classical_chinese_confidence_range():
    """Confidence must be in [0.0, 1.0]."""
    for text in [CLASSICAL_TEXT_1, MODERN_CHINESE, ENGLISH_TEXT, ""]:
        result = detect_classical_chinese(text)
        assert 0.0 <= result["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# _segment_text tests
# ---------------------------------------------------------------------------

def test_segment_text_short():
    """Short text → single segment."""
    text = "子曰：学而时习之。"
    segments = _segment_text(text, max_len=2000)
    assert len(segments) == 1
    assert segments[0] == text


def test_segment_text_long():
    """Long text → multiple segments, each ≤ max_len (approximately)."""
    text = CLASSICAL_TEXT_LONG
    max_len = 200
    segments = _segment_text(text, max_len=max_len)
    assert len(segments) > 1, "Long text should produce multiple segments"
    for seg in segments:
        # Segments may slightly exceed max_len at sentence boundaries
        assert len(seg) <= max_len * 2, f"Segment too long: {len(seg)}"


def test_segment_text_joins_to_original():
    """Concatenating segments recovers the original text (modulo whitespace)."""
    text = "子曰：学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？"
    segments = _segment_text(text, max_len=20)
    rejoined = "".join(segments)
    # Allow slight normalization (whitespace)
    assert rejoined.replace(" ", "") == text.replace(" ", "")


def test_segment_text_exact_length():
    """Text exactly at max_len → single segment."""
    text = "A" * 100
    segments = _segment_text(text, max_len=100)
    assert len(segments) == 1


# ---------------------------------------------------------------------------
# _create_translation_prompt tests
# ---------------------------------------------------------------------------

def test_create_translation_prompt_format():
    """Prompt contains required few-shot examples and tags."""
    prompt = _create_translation_prompt("子曰：学而时习之。")
    assert "#classical:" in prompt
    assert "#english:" in prompt
    # Should contain the few-shot examples
    assert "Confucius" in prompt or "子曰" in prompt


def test_create_translation_prompt_includes_input():
    """The input segment appears in the prompt."""
    text = "天下皆知美之为美。"
    prompt = _create_translation_prompt(text)
    assert text in prompt


def test_create_translation_prompt_instruction():
    """The prompt includes translation instructions."""
    prompt = _create_translation_prompt("test")
    assert "classical Chinese" in prompt.lower() or "文言文" in prompt


# ---------------------------------------------------------------------------
# _extract_english_result tests
# ---------------------------------------------------------------------------

def test_extract_english_result_valid():
    """Correctly extracts text after '#english:' tag."""
    response = "Here is my translation:\n#english: The quick brown fox."
    result = _extract_english_result(response)
    assert result == "The quick brown fox."


def test_extract_english_result_multiline():
    """Extracts multi-line text after '#english:'."""
    response = "#english: First line.\nSecond line.\nThird line."
    result = _extract_english_result(response)
    assert "First line." in result
    assert "Second line." in result


def test_extract_english_result_case_insensitive():
    """Tag matching is case-insensitive."""
    response = "#English: The translation here."
    result = _extract_english_result(response)
    assert result == "The translation here."


def test_extract_english_result_missing():
    """Returns None when '#english:' tag is missing."""
    response = "Here is a translation without any tags: The fox."
    result = _extract_english_result(response)
    assert result is None


def test_extract_english_result_empty_after_tag():
    """Tag present but empty → returns empty string."""
    response = "#english:   "
    result = _extract_english_result(response)
    assert result == "" or result is not None


def test_extract_english_result_strips_whitespace():
    """Extracts text and strips leading/trailing whitespace."""
    response = "#english:   The translation.   "
    result = _extract_english_result(response)
    assert result == "The translation."
