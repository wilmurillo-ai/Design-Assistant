#!/usr/bin/env python3
"""深知可信问答 - API 调用脚本"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def _load_config():
    """从 OpenClaw 配置文件读取环境变量（兜底机制）。

    优先级：进程环境变量 > skills.entries.env > 顶层 env
    """
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if not os.path.isfile(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _get_env(name, config=None):
    """获取环境变量，兜底读取 OpenClaw 配置文件。"""
    val = os.environ.get(name)
    if val:
        return val

    if config is None:
        config = _load_config()

    try:
        val = config["skills"]["entries"]["dknowc-qa"]["env"][name]
        if val:
            return val
    except (KeyError, TypeError):
        pass

    try:
        val = config["env"][name]
        if val:
            return val
    except (KeyError, TypeError):
        pass

    return None


def ask(question, area=None, scope=None, material=False, recommended=False, session_id=None):
    config = _load_config()
    api_key = _get_env("DKNOWC_QA_API_KEY", config)
    endpoint = _get_env("DKNOWC_QA_ENDPOINT", config)

    if not api_key:
        print("错误：未配置 DKNOWC_QA_API_KEY", file=sys.stderr)
        print("请提供深知可信问答的 API Key，OpenClaw 会自动写入配置。", file=sys.stderr)
        print("获取指南见：https://platform.dknowc.cn", file=sys.stderr)
        sys.exit(1)

    if not endpoint:
        print("错误：未配置 DKNOWC_QA_ENDPOINT", file=sys.stderr)
        print("请提供深知可信问答的调用地址，格式：", file=sys.stderr)
        print("https://open.dnowc.cn/chat/trusted/unification/{你的AppID}", file=sys.stderr)
        sys.exit(1)

    # 构建请求参数
    payload = {"input": question, "knowledgeServiceType": "credibleChat"}

    if area:
        payload["area"] = area
    if scope:
        payload["credibleChatScope"] = scope
    if material:
        payload["material"] = True
    if recommended:
        payload["recommendedQuestions"] = True
    if session_id:
        payload["sessionId"] = session_id

    # 发送请求
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, method="POST")
    req.add_header("api-key", api_key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8").replace("\x00", "")
            body = json.loads(raw)
    except urllib.error.HTTPError as e:
        code = e.code
        if code == 401:
            print("错误：API Key 无效，请检查配置", file=sys.stderr)
        elif code == 403:
            print("错误：权限不足，请检查 API Key 对应的应用权限", file=sys.stderr)
        elif code == 429:
            print("错误：余额不足，请登录 https://platform.dknowc.cn 充值", file=sys.stderr)
        else:
            print(f"错误：HTTP {code} - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"错误：网络请求失败 - {e.reason}", file=sys.stderr)
        sys.exit(1)

    # 输出格式化结果
    safe_type = body.get("safeType", "")
    knowledge_scope = body.get("knowledgeScope", "")

    print(f"=== 深知可信问答 ===")
    print(f"问题：{question}")
    print(f"安全状态：{safe_type}")
    if knowledge_scope:
        scope_map = {"Norms": "规范性知识", "Mix": "混合知识", "ChitChat": "闲聊", "Other": "其他"}
        print(f"知识范围：{scope_map.get(knowledge_scope, knowledge_scope)}")
    print()

    resp_data = body.get("resp", {})

    # 地域提示语
    area_tip = resp_data.get("areaTip", "")
    if area_tip:
        print(f"提示：{area_tip}")
        print()

    # 推断地域
    resp_area = body.get("area", "")
    if resp_area:
        print(f"识别地域：{resp_area}")
        print()

    # 主要内容
    content = resp_data.get("content", "")
    if content:
        print(content)
    else:
        print("（此问题不在政策法规知识范围内，建议使用通用模型回答）")

    # 参考材料
    ref_materials = body.get("referenceMaterials", [])
    if ref_materials:
        print()
        print("=== 参考材料 ===")
        for rm in ref_materials:
            rm_title = rm.get("title", "")
            rm_url = rm.get("sourceUrl", "")
            rm_date = rm.get("createDate", "")
            print(f"  · {rm_title}")
            if rm_date:
                print(f"    发布日期：{rm_date}")
            if rm_url:
                print(f"    源网址：{rm_url}")
        print()

    # 输出原始 JSON（供程序化使用）
    print("=== RAW_JSON_START ===")
    print(json.dumps(body, ensure_ascii=False, indent=2))
    print("=== RAW_JSON_END ===")

    return body


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="深知可信问答")
    parser.add_argument("question", help="问题内容")
    parser.add_argument("--area", help="用户地域，如 北京市、广东省")
    parser.add_argument("--scope", choices=["onlyNorms", "needNorms", "all"],
                        help="问答范围：onlyNorms 仅政务、needNorms 政务+公共服务、all 全领域")
    parser.add_argument("--material", action="store_true", help="返回参考材料及引用角标")
    parser.add_argument("--recommended", action="store_true", help="返回猜你想问列表")
    parser.add_argument("--session-id", help="会话ID，用于多轮对话上下文")

    args = parser.parse_args()

    ask(
        question=args.question,
        area=args.area,
        scope=args.scope,
        material=args.material,
        recommended=args.recommended,
        session_id=args.session_id,
    )
