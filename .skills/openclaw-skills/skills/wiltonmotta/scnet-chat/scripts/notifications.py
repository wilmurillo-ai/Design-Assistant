#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet 通知模块 - 统一处理各种通知渠道

支持的通知方式：
- 飞书（Feishu/Lark）
"""

import json
import os
import urllib.request
import ssl
from typing import Optional


class NotificationError(Exception):
    """通知发送异常"""
    pass


class FeishuNotifier:
    """飞书通知器"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        初始化飞书通知器
        
        Args:
            webhook_url: 飞书 webhook URL，如果为None则从配置文件读取
        """
        self.webhook_url = webhook_url or self._load_webhook_from_config()
    
    def _load_webhook_from_config(self) -> Optional[str]:
        """从配置文件加载 webhook URL"""
        # 尝试多个可能的配置文件路径
        config_paths = [
            os.path.expanduser("~/.openclaw/skills/feishu-notify/config.json"),
            os.path.expanduser("~/.openclaw/openclaw.json"),
        ]
        
        for config_path in config_paths:
            if not os.path.exists(config_path):
                continue
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # 处理可能的尾随逗号
                import re
                config_content = re.sub(r',(\s*[}\]])', r'\1', config_content)
                config = json.loads(config_content)
                
                # 方式1: 从 feishu-notify 配置读取
                if 'webhooks' in config:
                    webhook = config.get('webhooks', {}).get('default')
                    if webhook:
                        return webhook
                
                # 方式2: 从 channels.feishu 读取
                if 'channels' in config and 'feishu' in config['channels']:
                    webhook = config['channels']['feishu'].get('webhook')
                    if webhook:
                        return webhook
                
                # 方式3: 从 skills.*.env 读取
                if 'skills' in config:
                    for skill_name, skill_config in config['skills'].items():
                        if isinstance(skill_config, dict):
                            if 'env' in skill_config and 'FEISHU_WEBHOOK' in skill_config['env']:
                                return skill_config['env']['FEISHU_WEBHOOK']
                            # 检查 entries
                            if 'entries' in skill_config:
                                for entry_name, entry_config in skill_config['entries'].items():
                                    if isinstance(entry_config, dict) and 'env' in entry_config:
                                        if 'FEISHU_WEBHOOK' in entry_config['env']:
                                            return entry_config['env']['FEISHU_WEBHOOK']
            
            except Exception:
                continue
        
        return None
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """创建SSL上下文（禁用证书验证）"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    
    def send_text(self, message: str) -> bool:
        """
        发送文本消息
        
        Args:
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("⚠️ 飞书 webhook URL 未配置")
            return False
        
        payload = {
            "msg_type": "text",
            "content": {"text": message}
        }
        
        return self._send_request(payload)
    
    def send_card(self, title: str, content: str, template: str = "blue") -> bool:
        """
        发送富文本卡片消息
        
        Args:
            title: 卡片标题
            content: 卡片内容（支持 Markdown）
            template: 卡片颜色主题 (blue/green/red/orange/purple)
            
        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("⚠️ 飞书 webhook URL 未配置")
            return False
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": template
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }
        
        return self._send_request(payload)
    
    def _send_request(self, payload: dict) -> bool:
        """发送HTTP请求"""
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            ctx = self._create_ssl_context()
            
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                success = result.get('code') == 0
                if success:
                    print("✅ 飞书通知发送成功")
                else:
                    print(f"❌ 飞书通知发送失败: {result}")
                return success
                
        except Exception as e:
            print(f"❌ 飞书通知发送异常: {e}")
            return False


# 便捷函数
def send_feishu_text(message: str, webhook_url: Optional[str] = None) -> bool:
    """
    发送飞书文本消息（便捷函数）
    
    Args:
        message: 消息内容
        webhook_url: 可选的 webhook URL
        
    Returns:
        是否发送成功
    """
    notifier = FeishuNotifier(webhook_url)
    return notifier.send_text(message)


def send_feishu_card(title: str, content: str, template: str = "blue", 
                     webhook_url: Optional[str] = None) -> bool:
    """
    发送飞书卡片消息（便捷函数）
    
    Args:
        title: 卡片标题
        content: 卡片内容
        template: 卡片颜色主题
        webhook_url: 可选的 webhook URL
        
    Returns:
        是否发送成功
    """
    notifier = FeishuNotifier(webhook_url)
    return notifier.send_card(title, content, template)


# 导出
__all__ = [
    'FeishuNotifier',
    'NotificationError',
    'send_feishu_text',
    'send_feishu_card',
]
