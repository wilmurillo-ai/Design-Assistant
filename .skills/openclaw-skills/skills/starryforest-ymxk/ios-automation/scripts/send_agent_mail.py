#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送符合 StarryForest Agent Mail API v1 协议的邮件
使用 126 邮箱发送
"""

import smtplib
import json
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from email.header import Header
import argparse

# 邮箱配置
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "starryforest_ymxk@126.com"
SMTP_PASSWORD = "VCddC36LS9CRjd36"

def create_agent_mail(to_email, title, actions):
    """
    创建符合 Agent Mail API v1 的邮件
    
    Args:
        to_email: 收件人邮箱
        title: 邮件标题
        actions: 动作列表
    
    Returns:
        MIMEMultipart 对象
    """
    import uuid
    from datetime import datetime
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = Header(title, 'utf-8')
    msg['Date'] = formatdate(localtime=True)
    
    # 生成唯一 ID
    msg_id = f"agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
    
    # 构建 Agent Payload
    payload = {
        "version": 1,
        "token": "starryforest_agent",
        "id": msg_id,
        "actions": actions
    }
    
    # 邮件正文
    body = f"""{title}

AGENT_PAYLOAD_BEGIN
{json.dumps(payload, ensure_ascii=False, indent=2)}
AGENT_PAYLOAD_END
"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    return msg

def send_mail(to_email, title, actions):
    """
    发送邮件
    
    Args:
        to_email: 收件人邮箱
        title: 邮件标题
        actions: 动作列表
    
    Returns:
        成功返回 True，失败返回 False
    """
    try:
        # 创建邮件
        msg = create_agent_mail(to_email, title, actions)
        
        # 连接 SMTP 服务器并发送
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ 邮件发送成功: {to_email}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='发送 StarryForest Agent 邮件')
    parser.add_argument('--to', required=True, help='收件人邮箱')
    parser.add_argument('--title', default='自动化推送', help='邮件标题')
    parser.add_argument('--action', action='append', help='动作（JSON 格式，可多次使用）')
    
    args = parser.parse_args()
    
    # 解析动作
    actions = []
    if args.action:
        for action_str in args.action:
            try:
                action = json.loads(action_str)
                actions.append(action)
            except json.JSONDecodeError as e:
                print(f"❌ 动作 JSON 解析失败: {e}")
                sys.exit(1)
    
    if not actions:
        print("❌ 未提供任何动作")
        sys.exit(1)
    
    # 发送邮件
    success = send_mail(args.to, args.title, actions)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
