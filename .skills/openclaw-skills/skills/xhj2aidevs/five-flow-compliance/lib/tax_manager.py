#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税务管理模块
"""

import json
from datetime import datetime
from pathlib import Path

class TaxManager:
    """税务管理器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.tax_dir = self.data_dir / 'tax'
        self.tax_dir.mkdir(exist_ok=True)
    
    def calculate_vat(self, period):
        """计算增值税"""
        # 从发票数据计算
        from invoice_manager import InvoiceManager
        im = InvoiceManager(self.data_dir)
        
        summary = im.get_summary_by_period(period)
        
        output_tax = summary['output_tax']  # 销项税额
        input_tax = summary['input_tax']    # 进项税额
        vat_payable = output_tax - input_tax  # 应纳增值税
        
        result = {
            'period': period,
            'output_amount': summary['output_amount'],
            'output_tax': output_tax,
            'input_amount': summary['input_amount'],
            'input_tax': input_tax,
            'vat_payable': max(0, vat_payable),
            'input_tax_credit': max(0, -vat_payable),
            'calculated_at': datetime.now().isoformat()
        }
        
        # 保存计算结果
        file_path = self.tax_dir / f'vat_{period}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def generate_vat_return(self, period):
        """生成增值税申报表"""
        vat_data = self.calculate_vat(period)
        
        # 小规模纳税人简化申报表
        return_form = {
            'form_type': '增值税纳税申报表（小规模纳税人适用）',
            'period': period,
            'taxpayer_info': self._get_taxpayer_info(),
            'sales_data': {
                'taxable_sales': vat_data['output_amount'],
                'tax_free_sales': 0,
                'export_sales': 0
            },
            'tax_calculation': {
                'tax_rate': '3%或1%',
                'tax_payable': vat_data['vat_payable'],
                'tax_reduction': 0,
                'tax_final': vat_data['vat_payable']
            },
            'generated_at': datetime.now().isoformat()
        }
        
        file_path = self.tax_dir / f'vat_return_{period}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(return_form, f, ensure_ascii=False, indent=2)
        
        return return_form
    
    def calculate_income_tax(self, period, tax_type='corporate'):
        """计算所得税"""
        from accounting_manager import AccountingManager
        am = AccountingManager(self.data_dir)
        
        profit_data = am.generate_report('profit', period)
        taxable_income = profit_data['operating_profit']
        
        if tax_type == 'corporate':
            # 企业所得税（小微企业优惠税率）
            if taxable_income <= 1000000:
                rate = 0.025  # 2.5%
            elif taxable_income <= 3000000:
                rate = 0.05   # 5%
            else:
                rate = 0.25   # 25%
            
            tax_name = '企业所得税'
        else:
            # 个人所得税（经营所得）
            # 简化计算，实际应按累进税率
            rate = 0.05
            tax_name = '个人所得税（经营所得）'
        
        tax_payable = max(0, taxable_income * rate)
        
        result = {
            'period': period,
            'tax_type': tax_name,
            'taxable_income': taxable_income,
            'tax_rate': f"{rate*100}%",
            'tax_payable': tax_payable,
            'calculated_at': datetime.now().isoformat()
        }
        
        file_path = self.tax_dir / f'income_tax_{tax_type}_{period}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def calculate_surtaxes(self, period):
        """计算附加税费"""
        vat_data = self.calculate_vat(period)
        vat_amount = vat_data['vat_payable']
        
        # 城建税 7% + 教育费附加 3% + 地方教育附加 2% = 12%
        # 小规模纳税人减半征收 = 6%
        surtax_rate = 0.06
        surtax = vat_amount * surtax_rate
        
        return {
            'period': period,
            'vat_amount': vat_amount,
            'urban_construction_tax': vat_amount * 0.035,  # 7% * 50%
            'education_surcharge': vat_amount * 0.015,     # 3% * 50%
            'local_education_surcharge': vat_amount * 0.01, # 2% * 50%
            'total_surtax': surtax,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _get_taxpayer_info(self):
        """获取纳税人信息"""
        config_file = self.data_dir / 'config.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {
                    'company_name': config.get('company_name', ''),
                    'tax_id': config.get('tax_id', '')
                }
        return {'company_name': '', 'tax_id': ''}
    
    def get_tax_summary(self, period):
        """获取税务汇总"""
        vat = self.calculate_vat(period)
        surtax = self.calculate_surtaxes(period)
        income = self.calculate_income_tax(period, 'corporate')
        
        total_tax = vat['vat_payable'] + surtax['total_surtax'] + income['tax_payable']
        
        return {
            'period': period,
            'vat': vat['vat_payable'],
            'surtax': surtax['total_surtax'],
            'income_tax': income['tax_payable'],
            'total_tax': total_tax,
            'output_amount': vat.get('output_amount', 0),
            'input_amount': vat.get('input_amount', 0),
            'tax_burden_rate': total_tax / income['taxable_income'] if income['taxable_income'] > 0 else 0
        }
