#!/usr/bin/env python3
"""Minimal self-test for cognitive-reframe skill"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from crisis_detector import is_crisis
from reframe import detect_distortion, generate_reframe, generate_response

def test_crisis_detector():
    print("=== Crisis Detector Tests ===")
    r, lvl = is_crisis("我想死，不想活了")
    assert r == True and lvl == "high", f"FAIL high risk: {r}, {lvl}"
    print("  [PASS] high risk detection")
    r, lvl = is_crisis("活着好累")
    assert r == True and lvl == "high"
    print("  [PASS] high risk (活着好累)")
    r, lvl = is_crisis("自杀")
    assert r == True and lvl == "high"
    print("  [PASS] high risk (自杀)")
    r, lvl = is_crisis("我很焦虑")
    assert r == True and lvl == "medium"
    print("  [PASS] medium risk detection")
    r, lvl = is_crisis("今天天气不错")
    assert r == False and lvl == "safe"
    print("  [PASS] safe text")
    print("  Crisis Detector: ALL PASS\n")

def test_distortion_detection():
    print("=== Distortion Detection Tests ===")
    # regression: "肯定" should trigger 情绪推理
    d = detect_distortion("我肯定过不了")
    assert "情绪推理" in d, f"FAIL: 情绪推理 not detected in {d}"
    print("  [PASS] 肯定 triggers 情绪推理")
    # regression: "彻底垮了" should trigger 灾难化
    d = detect_distortion("彻底垮了")
    assert "灾难化" in d, f"FAIL: 灾难化 not detected in {d}"
    print("  [PASS] 彻底垮了 triggers 灾难化")
    # regression: "应当总是" should only trigger 应当思维
    d = detect_distortion("我应当总是保持高效")
    assert "应当思维" in d and "全或无思维" not in d, f"FAIL: {d}"
    print("  [PASS] 应当总是 only triggers 应当思维")
    # regression: "项目完了" should NOT trigger
    d = detect_distortion("项目完了")
    assert len(d) == 0, f"FAIL: 项目完了 should not trigger, got {d}"
    print("  [PASS] 项目完了 no false positive")
    print("  Distortion Detection: ALL PASS\n")

def test_disclaimer():
    print("=== Disclaimer Tests ===")
    # crisis response should NOT include disclaimer (it's a safety message)
    resp = generate_response("我不想活了")
    assert resp["type"] == "crisis"
    print("  [PASS] crisis response is crisis type")
    # normal response should include disclaimer
    resp = generate_response("我感觉很糟糕")
    assert "disclaimer" in resp and "心理治疗" in resp["disclaimer"], f"FAIL: missing disclaimer"
    print("  [PASS] normal response has disclaimer")
    resp = generate_response("我完全失败了")
    assert "disclaimer" in resp
    print("  [PASS] distortion response has disclaimer")
    print("  Disclaimer: ALL PASS\n")

def test_generate_response():
    print("=== Generate Response Tests ===")
    resp = generate_response("我不想活了")
    assert resp["type"] == "crisis"
    assert resp["risk_level"] == "high"
    print("  [PASS] crisis response")
    resp = generate_response("我完全失败了")
    assert resp["type"] == "normal"
    assert "全或无思维" in resp["distortions"]
    print("  [PASS] normal with distortion")
    resp = generate_response("今天天气不错")
    assert resp["type"] == "normal"
    print("  [PASS] normal generic")
    print("  Generate Response: ALL PASS\n")

def test_reframe_integration():
    print("=== Integration: Full Flow ===")
    user_input = "我完全失败了，什么都做不好"
    resp = generate_response(user_input)
    assert resp["type"] == "normal"
    assert len(resp["distortions"]) > 0, f"FAIL: no distortions for '{user_input}'"
    assert len(resp["reframes"]) > 0
    print(f"  Input: {user_input}")
    print(f"  Detected: {resp['distortions']}")
    print(f"  Reframes: {[r['重构方向'] for r in resp['reframes']]}")
    print("  Integration: PASS\n")

if __name__ == "__main__":
    print("\n========== Cognitive Reframe Self-Test ==========\n")
    test_crisis_detector()
    test_distortion_detection()
    test_disclaimer()
    test_generate_response()
    test_reframe_integration()
    print("========== ALL TESTS PASSED ==========\n")
