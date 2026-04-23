import argparse
import base64
import json
import sys
import urllib.request
import urllib.error
import os
import re
from datetime import datetime

API_URL = "https://smart.processon.com/v1/api/generate_diagram"


def normalize_title(title):
    if not title:
        return "processon-diagram"
    normalized = title.strip("，。；：、 ,.-_")
    if not normalized:
        return "processon-diagram"
    return normalized[:20]


def slugify_filename(title):
    if not title:
        return "processon-diagram"
    slug = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9_-]+", "-", title).strip("-_")
    if not slug:
        slug = "processon-diagram"
    return slug[:40]


def save_image_content(title, content_items, output_dir=None):
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "outputs", "processon")

    saved_paths = []
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    image_index = 1
    title = normalize_title(title)
    filename_slug = slugify_filename(title)

    for item in content_items:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "image":
            continue
        if item.get("mimeType") != "image/png":
            continue

        image_data = item.get("data", "")
        if not image_data:
            continue

        if image_index == 1:
            filename = f"{filename_slug}-{timestamp}.png"
        else:
            filename = f"{filename_slug}-{timestamp}-{image_index}.png"
        file_path = os.path.abspath(os.path.join(output_dir, filename))
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        saved_paths.append(file_path)
        image_index += 1

    return {
        "title": title,
        "filename_slug": filename_slug,
        "saved_paths": saved_paths,
    }

def generate_diagram(prompt, title=None):
    payload = {
        "prompt": prompt
    }

    def mcp_print(payload):
        print(json.dumps(payload, ensure_ascii=False))

    def mcp_print_text(text, data=None):
        payload = {"content": [{"type": "text", "text": text}]}
        if data is not None:
            payload["data"] = data
        mcp_print(payload)

    def normalize_content_items(content_items):
        normalized = []
        for item in content_items:
            if not isinstance(item, dict):
                continue
            normalized_item = dict(item)
            if "data" in normalized_item and "text" not in normalized_item and normalized_item.get("type") == "text":
                normalized_item["text"] = normalized_item["data"]
            normalized.append(normalized_item)
        return normalized

    def filter_display_content(content_items):
        filtered = []
        for item in content_items:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "image":
                filtered.append(item)
                continue
            if item.get("type") == "text":
                mime_type = item.get("mimeType")
                if mime_type == "text/plain":
                    continue
                filtered.append(item)
                continue
            filtered.append(item)
        return filtered

    def normalize_bearer(api_key):
        if not api_key:
            return None
        api_key = api_key.strip()
        if not api_key:
            return None
        if api_key.lower().startswith("bearer "):
            return api_key
        return f"Bearer {api_key}"

    def build_headers(api_key):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "ProcessOn-Architect-Skill/2.0"
        }
        bearer = normalize_bearer(api_key)
        if bearer:
            headers["Authorization"] = bearer
        return headers

    def do_request(headers):
        json_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(API_URL, data=json_payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)

    def build_credential_metadata():
        macos_command = 'export PROCESSON_API_KEY="<your-processon-api-key>"'
        windows_powershell_command = '$env:PROCESSON_API_KEY="<your-processon-api-key>"'
        windows_cmd_command = 'set PROCESSON_API_KEY=<your-processon-api-key>'
        return {
            "credential": {
                "name": "PROCESSON_API_KEY",
                "label": "ProcessOn API Key",
                "kind": "secret",
                "required": True,
                "envVar": "PROCESSON_API_KEY",
                "placeholder": "<your-processon-api-key>",
                "description": "用于 ProcessOn API 回退模式的鉴权密钥。",
            },
            "actions": [
                {
                    "type": "request_credential",
                    "credential": "PROCESSON_API_KEY",
                    "label": "配置 ProcessOn API Key",
                    "mode": "secret",
                },
                {
                    "type": "show_config_example",
                    "target": "processon-api",
                    "label": "查看配置示例",
                },
                {
                    "type": "copy_command",
                    "label": "复制 macOS/Linux 配置命令",
                    "command": macos_command,
                    "platform": ["macos", "linux"],
                },
                {
                    "type": "copy_command",
                    "label": "复制 Windows PowerShell 配置命令",
                    "command": windows_powershell_command,
                    "platform": ["windows"],
                    "shell": "powershell",
                },
                {
                    "type": "copy_command",
                    "label": "复制 Windows CMD 配置命令",
                    "command": windows_cmd_command,
                    "platform": ["windows"],
                    "shell": "cmd",
                },
                {
                    "type": "retry",
                    "label": "配置完成后重试",
                },
            ],
            "suggestedCommands": {
                "macos_linux": macos_command,
                "windows_powershell": windows_powershell_command,
                "windows_cmd": windows_cmd_command,
                "verify": "echo $PROCESSON_API_KEY",
                "retryPrompt": "继续生成流程图",
            },
            "interactive": {
                "canRequestCredential": True,
                "preferredAction": "request_credential",
            },
        }

    def build_missing_api_key_payload():
        hint = "\n".join([
            "当前还没有检测到可用的 ProcessOn 凭证，所以暂时无法直接生成图片版流程图。",
            "当前未使用 MCP，已回退到 API 请求模式。请先配置 PROCESSON_API_KEY，然后再次执行生成。",
            "",
            "如果当前宿主支持交互式凭证录入，请直接点击“配置 ProcessOn API Key”之类的控件完成填写。",
            "如果宿主没有弹出交互控件，请手动执行下面的命令：",
            "",
            "macOS/Linux:",
            "  export PROCESSON_API_KEY=\"<your-processon-api-key>\"",
            "Windows PowerShell:",
            "  $env:PROCESSON_API_KEY=\"<your-processon-api-key>\"",
            "Windows CMD:",
            "  set PROCESSON_API_KEY=<your-processon-api-key>",
            "",
            "配置完成后，重新发起“继续生成流程图”即可。",
            "如需确认是否配置成功，可执行：",
            "  echo $PROCESSON_API_KEY",
        ])
        payload = {
            "content": [{"type": "text", "text": hint}],
            "data": {
                "errorCode": "MISSING_API_KEY",
            },
        }
        payload["data"].update(build_credential_metadata())
        return payload

    def build_invalid_api_key_payload(http_message):
        hint = "\n".join([
            "检测到 PROCESSON_API_KEY，但鉴权失败。当前配置的 API Key 可能无效、已过期，或不适用于当前接口。",
            "",
            f"失败原因：{http_message}",
            "",
            "请检查：",
            "1. PROCESSON_API_KEY 是否填写正确",
            "2. 该 Key 是否具备 smart.processon.com 接口访问权限",
            "3. 是否误填了其他系统的 token",
        ])
        payload = {
            "content": [{"type": "text", "text": hint}],
            "data": {
                "errorCode": "INVALID_API_KEY",
            },
        }
        payload["data"].update(build_credential_metadata())
        return payload

    api_key = os.environ.get("PROCESSON_API_KEY", "")

    try:
        if not api_key.strip():
            mcp_print(build_missing_api_key_payload())
            sys.exit(1)
        result = do_request(build_headers(api_key))
        if isinstance(result, dict):
            content = None
            if isinstance(result.get("content"), list):
                content = result["content"]
            elif isinstance(result.get("data"), dict) and isinstance(result["data"].get("content"), list):
                content = result["data"]["content"]

            if content is not None:
                normalized_content = normalize_content_items(content)
                save_result = save_image_content(title, normalized_content)
                saved_paths = save_result["saved_paths"]
                output_content = filter_display_content(normalized_content)
                if saved_paths:
                    path_lines = [
                        f"图片标题：{save_result['title']}",
                        "图片已保存：",
                    ] + saved_paths
                    output_content.append({
                        "type": "text",
                        "text": "\n".join(path_lines)
                    })
                output_payload = {"content": output_content}
                if isinstance(result.get("data"), dict):
                    output_payload["data"] = result["data"]
                if saved_paths:
                    if "data" not in output_payload:
                        output_payload["data"] = {}
                    output_payload["data"].update({
                        "imageTitle": save_result["title"],
                        "savedImagePaths": saved_paths,
                        "primarySavedImagePath": saved_paths[0],
                        "preferredDisplay": "inline",
                        "showInlineIfPossible": True,
                    })
                mcp_print(output_payload)
                return

        raise ValueError("Invalid MCP response: missing 'content' array at top level or in 'data.content'")
            
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
            msg = f"HTTP {e.code} {e.reason}: {body}"
        except:
            msg = f"HTTP {e.code} {e.reason}"
        current_api_key = os.environ.get("PROCESSON_API_KEY", "").strip()
        if e.code in (401, 403) and not current_api_key:
            missing_payload = build_missing_api_key_payload()
            missing_payload["content"][0]["text"] = f"{msg}\n\n{missing_payload['content'][0]['text']}"
            mcp_print(missing_payload)
            sys.exit(1)
        if e.code in (401, 403) and current_api_key:
            mcp_print(build_invalid_api_key_payload(msg))
            sys.exit(1)
        mcp_print_text(msg)
        sys.exit(1)
        
    except urllib.error.URLError as e:
        mcp_print_text(f"Connection Error: {e.reason}")
        sys.exit(1)
        
    except Exception as e:
        mcp_print_text(str(e))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ProcessOn AI Diagram Generator (Zero Dependency)')
    parser.add_argument('prompt', type=str, help='The optimized prompt for the diagram')
    parser.add_argument('--title', type=str, default='processon-diagram', help='Short title for the saved image filename')
    
    args = parser.parse_args()
    
    generate_diagram(args.prompt, args.title)
