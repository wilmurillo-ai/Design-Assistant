#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合规检查模块
"""

import json
from datetime import datetime
from pathlib import Path

class ComplianceChecker:
    """合规检查器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
    
    def check_five_flow_consistency(self, project_id=None):
        """
        五流合一一致性检查
        五流：业务流、合同流、票据流、资金流、财务流
        """
        results = []
        
        from project_manager import ProjectManager
        from contract_manager import ContractManager
        from invoice_manager import InvoiceManager
        from bank_manager import BankManager
        from accounting_manager import AccountingManager
        
        pm = ProjectManager(self.data_dir)
        cm = ContractManager(self.data_dir)
        im = InvoiceManager(self.data_dir)
        bm = BankManager(self.data_dir)
        am = AccountingManager(self.data_dir)
        
        if project_id:
            # 检查指定项目
            projects = [pm.get_project(project_id)]
        else:
            # 检查所有活跃项目
            projects = pm.list_projects(status='active')
        
        for project in projects:
            pid = project['id']
            
            # 1. 检查业务流-合同流一致性
            contracts = cm.get_contracts_by_project(pid)
            contract_total = sum(c['amount'] for c in contracts)
            budget = project.get('budget', 0)
            
            results.append({
                'check_item': f'项目 {pid} 合同-预算匹配',
                'consistent': abs(contract_total - budget) / max(budget, 1) < 0.1 if budget > 0 else True,
                'message': f'合同总额 {contract_total:,.2f} vs 预算 {budget:,.2f}',
                'project_id': pid
            })
            
            # 2. 检查合同流-票据流一致性
            for contract in contracts:
                cid = contract['id']
                invoiced = contract.get('invoiced_amount', 0)
                contract_amount = contract['amount']
                
                results.append({
                    'check_item': f'合同 {cid} 发票匹配',
                    'consistent': abs(invoiced - contract_amount) / max(contract_amount, 1) < 0.01,
                    'message': f'已开票 {invoiced:,.2f} vs 合同金额 {contract_amount:,.2f}',
                    'contract_id': cid
                })
            
            # 3. 检查票据流-资金流一致性
            for contract in contracts:
                cid = contract['id']
                paid = contract.get('paid_amount', 0)
                invoiced = contract.get('invoiced_amount', 0)
                
                results.append({
                    'check_item': f'合同 {cid} 资金-发票匹配',
                    'consistent': paid <= invoiced * 1.01,  # 允许微小误差
                    'message': f'已付款 {paid:,.2f} vs 已开票 {invoiced:,.2f}',
                    'contract_id': cid
                })
        
        # 4. 检查整体资金-票据匹配
        bank_stats = bm.get_statistics()
        invoice_summary = im.get_summary_by_period(datetime.now().strftime('%Y-%m'))
        
        results.append({
            'check_item': '整体资金-票据匹配',
            'consistent': abs(bank_stats['total_income'] - invoice_summary['output_amount']) / max(invoice_summary['output_amount'], 1) < 0.1,
            'message': f'银行收入 {bank_stats["total_income"]:,.2f} vs 销项金额 {invoice_summary["output_amount"]:,.2f}'
        })
        
        return results
    
    def check_tax_risks(self, period):
        """税务风险检查"""
        risks = []
        
        from tax_manager import TaxManager
        from invoice_manager import InvoiceManager
        from accounting_manager import AccountingManager
        
        tm = TaxManager(self.data_dir)
        im = InvoiceManager(self.data_dir)
        am = AccountingManager(self.data_dir)
        
        # 1. 税负率检查
        tax_summary = tm.get_tax_summary(period)
        output_amount = tax_summary.get('output_amount', 0)
        vat_burden = tax_summary['vat'] / output_amount * 100 if output_amount > 0 else 0
        
        if vat_burden < 1:
            risks.append({
                'level': 'high',
                'item': '增值税税负率',
                'message': f'增值税税负率 {vat_burden:.2f}% 偏低，可能存在进项虚抵风险',
                'value': vat_burden
            })
        elif vat_burden > 10:
            risks.append({
                'level': 'medium',
                'item': '增值税税负率',
                'message': f'增值税税负率 {vat_burden:.2f}% 偏高，建议检查销项计算',
                'value': vat_burden
            })
        else:
            risks.append({
                'level': 'low',
                'item': '增值税税负率',
                'message': f'增值税税负率 {vat_burden:.2f}% 正常',
                'value': vat_burden
            })
        
        # 2. 成本费用率检查
        profit_report = am.generate_report('profit', period)
        if profit_report['revenue'] > 0:
            cost_rate = (profit_report['cost'] + profit_report['expenses']) / profit_report['revenue'] * 100
            
            if cost_rate > 95:
                risks.append({
                    'level': 'high',
                    'item': '成本费用率',
                    'message': f'成本费用率 {cost_rate:.2f}% 过高，可能存在虚增成本风险',
                    'value': cost_rate
                })
            elif cost_rate > 85:
                risks.append({
                    'level': 'medium',
                    'item': '成本费用率',
                    'message': f'成本费用率 {cost_rate:.2f}% 偏高，建议核实',
                    'value': cost_rate
                })
            else:
                risks.append({
                    'level': 'low',
                    'item': '成本费用率',
                    'message': f'成本费用率 {cost_rate:.2f}% 正常',
                    'value': cost_rate
                })
        
        # 3. 进销项匹配检查
        invoice_summary = im.get_summary_by_period(period)
        if invoice_summary['input_amount'] > invoice_summary['output_amount'] * 1.5:
            risks.append({
                'level': 'medium',
                'item': '进销项匹配',
                'message': f'进项金额 {invoice_summary["input_amount"]:,.2f} 远大于销项金额 {invoice_summary["output_amount"]:,.2f}，可能存在库存积压或虚假进项',
                'value': invoice_summary['input_amount'] / max(invoice_summary['output_amount'], 1)
            })
        
        # 4. 利润率检查
        if profit_report['revenue'] > 0:
            profit_margin = profit_report['operating_profit'] / profit_report['revenue'] * 100
            
            if profit_margin < 0:
                risks.append({
                    'level': 'high',
                    'item': '利润率',
                    'message': f'利润率为负 ({profit_margin:.2f}%)，企业经营亏损',
                    'value': profit_margin
                })
            elif profit_margin < 3:
                risks.append({
                    'level': 'medium',
                    'item': '利润率',
                    'message': f'利润率 {profit_margin:.2f}% 偏低，建议关注成本控制',
                    'value': profit_margin
                })
            else:
                risks.append({
                    'level': 'low',
                    'item': '利润率',
                    'message': f'利润率 {profit_margin:.2f}% 正常',
                    'value': profit_margin
                })
        
        return risks
    
    def check_invoice_compliance(self, invoice_id):
        """检查单张发票合规性"""
        from invoice_manager import InvoiceManager
        im = InvoiceManager(self.data_dir)
        
        invoice = im.get_invoice(invoice_id)
        if not invoice:
            return {'valid': False, 'errors': ['发票不存在']}
        
        errors = []
        warnings = []
        
        # 1. 检查发票号码格式
        if not invoice.get('invoice_no'):
            errors.append('发票号码为空')
        
        # 2. 检查金额
        if invoice.get('amount', 0) <= 0:
            errors.append('金额必须大于0')
        
        # 3. 检查销售方和购买方
        if not invoice.get('seller'):
            errors.append('销售方信息为空')
        if not invoice.get('buyer'):
            errors.append('购买方信息为空')
        
        # 4. 检查日期
        if not invoice.get('date'):
            warnings.append('开票日期为空')
        
        # 5. 检查重复
        duplicate = im.check_duplicate(invoice.get('invoice_no', ''))
        if duplicate and duplicate['id'] != invoice_id:
            errors.append(f"发票重复: 已存在 {duplicate['id']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def generate_compliance_report(self, period):
        """生成合规检查报告"""
        five_flow_results = self.check_five_flow_consistency()
        tax_risks = self.check_tax_risks(period)
        
        # 统计
        five_flow_pass = sum(1 for r in five_flow_results if r['consistent'])
        five_flow_fail = len(five_flow_results) - five_flow_pass
        
        high_risks = sum(1 for r in tax_risks if r['level'] == 'high')
        medium_risks = sum(1 for r in tax_risks if r['level'] == 'medium')
        low_risks = sum(1 for r in tax_risks if r['level'] == 'low')
        
        return {
            'report_type': '合规检查报告',
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'five_flow_check': {
                'total': len(five_flow_results),
                'passed': five_flow_pass,
                'failed': five_flow_fail,
                'pass_rate': five_flow_pass / len(five_flow_results) * 100 if five_flow_results else 0,
                'details': five_flow_results
            },
            'tax_risk_check': {
                'high': high_risks,
                'medium': medium_risks,
                'low': low_risks,
                'details': tax_risks
            },
            'overall_status': 'PASS' if five_flow_fail == 0 and high_risks == 0 else 'WARNING' if high_risks == 0 else 'FAIL'
        }
