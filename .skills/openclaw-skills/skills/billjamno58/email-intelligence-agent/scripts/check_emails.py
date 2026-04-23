#!/usr/bin/env python3
"""
邮件客服助手 - 检查新邮件主脚本
功能：IMAP读取 → AI分类 → 回复建议 → 飞书推送

ClawHub 版本使用 SkillPay 计费
"""

import sys
import json
import argparse
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional

# 导入本地模块
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from imap_client import IMAPClient
from classifier import EmailClassifier
from reply_generator import ReplyGenerator
from feishu_pusher import FeishuPusher


# ═══════════════════════════════════════════════════════════════
# SkillPay Billing Integration / ClawHub 计费
# 实际调用时扣费，API Key/Skill ID 从环境变量读取
# ═══════════════════════════════════════════════════════════════
BILLING_API_URL = "https://skillpay.me/api/v1/billing"
CALL_PRICE = 0.05  # USDT per call


def _get_billing_headers() -> dict:
    api_key = os.environ.get("SKILL_BILLING_API_KEY", "")
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def _get_skill_id() -> str:
    return os.environ.get("SKILL_BILLING_SKILL_ID", "")


def check_balance(user_id: str) -> float:
    """查询用户余额 (USDT)"""
    resp = requests.get(
        f"{BILLING_API_URL}/balance",
        params={"user_id": user_id},
        headers=_get_billing_headers(),
        timeout=10,
    )
    return resp.json().get("balance", 0.0)


def charge_user(user_id: str) -> dict:
    """
    每次调用扣费。
    余额不足时返回 payment_url（充值链接）。
    """
    resp = requests.post(
        f"{BILLING_API_URL}/charge",
        headers=_get_billing_headers(),
        json={
            "user_id": user_id,
            "skill_id": _get_skill_id(),
            "amount": CALL_PRICE,
        },
        timeout=10,
    )
    data = resp.json()
    if data.get("success"):
        return {"ok": True, "balance": data.get("balance", 0.0)}
    return {
        "ok": False,
        "balance": data.get("balance", 0.0),
        "payment_url": data.get("payment_url"),
    }


def get_payment_link(user_id: str, amount: float = 8.0) -> str:
    """生成充值链接"""
    resp = requests.post(
        f"{BILLING_API_URL}/payment-link",
        headers=_get_billing_headers(),
        json={"user_id": user_id, "amount": amount},
        timeout=10,
    )
    return resp.json().get("payment_url", "")


class EmailAssistant:
    """邮件客服助手主类"""

    def __init__(self, config: dict, api_key: str = ""):
        self.config = config
        self.user_id = os.environ.get("FEISHU_USER_ID", "")
        self.tier = config.get("tier", "FREE")
        # 延迟初始化，避免 IMAP 连接提前建立
        self._imap_client = None
        self._classifier = None
        self._reply_gen = None
        self._pusher = None

    def _get_imap_client(self):
        if self._imap_client is None:
            self._imap_client = IMAPClient(self.config.get('imap', {}))
        return self._imap_client

    def _get_classifier(self):
        if self._classifier is None:
            self._classifier = EmailClassifier(self.config.get('ai', {}))
        return self._classifier

    def _get_reply_gen(self):
        if self._reply_gen is None:
            self._reply_gen = ReplyGenerator(self.config.get('ai', {}))
        return self._reply_gen

    def _get_pusher(self):
        if self._pusher is None:
            self._pusher = FeishuPusher(self.config.get('feishu', {}))
        return self._pusher

    def process_emails(self, limit: int = 10) -> list:
        """
        检查并处理邮件

        Args:
            limit: 最多处理邮件数

        Returns:
            处理结果列表
        """
        # ── SkillPay 扣费（实际执行时才扣）─────────────────────────────
        if self.user_id:
            billing = charge_user(self.user_id)
            if not billing["ok"]:
                payment_url = billing.get("payment_url", "")
                print(f"[WARN] Balance insufficient. Payment: {payment_url}")
                return [{"error": "Insufficient balance. Please top up.", "payment_url": payment_url}]
            else:
                print(f"[INFO] Charged {CALL_PRICE} USDT, balance: {billing['balance']}")

        # 连接邮箱
        imap_client = self._get_imap_client()
        if not imap_client.connect():
            return [{'error': '连接邮箱失败'}]

        try:
            # 获取最新邮件
            emails = imap_client.fetch_unread(limit=limit)
            if not emails:
                return []

            classifier = self._get_classifier()
            reply_gen = self._get_reply_gen()
            pusher = self._get_pusher()

            results = []
            for email in emails:
                # AI分类
                category = classifier.classify(email)
                email['category'] = category

                # 生成回复建议
                reply_suggestion = reply_gen.generate(email)
                email['reply_suggestion'] = reply_suggestion

                results.append(email)

            # 推送飞书
            if results and self.config.get('feishu', {}).get('enabled'):
                pusher.push_summary(results)

            return results

        finally:
            imap_client.disconnect()

    def generate_report(self, results: list) -> str:
        """生成处理报告"""
        if not results:
            return "✅ 没有新邮件"

        report = ["📧 邮件处理报告", "=" * 30, ""]

        categories = {}
        for r in results:
            cat = r.get('category', '🟢 可延后')
            categories[cat] = categories.get(cat, 0) + 1

        report.append(f"总计: {len(results)} 封")
        report.append("")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            report.append(f"  {cat}: {count} 封")

        report.append("")
        report.append("-" * 30)

        for i, r in enumerate(results, 1):
            cat = r.get('category', '🟢 可延后')
            subject = r.get('subject', '(无主题)')[:50]
            from_ = r.get('from', '未知发件人')
            snippet = r.get('snippet', '')[:100]

            report.append(f"\n{i}. {cat}")
            report.append(f"   主题: {subject}")
            report.append(f"   发件人: {from_}")
            if snippet:
                report.append(f"   摘要: {snippet}...")

        return "\n".join(report)


def load_config(config_path: str = 'config/config.yaml') -> dict:
    """加载配置文件"""
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        json_path = config_path.replace('.yaml', '.json').replace('config/', 'config/')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}


def main():
    parser = argparse.ArgumentParser(description='邮件客服助手')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--limit', '-l', type=int, default=10, help='处理邮件数量上限')
    parser.add_argument('--api-key', default='', help='API key (deprecated, unused in ClawHub version)')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')
    parser.add_argument('--dry-run', action='store_true', help='仅检查不推送')

    args = parser.parse_args()

    config = load_config(args.config)
    assistant = EmailAssistant(config, api_key=args.api_key)

    results = assistant.process_emails(limit=args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(assistant.generate_report(results))

    urgent = [r for r in results if '🔴' in r.get('category', '')]
    if urgent:
        print("\n" + "=" * 30)
        print("⚠️  紧急邮件回复建议")
        print("=" * 30)
        for r in urgent:
            print(f"\n主题: {r.get('subject')}")
            print(f"建议回复:\n{r.get('reply_suggestion', '暂无建议')}")
            print("-" * 20)


if __name__ == '__main__':
    main()
