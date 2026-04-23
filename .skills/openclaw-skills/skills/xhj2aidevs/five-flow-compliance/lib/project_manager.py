#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目管理模块
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class ProjectManager:
    """项目管理器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.projects_dir = self.data_dir / 'projects'
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_project(self, name, client, budget=0, start_date=None, end_date=None):
        """创建新项目"""
        project_id = f"PRJ{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        project = {
            "id": project_id,
            "name": name,
            "client": client,
            "budget": float(budget),
            "start_date": start_date or datetime.now().strftime('%Y-%m-%d'),
            "end_date": end_date,
            "status": "active",
            "income": 0,
            "expense": 0,
            "profit": 0,
            "contracts": [],
            "invoices": [],
            "transactions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        file_path = self.projects_dir / f"{project_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        return project
    
    def list_projects(self, status=None):
        """列出所有项目"""
        projects = []
        for file_path in self.projects_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                project = json.load(f)
                if status is None or project.get('status') == status:
                    projects.append(project)
        return sorted(projects, key=lambda x: x['created_at'], reverse=True)
    
    def get_project(self, project_id):
        """获取项目详情"""
        file_path = self.projects_dir / f"{project_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def update_project(self, project_id, data):
        """更新项目"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 更新字段
        for key in ['name', 'client', 'budget', 'start_date', 'end_date', 'status']:
            if key in data and data[key] is not None:
                project[key] = data[key]
        
        project['updated_at'] = datetime.now().isoformat()
        
        file_path = self.projects_dir / f"{project_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        return project
    
    def close_project(self, project_id):
        """结项项目"""
        return self.update_project(project_id, {'status': 'closed'})
    
    def link_contract(self, project_id, contract_id):
        """关联合同"""
        project = self.get_project(project_id)
        if project and contract_id not in project['contracts']:
            project['contracts'].append(contract_id)
            self.update_project(project_id, project)
    
    def link_invoice(self, project_id, invoice_id):
        """关联发票"""
        project = self.get_project(project_id)
        if project and invoice_id not in project['invoices']:
            project['invoices'].append(invoice_id)
            self.update_project(project_id, project)
    
    def link_transaction(self, project_id, transaction_id):
        """关联银行流水"""
        project = self.get_project(project_id)
        if project and transaction_id not in project['transactions']:
            project['transactions'].append(transaction_id)
            self.update_project(project_id, project)
    
    def update_financials(self, project_id):
        """更新项目财务数据"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 从关联数据计算
        # 这里简化处理，实际应该从关联的合同、发票、流水计算
        project['profit'] = project['income'] - project['expense']
        project['updated_at'] = datetime.now().isoformat()
        
        file_path = self.projects_dir / f"{project_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        return project
