#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五流合一系统 - 功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from pathlib import Path
from project_manager import ProjectManager
from contract_manager import ContractManager
from invoice_manager import InvoiceManager
from tax_manager import TaxManager
from compliance_checker import ComplianceChecker

DATA_DIR = Path(__file__).parent / 'data'

def test_project_management():
    """测试项目管理"""
    print("=" * 50)
    print("TEST 1: Project Management")
    print("=" * 50)
    
    pm = ProjectManager(DATA_DIR)
    
    # 创建项目
    project = pm.create_project(
        name="Website Development",
        client="TechCorp",
        budget=50000,
        start_date="2024-01-01",
        end_date="2024-03-31"
    )
    print(f"[OK] Created project: {project['id']}")
    
    # 列出项目
    projects = pm.list_projects()
    print(f"[OK] Total projects: {len(projects)}")
    
    # 获取项目详情
    p = pm.get_project(project['id'])
    print(f"[OK] Project name: {p['name']}, Client: {p['client']}")
    
    return project['id']

def test_contract_management(project_id):
    """测试合同管理"""
    print("\n" + "=" * 50)
    print("TEST 2: Contract Management")
    print("=" * 50)
    
    cm = ContractManager(DATA_DIR)
    
    # 创建销售合同
    contract = cm.create_contract(
        contract_type="sales",
        counterparty="TechCorp",
        amount=50000,
        project_id=project_id,
        sign_date="2024-01-05",
        items=[{"name": "Website Development", "quantity": 1, "price": 50000}]
    )
    print(f"[OK] Created sales contract: {contract['id']}")
    
    # 创建采购合同
    purchase = cm.create_contract(
        contract_type="purchase",
        counterparty="CloudProvider",
        amount=5000,
        project_id=project_id,
        sign_date="2024-01-10",
        items=[{"name": "Cloud Server", "quantity": 1, "price": 5000}]
    )
    print(f"[OK] Created purchase contract: {purchase['id']}")
    
    # 列出合同
    contracts = cm.list_contracts()
    print(f"[OK] Total contracts: {len(contracts)}")
    
    return contract['id'], purchase['id']

def test_invoice_management():
    """测试发票管理"""
    print("\n" + "=" * 50)
    print("TEST 3: Invoice Management")
    print("=" * 50)
    
    im = InvoiceManager(DATA_DIR)
    
    # 创建销项发票
    output_inv = im.create_invoice(
        invoice_type="output",
        invoice_no="4400123456",
        amount=50000,
        tax_amount=6500,
        seller="MyCompany",
        buyer="TechCorp",
        date="2024-01-15",
        items=[{"name": "Service", "amount": 50000}]
    )
    print(f"[OK] Created output invoice: {output_inv['id']}")
    
    # 创建进项发票
    input_inv = im.create_invoice(
        invoice_type="input",
        invoice_no="4400654321",
        amount=5000,
        tax_amount=650,
        seller="CloudProvider",
        buyer="MyCompany",
        date="2024-01-20",
        items=[{"name": "Server", "amount": 5000}]
    )
    print(f"[OK] Created input invoice: {input_inv['id']}")
    
    # 查重检查
    dup = im.check_duplicate("4400123456")
    if dup:
        print(f"[OK] Duplicate check works: found {dup['id']}")
    
    # 发票汇总
    summary = im.get_summary_by_period("2024-01")
    print(f"[OK] Invoice summary: Output={summary['output_amount']}, Input={summary['input_amount']}")
    
    return output_inv['id'], input_inv['id']

def test_tax_calculation():
    """测试税务计算"""
    print("\n" + "=" * 50)
    print("TEST 4: Tax Calculation")
    print("=" * 50)
    
    tm = TaxManager(DATA_DIR)
    
    # 计算增值税
    vat = tm.calculate_vat("2024-01")
    print(f"[OK] VAT: Output={vat['output_tax']}, Input={vat['input_tax']}, Payable={vat['vat_payable']}")
    
    # 计算附加税
    surtax = tm.calculate_surtaxes("2024-01")
    print(f"[OK] Surtax: Total={surtax['total_surtax']:.2f}")
    
    # 计算所得税
    income = tm.calculate_income_tax("2024-01", "corporate")
    print(f"[OK] Income Tax: Taxable={income['taxable_income']:.2f}, Payable={income['tax_payable']:.2f}")
    
    # 税务汇总
    summary = tm.get_tax_summary("2024-01")
    print(f"[OK] Total tax: {summary['total_tax']:.2f}")

def test_compliance_check(project_id):
    """测试合规检查"""
    print("\n" + "=" * 50)
    print("TEST 5: Compliance Check")
    print("=" * 50)
    
    cc = ComplianceChecker(DATA_DIR)
    
    # 五流合一检查
    results = cc.check_five_flow_consistency(project_id)
    print(f"[OK] Five-flow check: {len(results)} items checked")
    passed = sum(1 for r in results if r['consistent'])
    print(f"       Passed: {passed}, Failed: {len(results) - passed}")
    
    # 税务风险检查
    risks = cc.check_tax_risks("2024-01")
    print(f"[OK] Tax risk check: {len(risks)} risks found")
    high = sum(1 for r in risks if r['level'] == 'high')
    medium = sum(1 for r in risks if r['level'] == 'medium')
    low = sum(1 for r in risks if r['level'] == 'low')
    print(f"       High: {high}, Medium: {medium}, Low: {low}")

def main():
    print("\n" + "=" * 50)
    print("Five-Flow Compliance System - Test Suite")
    print("=" * 50)
    
    try:
        # 运行测试
        project_id = test_project_management()
        sales_id, purchase_id = test_contract_management(project_id)
        output_inv_id, input_inv_id = test_invoice_management()
        test_tax_calculation()
        test_compliance_check(project_id)
        
        print("\n" + "=" * 50)
        print("All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
