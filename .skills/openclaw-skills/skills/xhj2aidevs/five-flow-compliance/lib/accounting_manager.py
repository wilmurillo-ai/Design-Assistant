#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务记账模块
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class AccountingManager:
    """财务管理器"""
    
    # 会计科目表（简化版）
    ACCOUNTS = {
        '1001': {'name': '库存现金', 'type': 'asset'},
        '1002': {'name': '银行存款', 'type': 'asset'},
        '1122': {'name': '应收账款', 'type': 'asset'},
        '1123': {'name': '预付账款', 'type': 'asset'},
        '1403': {'name': '原材料', 'type': 'asset'},
        '1405': {'name': '库存商品', 'type': 'asset'},
        '1601': {'name': '固定资产', 'type': 'asset'},
        '1602': {'name': '累计折旧', 'type': 'asset'},
        '2001': {'name': '短期借款', 'type': 'liability'},
        '2202': {'name': '应付账款', 'type': 'liability'},
        '2203': {'name': '预收账款', 'type': 'liability'},
        '2221': {'name': '应交税费', 'type': 'liability'},
        '4001': {'name': '实收资本', 'type': 'equity'},
        '4103': {'name': '本年利润', 'type': 'equity'},
        '4104': {'name': '利润分配', 'type': 'equity'},
        '5001': {'name': '生产成本', 'type': 'cost'},
        '6001': {'name': '主营业务收入', 'type': 'revenue'},
        '6051': {'name': '其他业务收入', 'type': 'revenue'},
        '6401': {'name': '主营业务成本', 'type': 'expense'},
        '6403': {'name': '营业税金及附加', 'type': 'expense'},
        '6601': {'name': '销售费用', 'type': 'expense'},
        '6602': {'name': '管理费用', 'type': 'expense'},
        '6603': {'name': '财务费用', 'type': 'expense'},
        '6801': {'name': '所得税费用', 'type': 'expense'},
    }
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.vouchers_dir = self.data_dir / 'vouchers'
        self.vouchers_dir.mkdir(exist_ok=True)
    
    def generate_voucher(self, date, description, entries):
        """生成会计凭证"""
        # entries 格式: [{"account": "1002", "debit": 1000, "credit": 0}, ...]
        if isinstance(entries, str):
            entries = json.loads(entries)
        
        # 验证借贷平衡
        total_debit = sum(e.get('debit', 0) for e in entries)
        total_credit = sum(e.get('credit', 0) for e in entries)
        
        if abs(total_debit - total_credit) > 0.01:
            raise ValueError(f"借贷不平衡: 借方 {total_debit} != 贷方 {total_credit}")
        
        voucher_id = f"VOU{date.replace('-', '')}{uuid.uuid4().hex[:6].upper()}"
        
        voucher = {
            "id": voucher_id,
            "date": date,
            "description": description,
            "entries": entries,
            "debit_total": total_debit,
            "credit_total": total_credit,
            "attachments": [],
            "created_at": datetime.now().isoformat()
        }
        
        file_path = self.vouchers_dir / f"{voucher_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(voucher, f, ensure_ascii=False, indent=2)
        
        return voucher
    
    def list_vouchers(self, start_date=None, end_date=None):
        """列出凭证"""
        vouchers = []
        for file_path in self.vouchers_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                voucher = json.load(f)
                if start_date and voucher.get('date', '') < start_date:
                    continue
                if end_date and voucher.get('date', '') > end_date:
                    continue
                vouchers.append(voucher)
        return sorted(vouchers, key=lambda x: x['date'], reverse=True)
    
    def get_voucher(self, voucher_id):
        """获取凭证详情"""
        file_path = self.vouchers_dir / f"{voucher_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_account_balances(self, period=None):
        """获取科目余额"""
        # 简化实现：统计每个科目的借贷发生额
        vouchers = self.list_vouchers()
        
        balances = {}
        for code, info in self.ACCOUNTS.items():
            balances[code] = {
                'code': code,
                'name': info['name'],
                'type': info['type'],
                'opening': 0,
                'debit': 0,
                'credit': 0,
                'closing': 0
            }
        
        for voucher in vouchers:
            for entry in voucher.get('entries', []):
                code = entry.get('account_code')
                if code in balances:
                    balances[code]['debit'] += entry.get('debit', 0)
                    balances[code]['credit'] += entry.get('credit', 0)
        
        # 计算期末余额（简化处理）
        for code in balances:
            b = balances[code]
            if b['type'] in ['asset', 'expense', 'cost']:
                b['closing'] = b['opening'] + b['debit'] - b['credit']
            else:
                b['closing'] = b['opening'] + b['credit'] - b['debit']
        
        return list(balances.values())
    
    def generate_report(self, report_type, period):
        """生成财务报表"""
        if report_type == 'profit':
            return self._generate_profit_statement(period)
        elif report_type == 'balance':
            return self._generate_balance_sheet(period)
        elif report_type == 'cashflow':
            return self._generate_cashflow_statement(period)
        else:
            raise ValueError(f"未知的报表类型: {report_type}")
    
    def _generate_profit_statement(self, period):
        """生成利润表"""
        balances = self.get_account_balances(period)
        
        revenue = sum(b['credit'] for b in balances if b['type'] == 'revenue')
        # 成本包括: 主营业务成本(6401) 和 生产成本(5001)
        cost = sum(b['debit'] for b in balances if b['code'] in ['6401', '5001'])
        expense = sum(b['debit'] for b in balances if b['type'] == 'expense' and b['code'] not in ['6401', '5001'])
        
        gross_profit = revenue - cost
        operating_profit = gross_profit - expense
        
        return {
            'period': period,
            'report_type': '利润表',
            'revenue': revenue,
            'cost': cost,
            'gross_profit': gross_profit,
            'expenses': expense,
            'operating_profit': operating_profit,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_balance_sheet(self, period):
        """生成资产负债表"""
        balances = self.get_account_balances(period)
        
        assets = sum(b['closing'] for b in balances if b['type'] == 'asset')
        liabilities = sum(b['closing'] for b in balances if b['type'] == 'liability')
        equity = sum(b['closing'] for b in balances if b['type'] == 'equity')
        
        return {
            'period': period,
            'report_type': '资产负债表',
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'liabilities_and_equity': liabilities + equity,
            'balanced': abs(assets - (liabilities + equity)) < 0.01,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_cashflow_statement(self, period):
        """生成现金流量表（简化版）"""
        vouchers = self.list_vouchers()
        
        operating_in = 0
        operating_out = 0
        investing_in = 0
        investing_out = 0
        financing_in = 0
        financing_out = 0
        
        for voucher in vouchers:
            for entry in voucher.get('entries', []):
                if entry.get('account_code') == '1002':  # 银行存款
                    if entry.get('debit', 0) > 0:
                        operating_in += entry['debit']
                    if entry.get('credit', 0) > 0:
                        operating_out += entry['credit']
        
        return {
            'period': period,
            'report_type': '现金流量表',
            'operating_cash_in': operating_in,
            'operating_cash_out': operating_out,
            'operating_cash_net': operating_in - operating_out,
            'investing_cash_net': investing_in - investing_out,
            'financing_cash_net': financing_in - financing_out,
            'cash_increase': (operating_in - operating_out) + (investing_in - investing_out) + (financing_in - financing_out),
            'generated_at': datetime.now().isoformat()
        }
