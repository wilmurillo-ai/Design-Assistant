# IndexTTS 飞书应用集成指南

> 📌 **重要说明**: 将 IndexTTS 技能上架到飞书需要开发一个**飞书自建应用**，这与 ClawHub 技能是不同的分发渠道。

---

## 🎯 方案概述

### 方案 A: 飞书自建机器人（推荐）
- **开发周期**: 1-2 天
- **难度**: ⭐⭐ 中等
- **适用场景**: 企业内部使用，快速部署
- **特点**: 通过飞书开放平台创建机器人，后端调用 IndexTTS API

### 方案 B: 飞书小程序
- **开发周期**: 1-2 周
- **难度**: ⭐⭐⭐⭐ 较高
- **适用场景**: 需要 UI 界面、复杂交互
- **特点**: 完整的飞书原生应用体验

### 方案 C: 飞书集成 OpenClaw（最简单）
- **开发周期**: 几小时
- **难度**: ⭐ 简单
- **适用场景**: 已有 OpenClaw 部署
- **特点**: 通过 OpenClaw 的飞书集成间接使用技能

---

## 📋 方案 A: 飞书自建机器人开发指南

### 第一步：准备工作

1. **注册飞书开放平台账号**
   - 访问：https://open.feishu.cn/
   - 使用企业账号登录（需要企业管理员权限）

2. **准备 IndexTTS API 签名**
   - 确保已购买 IndexTTS 企业会员
   - 获取 API 签名（从 IndexTTS 开发者中心）

3. **准备服务器**
   - 需要一台可公网访问的服务器（用于部署后端服务）
   - 或使用内网穿透工具（如 ngrok、花生壳）

---

### 第二步：创建飞书应用

1. **登录飞书开放平台**
   - 进入「应用开发」→「自建应用」
   - 点击「创建应用」

2. **填写应用信息**
   ```
   应用名称：IndexTTS 语音助手
   应用图标：上传 TTS 相关图标
   应用描述：智能语音合成助手，支持声音克隆和情感合成
   ```

3. **添加应用能力**
   - 在「应用能力」页面添加：
     - ✅ 机器人
     - ✅ 消息与群组（如需群聊使用）

4. **配置机器人**
   - 进入「机器人」配置页
   - 设置机器人名称和头像
   - 配置回调地址（后续部署后端服务后填写）

---

### 第三步：配置权限

在「权限管理」页面添加以下权限：

| 权限名称 | 权限标识 | 用途 |
|---------|---------|------|
| 发送消息 | `im:message` | 向用户发送语音合成结果 |
| 读取消息 | `im:message:read` | 接收用户指令 |
| 群组机器人 | `im:chat` | 在群聊中使用 |

---

### 第四步：开发后端服务

#### 项目结构
```
feishu-indextts-bot/
├── app.py                 # 主应用（Flask/FastAPI）
├── config.py              # 配置文件
├── indextts_client.py     # IndexTTS API 客户端
├── feishu_client.py       # 飞书 API 客户端
├── requirements.txt       # Python 依赖
└── .env                   # 环境变量
```

#### 核心代码示例

**requirements.txt**
```txt
flask==2.3.0
requests==2.31.0
python-dotenv==1.0.0
```

**config.py**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# 飞书配置
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')
FEISHU_VERIFICATION_TOKEN = os.getenv('FEISHU_VERIFICATION_TOKEN')
FEISHU_ENCRYPTION_KEY = os.getenv('FEISHU_ENCRYPTION_KEY')

# IndexTTS 配置
INDEX_API_SIGN = os.getenv('INDEX_API_SIGN')
INDEX_BASE_URL = os.getenv('INDEX_BASE_URL', 'https://openapi.indextts.cn')

# 服务器配置
PORT = int(os.getenv('PORT', 5000))
```

**indextts_client.py**
```python
import requests
import hashlib
import time

class IndexTTSClient:
    def __init__(self, api_sign, base_url='https://openapi.indextts.cn'):
        self.api_sign = api_sign
        self.base_url = f"{base_url}/api/third"
    
    def _get_headers(self):
        return {'sign': self.api_sign}
    
    def create_model(self, name, audio_path, describe=''):
        """创建声音模型"""
        url = f"{self.base_url}/reference/upload"
        with open(audio_path, 'rb') as f:
            files = {'file': f}
            data = {'name': name, 'describe': describe}
            response = requests.post(url, headers=self._get_headers(), files=files, data=data)
        return response.json()
    
    def list_models(self, page=1, page_size=10):
        """获取模型列表"""
        url = f"{self.base_url}/reference/list"
        params = {'page': page, 'pageSize': page_size}
        response = requests.get(url, headers=self._get_headers(), params=params)
        return response.json()
    
    def tts_create(self, text, audio_id, style=1, speed=1.0, genre=0, **kwargs):
        """创建语音合成任务"""
        url = f"{self.base_url}/tts/create"
        data = {
            'text': text,
            'audioId': audio_id,
            'style': style,
            'speed': speed,
            'genre': genre
        }
        # 添加情感参数
        if genre == 1:
            for emotion in ['happy', 'angry', 'sad', 'afraid', 'disgusted', 'melancholic', 'surprised', 'calm']:
                if emotion in kwargs:
                    data[emotion] = kwargs[emotion]
        if genre == 2 and 'emotion_path' in kwargs:
            data['emotionPath'] = kwargs['emotion_path']
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        return response.json()
    
    def tts_result(self, task_id):
        """查询合成结果"""
        url = f"{self.base_url}/tts/result"
        params = {'taskId': task_id}
        response = requests.get(url, headers=self._get_headers(), params=params)
        return response.json()
    
    def download_audio(self, voice_url, save_path):
        """下载音频文件"""
        response = requests.get(voice_url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
```

**app.py**
```python
from flask import Flask, request, jsonify
import requests
import os
import tempfile
from config import *
from indextts_client import IndexTTSClient

app = Flask(__name__)
tts_client = IndexTTSClient(INDEX_API_SIGN, INDEX_BASE_URL)

# 飞书 API 基础 URL
FEISHU_API_BASE = 'https://open.feishu.cn/open-apis'

def get_feishu_access_token():
    """获取飞书访问令牌"""
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    data = {
        'app_id': FEISHU_APP_ID,
        'app_secret': FEISHU_APP_SECRET
    }
    response = requests.post(url, json=data)
    result = response.json()
    return result.get('tenant_access_token')

def send_message_to_feishu(open_id, content, content_type='text'):
    """发送消息到飞书"""
    token = get_feishu_access_token()
    url = f"{FEISHU_API_BASE}/im/v1/messages"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'receive_id': open_id,
        'msg_type': content_type,
        'content': content
    }
    params = {'receive_id_type': 'open_id'}
    response = requests.post(url, headers=headers, json=data, params=params)
    return response.json()

@app.route('/webhook', methods=['POST'])
def feishu_webhook():
    """处理飞书回调"""
    data = request.json
    
    # 处理 URL 验证挑战
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    # 处理消息事件
    if data.get('type') == 'im.message.receive_v1':
        event = data.get('event', {})
        message = event.get('message', {})
        sender = event.get('sender', {})
        
        # 获取用户信息
        user_id = sender.get('sender_id', {}).get('open_id')
        chat_type = message.get('chat_type')
        content = message.get('content')
        
        # 解析消息内容（飞书消息是 JSON 字符串）
        import json
        msg_content = json.loads(content)
        text = msg_content.get('text', '')
        
        # 处理指令
        if text.startswith('/tts '):
            # 语音合成指令
            tts_text = text[5:]  # 去掉 "/tts " 前缀
            
            # 获取默认声音模型（需要先配置或让用户选择）
            models = tts_client.list_models()
            if models.get('code') == 0 and models.get('data', {}).get('list'):
                audio_id = models['data']['list'][0]['audioId']
                
                # 创建合成任务
                result = tts_client.tts_create(tts_text, audio_id)
                
                if result.get('code') == 0:
                    task_id = result['data']['taskId']
                    
                    # 等待合成完成（轮询）
                    import time
                    for _ in range(10):
                        time.sleep(2)
                        task_result = tts_client.tts_result(task_id)
                        if task_result.get('data', {}).get('status') == 2:
                            voice_url = task_result['data'].get('voiceUrl')
                            if voice_url:
                                # 发送音频消息
                                audio_content = json.dumps({
                                    'file_key': upload_to_feishu(voice_url)
                                })
                                send_message_to_feishu(user_id, audio_content, 'audio')
                                send_message_to_feishu(user_id, json.dumps({'text': '✅ 语音合成完成！'}))
                            break
                    
                    if task_result.get('data', {}).get('status') != 2:
                        send_message_to_feishu(user_id, json.dumps({'text': '⏳ 合成处理中，请稍后重试'}))
                else:
                    send_message_to_feishu(user_id, json.dumps({'text': f'❌ 合成失败：{result.get("msg")}'}))
            else:
                send_message_to_feishu(user_id, json.dumps({'text': '❌ 未找到声音模型，请先创建模型'}))
        
        elif text.startswith('/models'):
            # 查询模型列表
            models = tts_client.list_models()
            if models.get('code') == 0:
                model_list = models.get('data', {}).get('list', [])
                text_response = '📋 声音模型列表:\n\n' + '\n'.join([
                    f"• {m['name']} (ID: {m['audioId'][:8]}...)"
                    for m in model_list
                ])
                send_message_to_feishu(user_id, json.dumps({'text': text_response}))
    
    return jsonify({'success': True})

def upload_to_feishu(file_url):
    """上传文件到飞书（获取 file_key）"""
    token = get_feishu_access_token()
    
    # 下载文件
    response = requests.get(file_url)
    
    # 上传到飞书
    url = f"{FEISHU_API_BASE}/im/v1/files"
    headers = {'Authorization': f'Bearer {token}'}
    files = {'file': ('audio.wav', response.content, 'audio/wav')}
    result = requests.post(url, headers=headers, files=files).json()
    
    return result.get('data', {}).get('file_key')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
```

**.env.example**
```bash
# 飞书配置（从飞书开放平台获取）
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxxxxxxx
FEISHU_ENCRYPTION_KEY=xxxxxxxxxxxxxxxxxxxxx

# IndexTTS 配置
INDEX_API_SIGN=你的 API 签名
INDEX_BASE_URL=https://openapi.indextts.cn

# 服务器配置
PORT=5000
```

---

### 第五步：部署服务

1. **本地测试**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

2. **使用 ngrok 暴露本地服务（测试用）**
   ```bash
   ngrok http 5000
   ```

3. **配置飞书回调地址**
   - 在飞书开放平台「事件订阅」页面
   - 填写回调 URL：`https://your-domain.com/webhook`
   - 完成验证

4. **生产部署**
   - 使用云服务器（阿里云、腾讯云等）
   - 或使用 PaaS 平台（Railway、Render、Vercel 等）
   - 配置 HTTPS（飞书要求 HTTPS）

---

### 第六步：发布应用

1. **版本管理**
   - 在飞书开放平台创建新版本
   - 填写版本说明

2. **提交审核**
   - 企业内部应用：通常自动通过
   - 公开应用：需要飞书官方审核（1-3 个工作日）

3. **安装应用**
   - 企业内部：管理员在后台安装
   - 公开应用：用户在飞书应用中心安装

---

## 🚀 快速启动命令

```bash
# 1. 创建项目目录
mkdir feishu-indextts-bot
cd feishu-indextts-bot

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install flask requests python-dotenv

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 5. 运行服务
python app.py

# 6. 本地测试（使用 ngrok）
ngrok http 5000
```

---

## 📱 用户指令示例

在飞书中与机器人交互：

```
/tts 你好，这是测试文本
/models
/create-model 我的声音 voice.wav
```

---

## ⚠️ 注意事项

1. **API 调用限制**
   - IndexTTS 企业会员有配额限制
   - 飞书 API 也有调用频率限制

2. **音频文件有效期**
   - IndexTTS 合成的音频 24 小时后失效
   - 建议用户及时下载保存

3. **安全性**
   - 不要将 API 签名硬编码到代码中
   - 使用环境变量管理敏感信息
   - 飞书回调需要验证签名

4. **审核要求**
   - 如需公开发布，需符合飞书应用审核规范
   - 准备应用截图、使用说明等材料

---

## 📞 相关资源

- **飞书开放平台**: https://open.feishu.cn/
- **飞书 API 文档**: https://open.feishu.cn/document/
- **IndexTTS API 文档**: https://indextts.cn/main/developer
- **ClawHub 技能**: https://clawhub.ai/skills/indextts-voice

---

## 💡 需要帮助？

如果你需要我帮你：
1. 生成完整的飞书应用代码
2. 配置飞书开放平台
3. 部署到服务器
4. 提交应用审核

请告诉我具体需要哪方面的帮助！
