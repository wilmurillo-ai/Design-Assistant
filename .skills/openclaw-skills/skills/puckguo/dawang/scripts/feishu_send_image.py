#!/usr/bin/env python3
"""
飞书图片发送工具
用于将本地图片上传到飞书并获取 image_key，然后发送消息
"""

import requests
import sys
import os

def get_tenant_access_token():
    """获取飞书 tenant access token"""
    import json
    
    # 从环境变量获取
    app_id = os.environ.get('FEISHU_APP_ID')
    app_secret = os.environ.get('FEISHU_APP_SECRET')
    
    if not app_id or not app_secret:
        # 尝试从配置文件读取
        config_paths = [
            os.path.expanduser('~/.openclaw/config.json'),
            os.path.expanduser('~/.openclaw/feishu.json'),
        ]
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        app_id = config.get('feishu', {}).get('appId') or config.get('appId')
                        app_secret = config.get('feishu', {}).get('appSecret') or config.get('appSecret')
                        if app_id and app_secret:
                            break
                except:
                    continue
    
    if not app_id or not app_secret:
        raise ValueError("无法获取 Feishu App ID 和 App Secret，请设置环境变量或配置文件")
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") != 0:
        raise Exception(f"获取 token 失败: {result}")
    
    return result["tenant_access_token"]

def upload_image(image_path, token):
    """上传图片到飞书，获取 image_key"""
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(image_path, 'rb') as f:
        files = {
            'image': (os.path.basename(image_path), f, 'image/png')
        }
        data = {
            'image_type': 'message'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
    
    result = response.json()
    
    if result.get("code") != 0:
        raise Exception(f"上传图片失败: {result}")
    
    return result["data"]["image_key"]

def send_image_message(image_key, chat_id, token):
    """发送图片消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "receive_id_type": "chat_id"
    }
    
    # 构建消息内容
    content = {
        "image_key": image_key
    }
    
    import json
    data = {
        "receive_id": chat_id,
        "msg_type": "image",
        "content": json.dumps(content)
    }
    
    response = requests.post(url, headers=headers, params=params, json=data)
    result = response.json()
    
    if result.get("code") != 0:
        raise Exception(f"发送消息失败: {result}")
    
    return result

def main():
    if len(sys.argv) < 3:
        print("用法: python3 feishu_send_image.py <图片路径> <聊天ID>")
        print("示例: python3 feishu_send_image.py /path/to/image.png ou_xxx")
        sys.exit(1)
    
    image_path = sys.argv[1]
    chat_id = sys.argv[2]
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在 {image_path}")
        sys.exit(1)
    
    try:
        # 获取 token
        print("正在获取 access token...")
        token = get_tenant_access_token()
        print("✓ 获取 token 成功")
        
        # 上传图片
        print(f"正在上传图片: {image_path}")
        image_key = upload_image(image_path, token)
        print(f"✓ 图片上传成功，image_key: {image_key}")
        
        # 发送消息
        print(f"正在发送消息到: {chat_id}")
        result = send_image_message(image_key, chat_id, token)
        print(f"✓ 消息发送成功!")
        print(f"  Message ID: {result['data']['message_id']}")
        
        # 输出 image_key 供其他工具使用
        print(f"\nIMAGE_KEY:{image_key}")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
