#!/usr/bin/env python3
"""Cognitive Reframe - 认知重构工具"""
import json
import sys
import os

DISCLAIMER = (
    "💡 这是一种日常自我调节练习，不构成专业心理治疗或医疗建议。"
    "如果负面思维持续困扰你，建议咨询专业心理咨询师。"
    "如遇紧急危险，请直接拨打120/110。"
)

COGNITIVE_DISTORTIONS = {
    "全或无思维": {"特征": "非黑即白的极端判断", "例子": "我完全失败了", "重构": "尝试看到中间的灰色地带"},
    "心理过滤": {"特征": "只关注负面，忽略正面", "例子": "这次说得不好不算什么", "重构": "有意识地关注正面事件"},
    "灾难化": {"特征": "夸大负面后果", "例子": "如果失败就彻底完了", "重构": "评估实际可能性和应对能力"},
    "读心术": {"特征": "假设知道别人想法", "例子": "他们一定觉得我很笨", "重构": "没有确凿证据时，不要假设"},
    "情绪推理": {"特征": "把感觉当成事实", "例子": "我觉得自己没用所以一定没用", "重构": "感觉不等于事实"},
    "应当思维": {"特征": "给自己设不切实际的应当标准", "例子": "我应当总是保持高效", "重构": "接受人都有状态起伏"},
    "贴标签": {"特征": "给自己贴负面标签", "例子": "我就是一个失败者", "重构": "行为不等于身份"},
    "否定正面": {"特征": "把正面经历不当回事", "例子": "那只是运气好", "重构": "承认自己的努力和成就"}
}

REFRAME_PROMPTS = {
    "证据法": "支持这个想法的证据是什么？反对的证据呢？",
    "替代解释": "还有没有其他可能的解释？",
    "去灾难化": "最坏的情况是什么？我能承受吗？最好的情况是什么？",
    "朋友视角": "如果我的朋友有这个想法，我会怎么劝TA？",
    "比例思考": "这件事在一年后的我看来会有多重要？"
}

# 显式模式 → 扭曲类型（支持多标签）
PATTERNS = [
    # 灾难化：灾难性后果表述
    ("彻底完了",          "灾难化"),
    ("彻底毁灭",          "灾难化"),
    ("彻底完蛋",          "灾难化"),
    ("彻底垮了",          "灾难化"),
    ("彻底崩了",          "灾难化"),
    ("彻底失败",          "灾难化"),
    ("彻底无用",          "灾难化"),
    ("彻底无能",          "灾难化"),
    # 全或无思维（彻底+失败/无用/无能）
    ("彻底失败",          "全或无思维"),
    ("彻底无用",          "全或无思维"),
    ("彻底无能",          "全或无思维"),
    ("完全失败",          "全或无思维"),
    # 应当思维（完整表述优先）
    ("应当总是",          "应当思维"),
    ("应该总是",          "应当思维"),
    ("必须总是",          "应当思维"),
    ("我应当",            "应当思维"),
    ("我应该",            "应当思维"),
    # 贴标签
    ("我就是一个",        "贴标签"),
    ("我这人",            "贴标签"),
    # 读心术（需要明确的"他人想法"前缀）
    ("他们肯定",          "读心术"),
    ("他们一定",          "读心术"),
    ("他们觉得",          "读心术"),
    ("肯定觉得",          "读心术"),
    ("一定认为",          "读心术"),
    # 情绪推理（高确信判断）
    ("所以",              "情绪推理"),
    ("肯定",              "情绪推理"),   # "我肯定…"类高确信判断
    ("必然是",            "情绪推理"),
    # 心理过滤
    ("但是",              "心理过滤"),
    ("不过",              "心理过滤"),
    ("虽然",              "心理过滤"),
    # 否定正面
    ("只是",              "否定正面"),
    ("不过是",            "否定正面"),
    ("运气好",            "否定正面"),
]

# 全or无兜底关键词（仅在未触发任何模式时使用）
ALL_OR_NONE_FALLBACK = ["永远", "总是", "从不"]

def detect_distortion(thought):
    """检测认知扭曲类型"""
    detected = set()

    for pattern, distortion in PATTERNS:
        if pattern in thought:
            detected.add(distortion)

    if not detected:
        for kw in ALL_OR_NONE_FALLBACK:
            if kw in thought:
                detected.add("全或无思维")
                break

    return list(detected)

def generate_reframe(distortions):
    """生成重构建议"""
    suggestions = []
    for d in distortions:
        if d in COGNITIVE_DISTORTIONS:
            suggestions.append({
                "类型": d,
                "特征": COGNITIVE_DISTORTIONS[d]["特征"],
                "重构方向": COGNITIVE_DISTORTIONS[d]["重构"]
            })
    return suggestions

def generate_response(user_input):
    """生成响应"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from crisis_detector import is_crisis

    is_crisis_result, risk_level = is_crisis(user_input)

    if is_crisis_result and risk_level == "high":
        return {
            "type": "crisis",
            "risk_level": "high",
            "message": "谢谢你愿意说出来。我很在意你的状态。建议现在联系：全国心理援助热线400-161-99-95，或告诉身边信任的人。如有危险请直接拨打120/110。"
        }
    elif is_crisis_result and risk_level == "medium":
        return {
            "type": "crisis",
            "risk_level": "medium",
            "message": "我注意到你似乎正在经历一些困难。你愿意多说说吗？如果感觉难以承受，建议联系：全国心理援助热线400-161-99-95。"
        }

    distortions = detect_distortion(user_input)
    if distortions:
        reframes = generate_reframe(distortions)
        return {
            "type": "normal",
            "distortions": distortions,
            "reframes": reframes,
            "prompts": list(REFRAME_PROMPTS.values())[:3],
            "disclaimer": DISCLAIMER
        }

    return {
        "type": "normal",
        "message": "我听到你有一些想法。能详细说说是什么想法在脑海中浮现吗？",
        "disclaimer": DISCLAIMER
    }

def main():
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not user_input:
        print("请输入你想要处理的想法...")
        return

    resp = generate_response(user_input)
    print("\n=== Cognitive Reframe ===\n")
    print(json.dumps(resp, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
