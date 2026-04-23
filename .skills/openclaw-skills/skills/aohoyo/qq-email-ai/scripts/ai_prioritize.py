#!/usr/bin/env python3
"""
AI 邮件优先级排序
根据内容、发件人、时间等智能评估邮件优先级
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict
from fetch_emails import QQEmailClient


class EmailPrioritizer(QQEmailClient):
    """邮件优先级评估器"""
    
    # 优先级定义
    PRIORITIES = {
        "urgent": {
            "label": "紧急",
            "description": "需立即处理（今天内）",
            "color": "🔴"
        },
        "high": {
            "label": "高",
            "description": "24 小时内处理",
            "color": "🟠"
        },
        "medium": {
            "label": "中",
            "description": "本周内处理",
            "color": "🟡"
        },
        "low": {
            "label": "低",
            "description": "可延后处理",
            "color": "🟢"
        }
    }
    
    # 紧急关键词
    URGENT_KEYWORDS = [
        "紧急", "急", "尽快", "立即", "马上", "today", "ASAP",
        "截止", "deadline", "超时", "过期", "最后"
    ]
    
    # 重要发件人模式（可配置）
    IMPORTANT_SENDER_PATTERNS = ["boss", "ceo", "manager", "hr", "finance"]
    
    def calculate_priority(self, email: Dict) -> Dict:
        """
        计算邮件优先级
        
        考虑因素：
        1. 关键词紧急程度
        2. 发件人重要性
        3. 邮件时效性
        4. 是否未读
        5. 是否有附件
        """
        score = 0  # 0-100 分
        reasons = []
        
        subject = email.get("subject", "").lower()
        body = email.get("body_text", "").lower()[:1000]
        sender = email.get("sender", "").lower()
        text = f"{subject} {body}"
        
        # 1. 紧急关键词 (+30 分)
        urgent_count = sum(1 for kw in self.URGENT_KEYWORDS if kw.lower() in text)
        if urgent_count >= 3:
            score += 30
            reasons.append(f"包含多个紧急关键词 ({urgent_count}个)")
        elif urgent_count >= 1:
            score += 15
            reasons.append(f"包含紧急关键词")
        
        # 2. 重要发件人 (+25 分)
        for pattern in self.IMPORTANT_SENDER_PATTERNS:
            if pattern in sender:
                score += 25
                reasons.append(f"重要发件人 ({pattern})")
                break
        
        # 3. 时效性 (+20 分)
        try:
            email_date = datetime.strptime(email.get("date", ""), "%Y-%m-%d %H:%M:%S")
            hours_old = (datetime.now() - email_date).total_seconds() / 3600
            if hours_old < 2:
                score += 20
                reasons.append("2 小时内的新邮件")
            elif hours_old < 24:
                score += 10
                reasons.append("24 小时内的邮件")
        except:
            pass
        
        # 4. 未读邮件 (+10 分)
        if "\\Seen" not in email.get("flags", []):
            score += 10
            reasons.append("未读邮件")
        
        # 5. 有附件 (+5 分)
        if email.get("attachments"):
            score += 5
            reasons.append("包含附件")
        
        # 6. 主题包含问号/请求 (+10 分)
        if "?" in subject or "请" in subject or "help" in subject.lower():
            score += 10
            reasons.append("包含请求/问题")
        
        # 确定优先级
        if score >= 70:
            priority = "urgent"
        elif score >= 50:
            priority = "high"
        elif score >= 30:
            priority = "medium"
        else:
            priority = "low"
        
        return {
            "priority": priority,
            "priority_label": self.PRIORITIES[priority]["label"],
            "priority_emoji": self.PRIORITIES[priority]["color"],
            "score": min(score, 100),
            "reasons": reasons
        }
    
    def prioritize_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        email_ids: List[str] = None
    ) -> List[Dict]:
        """批量评估邮件优先级"""
        # 获取邮件
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
            emails = self.fetch_emails(folder, limit, False)
        
        # 评估优先级
        results = []
        for email in emails:
            priority_info = self.calculate_priority(email)
            
            results.append({
                "id": email["id"],
                "subject": email["subject"],
                "sender": email["sender"],
                "date": email["date"],
                "is_unread": "\\Seen" not in email.get("flags", []),
                "has_attachments": len(email.get("attachments", [])) > 0,
                **priority_info
            })
        
        # 按优先级排序
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        results.sort(key=lambda x: (priority_order[x["priority"]], -x["score"]))
        
        return results


def main():
    parser = argparse.ArgumentParser(description="AI 邮件优先级排序")
    parser.add_argument("--folder", default="INBOX", help="文件夹")
    parser.add_argument("--limit", type=int, default=50, help="处理数量")
    parser.add_argument("--email-ids", help="指定邮件 ID（逗号分隔）")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码")
    
    args = parser.parse_args()
    
    email_ids = None
    if args.email_ids:
        email_ids = [eid.strip() for eid in args.email_ids.split(",")]
    
    try:
        prioritizer = EmailPrioritizer(args.email, args.auth_code)
        with prioritizer:
            results = prioritizer.prioritize_emails(
                folder=args.folder,
                limit=args.limit,
                email_ids=email_ids
            )
            
            # 统计优先级分布
            stats = {}
            for r in results:
                p = r["priority"]
                stats[p] = stats.get(p, 0) + 1
            
            result = {
                "success": True,
                "total": len(results),
                "statistics": {
                    p: {
                        "count": stats.get(p, 0),
                        "label": EmailPrioritizer.PRIORITIES[p]["label"],
                        "emoji": EmailPrioritizer.PRIORITIES[p]["color"]
                    }
                    for p in ["urgent", "high", "medium", "low"]
                },
                "emails": results
            }
            
            output = json.dumps(result, ensure_ascii=False, indent=2)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"结果已保存到：{args.output}")
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
