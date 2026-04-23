#!/usr/bin/env python3
"""
QQ 邮箱邮件管理工具
支持标记已读/未读、删除、移动邮件
"""

import os
import json
import argparse
from fetch_emails import QQEmailClient


class EmailManager(QQEmailClient):
    """邮件管理器"""
    
    def mark_read(self, email_ids: list, folder: str = "INBOX"):
        """标记为已读"""
        self.conn.select(folder)
        for eid in email_ids:
            self.conn.store(eid.encode(), '+FLAGS', '\\Seen')
        return {"action": "mark_read", "count": len(email_ids)}
    
    def mark_unread(self, email_ids: list, folder: str = "INBOX"):
        """标记为未读"""
        self.conn.select(folder)
        for eid in email_ids:
            self.conn.store(eid.encode(), '-FLAGS', '\\Seen')
        return {"action": "mark_unread", "count": len(email_ids)}
    
    def delete(self, email_ids: list, folder: str = "INBOX"):
        """删除邮件（移动到已删除文件夹）"""
        self.conn.select(folder)
        for eid in email_ids:
            self.conn.store(eid.encode(), '+FLAGS', '\\Deleted')
        self.conn.expunge()
        return {"action": "delete", "count": len(email_ids)}
    
    def move(self, email_ids: list, target_folder: str, source_folder: str = "INBOX"):
        """移动邮件到指定文件夹"""
        self.conn.select(source_folder)
        results = []
        for eid in email_ids:
            # 复制到目标文件夹
            status, _ = self.conn.copy(eid.encode(), target_folder)
            if status == "OK":
                # 标记原邮件为删除
                self.conn.store(eid.encode(), '+FLAGS', '\\Deleted')
                results.append(eid)
        self.conn.expunge()
        return {"action": "move", "count": len(results), "target": target_folder}
    
    def list_folders(self):
        """列出所有文件夹"""
        status, folders = self.conn.list()
        if status != "OK":
            return []
        
        folder_list = []
        for folder in folders:
            if folder:
                # 解析文件夹名称
                parts = folder.decode().split(' "/" ')
                if len(parts) >= 2:
                    folder_name = parts[-1].strip('"')
                    folder_list.append(folder_name)
        
        return folder_list


def main():
    parser = argparse.ArgumentParser(description="管理 QQ 邮箱邮件")
    parser.add_argument("--id", required=True, help="邮件 ID（多个用逗号分隔）")
    parser.add_argument("--action", required=True, 
                      choices=["mark_read", "mark_unread", "delete", "move", "list_folders"],
                      help="操作类型")
    parser.add_argument("--folder", default="INBOX", help="源文件夹")
    parser.add_argument("--target-folder", help="目标文件夹（move 操作需要）")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码")
    
    args = parser.parse_args()
    
    try:
        manager = EmailManager(args.email, args.auth_code)
        with manager:
            if args.action == "list_folders":
                folders = manager.list_folders()
                result = {
                    "success": True,
                    "action": "list_folders",
                    "folders": folders
                }
            else:
                email_ids = [eid.strip() for eid in args.id.split(",")]
                
                if args.action == "mark_read":
                    action_result = manager.mark_read(email_ids, args.folder)
                elif args.action == "mark_unread":
                    action_result = manager.mark_unread(email_ids, args.folder)
                elif args.action == "delete":
                    action_result = manager.delete(email_ids, args.folder)
                elif args.action == "move":
                    if not args.target_folder:
                        raise ValueError("move 操作需要 --target-folder 参数")
                    action_result = manager.move(email_ids, args.target_folder, args.folder)
                
                result = {
                    "success": True,
                    **action_result,
                    "email_ids": email_ids
                }
            
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
