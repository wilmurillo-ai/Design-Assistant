#!/usr/bin/env python3
"""
QQ 邮箱邮件获取工具
支持读取收件箱、未读邮件、指定文件夹
"""

import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime


class QQEmailClient:
    """QQ 邮箱 IMAP 客户端"""
    
    IMAP_SERVER = "imap.qq.com"
    IMAP_PORT = 993
    
    def __init__(self, email: str = None, auth_code: str = None):
        self.email = email or os.getenv("QQ_EMAIL")
        self.auth_code = auth_code or os.getenv("QQ_EMAIL_AUTH_CODE")
        self.conn = None
        
        if not self.email or not self.auth_code:
            raise ValueError("请设置 QQ_EMAIL 和 QQ_EMAIL_AUTH_CODE 环境变量")
    
    def connect(self):
        """连接 IMAP 服务器"""
        self.conn = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
        self.conn.login(self.email, self.auth_code)
        return self
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            self.conn.logout()
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def decode_str(self, s: str) -> str:
        """解码邮件头"""
        if not s:
            return ""
        decoded = decode_header(s)
        result = []
        for value, charset in decoded:
            if isinstance(value, bytes):
                result.append(value.decode(charset or 'utf-8', errors='ignore'))
            else:
                result.append(value)
        return ''.join(result)
    
    def parse_email(self, msg_data: bytes) -> Dict:
        """解析邮件内容"""
        msg = email.message_from_bytes(msg_data)
        
        # 基本信息
        subject = self.decode_str(msg.get("Subject", ""))
        sender = self.decode_str(msg.get("From", ""))
        to = self.decode_str(msg.get("To", ""))
        date_str = msg.get("Date", "")
        
        # 解析日期
        try:
            date = parsedate_to_datetime(date_str)
            date_formatted = date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            date_formatted = date_str
        
        # 获取正文
        body_text = ""
        body_html = ""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # 附件
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(self.decode_str(filename))
                # 正文
                elif content_type == "text/plain" and not body_text:
                    try:
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html" and not body_html:
                    try:
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            content_type = msg.get_content_type()
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                if content_type == "text/html":
                    body_html = body
                else:
                    body_text = body
            except:
                pass
        
        return {
            "subject": subject,
            "sender": sender,
            "to": to,
            "date": date_formatted,
            "body_text": body_text[:5000] if body_text else "",  # 限制长度
            "body_html": body_html[:10000] if body_html else "",
            "attachments": attachments,
            "flags": []
        }
    
    def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = False,
        since: str = None
    ) -> List[Dict]:
        """
        获取邮件列表
        
        Args:
            folder: 文件夹名称
            limit: 返回数量限制
            unread_only: 仅未读邮件
            since: 起始日期 (YYYY-MM-DD)
        """
        # 选择文件夹
        status, _ = self.conn.select(folder)
        if status != "OK":
            raise Exception(f"无法选择文件夹: {folder}")
        
        # 构建搜索条件
        search_criteria = ["ALL"]
        if unread_only:
            search_criteria = ["UNSEEN"]
        if since:
            date_obj = datetime.strptime(since, "%Y-%m-%d")
            search_criteria.append("SINCE")
            search_criteria.append(date_obj.strftime("%d-%b-%Y"))
        
        # 搜索邮件
        status, messages = self.conn.search(None, *search_criteria)
        if status != "OK":
            return []
        
        email_ids = messages[0].split()
        # 获取最新的 limit 封
        email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
        email_ids.reverse()  # 最新的在前
        
        emails = []
        for eid in email_ids:
            status, msg_data = self.conn.fetch(eid, "(RFC822)")
            if status == "OK":
                email_content = msg_data[0][1]
                email_info = self.parse_email(email_content)
                email_info["id"] = eid.decode('utf-8')
                
                # 获取邮件状态
                status, flags_data = self.conn.fetch(eid, "(FLAGS)")
                if status == "OK":
                    flags_str = flags_data[0].decode('utf-8')
                    if "\\Seen" in flags_str:
                        email_info["flags"].append("\\Seen")
                
                emails.append(email_info)
        
        return emails


def main():
    parser = argparse.ArgumentParser(description="获取 QQ 邮箱邮件")
    parser.add_argument("--folder", default="INBOX", help="文件夹名称 (默认: INBOX)")
    parser.add_argument("--limit", type=int, default=10, help="获取数量限制 (默认: 10)")
    parser.add_argument("--unread", action="store_true", help="仅获取未读邮件")
    parser.add_argument("--since", help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--output", help="输出文件路径 (JSON 格式)")
    parser.add_argument("--email", help="邮箱地址 (覆盖环境变量)")
    parser.add_argument("--auth-code", help="授权码 (覆盖环境变量)")
    
    args = parser.parse_args()
    
    try:
        client = QQEmailClient(args.email, args.auth_code)
        with client:
            emails = client.fetch_emails(
                folder=args.folder,
                limit=args.limit,
                unread_only=args.unread,
                since=args.since
            )
            
            result = {
                "success": True,
                "folder": args.folder,
                "count": len(emails),
                "emails": emails
            }
            
            output = json.dumps(result, ensure_ascii=False, indent=2)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"结果已保存到: {args.output}")
            else:
                print(output)
                
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        exit(1)


if __name__ == "__main__":
    main()
