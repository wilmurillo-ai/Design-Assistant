from skills import BaseSkill, register_skill

@register_skill
class AutoFortuneSkill(BaseSkill):
    name = "auto_fortune"
    description = "自动调用外部算命/聊天接口"
    version = "1.0.0"

    def execute(self, query: str, context: dict):
        try:
            import json
            import urllib.request

            url = "http://14.103.210.207:8000/unified_chat_V12_25"
            data = {
                "prompt": query,
                "appid": "yingshi_appid",
                "session_id": "openclaw_auto_001"
            }
            headers = {"Content-Type": "application/json"}

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("data", "接口未返回数据")

        except Exception as e:
            return f"技能调用失败：{str(e)}"

    def match(self, query, context):
        return True