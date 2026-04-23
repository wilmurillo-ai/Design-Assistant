#!/usr/bin/env python3
"""
AI 邮件摘要生成器
使用大模型为邮件生成简洁摘要
"""

import os
import json
import argparse
from typing import List, Dict
from fetch_emails import QQEmailClient


class AISummarizer(QQEmailClient):
    """AI 邮件摘要器"""
    
    def __init__(self, email: str = None, auth_code: str = None, model: str = "qwen"):
        super().__init__(email, auth_code)
        self.model = model
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
    
    def generate_summary(self, subject: str, body: str, max_length: int = 200) -> Dict:
        """
        生成邮件摘要
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            max_length: 摘要最大长度
        """
        # 构建提示词
        prompt = f"""请为以下邮件生成简洁摘要：

主题：{subject}

内容：
{body[:2000]}

要求：
1. 用一句话概括邮件核心内容（50 字以内）
2. 提取 3-5 个关键信息点（时间、地点、任务等）
3. 如果有明确的行动要求，请标注

输出 JSON 格式：
{{
  "one_sentence": "一句话摘要",
  "key_points": ["关键点 1", "关键点 2", ...],
  "action_required": "需要做什么" 或 null
}}
"""
        
        try:
            # 调用通义千问 API
            import dashscope
            from dashscope import Generation
            
            response = Generation.call(
                model="qwen-plus",
                api_key=self.api_key,
                messages=[{"role": "user", "content": prompt}],
                result_format="message"
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 提取 JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    summary_data = json.loads(json_match.group())
                    return {
                        "success": True,
                        "summary": summary_data
                    }
            
            # 备用方案：简单摘要
            return self._simple_summary(subject, body, max_length)
            
        except Exception as e:
            # 降级到简单摘要
            print(f"AI 摘要失败，使用简单摘要：{e}")
            return self._simple_summary(subject, body, max_length)
    
    def _simple_summary(self, subject: str, body: str, max_length: int = 200) -> Dict:
        """简单摘要（不使用 AI）"""
        # 提取前 200 字
        clean_body = body.replace('\n', ' ').strip()
        summary = clean_body[:max_length] + "..." if len(clean_body) > max_length else clean_body
        
        # 提取可能的时间点
        import re
        time_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}[日天]?|\d{1,2}:\d{2}'
        times = re.findall(time_pattern, body[:500])
        
        return {
            "success": True,
            "summary": {
                "one_sentence": summary,
                "key_points": times[:3] if times else ["无明确时间点"],
                "action_required": None
            }
        }
    
    def summarize_emails(
        self,
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = False,
        email_ids: List[str] = None
    ) -> List[Dict]:
        """
        批量摘要邮件
        
        Args:
            folder: 文件夹
            limit: 数量限制
            unread_only: 仅未读
            email_ids: 指定邮件 ID 列表
        """
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
            emails = self.fetch_emails(folder, limit, unread_only)
        
        # 生成摘要
        results = []
        for email in emails:
            print(f"处理：{email.get('subject', '无主题')}...")
            summary_result = self.generate_summary(
                email.get("subject", ""),
                email.get("body_text", "")
            )
            
            results.append({
                "id": email["id"],
                "subject": email["subject"],
                "sender": email["sender"],
                "date": email["date"],
                "summary": summary_result.get("summary", {}),
                "ai_success": summary_result.get("success", False)
            })
        
        return results


def main():
    parser = argparse.ArgumentParser(description="AI 邮件摘要生成")
    parser.add_argument("--folder", default="INBOX", help="文件夹")
    parser.add_argument("--limit", type=int, default=10, help="处理数量")
    parser.add_argument("--unread", action="store_true", help="仅未读邮件")
    parser.add_argument("--email-ids", help="指定邮件 ID（逗号分隔）")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码")
    
    args = parser.parse_args()
    
    email_ids = None
    if args.email_ids:
        email_ids = [eid.strip() for eid in args.email_ids.split(",")]
    
    try:
        summarizer = AISummarizer(args.email, args.auth_code)
        with summarizer:
            results = summarizer.summarize_emails(
                folder=args.folder,
                limit=args.limit,
                unread_only=args.unread,
                email_ids=email_ids
            )
            
            result = {
                "success": True,
                "total": len(results),
                "summaries": results
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
