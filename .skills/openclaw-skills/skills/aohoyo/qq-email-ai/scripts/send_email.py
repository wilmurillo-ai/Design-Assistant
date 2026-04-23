#!/usr/bin/env python3
"""
QQ 邮箱发送工具
支持发送纯文本、HTML 邮件，支持附件
"""

import os
import json
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from pathlib import Path


class QQEmailSender:
    """QQ 邮箱 SMTP 发送器"""
    
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    
    def __init__(self, email: str = None, auth_code: str = None):
        self.email = email or os.getenv("QQ_EMAIL")
        self.auth_code = auth_code or os.getenv("QQ_EMAIL_AUTH_CODE")
        
        if not self.email or not self.auth_code:
            raise ValueError("请设置 QQ_EMAIL 和 QQ_EMAIL_AUTH_CODE 环境变量")
    
    def send(
        self,
        to: str,
        subject: str,
        body: str = None,
        html: str = None,
        cc: str = None,
        attachments: list = None
    ) -> dict:
        """
        发送邮件
        
        Args:
            to: 收件人（多个用逗号分隔）
            subject: 主题
            body: 纯文本正文
            html: HTML 正文（优先于 body）
            cc: 抄送（多个用逗号分隔）
            attachments: 附件路径列表
        """
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to
        msg['Subject'] = Header(subject, 'utf-8')
        
        if cc:
            msg['Cc'] = cc
        
        # 添加正文
        if html:
            msg.attach(MIMEText(html, 'html', 'utf-8'))
        elif body:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        else:
            msg.attach(MIMEText("", 'plain', 'utf-8'))
        
        # 添加附件
        if attachments:
            for filepath in attachments:
                filepath = filepath.strip()
                if not os.path.exists(filepath):
                    print(f"警告：附件不存在: {filepath}")
                    continue
                
                filename = os.path.basename(filepath)
                with open(filepath, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
                msg.attach(attachment)
        
        # 构建收件人列表
        recipients = to.split(',')
        if cc:
            recipients.extend(cc.split(','))
        
        # 发送邮件
        with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT) as server:
            server.login(self.email, self.auth_code)
            server.sendmail(self.email, recipients, msg.as_string())
        
        return {
            "success": True,
            "to": to,
            "subject": subject,
            "attachments_count": len(attachments) if attachments else 0
        }


def main():
    parser = argparse.ArgumentParser(description="发送 QQ 邮箱邮件")
    parser.add_argument("--to", required=True, help="收件人邮箱（多个用逗号分隔）")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--body", help="纯文本正文")
    parser.add_argument("--html", help="HTML 正文（优先于 --body）")
    parser.add_argument("--cc", help="抄送邮箱（多个用逗号分隔）")
    parser.add_argument("--attachments", help="附件路径（多个用逗号分隔）")
    parser.add_argument("--email", help="发件人邮箱（覆盖环境变量）")
    parser.add_argument("--auth-code", help="授权码（覆盖环境变量）")
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.body and not args.html:
        print("错误：请提供 --body 或 --html 参数")
        exit(1)
    
    # 解析附件
    attachments = None
    if args.attachments:
        attachments = [a.strip() for a in args.attachments.split(',')]
    
    try:
        sender = QQEmailSender(args.email, args.auth_code)
        result = sender.send(
            to=args.to,
            subject=args.subject,
            body=args.body,
            html=args.html,
            cc=args.cc,
            attachments=attachments
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        exit(1)


if __name__ == "__main__":
    main()
