#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子归档模块
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

class ArchiveManager:
    """电子归档管理器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.archive_dir = self.data_dir / 'archive'
        self.archive_dir.mkdir(exist_ok=True)
    
    def archive_project(self, project_id):
        """归档项目资料"""
        from project_manager import ProjectManager
        pm = ProjectManager(self.data_dir)
        
        project = pm.get_project(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 收集项目相关资料
        archive_data = {
            'type': 'project',
            'id': project_id,
            'name': project['name'],
            'project_data': project,
            'contracts': [],
            'invoices': [],
            'transactions': [],
            'archived_at': datetime.now().isoformat()
        }
        
        # 收集关联合同
        from contract_manager import ContractManager
        cm = ContractManager(self.data_dir)
        for contract_id in project.get('contracts', []):
            contract = cm.get_contract(contract_id)
            if contract:
                archive_data['contracts'].append(contract)
        
        # 收集关联发票
        from invoice_manager import InvoiceManager
        im = InvoiceManager(self.data_dir)
        for invoice_id in project.get('invoices', []):
            invoice = im.get_invoice(invoice_id)
            if invoice:
                archive_data['invoices'].append(invoice)
        
        # 保存归档文件
        file_path = self.archive_dir / f'project_{project_id}_{datetime.now().strftime("%Y%m%d")}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
        return archive_data
    
    def archive_contract(self, contract_id):
        """归档合同"""
        from contract_manager import ContractManager
        cm = ContractManager(self.data_dir)
        
        contract = cm.get_contract(contract_id)
        if not contract:
            raise ValueError(f"合同不存在: {contract_id}")
        
        archive_data = {
            'type': 'contract',
            'id': contract_id,
            'name': f"{contract['type_name']}-{contract['counterparty']}",
            'contract_data': contract,
            'archived_at': datetime.now().isoformat()
        }
        
        file_path = self.archive_dir / f'contract_{contract_id}_{datetime.now().strftime("%Y%m%d")}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
        return archive_data
    
    def archive_period(self, period):
        """按期间归档所有资料"""
        # period 格式: YYYY-MM 或 YYYY-QN
        
        archive_data = {
            'type': 'period',
            'period': period,
            'projects': [],
            'contracts': [],
            'invoices': [],
            'transactions': [],
            'vouchers': [],
            'tax_returns': [],
            'archived_at': datetime.now().isoformat()
        }
        
        # 归档该期间的发票
        from invoice_manager import InvoiceManager
        im = InvoiceManager(self.data_dir)
        invoices = im.list_invoices()
        for inv in invoices:
            if period in inv.get('date', ''):
                archive_data['invoices'].append(inv)
        
        # 归档该期间的凭证
        from accounting_manager import AccountingManager
        am = AccountingManager(self.data_dir)
        vouchers = am.list_vouchers()
        for vou in vouchers:
            if period in vou.get('date', ''):
                archive_data['vouchers'].append(vou)
        
        # 归档该期间的税务申报
        tax_dir = self.data_dir / 'tax'
        for tax_file in tax_dir.glob(f'*{period}*.json'):
            with open(tax_file, 'r', encoding='utf-8') as f:
                archive_data['tax_returns'].append(json.load(f))
        
        # 保存归档文件
        file_path = self.archive_dir / f'period_{period}_{datetime.now().strftime("%Y%m%d")}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
        return archive_data
    
    def list_archives(self):
        """列出所有归档"""
        archives = []
        for file_path in self.archive_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                archive = json.load(f)
                archives.append({
                    'id': f"{archive['type']}_{archive.get('id', archive.get('period', ''))}",
                    'type': archive['type'],
                    'name': archive.get('name', archive.get('period', 'Unknown')),
                    'archived_at': archive['archived_at'],
                    'file': str(file_path)
                })
        return sorted(archives, key=lambda x: x['archived_at'], reverse=True)
    
    def get_archive(self, archive_id):
        """获取归档详情"""
        for file_path in self.archive_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                archive = json.load(f)
                if archive.get('id') == archive_id or f"{archive['type']}_{archive.get('id', archive.get('period', ''))}" == archive_id:
                    return archive
        return None
    
    def export_archive(self, archive_id, export_dir):
        """导出归档到指定目录"""
        archive = self.get_archive(archive_id)
        if not archive:
            raise ValueError(f"归档不存在: {archive_id}")
        
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        file_path = export_path / f"{archive_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(archive, f, ensure_ascii=False, indent=2)
        
        return file_path
