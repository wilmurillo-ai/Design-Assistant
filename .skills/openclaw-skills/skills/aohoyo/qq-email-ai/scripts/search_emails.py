#!/usr/bin/env python3
"""
QQ 邮箱搜索工具
支持按关键词、发件人、时间等条件搜索邮件
"""

import os
import json
import argparse
from datetime import datetime
from fetch_emails import QQEmailClient


class EmailSearcher(QQEmailClient):
    """邮件搜索器"""
    
    def search(
        self,
        folder: str = "INBOX",
        query: str = None,
        from_addr: str = None,
        to_addr: str = None,
        subject: str = None,
        since: str = None,
        before: str = None,
        unread_only: bool = False,
        limit: int = 50
    ) -> list:
        """
        搜索邮件
        
        Args:
            folder: 文件夹
            query: 关键词（搜索主题和内容）
            from_addr: 发件人
            to_addr: 收件人
            subject: 主题关键词
            since: 起始日期 (YYYY-MM-DD)
            before: 结束日期 (YYYY-MM-DD)
            unread_only: 仅未读
            limit: 返回数量限制
        """
        # 选择文件夹
        status, _ = self.conn.select(folder)
        if status != "OK":
            raise Exception(f"无法选择文件夹: {folder}")
        
        # 构建搜索条件
        search_criteria = []
        
        if unread_only:
            search_criteria.append("UNSEEN")
        
        if from_addr:
            search_criteria.extend(["FROM", from_addr])
        
        if to_addr:
            search_criteria.extend(["TO", to_addr])
        
        if subject:
            search_criteria.extend(["SUBJECT", subject])
        
        if since:
            date_obj = datetime.strptime(since, "%Y-%m-%d")
            search_criteria.extend(["SINCE", date_obj.strftime("%d-%b-%Y")])
        
        if before:
            date_obj = datetime.strptime(before, "%Y-%m-%d")
            search_criteria.extend(["BEFORE", date_obj.strftime("%d-%b-%Y")])
        
        # 如果没有特定条件，搜索全部
        if not search_criteria:
            search_criteria = ["ALL"]
        
        # 搜索邮件
        status, messages = self.conn.search(None, *search_criteria)
        if status != "OK":
            return []
        
        email_ids = messages[0].split()
        
        # 获取邮件详情
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
        
        # 如果有 query 关键词，在主题和内容中过滤
        if query:
            query_lower = query.lower()
            filtered_emails = []
            for email in emails:
                subject_match = query_lower in email.get("subject", "").lower()
                body_match = query_lower in email.get("body_text", "").lower()
                if subject_match or body_match:
                    filtered_emails.append(email)
            emails = filtered_emails
        
        # 限制数量，最新的在前
        emails.reverse()
        emails = emails[:limit]
        
        return emails


def main():
    parser = argparse.ArgumentParser(description="搜索 QQ 邮箱邮件")
    parser.add_argument("--folder", default="INBOX", help="文件夹名称")
    parser.add_argument("--query", help="关键词（搜索主题和内容）")
    parser.add_argument("--from", dest="from_addr", help="发件人邮箱")
    parser.add_argument("--to", dest="to_addr", help="收件人邮箱")
    parser.add_argument("--subject", help="主题关键词")
    parser.add_argument("--since", help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--before", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--unread", action="store_true", help="仅未读邮件")
    parser.add_argument("--limit", type=int, default=50, help="返回数量限制")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码")
    
    args = parser.parse_args()
    
    try:
        searcher = EmailSearcher(args.email, args.auth_code)
        with searcher:
            emails = searcher.search(
                folder=args.folder,
                query=args.query,
                from_addr=args.from_addr,
                to_addr=args.to_addr,
                subject=args.subject,
                since=args.since,
                before=args.before,
                unread_only=args.unread,
                limit=args.limit
            )
            
            result = {
                "success": True,
                "folder": args.folder,
                "search_params": {
                    "query": args.query,
                    "from": args.from_addr,
                    "subject": args.subject,
                    "since": args.since,
                    "before": args.before,
                    "unread": args.unread
                },
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
