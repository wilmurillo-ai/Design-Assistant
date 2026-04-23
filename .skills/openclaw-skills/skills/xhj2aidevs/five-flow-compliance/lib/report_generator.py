#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块
"""

import json
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.reports_dir = self.data_dir / 'reports'
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_business_report(self, period):
        """生成经营分析报告"""
        from project_manager import ProjectManager
        from contract_manager import ContractManager
        from invoice_manager import InvoiceManager
        from bank_manager import BankManager
        
        pm = ProjectManager(self.data_dir)
        cm = ContractManager(self.data_dir)
        im = InvoiceManager(self.data_dir)
        bm = BankManager(self.data_dir)
        
        # 项目统计
        projects = pm.list_projects()
        active_projects = [p for p in projects if p['status'] == 'active']
        closed_projects = [p for p in projects if p['status'] == 'closed']
        
        # 合同统计
        contracts = cm.list_contracts()
        sales_contracts = [c for c in contracts if c['type'] == 'sales']
        purchase_contracts = [c for c in contracts if c['type'] == 'purchase']
        
        # 发票统计
        invoice_summary = im.get_summary_by_period(period)
        
        # 银行流水统计
        bank_stats = bm.get_statistics()
        
        report = {
            'report_type': '经营分析报告',
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'project_summary': {
                'total_projects': len(projects),
                'active_projects': len(active_projects),
                'closed_projects': len(closed_projects),
                'total_budget': sum(p.get('budget', 0) for p in projects)
            },
            'contract_summary': {
                'total_contracts': len(contracts),
                'sales_contracts': len(sales_contracts),
                'purchase_contracts': len(purchase_contracts),
                'sales_amount': sum(c['amount'] for c in sales_contracts),
                'purchase_amount': sum(c['amount'] for c in purchase_contracts)
            },
            'invoice_summary': invoice_summary,
            'cashflow_summary': bank_stats,
            'profit_analysis': {
                'revenue': invoice_summary['output_amount'],
                'cost': invoice_summary['input_amount'],
                'gross_profit': invoice_summary['output_amount'] - invoice_summary['input_amount'],
                'profit_margin': 0
            }
        }
        
        if report['profit_analysis']['revenue'] > 0:
            report['profit_analysis']['profit_margin'] = (
                report['profit_analysis']['gross_profit'] / report['profit_analysis']['revenue'] * 100
            )
        
        return report
    
    def generate_tax_report(self, period):
        """生成税务分析报告"""
        from tax_manager import TaxManager
        from invoice_manager import InvoiceManager
        
        tm = TaxManager(self.data_dir)
        im = InvoiceManager(self.data_dir)
        
        # 税务计算
        vat = tm.calculate_vat(period)
        surtax = tm.calculate_surtaxes(period)
        income_tax = tm.calculate_income_tax(period, 'corporate')
        
        # 发票分析
        invoices = im.list_invoices()
        period_invoices = [inv for inv in invoices if period in inv.get('date', '')]
        
        input_invoices = [inv for inv in period_invoices if inv['type'] == 'input']
        output_invoices = [inv for inv in period_invoices if inv['type'] == 'output']
        
        report = {
            'report_type': '税务分析报告',
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'vat_analysis': vat,
            'surtax_analysis': surtax,
            'income_tax_analysis': income_tax,
            'total_tax': vat['vat_payable'] + surtax['total_surtax'] + income_tax['tax_payable'],
            'invoice_analysis': {
                'input_invoice_count': len(input_invoices),
                'output_invoice_count': len(output_invoices),
                'input_tax_amount': sum(inv['tax_amount'] for inv in input_invoices),
                'output_tax_amount': sum(inv['tax_amount'] for inv in output_invoices)
            },
            'tax_burden_analysis': {
                'vat_burden': vat['vat_payable'] / vat['output_amount'] * 100 if vat['output_amount'] > 0 else 0,
                'overall_burden': 0
            }
        }
        
        if income_tax['taxable_income'] > 0:
            report['tax_burden_analysis']['overall_burden'] = (
                report['total_tax'] / income_tax['taxable_income'] * 100
            )
        
        return report
    
    def generate_cashflow_report(self, period):
        """生成资金分析报告"""
        from bank_manager import BankManager
        from contract_manager import ContractManager
        from invoice_manager import InvoiceManager
        
        bm = BankManager(self.data_dir)
        cm = ContractManager(self.data_dir)
        im = InvoiceManager(self.data_dir)
        
        # 银行流水统计
        stats = bm.get_statistics()
        
        # 未匹配流水
        unmatched = bm.get_unmatched_transactions()
        
        # 合同收款/付款情况
        contracts = cm.list_contracts()
        sales_contracts = [c for c in contracts if c['type'] == 'sales']
        purchase_contracts = [c for c in contracts if c['type'] == 'purchase']
        
        report = {
            'report_type': '资金分析报告',
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'cashflow_summary': {
                'total_income': stats['total_income'],
                'total_expense': stats['total_expense'],
                'net_cashflow': stats['net_amount']
            },
            'matching_analysis': {
                'matched_income': stats['matched_income'],
                'matched_expense': stats['matched_expense'],
                'unmatched_income': stats['unmatched_income'],
                'unmatched_expense': stats['unmatched_expense'],
                'matching_rate': 0
            },
            'unmatched_transactions': [
                {
                    'id': t['id'],
                    'date': t['date'],
                    'amount': t['amount'],
                    'counterparty': t.get('counterparty', ''),
                    'remark': t.get('remark', '')
                }
                for t in unmatched[:20]  # 只显示前20条
            ],
            'contract_collection': {
                'total_sales': sum(c['amount'] for c in sales_contracts),
                'collected': sum(c.get('paid_amount', 0) for c in sales_contracts),
                'uncollected': sum(c['amount'] for c in sales_contracts) - sum(c.get('paid_amount', 0) for c in sales_contracts),
                'total_purchase': sum(c['amount'] for c in purchase_contracts),
                'paid': sum(c.get('paid_amount', 0) for c in purchase_contracts),
                'unpaid': sum(c['amount'] for c in purchase_contracts) - sum(c.get('paid_amount', 0) for c in purchase_contracts)
            }
        }
        
        if stats['total_income'] > 0:
            report['matching_analysis']['matching_rate'] = (
                stats['matched_income'] / stats['total_income'] * 100
            )
        
        return report
    
    def generate_project_report(self, project_id):
        """生成项目利润报告"""
        from project_manager import ProjectManager
        from contract_manager import ContractManager
        from invoice_manager import InvoiceManager
        
        pm = ProjectManager(self.data_dir)
        cm = ContractManager(self.data_dir)
        im = InvoiceManager(self.data_dir)
        
        project = pm.get_project(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 获取项目关联数据
        contracts = cm.get_contracts_by_project(project_id)
        sales = [c for c in contracts if c['type'] == 'sales']
        purchases = [c for c in contracts if c['type'] == 'purchase']
        
        report = {
            'report_type': '项目利润报告',
            'project_id': project_id,
            'project_name': project['name'],
            'generated_at': datetime.now().isoformat(),
            'project_info': {
                'client': project['client'],
                'budget': project['budget'],
                'start_date': project['start_date'],
                'end_date': project['end_date'],
                'status': project['status']
            },
            'contract_summary': {
                'sales_contracts': len(sales),
                'purchase_contracts': len(purchases),
                'sales_amount': sum(c['amount'] for c in sales),
                'purchase_amount': sum(c['amount'] for c in purchases)
            },
            'profit_analysis': {
                'revenue': sum(c['amount'] for c in sales),
                'cost': sum(c['amount'] for c in purchases),
                'gross_profit': sum(c['amount'] for c in sales) - sum(c['amount'] for c in purchases),
                'profit_margin': 0,
                'budget_usage': 0
            }
        }
        
        if report['profit_analysis']['revenue'] > 0:
            report['profit_analysis']['profit_margin'] = (
                report['profit_analysis']['gross_profit'] / report['profit_analysis']['revenue'] * 100
            )
        
        if project['budget'] > 0:
            report['profit_analysis']['budget_usage'] = (
                report['profit_analysis']['cost'] / project['budget'] * 100
            )
        
        return report
    
    def export_report(self, report, format='json'):
        """导出报告"""
        if format == 'json':
            return json.dumps(report, ensure_ascii=False, indent=2)
        elif format == 'csv':
            # 简化 CSV 导出
            return "Not implemented"
        else:
            raise ValueError(f"不支持的格式: {format}")
