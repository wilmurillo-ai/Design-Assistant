#!/usr/bin/env python3
"""
AI 待办事项提取器
从邮件中自动提取待办任务和截止日期
"""

import os
import json
import argparse
import re
from datetime import datetime
from typing import List, Dict
from fetch_emails import QQEmailClient


class TodoExtractor(QQEmailClient):
    """待办事项提取器"""
    
    # 任务关键词
    TASK_PATTERNS = [
        r"请 (.+?)[。.!]",
        r"需要 (.+?)[。.!]",
        r"记得 (.+?)[。.!]",
        r"安排 (.+?)[。.!]",
        r"准备 (.+?)[。.!]",
        r"完成 (.+?)[。.!]",
        r"提交 (.+?)[。.!]",
        r"处理 (.+?)[。.!]",
        r"todo: (.+)",
        r"task: (.+)",
        r"action item: (.+)",
    ]
    
    # 日期时间模式
    DATE_PATTERNS = [
        r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        r"(\d{1,2}月\d{1,2}日)",
        r"(\d{1,2}:\d{2})",
        r"(今天 | 明天 | 后天 | 本周五 | 下周一)",
        r"(本周 | 下周 | 月底 | 月初)",
    ]
    
    def extract_date(self, text: str) -> str:
        """从文本中提取日期"""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1) if match.lastindex else match.group(0)
                return self._normalize_date(date_str)
        return None
    
    def _normalize_date(self, date_str: str) -> str:
        """标准化日期格式"""
        # 简单处理，实际可更复杂
        if "月" in date_str and "日" in date_str:
            # "3 月 25 日" -> "2026-03-25"
            match = re.match(r"(\d{1,2}) 月 (\d{1,2}) 日", date_str)
            if match:
                month, day = match.groups()
                year = datetime.now().year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        if "今天" in date_str:
            return datetime.now().strftime("%Y-%m-%d")
        elif "明天" in date_str:
            from datetime import timedelta
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "后天" in date_str:
            from datetime import timedelta
            return (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        # YYYY-MM-DD 格式
        if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
            return date_str
        
        return date_str
    
    def extract_todos_from_email(self, email: Dict) -> List[Dict]:
        """从单封邮件提取待办"""
        subject = email.get("subject", "")
        body = email.get("body_text", "")
        text = f"{subject}\n{body}"
        
        todos = []
        
        # 提取任务
        for pattern in self.TASK_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                task_text = match.strip()
                if len(task_text) > 5 and len(task_text) < 200:  # 过滤太短或太长的
                    # 尝试从上下文中提取截止日期
                    deadline = self.extract_date(text)
                    
                    # 评估优先级
                    priority = "medium"
                    if any(kw in task_text.lower() for kw in ["紧急", "急", "asap", "today"]):
                        priority = "high"
                    elif any(kw in task_text.lower() for kw in ["最好", "有空", "方便"]):
                        priority = "low"
                    
                    todos.append({
                        "task": task_text,
                        "deadline": deadline,
                        "priority": priority,
                        "source": "pattern"
                    })
        
        # 去重
        seen = set()
        unique_todos = []
        for todo in todos:
            task_key = todo["task"][:50]
            if task_key not in seen:
                seen.add(task_key)
                unique_todos.append(todo)
        
        return unique_todos
    
    def extract_todos_with_ai(self, email: Dict) -> List[Dict]:
        """使用 AI 提取待办（更准确）"""
        subject = email.get("subject", "")
        body = email.get("body_text", "")[:2000]
        
        prompt = f"""请从以下邮件中提取所有待办事项和任务：

主题：{subject}

内容：
{body}

要求：
1. 提取所有明确的任务/待办事项
2. 识别截止日期（如果有）
3. 评估优先级 (high/medium/low)

输出 JSON 数组格式：
[
  {{
    "task": "具体任务描述",
    "deadline": "YYYY-MM-DD" 或 null,
    "priority": "high|medium|low"
  }}
]

如果没有明确任务，返回空数组 []。
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
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    todos = json.loads(json_match.group())
                    for todo in todos:
                        todo["source"] = "ai"
                    return todos
        except Exception as e:
            print(f"AI 提取失败：{e}")
        
        # 降级到规则提取
        return self.extract_todos_from_email(email)
    
    def extract_all(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        email_ids: List[str] = None,
        use_ai: bool = True
    ) -> List[Dict]:
        """批量提取待办"""
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
        
        # 提取待办
        results = []
        for email in emails:
            print(f"提取：{email.get('subject', '无主题')}...")
            
            if use_ai:
                todos = self.extract_todos_with_ai(email)
            else:
                todos = self.extract_todos_from_email(email)
            
            if todos:
                results.append({
                    "email_id": email["id"],
                    "subject": email["subject"],
                    "sender": email["sender"],
                    "date": email["date"],
                    "todos": todos,
                    "todo_count": len(todos)
                })
        
        # 按待办数量排序
        results.sort(key=lambda x: -x["todo_count"])
        
        return results


def main():
    parser = argparse.ArgumentParser(description="AI 待办事项提取")
    parser.add_argument("--folder", default="INBOX", help="文件夹")
    parser.add_argument("--limit", type=int, default=50, help="处理数量")
    parser.add_argument("--email-ids", help="指定邮件 ID（逗号分隔）")
    parser.add_argument("--no-ai", action="store_true", help="不使用 AI，仅规则提取")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码")
    
    args = parser.parse_args()
    
    email_ids = None
    if args.email_ids:
        email_ids = [eid.strip() for eid in args.email_ids.split(",")]
    
    try:
        extractor = TodoExtractor(args.email, args.auth_code)
        with extractor:
            results = extractor.extract_all(
                folder=args.folder,
                limit=args.limit,
                email_ids=email_ids,
                use_ai=not args.no_ai
            )
            
            # 统计
            total_todos = sum(r["todo_count"] for r in results)
            
            result = {
                "success": True,
                "emails_with_todos": len(results),
                "total_todos": total_todos,
                "todos_by_email": results
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
