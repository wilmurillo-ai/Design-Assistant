#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Email Client
使用Python标准库imaplib和smtplib访问QQ邮箱
"""

import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import ssl
import json
from datetime import datetime
from typing import List, Dict, Optional, Union
import io

# QQ邮箱配置
IMAP_CONFIG = {
    "host": "imap.qq.com",
    "port": 993,
    "user": "1911308683@qq.com",
    "password": "nllzqegzklliebbh",
}

SMTP_CONFIG = {
    "host": "smtp.qq.com",
    "port": 465,
    "user": "1911308683@qq.com",
    "password": "nllzqegzklliebbh",
}


class QQEmailClient:
    """QQ邮箱客户端"""

    def __init__(self):
        """初始化客户端"""
        self.imap_conn = None
        self.smtp_conn = None
        self.connected_imap = False
        self.connected_smtp = False

    def connect_imap(self) -> None:
        """连接IMAP服务器"""
        if self.connected_imap:
            return

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            self.imap_conn = imaplib.IMAP4_SSL(
                IMAP_CONFIG["host"],
                IMAP_CONFIG["port"],
                ssl_context=context,
                timeout=30,
            )
            self.imap_conn.login(IMAP_CONFIG["user"], IMAP_CONFIG["password"])
            self.connected_imap = True

        except Exception as e:
            raise ConnectionError(f"IMAP连接失败: {e}")

    def disconnect_imap(self) -> None:
        """断开IMAP连接"""
        if self.imap_conn and self.connected_imap:
            try:
                self.imap_conn.close()
            except:
                pass
            finally:
                self.imap_conn = None
                self.connected_imap = False

    def connect_smtp(self) -> None:
        """连接SMTP服务器"""
        if self.connected_smtp:
            return

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            self.smtp_conn = smtplib.SMTP_SSL(
                SMTP_CONFIG["host"], SMTP_CONFIG["port"], context=context, timeout=30
            )
            self.smtp_conn.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            self.connected_smtp = True

        except Exception as e:
            raise ConnectionError(f"SMTP连接失败: {e}")

    def disconnect_smtp(self) -> None:
        """断开SMTP连接"""
        if self.smtp_conn and self.connected_smtp:
            try:
                self.smtp_conn.quit()
            except:
                pass
            finally:
                self.smtp_conn = None
                self.connected_smtp = False

    def list_emails(self, limit: int = 10, folder: str = "INBOX") -> List[Dict]:
        """
        列出最近邮件

        Args:
            limit: 返回邮件数量
            folder: 文件夹名称（默认INBOX）

        Returns:
            邮件列表
        """
        if not self.connected_imap:
            self.connect_imap()

        try:
            self.imap_conn.select(folder, readonly=True)
            status, messages = self.imap_conn.search(None, "ALL")

            if status != "OK":
                return []

            email_ids = messages[0].split()[-limit:]
            emails = []

            for email_id in reversed(email_ids):
                try:
                    status, msg_data = self.imap_conn.fetch(email_id, "(RFC822.HEADER)")
                    if status != "OK":
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # 解码主题
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                    # 获取发件人和日期
                    from_ = msg.get("From", "")
                    date_ = msg.get("Date", "")

                    emails.append(
                        {
                            "id": email_id.decode(),
                            "from": from_,
                            "to": msg.get("To", ""),
                            "subject": subject,
                            "date": date_,
                            "size": len(raw_email),
                        }
                    )

                except Exception as e:
                    print(f"解析邮件失败 {email_id}: {e}")
                    continue

            return emails

        except Exception as e:
            raise Exception(f"列出邮件失败: {e}")

    def read_email(self, email_id: str) -> Dict:
        """
        读取邮件内容

        Args:
            email_id: 邮件ID

        Returns:
            邮件详情
        """
        if not self.connected_imap:
            self.connect_imap()

        try:
            status, msg_data = self.imap_conn.fetch(email_id, "(RFC822)")

            if status != "OK":
                raise Exception(f"读取邮件失败")

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 解码主题
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            # 解码发件人和收件人
            from_ = msg.get("From", "")
            to_ = msg.get("To", "")
            cc = msg.get("Cc", "")
            date_ = msg.get("Date", "")

            # 提取邮件正文
            body_text = ""
            body_html = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()

                    if content_type == "text/plain":
                        try:
                            body_text = part.get_payload(decode=True)
                        except:
                            body_text = part.get_payload()
                    elif content_type == "text/html":
                        try:
                            body_html = part.get_payload(decode=True)
                        except:
                            body_html = part.get_payload()
            else:
                body_text = msg.get_payload(decode=True)

            # 提取附件
            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_filename():
                        filename = part.get_filename()
                        content = part.get_payload(decode=True)

                        attachments.append(
                            {
                                "filename": filename,
                                "content": content,
                                "size": len(content) if content else 0,
                            }
                        )

            return {
                "id": email_id,
                "from": from_,
                "to": to_,
                "cc": cc,
                "subject": subject,
                "date": date_,
                "body": body_text,
                "html": body_html,
                "attachments": attachments,
                "raw": raw_email,
            }

        except Exception as e:
            raise Exception(f"读取邮件失败: {e}")

    def search_emails(self, criteria: str, limit: int = 20) -> List[Dict]:
        """
        搜索邮件

        Args:
            criteria: 搜索条件（主题、发件人等）
            limit: 返回结果数量

        Returns:
            匹配的邮件列表
        """
        if not self.connected_imap:
            self.connect_imap()

        try:
            self.imap_conn.select("INBOX", readonly=True)

            # 使用IMAP搜索命令
            status, messages = self.imap_conn.search(
                None, f'(OR SUBJECT "{criteria}" FROM "{criteria}")'
            )

            if status != "OK":
                return []

            email_ids = messages[0].split()[-limit:]
            emails = []

            for email_id in reversed(email_ids):
                try:
                    status, msg_data = self.imap_conn.fetch(email_id, "(RFC822.HEADER)")
                    if status != "OK":
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # 解码主题
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                    # 获取发件人和日期
                    from_ = msg.get("From", "")
                    date_ = msg.get("Date", "")

                    emails.append(
                        {
                            "id": email_id.decode(),
                            "from": from_,
                            "subject": subject,
                            "date": date_,
                        }
                    )

                except Exception as e:
                    print(f"解析邮件失败 {email_id}: {e}")
                    continue

            return emails

        except Exception as e:
            raise Exception(f"搜索邮件失败: {e}")

    def list_folders(self) -> List[str]:
        """
        列出所有文件夹

        Returns:
            文件夹名称列表
        """
        if not self.connected_imap:
            self.connect_imap()

        try:
            status, folders = self.imap_conn.list()

            if status != "OK":
                return []

            folder_names = []
            for folder in folders:
                # 解析文件夹名称
                if b'"' in folder:
                    folder_name = folder.decode().split('"')[3]
                    folder_names.append(folder_name)

            return folder_names

        except Exception as e:
            raise Exception(f"列出文件夹失败: {e}")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> None:
        """
        发送邮件

        Args:
            to: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            html: HTML正文（可选）
            attachments: 附件列表（可选）
        """
        if not self.connected_smtp:
            self.connect_smtp()

        try:
            msg = MIMEMultipart()
            msg["From"] = SMTP_CONFIG["user"]
            msg["To"] = to
            msg["Subject"] = subject

            # 添加正文
            if html:
                msg.attach(MIMEText(html, "html", "utf-8"))
            else:
                msg.attach(MIMEText(body, "plain", "utf-8"))

            # 添加附件
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(
                        attachment["content"], Name=attachment["filename"]
                    )
                    msg.attach(part)

            # 发送邮件
            self.smtp_conn.send_message(msg)

        except Exception as e:
            raise Exception(f"发送邮件失败: {e}")

    def reply_email(
        self, email_id: str, body: str, quote_original: bool = True
    ) -> None:
        """
        回复邮件

        Args:
            email_id: 要回复的邮件ID
            body: 回复内容
            quote_original: 是否引用原始邮件
        """
        if not self.connected_imap:
            self.connect_imap()

        try:
            # 读取原始邮件
            original_email = self.read_email(email_id)

            # 连接SMTP
            self.connect_smtp()

            # 构建回复
            msg = MIMEMultipart()
            msg["In-Reply-To"] = email_id
            msg["References"] = email_id
            msg["Subject"] = f"Re: {original_email['subject']}"
            msg["To"] = original_email["from"]

            # 添加回复内容
            if quote_original:
                quoted_body = f"\n\n--- 原始邮件 ---\n{original_email['from']}\n{original_email['date']}\n{original_email['body']}"
                reply_body = body + quoted_body
            else:
                reply_body = body

            msg.attach(MIMEText(reply_body, "plain", "utf-8"))

            # 发送
            self.smtp_conn.send_message(msg)

        except Exception as e:
            raise Exception(f"回复邮件失败: {e}")

    def forward_email(self, email_id: str, to: str, additional_note: str = "") -> None:
        """
        转发邮件

        Args:
            email_id: 要转发的邮件ID
            to: 转发目标邮箱
            additional_note: 附加说明
        """
        if not self.connected_imap:
            self.connect_imap()

        try:
            # 读取原始邮件
            original_email = self.read_email(email_id)

            # 连接SMTP
            self.connect_smtp()

            # 构建转发邮件
            msg = MIMEMultipart()
            msg["Subject"] = f"Fwd: {original_email['subject']}"
            msg["To"] = to

            # 添加转发内容
            body = f"--- 转发邮件 ---\n\n"
            body += f"发件人: {original_email['from']}\n"
            body += f"日期: {original_email['date']}\n"
            body += f"主题: {original_email['subject']}\n\n"
            body += "--- 原始内容 ---\n"
            body += original_email["body"]

            if additional_note:
                body += f"\n\n--- 转发说明 ---\n{additional_note}"

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送
            self.smtp_conn.send_message(msg)

        except Exception as e:
            raise Exception(f"转发邮件失败: {e}")

    def __enter__(self):
        """支持上下文管理器"""
        self.connect_imap()
        self.connect_smtp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.disconnect_imap()
        self.disconnect_smtp()


# 快捷函数
def list_emails(limit: int = 10) -> List[Dict]:
    """快捷函数：列出最近邮件"""
    with QQEmailClient() as client:
        return client.list_emails(limit=limit)


def read_email(email_id: str) -> Dict:
    """快捷函数：读取邮件"""
    with QQEmailClient() as client:
        return client.read_email(email_id)


def search_emails(criteria: str, limit: int = 20) -> List[Dict]:
    """快捷函数：搜索邮件"""
    with QQEmailClient() as client:
        return client.search_emails(criteria, limit=limit)


def send_email(to: str, subject: str, body: str, html: Optional[str] = None) -> None:
    """快捷函数：发送邮件"""
    with QQEmailClient() as client:
        return client.send_email(to, subject, body, html)


def list_folders() -> List[str]:
    """快捷函数：列出文件夹"""
    with QQEmailClient() as client:
        return client.list_folders()


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            emails = list_emails(5)
            print(json.dumps(emails, indent=2, ensure_ascii=False))
        elif sys.argv[1] == "read":
            if len(sys.argv) > 2:
                email = read_email(sys.argv[2])
                print(f"主题: {email['subject']}")
                print(f"正文: {email['body']}")
        elif sys.argv[1] == "search":
            if len(sys.argv) > 2:
                emails = search_emails(sys.argv[2], 5)
                print(f"找到 {len(emails)} 封邮件")
                for email in emails:
                    print(f"  - {email['subject']}")
