#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票管理模块
"""

import json
import uuid
import re
from datetime import datetime
from pathlib import Path

class InvoiceManager:
    """发票管理器"""
    
    INVOICE_TYPES = {
        'input': '进项发票',
        'output': '销项发票'
    }
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.invoices_dir = self.data_dir / 'invoices'
        self.invoices_dir.mkdir(exist_ok=True)
    
    def create_invoice(self, invoice_type, invoice_no, amount, tax_amount=0,
                       seller=None, buyer=None, date=None, items=None):
        """录入发票"""
        # 检查发票号码格式
        if not self._validate_invoice_no(invoice_no):
            raise ValueError(f"发票号码格式不正确: {invoice_no}")
        
        # 检查是否重复
        existing = self.find_by_invoice_no(invoice_no)
        if existing:
            raise ValueError(f"发票已存在: {existing['id']}")
        
        invoice_id = f"INV{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        invoice = {
            "id": invoice_id,
            "type": invoice_type,
            "type_name": self.INVOICE_TYPES.get(invoice_type, invoice_type),
            "invoice_no": invoice_no,
            "amount": float(amount),
            "tax_amount": float(tax_amount),
            "total_amount": float(amount) + float(tax_amount),
            "seller": seller,
            "buyer": buyer,
            "date": date or datetime.now().strftime('%Y-%m-%d'),
            "items": items or [],
            "verified": False,
            "project_id": None,
            "contract_id": None,
            "transaction_id": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        file_path = self.invoices_dir / f"{invoice_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(invoice, f, ensure_ascii=False, indent=2)
        
        return invoice
    
    def _validate_invoice_no(self, invoice_no):
        """验证发票号码格式"""
        # 增值税发票号码通常为10-20位数字或字母组合
        if not invoice_no:
            return False
        # 基本格式检查
        pattern = r'^[A-Za-z0-9]{10,20}$'
        return bool(re.match(pattern, str(invoice_no)))
    
    def list_invoices(self, invoice_type=None, start_date=None, end_date=None):
        """列出发票"""
        invoices = []
        for file_path in self.invoices_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                invoice = json.load(f)
                if invoice_type and invoice.get('type') != invoice_type:
                    continue
                if start_date and invoice.get('date', '') < start_date:
                    continue
                if end_date and invoice.get('date', '') > end_date:
                    continue
                invoices.append(invoice)
        return sorted(invoices, key=lambda x: x['date'], reverse=True)
    
    def get_invoice(self, invoice_id):
        """获取发票详情"""
        file_path = self.invoices_dir / f"{invoice_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def find_by_invoice_no(self, invoice_no):
        """根据发票号码查找"""
        for file_path in self.invoices_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                invoice = json.load(f)
                if invoice.get('invoice_no') == invoice_no:
                    return invoice
        return None
    
    def check_duplicate(self, invoice_no):
        """检查发票是否重复"""
        return self.find_by_invoice_no(invoice_no)
    
    def update_invoice(self, invoice_id, data):
        """更新发票"""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None
        
        for key in ['invoice_no', 'amount', 'tax_amount', 'seller', 'buyer', 
                    'date', 'items', 'verified', 'project_id', 'contract_id']:
            if key in data and data[key] is not None:
                invoice[key] = data[key]
        
        # 重新计算价税合计
        invoice['total_amount'] = invoice['amount'] + invoice['tax_amount']
        invoice['updated_at'] = datetime.now().isoformat()
        
        file_path = self.invoices_dir / f"{invoice_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(invoice, f, ensure_ascii=False, indent=2)
        
        return invoice
    
    def link_contract(self, invoice_id, contract_id):
        """关联合同"""
        return self.update_invoice(invoice_id, {'contract_id': contract_id})
    
    def link_project(self, invoice_id, project_id):
        """关联项目"""
        return self.update_invoice(invoice_id, {'project_id': project_id})
    
    def get_summary_by_period(self, period):
        """按期间获取发票汇总"""
        # period 格式: YYYY-MM 或 YYYY-QN
        invoices = self.list_invoices()
        
        input_total = 0
        input_tax = 0
        output_total = 0
        output_tax = 0
        
        for inv in invoices:
            if period in inv.get('date', ''):
                if inv['type'] == 'input':
                    input_total += inv['amount']
                    input_tax += inv['tax_amount']
                else:
                    output_total += inv['amount']
                    output_tax += inv['tax_amount']
        
        return {
            'period': period,
            'input_amount': input_total,
            'input_tax': input_tax,
            'output_amount': output_total,
            'output_tax': output_tax
        }
