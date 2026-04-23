#!/usr/bin/env python3
"""上传TTS音频到飞书并插入文档"""
import subprocess, json, os, re
from datetime import datetime

SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspaces/dawang/scripts/podcasts")
REPORT_PATH = os.path.expanduser("~/.openclaw/workspaces/dawang/scripts/podcasts/latest_report.md")
APP_ID = "cli_a92d7a49c9399bca"
APP_SECRET = "45KmSon6mcZ1hPsSEdXtnLkDEqII5QAw"
USER_ID = "ou_2ef0900a3185db3f04cb7796f12e6ca1"

def get_access_token():
    r = subprocess.run([
        'curl', '-s', '--noproxy', '*', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})
    ], capture_output=True, text=True, timeout=15)
    resp = json.loads(r.stdout)
    return resp.get("tenant_access_token", "") if resp.get("code") == 0 else None

def upload_and_send_audio(audio_path):
    """上传音频并作为消息发送，返回(message_link, file_key)
    Feishu 语音消息需要 opus 格式，必须转换
    """
    token = get_access_token()
    if not token:
        return None, None
    
    filename = os.path.basename(audio_path)
    opus_path = audio_path
    
    # 如果是 MP3，先转成 opus
    if audio_path.endswith('.mp3'):
        opus_path = audio_path.replace('.mp3', '.opus')
        print(f"  🔄 转换 MP3 -> opus...")
        r_conv = subprocess.run([
            'ffmpeg', '-y', '-i', audio_path,
            '-c:a', 'libopus', '-b:a', '128k',
            opus_path
        ], capture_output=True, text=True, timeout=60)
        if r_conv.returncode != 0:
            print(f"  ⚠️ opus转换失败: {r_conv.stderr[-100:]}")
            return None, None
        print(f"  ✅ opus转换成功")
    
    # Step 1: Upload as opus
    r1 = subprocess.run([
        'curl', '-s', '--noproxy', '*', '-X', 'POST',
        'https://open.feishu.cn/open-apis/im/v1/files?receive_id_type=open_id',
        '-H', f'Authorization: Bearer {token}',
        '-F', f'file=@{opus_path}',
        '-F', 'file_name=' + filename.replace('.mp3', '.opus'),
        '-F', 'file_type=opus',
        '-F', f'receive_id={USER_ID}'
    ], capture_output=True, text=True, timeout=60)

    try:
        resp1 = json.loads(r1.stdout)
        code1 = resp1.get('code')
        if code1 != 0:
            print(f"  ⚠️ 上传失败: code={code1} msg={resp1.get('msg')}")
            return None, None
        file_key = resp1.get('data', {}).get('file_key', '')
        print(f"  ✅ 上传成功: file_key={file_key}")
    except:
        return None, None

    # Step 2: Send audio message
    r2 = subprocess.run([
        'curl', '-s', '--noproxy', '*', '-X', 'POST',
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            "receive_id": USER_ID,
            "msg_type": "audio",
            "content": json.dumps({"file_key": file_key})
        })
    ], capture_output=True, text=True, timeout=30)

    try:
        resp2 = json.loads(r2.stdout)
        code2 = resp2.get('code')
        if code2 == 0:
            msg_id = resp2.get('data', {}).get('message_id', '')
            chat_id = get_chat_id_from_msg(token, msg_id)
            if chat_id:
                msg_link = f"https://feishu.cn/im?安康={chat_id}&安康={msg_id}"
                return msg_link, file_key
            return f"om_{msg_id}", file_key
        else:
            print(f"  ⚠️ 发送消息失败: code={code2} msg={resp2.get('msg')}")
    except:
        pass
    return file_key, None

def get_chat_id_from_msg(token, msg_id):
    """从消息ID获取chat_id"""
    r = subprocess.run([
        'curl', '-s', '--noproxy', '*',
        f'https://open.feishu.cn/open-apis/im/v1/messages/{msg_id}',
        '-H', f'Authorization: Bearer {token}'
    ], capture_output=True, text=True, timeout=15)
    try:
        resp = json.loads(r.stdout)
        items = resp.get('data', {}).get('items', [])
        if items:
            return items[0].get('chat_id', '')
    except:
        pass
    return None

def make_file_public(file_key):
    """尝试设置文件为公开"""
    token = get_access_token()
    if not token:
        return False
    # 尝试设置公开
    r = subprocess.run([
        'curl', '-s', '--noproxy', '*', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/drive/v1/permissions/{file_key}/public?type=file',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', '{"link_share_entity": "anyone_readable"}'
    ], capture_output=True, text=True, timeout=15)
    resp = json.loads(r.stdout)
    return resp.get("code") == 0

def create_doc(title):
    token = get_access_token()
    if not token:
        return None
    r = subprocess.run([
        'curl', '-s', '--noproxy', '*', '-X', 'POST',
        'https://open.feishu.cn/open-apis/docx/v1/documents',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({"title": title})
    ], capture_output=True, text=True, timeout=15)
    resp = json.loads(r.stdout)
    return resp.get("data", {}).get("document", {}).get("document_id") if resp.get("code") == 0 else None

def set_public(doc_token):
    token = get_access_token()
    if not token:
        return
    r = subprocess.run([
        'curl', '-s', '--noproxy', '*', '-X', 'PATCH',
        f'https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/public?type=docx',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', '{"link_share_entity": "anyone_readable"}'
    ], capture_output=True, text=True, timeout=15)

def write_blocks(doc_token, content):
    """写入文档内容块（TTS音频通过聊天发送，不嵌入文档）"""
    token = get_access_token()
    if not token:
        return False
    
    lines = content.split('\n')
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('# '):
            blocks.append({"block_type": 3, "heading1": {"elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_element_style": {}}}], "style": {}}})
        elif line.startswith('## '):
            blocks.append({"block_type": 4, "heading2": {"elements": [{"type": "text_run", "text_run": {"content": line[3:], "text_element_style": {}}}], "style": {}}})
        elif line.startswith('### '):
            blocks.append({"block_type": 5, "heading3": {"elements": [{"type": "text_run", "text_run": {"content": line[4:], "text_element_style": {}}}], "style": {}}})
        elif line.startswith('- '):
            blocks.append({"block_type": 12, "bullet": {"elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_element_style": {}}}], "style": {}}})
        elif line.startswith('---') or line.strip() == '---':
            blocks.append({"block_type": 22, "divider": {}})
        elif line.strip():
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line, "text_element_style": {}}}], "style": {}}})
        i += 1
    
    # 分批写入
    BATCH_SIZE = 50
    for i in range(0, len(blocks), BATCH_SIZE):
        batch = blocks[i:i+BATCH_SIZE]
        payload = json.dumps({"children": batch, "index": i})
        r = subprocess.run([
            'curl', '-s', '--noproxy', '*', '-X', 'POST',
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children',
            '-H', f'Authorization: Bearer {token}',
            '-H', 'Content-Type: application/json',
            '-d', payload
        ], capture_output=True, text=True, timeout=30)
        resp = json.loads(r.stdout)
        if resp.get("code") != 0:
            print(f"  写入失败: {resp.get('msg')}")
            return False
    return True

# ========== 主流程 ==========
print("="*50)
print("TTS音频 -> 飞书文档")
print("="*50)

# 1. 加载TTS文件
print("\n[1/3] 加载TTS文件...")
with open(os.path.join(SCRIPT_DIR, "tts_audio_files.json")) as f:
    tts_files = json.load(f)
print(f"  {len(tts_files)} 个TTS文件")

# 2. 上传并发送音频，获取消息链接
print("\n[2/3] 上传音频并发送...")
TTS_MSG_LINKS = {}
for fname, fpath in tts_files.items():
    msg_link, file_key = upload_and_send_audio(fpath)
    if msg_link:
        TTS_MSG_LINKS[fname] = msg_link
        print(f"  ✅ {fname} -> {msg_link}")
    else:
        print(f"  ⚠️ {fname} 发送失败")
        TTS_MSG_LINKS[fname] = None

# 3. 创建文档
print("\n[3/3] 创建飞书文档...")
with open(REPORT_PATH) as f:
    content = f.read()

# 构建内容（报告已不含TTS链接，TTS通过聊天发送）
new_content = content

today = datetime.now().strftime("%Y-%m-%d")
doc_title = f"播客精选日报 {today} 🔊"
print(f"  文档标题: {doc_title}")
doc_id = create_doc(doc_title)
if not doc_id:
    print("  ❌ 创建失败")
    exit(1)
print(f"  ✅ doc_id={doc_id}")

set_public(doc_id)

if write_blocks(doc_id, new_content):
    doc_link = f"https://feishu.cn/docx/{doc_id}"
    print(f"  ✅ 内容写入成功")
    print(f"  🔗 {doc_link}")
    
    # 保存
    with open(os.path.join(SCRIPT_DIR, "feishu_doc_link.txt"), 'w') as f:
        f.write(doc_link)
    print(f"  ✅ 链接已保存")
    
    # 同时更新总表
    master_id = None
    mfile = os.path.join(SCRIPT_DIR, "master_doc_id.txt")
    if os.path.exists(mfile):
        with open(mfile) as f:
            master_id = f.read().strip()
    
    if master_id:
        # 追加到总表
        bullet = f"{today}  {doc_link}  ✅ {len(TTS_MSG_LINKS)}个音频"
        payload = json.dumps({"children": [{"block_type": 12, "bullet": {"elements": [{"type": "text_run", "text_run": {"content": bullet, "text_element_style": {}}}], "style": {}}}], "index": 5})
        token = get_access_token()
        subprocess.run([
            'curl', '-s', '--noproxy', '*', '-X', 'POST',
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{master_id}/blocks/{master_id}/children',
            '-H', f'Authorization: Bearer {token}',
            '-H', 'Content-Type: application/json',
            '-d', payload
        ], capture_output=True, timeout=15)
        print(f"  ✅ 已追加到总表")

print("\n" + "="*50)
print("完成!")
print("="*50)
