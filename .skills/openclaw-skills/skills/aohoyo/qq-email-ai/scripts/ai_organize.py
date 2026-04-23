#!/usr/bin/env python3
"""
AI 邮件一键智能整理
整合摘要、分类、优先级、待办提取的完整流程
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict

# 导入其他模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_emails import QQEmailClient
from ai_summarize import AISummarizer
from ai_classify import EmailClassifier
from ai_prioritize import EmailPrioritizer
from ai_extract_todos import TodoExtractor


class EmailOrganizer(QQEmailClient):
    """邮件智能整理器"""
    
    def organize(
        self,
        folder: str = "INBOX",
        limit: int = 30,
        unread_only: bool = False,
        email_ids: List[str] = None
    ) -> Dict:
        """
        一键智能整理邮件
        
        执行流程：
        1. 获取邮件列表
        2. 生成摘要
        3. 智能分类
        4. 优先级排序
        5. 提取待办
        6. 生成整理报告
        """
        print(f"📧 开始整理邮箱...\n")
        
        # 1. 获取邮件
        print("Step 1: 获取邮件列表...")
        if email_ids:
            emails = []
            self.conn.select(folder)
            for eid in email_ids:
                status, msg_data = self.conn.fetch(eid.encode(), "(RFC822)")
                if status == "OK":
                    email_info = self.parse_email(msg_data[0][1])
                    email_info["id"] = eid
                    emails.append(email_info)
        else:
            emails = self.fetch_emails(folder, limit, unread_only)
        
        print(f"   获取到 {len(emails)} 封邮件\n")
        
        if not emails:
            return {
                "success": True,
                "message": "没有邮件需要整理",
                "timestamp": datetime.now().isoformat()
            }
        
        # 2. 生成摘要
        print("Step 2: 生成 AI 摘要...")
        summarizer = AISummarizer(self.email, self.auth_code)
        summaries = {}
        for i, email in enumerate(emails, 1):
            print(f"   [{i}/{len(emails)}] {email.get('subject', '无主题')[:30]}...")
            summary_result = summarizer.generate_summary(
                email.get("subject", ""),
                email.get("body_text", "")
            )
            summaries[email["id"]] = summary_result.get("summary", {})
        print(f"   ✓ 完成 {len(summaries)} 封邮件摘要\n")
        
        # 3. 智能分类
        print("Step 3: 智能分类...")
        classifier = EmailClassifier(self.email, self.auth_code)
        classifications = {}
        category_stats = {}
        for i, email in enumerate(emails, 1):
            classification = classifier.classify_with_ai(
                email.get("subject", ""),
                email.get("body_text", ""),
                email.get("sender", "")
            )
            classifications[email["id"]] = classification
            cat = classification["category"]
            category_stats[cat] = category_stats.get(cat, 0) + 1
        print(f"   ✓ 完成分类：{category_stats}\n")
        
        # 4. 优先级排序
        print("Step 4: 优先级评估...")
        prioritizer = EmailPrioritizer(self.email, self.auth_code)
        priorities = {}
        priority_stats = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
        for email in emails:
            priority_info = prioritizer.calculate_priority(email)
            priorities[email["id"]] = priority_info
            priority_stats[priority_info["priority"]] += 1
        print(f"   ✓ 优先级分布：紧急{priority_stats['urgent']} 高{priority_stats['high']} "
              f"中{priority_stats['medium']} 低{priority_stats['low']}\n")
        
        # 5. 提取待办
        print("Step 5: 提取待办事项...")
        extractor = TodoExtractor(self.email, self.auth_code)
        todos_by_email = {}
        total_todos = 0
        for email in emails:
            todos = extractor.extract_todos_with_ai(email)
            if todos:
                todos_by_email[email["id"]] = todos
                total_todos += len(todos)
        print(f"   ✓ 从 {len(todos_by_email)} 封邮件中提取 {total_todos} 个待办\n")
        
        # 6. 生成整理报告
        print("Step 6: 生成整理报告...")
        organized_emails = []
        for email in emails:
            eid = email["id"]
            organized_emails.append({
                "id": eid,
                "subject": email["subject"],
                "sender": email["sender"],
                "date": email["date"],
                "is_unread": "\\Seen" not in email.get("flags", []),
                "summary": summaries.get(eid, {}),
                "classification": classifications.get(eid, {}),
                "priority": priorities.get(eid, {}),
                "todos": todos_by_email.get(eid, [])
            })
        
        # 按优先级排序
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        organized_emails.sort(key=lambda x: priority_order.get(
            x["priority"].get("priority", "low"), 3
        ))
        
        report = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_emails": len(emails),
                "unread_count": sum(1 for e in emails if "\\Seen" not in e.get("flags", [])),
                "category_distribution": category_stats,
                "priority_distribution": priority_stats,
                "todos_count": total_todos,
                "emails_with_todos": len(todos_by_email)
            },
            "emails": organized_emails
        }
        
        print("✓ 整理完成!\n")
        return report


def main():
    parser = argparse.ArgumentParser(description="AI 邮件一键智能整理")
    parser.add_argument("--folder", default="INBOX", help="文件夹")
    parser.add_argument("--limit", type=int, default=30, help="处理数量")
    parser.add_argument("--unread", action="store_true", help="仅未读邮件")
    parser.add_argument("--email-ids", help="指定邮件 ID（逗号分隔）")
    parser.add_argument("--output", help="输出报告文件路径")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码")
    
    args = parser.parse_args()
    
    email_ids = None
    if args.email_ids:
        email_ids = [eid.strip() for eid in args.email_ids.split(",")]
    
    try:
        organizer = EmailOrganizer(args.email, args.auth_code)
        with organizer:
            report = organizer.organize(
                folder=args.folder,
                limit=args.limit,
                unread_only=args.unread,
                email_ids=email_ids
            )
            
            output = json.dumps(report, ensure_ascii=False, indent=2)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"📄 报告已保存到：{args.output}")
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
