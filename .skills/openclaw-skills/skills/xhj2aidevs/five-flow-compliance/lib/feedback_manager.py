# -*- coding: utf-8 -*-
"""
用户反馈收集与自动提交模块

功能：
- 记录用户使用过程中遇到的问题
- 累计5条以上自动导出并发送到作者邮箱
- 保留反馈历史便于追踪优化
"""

import os
import json
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# SMTP 配置（可从环境变量读取）
SMTP_CONFIG = {
    'host': os.environ.get('SMTP_HOST', 'smtp.189.cn'),
    'port': int(os.environ.get('SMTP_PORT', '465')),
    'user': os.environ.get('SMTP_USER', ''),
    'password': os.environ.get('SMTP_PASSWORD', ''),
    'use_ssl': True
}

# 作者邮箱
AUTHOR_EMAIL = 'jacky.zhouxj@189.cn'
FEEDBACK_EMAIL_SUBJECT = '【五流合一】用户反馈问题汇总'

# 反馈文件路径
FEEDBACK_DIR = None  # 由 FeedbackManager 初始化时设置


class FeedbackManager:
    """反馈管理器"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            skill_dir = Path(__file__).parent.parent
            data_dir = skill_dir / 'data'
        
        self.data_dir = Path(data_dir)
        self.feedback_dir = self.data_dir / 'feedback'
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        self.issues_file = self.feedback_dir / 'issues.json'
        self.history_file = self.feedback_dir / 'history.json'
        
        self._load_issues()
    
    def _load_issues(self):
        """加载问题列表"""
        if self.issues_file.exists():
            with open(self.issues_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.issues = data.get('issues', [])
                self.last_sent = data.get('last_sent')
        else:
            self.issues = []
            self.last_sent = None
    
    def _save_issues(self):
        """保存问题列表"""
        data = {
            'issues': self.issues,
            'last_sent': self.last_sent,
            'count': len(self.issues)
        }
        with open(self.issues_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_issue(self, issue: str, context: str = '', 
                  session_id: str = '', user_id: str = '') -> Dict:
        """添加一个问题
        
        Args:
            issue: 问题描述（必填）
            context: 上下文/场景描述
            session_id: 会话ID
            user_id: 用户标识
            
        Returns:
            包含添加结果和自动发送状态
        """
        issue_entry = {
            'id': len(self.issues) + 1,
            'content': issue,
            'context': context,
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.issues.append(issue_entry)
        self._save_issues()
        
        count = len(self.issues)
        auto_send = False
        send_result = None
        
        # 累计 >= 5 条，自动发送
        if count >= 5:
            auto_send = True
            send_result = self._send_feedback_email()
        
        return {
            'added': True,
            'total_count': count,
            'auto_sent': auto_send,
            'send_result': send_result,
            'issue_id': issue_entry['id']
        }
    
    def get_issues(self, limit: int = 100) -> List[Dict]:
        """获取问题列表"""
        return self.issues[-limit:]
    
    def get_count(self) -> int:
        """获取问题数量"""
        return len(self.issues)
    
    def clear_issues(self, issue_ids: List[int] = None):
        """清除问题
        
        Args:
            issue_ids: 要清除的问题ID列表，None=全部清除
        """
        if issue_ids is None:
            self.issues = []
        else:
            self.issues = [i for i in self.issues if i['id'] not in issue_ids]
        
        self._save_issues()
    
    def _generate_feedback_report(self) -> tuple:
        """生成反馈报告文本和文件路径
        
        Returns:
            (报告文本, 附件文件路径)
        """
        now = datetime.now()
        
        report_lines = [
            "=" * 60,
            "五流合一企业合规经营管理系统 - 用户反馈报告",
            "=" * 60,
            f"生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"问题总数: {len(self.issues)}",
            "=" * 60,
            "",
            "【问题列表】",
            "-" * 60
        ]
        
        # 按时间倒序排列
        for issue in sorted(self.issues, key=lambda x: x['timestamp'], reverse=True):
            report_lines.extend([
                f"[#{issue['id']}] {issue['timestamp']}",
                f"问题: {issue['content']}",
                f"场景: {issue['context'] or '通用场景'}",
                f"会话: {issue['session_id'] or 'N/A'}",
                "-" * 40
            ])
        
        report_lines.extend([
            "",
            "=" * 60,
            "【系统信息】",
            f"Hostname: {socket.gethostname()}",
            f"Python: {socket.get_python_version() if hasattr(socket, 'get_python_version') else 'N/A'}",
            "=" * 60,
            "【建议】",
            "请作者根据上述问题进行优化，感谢使用！",
            ""
        ])
        
        report_text = '\n'.join(report_lines)
        
        # 生成附件文件
        report_filename = f"feedback_report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        report_file = self.feedback_dir / report_filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return report_text, str(report_file)
    
    def _send_feedback_email(self) -> Dict:
        """发送反馈邮件"""
        try:
            report_text, report_file = self._generate_feedback_report()
            
            # 构建邮件
            msg = MIMEMultipart('mixed')
            msg['From'] = formataddr(['五流合一系统', SMTP_CONFIG['user'] or 'noreply@system.local'])
            msg['To'] = AUTHOR_EMAIL
            msg['Subject'] = Header(FEEDBACK_EMAIL_SUBJECT, 'utf-8')
            
            # 邮件正文
            body = f"""
您好，

这是五流合一企业合规经营管理系统的自动反馈报告。

本次共收集到 {len(self.issues)} 条用户问题，已随邮件附件发送详细报告。

请根据反馈进行优化，感谢您的支持！

--
五流合一系统自动反馈
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            report_filename = Path(report_file).name
            with open(report_file, 'r', encoding='utf-8') as f:
                attachment = MIMEText(f.read(), 'plain', 'utf-8')
                attachment.add_header('Content-Disposition', 'attachment', 
                                   filename=Header(report_filename, 'utf-8').encode())
                msg.attach(attachment)
            
            # 发送邮件
            if SMTP_CONFIG['use_ssl']:
                with smtplib.SMTP_SSL(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
                    if SMTP_CONFIG['user'] and SMTP_CONFIG['password']:
                        server.login(SMTP_CONFIG['user'], SMTP_CONFIG['password'])
                    server.send_message(msg)
            else:
                with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
                    if SMTP_CONFIG['user'] and SMTP_CONFIG['password']:
                        server.login(SMTP_CONFIG['user'], SMTP_CONFIG['password'])
                    server.send_message(msg)
            
            # 更新状态
            self.last_sent = datetime.now().isoformat()
            self._save_issues()
            
            return {
                'success': True,
                'message': f'反馈已发送到 {AUTHOR_EMAIL}',
                'report_file': report_file
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'发送失败: {str(e)}',
                'error': str(e)
            }
    
    def send_manual_feedback(self, note: str = '') -> Dict:
        """手动发送反馈邮件（不依赖数量限制）
        
        Args:
            note: 备注信息
        """
        return self._send_feedback_email()
    
    def export_history(self) -> List[Dict]:
        """导出历史反馈记录"""
        history_file = self.feedback_dir / 'history.json'
        
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return []
    
    def add_to_history(self, report_file: str, recipient: str, status: str):
        """添加到发送历史"""
        history_file = self.feedback_dir / 'history.json'
        
        history = []
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            'timestamp': datetime.now().isoformat(),
            'report_file': report_file,
            'recipient': recipient,
            'status': status,
            'issue_count': len(self.issues)
        })
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    """命令行测试"""
    import sys
    
    fm = FeedbackManager()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python feedback_manager.py add <问题描述>")
        print("  python feedback_manager.py list")
        print("  python feedback_manager.py count")
        print("  python feedback_manager.py send")
        print("  python feedback_manager.py clear")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'add':
        if len(sys.argv) < 3:
            print("请提供问题描述")
            return
        issue = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ''
        
        result = fm.add_issue(issue, context)
        print(f"[OK] 问题已添加 (共 {result['total_count']} 条)")
        
        if result['auto_sent']:
            print(f"[AUTO] 已自动发送反馈: {result['send_result']['message']}")
    
    elif cmd == 'list':
        issues = fm.get_issues()
        if not issues:
            print("暂无问题记录")
            return
        
        for i in issues:
            print(f"  [#{i['id']}] {i['timestamp']}: {i['content']}")
    
    elif cmd == 'count':
        print(f"当前问题数量: {fm.get_count()}")
    
    elif cmd == 'send':
        result = fm.send_manual_feedback()
        print(result['message'])
    
    elif cmd == 'clear':
        fm.clear_issues()
        print("[OK] 问题已清除")


if __name__ == '__main__':
    main()
