#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同管理模块
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class ContractManager:
    """合同管理器"""
    
    CONTRACT_TYPES = {
        'purchase': '采购合同',
        'sales': '销售合同'
    }
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.contracts_dir = self.data_dir / 'contracts'
        self.contracts_dir.mkdir(exist_ok=True)
    
    def create_contract(self, contract_type, counterparty, amount, project_id=None, 
                        sign_date=None, items=None):
        """创建合同"""
        contract_id = f"CNT{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        contract = {
            "id": contract_id,
            "type": contract_type,
            "type_name": self.CONTRACT_TYPES.get(contract_type, contract_type),
            "counterparty": counterparty,
            "amount": float(amount),
            "project_id": project_id,
            "sign_date": sign_date or datetime.now().strftime('%Y-%m-%d'),
            "items": items or [],
            "status": "active",
            "invoiced_amount": 0,
            "paid_amount": 0,
            "invoices": [],
            "transactions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        file_path = self.contracts_dir / f"{contract_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(contract, f, ensure_ascii=False, indent=2)
        
        # 如果有关联项目，更新项目
        if project_id:
            from project_manager import ProjectManager
            pm = ProjectManager(self.data_dir)
            pm.link_contract(project_id, contract_id)
        
        return contract
    
    def list_contracts(self, contract_type=None, status=None):
        """列出合同"""
        contracts = []
        for file_path in self.contracts_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                contract = json.load(f)
                if contract_type and contract.get('type') != contract_type:
                    continue
                if status and contract.get('status') != status:
                    continue
                contracts.append(contract)
        return sorted(contracts, key=lambda x: x['created_at'], reverse=True)
    
    def get_contract(self, contract_id):
        """获取合同详情"""
        file_path = self.contracts_dir / f"{contract_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def update_contract(self, contract_id, data):
        """更新合同"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        for key in ['counterparty', 'amount', 'sign_date', 'status', 'items']:
            if key in data and data[key] is not None:
                contract[key] = data[key]
        
        contract['updated_at'] = datetime.now().isoformat()
        
        file_path = self.contracts_dir / f"{contract_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(contract, f, ensure_ascii=False, indent=2)
        
        return contract
    
    def archive_contract(self, contract_id):
        """归档合同"""
        return self.update_contract(contract_id, {'status': 'archived'})
    
    def link_invoice(self, contract_id, invoice_id, amount):
        """关联发票"""
        contract = self.get_contract(contract_id)
        if contract:
            if invoice_id not in contract['invoices']:
                contract['invoices'].append(invoice_id)
                contract['invoiced_amount'] = contract.get('invoiced_amount', 0) + amount
                contract['updated_at'] = datetime.now().isoformat()
                
                file_path = self.contracts_dir / f"{contract_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(contract, f, ensure_ascii=False, indent=2)
    
    def link_transaction(self, contract_id, transaction_id, amount):
        """关联银行流水"""
        contract = self.get_contract(contract_id)
        if contract:
            if transaction_id not in contract['transactions']:
                contract['transactions'].append(transaction_id)
                contract['paid_amount'] = contract.get('paid_amount', 0) + amount
                contract['updated_at'] = datetime.now().isoformat()
                
                file_path = self.contracts_dir / f"{contract_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(contract, f, ensure_ascii=False, indent=2)
    
    def get_contracts_by_project(self, project_id):
        """获取项目的所有合同"""
        contracts = []
        for file_path in self.contracts_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                contract = json.load(f)
                if contract.get('project_id') == project_id:
                    contracts.append(contract)
        return contracts
