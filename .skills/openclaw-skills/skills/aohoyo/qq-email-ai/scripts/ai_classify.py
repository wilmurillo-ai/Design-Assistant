#!/usr/bin/env python3
"""
AI 邮件智能分类器
自动将邮件分类到不同类别
"""

import os
import json
import argparse
from typing import List, Dict
from fetch_emails import QQEmailClient


class EmailClassifier(QQEmailClient):
    """邮件分类器"""
    
    # 预定义类别
    CATEGORIES = {
        "work": "工作相关（会议、项目、汇报、同事沟通）",
        "important": "重要邮件（老板、客户、紧急事项）",
        "promotion": "推广营销（广告、优惠、电商）",
        "social": "社交通知（朋友圈、社交软件、活动邀请）",
        "newsletter": "订阅邮件（资讯、周报、公众号）",
        "finance": "财务金融（银行、账单、发票、报销）",
        "travel": "出行旅游（机票、酒店、订单确认）",
        "spam": "垃圾邮件（可疑、诈骗、无关内容）"
    }
    
    # 关键词规则（快速分类）
    KEYWORDS = {
        "work": ["会议", "项目", "汇报", "工作", "任务", "deadline", "进度", "需求", "方案"],
        "promotion": ["优惠", "折扣", "促销", "限时", "购买", "下单", "优惠券", "满减"],
        "finance": ["银行", "账单", "发票", "报销", "付款", "收款", "转账", "余额"],
        "travel": ["机票", "酒店", "订单", "出行", "航班", "高铁", "预订", "行程"],
        "spam": ["中奖", "恭喜", "领取", "验证", "账户异常", "点击链接"]
    }
    
    def classify_with_rules(self, subject: str, body: str, sender: str) -> Dict:
        """基于规则快速分类"""
        text = f"{subject} {body[:500]} {sender}".lower()
        
        scores = {}
        for category, keywords in self.KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            scores[category] = score
        
        if max(scores.values()) > 0:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category] / 5.0, 0.95)
            return {
                "category": best_category,
                "confidence": confidence,
                "method": "rules"
            }
        
        return None
    
    def classify_with_ai(self, subject: str, body: str, sender: str) -> Dict:
        """使用 AI 分类"""
        categories_desc = "\n".join([f"- {k}: {v}" for k, v in self.CATEGORIES.items()])
        
        prompt = f"""请分析以下邮件并分类：

发件人：{sender}
主题：{subject}

内容摘要：
{body[:1000]}

可选类别：
{categories_desc}

要求：
1. 选择最匹配的一个类别
2. 给出置信度 (0-1)
3. 说明分类理由

输出 JSON 格式：
{{
  "category": "类别名",
  "confidence": 0.95,
  "reason": "分类理由"
}}
"""
        
        try:
            import dashscope
            from dashscope import Generation
            
            api_key = os.getenv("DASHSCOPE_API_KEY")
            response = Generation.call(
                model="qwen-plus",
                api_key=api_key,
                messages=[{"role": "user", "content": prompt}],
                result_format="message"
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    if result.get("category") in self.CATEGORIES:
                        result["method"] = "ai"
                        return result
            
            # AI 失败，降级到规则
            return self.classify_with_rules(subject, body, sender) or {
                "category": "social",
                "confidence": 0.5,
                "reason": "无法明确分类，默认为社交类",
                "method": "default"
            }
            
        except Exception as e:
            print(f"AI 分类失败：{e}")
            return self.classify_with_rules(subject, body, sender) or {
                "category": "social",
                "confidence": 0.5,
                "reason": "AI 不可用，使用默认分类",
                "method": "fallback"
            }
    
    def classify_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        email_ids: List[str] = None
    ) -> List[Dict]:
        """批量分类邮件"""
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
        
        # 分类
        results = []
        for email in emails:
            print(f"分类：{email.get('subject', '无主题')}...")
            
            # 先尝试规则分类
            rule_result = self.classify_with_rules(
                email.get("subject", ""),
                email.get("body_text", ""),
                email.get("sender", "")
            )
            
            # 规则不确定时用 AI
            if rule_result and rule_result["confidence"] > 0.7:
                classification = rule_result
            else:
                classification = self.classify_with_ai(
                    email.get("subject", ""),
                    email.get("body_text", ""),
                    email.get("sender", "")
                )
            
            results.append({
                "id": email["id"],
                "subject": email["subject"],
                "sender": email["sender"],
                "date": email["date"],
                **classification
            })
        
        return results


def main():
    parser = argparse.ArgumentParser(description="AI 邮件分类")
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
        classifier = EmailClassifier(args.email, args.auth_code)
        with classifier:
            results = classifier.classify_emails(
                folder=args.folder,
                limit=args.limit,
                email_ids=email_ids
            )
            
            # 统计分类结果
            stats = {}
            for r in results:
                cat = r["category"]
                stats[cat] = stats.get(cat, 0) + 1
            
            result = {
                "success": True,
                "total": len(results),
                "statistics": stats,
                "classifications": results
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
