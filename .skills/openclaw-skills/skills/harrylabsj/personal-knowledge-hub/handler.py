"""Personal Knowledge Hub - 个人知识枢纽"""
import json, re
from datetime import datetime

def parse_knowledge_input(text):
    result = {"action": None, "topic": None, "tags": []}
    if any(k in text for k in ["读", "书", "文章", "笔记"]): result["action"] = "capture"
    elif any(k in text for k in ["找", "搜", "查询", "复习"]): result["action"] = "retrieve"
    elif any(k in text for k in ["整理", "结构", "知识体系"]): result["action"] = "organize"
    cleaned = text.replace("读", "").replace("书", "").replace("文章", "").replace("笔记", "").replace("关于", "")
    result["topic"] = cleaned.strip()[:30]
    return result

def capture_note(topic, tags):
    lines = ["1. 核心观点（一句话）", "2. 关键论据（3条）", "3. 我的思考/疑问", "4. 行动指引（下一步）"]
    prompt = "\u8bf7\u8bb0\u5f55\u5173\u4e8e\u300c" + topic + "\u300d\u7684\u5185\u5bb9\uff1a\n" + "\n".join(lines)
    return {
        "note_id": "note-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "topic": topic,
        "tags": tags or ["\u672a\u5206\u7c7b"],
        "created": datetime.now().isoformat(),
        "status": "draft",
        "prompt": prompt
    }

def handle(text):
    parsed = parse_knowledge_input(text)
    if parsed["action"] == "capture":
        note = capture_note(parsed["topic"], parsed.get("tags", []))
        return {"action": "capture", "template": note, "message": "\u5df2\u521b\u5efa\u7b14\u8bb0\u6a21\u677f\u300c" + parsed["topic"] + "\u300d\uff0c\u8bf7\u586b\u5199\u5185\u5bb9"}
    elif parsed["action"] == "retrieve":
        return {"action": "retrieve", "message": "\u6b63\u5728\u68c0\u7d22\u5173\u4e8e\u300c" + parsed["topic"] + "\u300d\u7684\u5185\u5bb9...", "note": None}
    else:
        return {"action": "organize", "message": "\u6b63\u5728\u5206\u6790\u300c" + parsed["topic"] + "\u300d\u7684\u77e5\u8bc6\u7ed3\u6784...", "structure": None}

if __name__ == "__main__":
    for tc in ["\u6211\u60f3\u8bb0\u5f55\u4e00\u4e0b\u4eca\u5929\u8bfb\u5230\u7684\u5b66\u4e60\u65b9\u6cd5", "\u641c\u7d22\u5173\u4e8e\u521b\u9020\u529b\u7684\u7b14\u8bb0"]:
        r = handle(tc)
        print("Input: " + tc)
        print("  Action: " + r["action"] + " | " + r["message"])
        print()
