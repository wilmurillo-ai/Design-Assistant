#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五流合一企业合规经营管理系统 - 主入口
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from project_manager import ProjectManager
from contract_manager import ContractManager
from invoice_manager import InvoiceManager
from bank_manager import BankManager
from accounting_manager import AccountingManager
from tax_manager import TaxManager
from archive_manager import ArchiveManager
from report_generator import ReportGenerator
from compliance_checker import ComplianceChecker
from file_parser import FileParser
from feedback_manager import FeedbackManager

DATA_DIR = Path(__file__).parent / 'data'

def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for subdir in ['projects', 'contracts', 'invoices', 'bank', 'vouchers', 'tax', 'archive']:
        (DATA_DIR / subdir).mkdir(exist_ok=True)

def cmd_init(args):
    """初始化系统"""
    ensure_data_dir()
    config_file = DATA_DIR / 'config.json'
    if not config_file.exists():
        config = {
            "company_name": "",
            "tax_id": "",
            "bank_account": "",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("[OK] System initialized")
        print(f"  Data directory: {DATA_DIR}")
        print("  Please edit data/config.json to configure company info")
    else:
        print("System already initialized")

def cmd_project(args):
    """项目管理命令"""
    pm = ProjectManager(DATA_DIR)
    if args.subcommand == 'create':
        project = pm.create_project(
            name=args.name,
            client=args.client,
            budget=args.budget,
            start_date=args.start_date,
            end_date=args.end_date
        )
        print(f"[OK] Project created: {project['id']}")
        print(f"  Name: {project['name']}")
        print(f"  Client: {project['client']}")
    elif args.subcommand == 'list':
        projects = pm.list_projects()
        if not projects:
            print("No projects found")
            return
        print(f"{'ID':<12} {'Name':<20} {'Client':<15} {'Status':<8} {'Budget':>12}")
        print("-" * 75)
        for p in projects:
            print(f"{p['id']:<12} {p['name']:<20} {p['client']:<15} {p['status']:<8} {p.get('budget', 0):>12,.2f}")
    elif args.subcommand == 'show':
        project = pm.get_project(args.id)
        if project:
            print(json.dumps(project, ensure_ascii=False, indent=2))
        else:
            print(f"Project not found: {args.id}")
    elif args.subcommand == 'update':
        pm.update_project(args.id, vars(args))
        print(f"[OK] Project updated: {args.id}")
    elif args.subcommand == 'close':
        pm.close_project(args.id)
        print(f"[OK] Project closed: {args.id}")

def cmd_contract(args):
    """合同管理命令"""
    cm = ContractManager(DATA_DIR)
    if args.subcommand == 'create':
        contract = cm.create_contract(
            contract_type=args.type,
            counterparty=args.counterparty,
            amount=args.amount,
            project_id=args.project_id,
            sign_date=args.sign_date,
            items=args.items
        )
        print(f"[OK] Contract created: {contract['id']}")
        print(f"  Type: {'Purchase' if contract['type'] == 'purchase' else 'Sales'}")
        print(f"  Counterparty: {contract['counterparty']}")
        print(f"  Amount: {contract['amount']:,.2f}")
    elif args.subcommand == 'list':
        contracts = cm.list_contracts(contract_type=getattr(args, 'type', None))
        if not contracts:
            print("No contracts found")
            return
        print(f"{'ID':<12} {'Type':<8} {'Counterparty':<20} {'Amount':>12} {'Status':<8}")
        print("-" * 70)
        for c in contracts:
            ctype = 'Purchase' if c['type'] == 'purchase' else 'Sales'
            print(f"{c['id']:<12} {ctype:<8} {c['counterparty']:<20} {c['amount']:>12,.2f} {c['status']:<8}")
    elif args.subcommand == 'show':
        contract = cm.get_contract(args.id)
        if contract:
            print(json.dumps(contract, ensure_ascii=False, indent=2))
        else:
            print(f"Contract not found: {args.id}")
    elif args.subcommand == 'archive':
        cm.archive_contract(args.id)
        print(f"[OK] Contract archived: {args.id}")

def cmd_invoice(args):
    """发票管理命令"""
    im = InvoiceManager(DATA_DIR)
    if args.subcommand == 'create':
        invoice = im.create_invoice(
            invoice_type=args.type,
            invoice_no=args.no,
            amount=args.amount,
            tax_amount=args.tax,
            seller=args.seller,
            buyer=args.buyer,
            date=args.date,
            items=args.items
        )
        print(f"[OK] Invoice created: {invoice['id']}")
        print(f"  Type: {'Input' if invoice['type'] == 'input' else 'Output'}")
        print(f"  Invoice No: {invoice['invoice_no']}")
        print(f"  Amount: {invoice['amount']:,.2f}")
    elif args.subcommand == 'list':
        invoices = im.list_invoices(invoice_type=getattr(args, 'type', None))
        if not invoices:
            print("No invoices found")
            return
        print(f"{'ID':<12} {'Type':<8} {'Invoice No':<20} {'Amount':>12} {'Tax':>10} {'Date':<12}")
        print("-" * 80)
        for inv in invoices:
            itype = 'Input' if inv['type'] == 'input' else 'Output'
            print(f"{inv['id']:<12} {itype:<8} {inv['invoice_no']:<20} {inv['amount']:>12,.2f} {inv.get('tax_amount', 0):>10,.2f} {inv.get('date', '-'):<12}")
    elif args.subcommand == 'show':
        invoice = im.get_invoice(args.id)
        if invoice:
            print(json.dumps(invoice, ensure_ascii=False, indent=2))
        else:
            print(f"Invoice not found: {args.id}")
    elif args.subcommand == 'check':
        result = im.check_duplicate(args.no)
        if result:
            print(f"[WARN] Invoice already exists: {result['id']}")
            print(f"  Created at: {result['created_at']}")
        else:
            print("[OK] Invoice not duplicated")

def cmd_bank(args):
    """银行流水管理命令"""
    bm = BankManager(DATA_DIR)
    if args.subcommand == 'import':
        count = bm.import_from_file(args.file)
        print(f"[OK] Imported: {count} records")
    elif args.subcommand == 'list':
        transactions = bm.list_transactions(limit=getattr(args, 'limit', 50))
        if not transactions:
            print("No transactions found")
            return
        print(f"{'Date':<12} {'Income':>12} {'Expense':>12} {'Balance':>12} {'Remark':<20}")
        print("-" * 75)
        for t in transactions:
            income = t['amount'] if t['amount'] > 0 else 0
            expense = abs(t['amount']) if t['amount'] < 0 else 0
            print(f"{t['date']:<12} {income:>12,.2f} {expense:>12,.2f} {t.get('balance', 0):>12,.2f} {t.get('remark', '-'):<20}")
    elif args.subcommand == 'match':
        bm.match_transaction(args.id, args.project_id, args.invoice_id)
        print(f"[OK] Transaction matched: {args.id}")
    elif args.subcommand == 'stats':
        stats = bm.get_statistics(start_date=args.start_date, end_date=args.end_date)
        print(json.dumps(stats, ensure_ascii=False, indent=2))

def cmd_accounting(args):
    """财务记账命令"""
    am = AccountingManager(DATA_DIR)
    if args.subcommand == 'voucher':
        if args.voucher_command == 'generate':
            voucher = am.generate_voucher(
                date=args.date,
                description=args.description,
                entries=args.entries
            )
            print(f"[OK] Voucher generated: {voucher['id']}")
        elif args.voucher_command == 'list':
            vouchers = am.list_vouchers()
            if not vouchers:
                print("No vouchers found")
                return
            print(f"{'Voucher ID':<12} {'Date':<12} {'Description':<30} {'Debit':>12} {'Credit':>12}")
            print("-" * 85)
            for v in vouchers:
                print(f"{v['id']:<12} {v['date']:<12} {v['description']:<30} {v.get('debit_total', 0):>12,.2f} {v.get('credit_total', 0):>12,.2f}")
    elif args.subcommand == 'balance':
        balances = am.get_account_balances()
        print(f"{'Code':<12} {'Name':<20} {'Opening':>12} {'Debit':>12} {'Credit':>12} {'Closing':>12}")
        print("-" * 90)
        for b in balances:
            print(f"{b['code']:<12} {b['name']:<20} {b.get('opening', 0):>12,.2f} {b.get('debit', 0):>12,.2f} {b.get('credit', 0):>12,.2f} {b.get('closing', 0):>12,.2f}")
    elif args.subcommand == 'report':
        report = am.generate_report(report_type=args.type, period=args.period)
        print(json.dumps(report, ensure_ascii=False, indent=2))

def cmd_tax(args):
    """税务管理命令"""
    tm = TaxManager(DATA_DIR)
    if args.subcommand == 'vat':
        if args.vat_command == 'calculate':
            result = tm.calculate_vat(period=args.period)
            print(f"VAT Calculation Result ({args.period}):")
            print(f"  Output Tax: {result['output_tax']:,.2f}")
            print(f"  Input Tax: {result['input_tax']:,.2f}")
            print(f"  VAT Payable: {result['vat_payable']:,.2f}")
        elif args.vat_command == 'return':
            tm.generate_vat_return(period=args.period)
            print(f"[OK] VAT return form generated: tax/vat_return_{args.period}.json")
    elif args.subcommand == 'income':
        result = tm.calculate_income_tax(period=args.period, tax_type=args.type)
        print(f"Income Tax Calculation Result ({args.period}):")
        print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_archive(args):
    """电子归档命令"""
    am = ArchiveManager(DATA_DIR)
    if args.subcommand == 'project':
        am.archive_project(args.id)
        print(f"[OK] Project archived: {args.id}")
    elif args.subcommand == 'contract':
        am.archive_contract(args.id)
        print(f"[OK] Contract archived: {args.id}")
    elif args.subcommand == 'period':
        am.archive_period(args.period)
        print(f"[OK] Period archived: {args.period}")
    elif args.subcommand == 'list':
        archives = am.list_archives()
        for a in archives:
            print(f"{a['id']}: {a['type']} - {a['name']} ({a['archived_at']})")

def cmd_report(args):
    """统计报告命令"""
    rg = ReportGenerator(DATA_DIR)
    if args.subcommand == 'business':
        report = rg.generate_business_report(period=args.period)
        output_file = DATA_DIR / f'reports/business_report_{args.period}.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[OK] Business report generated: {output_file}")
        print(f"  Revenue: {report.get('revenue', 0):,.2f}")
        print(f"  Cost: {report.get('cost', 0):,.2f}")
        print(f"  Profit: {report.get('profit', 0):,.2f}")
    elif args.subcommand == 'tax':
        report = rg.generate_tax_report(period=args.period)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.subcommand == 'cashflow':
        report = rg.generate_cashflow_report(period=args.period)
        print(json.dumps(report, ensure_ascii=False, indent=2))

def cmd_check(args):
    """合规检查命令"""
    cc = ComplianceChecker(DATA_DIR)
    if args.subcommand == 'five-flow':
        results = cc.check_five_flow_consistency(project_id=getattr(args, 'project_id', None))
        print("Five-Flow Consistency Check Results:")
        for r in results:
            status = "[OK]" if r['consistent'] else "[FAIL]"
            print(f"  {status} {r['check_item']}: {r['message']}")
    elif args.subcommand == 'tax-risk':
        risks = cc.check_tax_risks(period=args.period)
        print("Tax Risk Check Results:")
        for r in risks:
            level = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(r['level'], "[INFO]")
            print(f"  {level} {r['item']}: {r['message']}")

def cmd_upload(args):
    """文件上传处理命令 - 核心改进：所有数据必须通过文件上传采集"""
    parser = FileParser(DATA_DIR)
    file_path = args.file
    
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        return
    
    print(f"\n[Processing] {file_path}")
    print("-" * 50)
    
    # 处理文件
    result = parser.process_uploaded_file(file_path)
    
    # 显示结果
    print(f"File Type: {result['file_type']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Parsed Records: {result['data_count']}")
    print(f"Archive Path: {result['archive_path']}")
    
    # 根据文件类型，将数据导入到对应模块
    if result['file_type'] == 'bank' and result['data']:
        print("\n[Importing to Bank Module]")
        bm = BankManager(DATA_DIR)
        imported = 0
        for record in result['data']:
            try:
                # 转换为银行流水格式
                tx = bm.import_transaction(record)
                if tx:
                    imported += 1
            except Exception as e:
                pass
        print(f"  Imported: {imported} transactions")
    
    elif result['file_type'] == 'invoice' and result['data']:
        print("\n[Invoice Data]")
        for inv in result['data']:
            if 'invoice_no' in inv:
                print(f"  Invoice No: {inv['invoice_no']}")
            if 'total_amount' in inv:
                print(f"  Total Amount: {inv['total_amount']}")
            if inv.get('requires_ocr'):
                print(f"  [Note] Requires OCR processing")
    
    print(f"\n[OK] File processed and archived")

def cmd_archives(args):
    """列出归档文件"""
    parser = FileParser(DATA_DIR)
    archives = parser.list_archives(getattr(args, 'period', None))
    
    if not archives:
        print("No archived files found.")
        return
    
    print(f"\nArchived Files ({len(archives)} total)")
    print("-" * 70)
    print(f"{'Type':<10} {'Name':<40} {'Size':>10} {'Modified':>18}")
    print("-" * 70)
    
    for arc in archives:
        size_kb = arc['size'] / 1024
        print(f"{arc['type']:<10} {arc['name'][:38]:<40} {size_kb:>8.1f}KB {arc['mtime']:>18}")

def cmd_feedback(args):
    """反馈管理命令"""
    fm = FeedbackManager(DATA_DIR)
    
    if args.subcommand == 'add':
        result = fm.add_issue(args.issue, args.context)
        print(f"[OK] Issue added (Total: {result['total_count']})")
        if result['auto_sent']:
            print(f"[AUTO-SEND] {result['send_result']['message']}")
    
    elif args.subcommand == 'list':
        issues = fm.get_issues(limit=args.limit)
        if not issues:
            print("No issues recorded.")
            return
        print(f"\nIssues ({len(issues)} total):")
        for i in issues:
            print(f"  [#{i['id']}] {i['timestamp']}: {i['content']}")
    
    elif args.subcommand == 'count':
        count = fm.get_count()
        print(f"Current issue count: {count}")
        if count >= 5:
            print("[READY] Ready to auto-send feedback")
        else:
            print(f"[WAIT] {5 - count} more to trigger auto-send")
    
    elif args.subcommand == 'send':
        result = fm.send_manual_feedback()
        print(result['message'])
    
    elif args.subcommand == 'clear':
        fm.clear_issues()
        print("[OK] Issues cleared")

def main():
    parser = argparse.ArgumentParser(
        description='Five-Flow Compliance Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    parser_init = subparsers.add_parser('init', help='Initialize system')
    
    # project command
    parser_project = subparsers.add_parser('project', help='Project management')
    project_sub = parser_project.add_subparsers(dest='subcommand')
    project_create = project_sub.add_parser('create', help='Create project')
    project_create.add_argument('--name', required=True, help='Project name')
    project_create.add_argument('--client', required=True, help='Client name')
    project_create.add_argument('--budget', type=float, default=0, help='Project budget')
    project_create.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    project_create.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    project_sub.add_parser('list', help='List projects')
    project_show = project_sub.add_parser('show', help='Show project')
    project_show.add_argument('id', help='Project ID')
    project_update = project_sub.add_parser('update', help='Update project')
    project_update.add_argument('id', help='Project ID')
    project_close = project_sub.add_parser('close', help='Close project')
    project_close.add_argument('id', help='Project ID')
    
    # contract command
    parser_contract = subparsers.add_parser('contract', help='Contract management')
    contract_sub = parser_contract.add_subparsers(dest='subcommand')
    contract_create = contract_sub.add_parser('create', help='Create contract')
    contract_create.add_argument('--type', choices=['purchase', 'sales'], required=True, help='Contract type')
    contract_create.add_argument('--counterparty', required=True, help='Counterparty')
    contract_create.add_argument('--amount', type=float, required=True, help='Contract amount')
    contract_create.add_argument('--project-id', help='Related project ID')
    contract_create.add_argument('--sign-date', help='Sign date')
    contract_create.add_argument('--items', help='Contract items (JSON format)')
    contract_list = contract_sub.add_parser('list', help='List contracts')
    contract_list.add_argument('--type', choices=['purchase', 'sales'], help='Filter by type')
    contract_show = contract_sub.add_parser('show', help='Show contract')
    contract_show.add_argument('id', help='Contract ID')
    contract_archive = contract_sub.add_parser('archive', help='Archive contract')
    contract_archive.add_argument('id', help='Contract ID')
    
    # invoice command
    parser_invoice = subparsers.add_parser('invoice', help='Invoice management')
    invoice_sub = parser_invoice.add_subparsers(dest='subcommand')
    invoice_create = invoice_sub.add_parser('create', help='Create invoice')
    invoice_create.add_argument('--type', choices=['input', 'output'], required=True, help='Invoice type')
    invoice_create.add_argument('--no', required=True, help='Invoice number')
    invoice_create.add_argument('--amount', type=float, required=True, help='Amount')
    invoice_create.add_argument('--tax', type=float, default=0, help='Tax amount')
    invoice_create.add_argument('--seller', required=True, help='Seller')
    invoice_create.add_argument('--buyer', required=True, help='Buyer')
    invoice_create.add_argument('--date', help='Invoice date')
    invoice_create.add_argument('--items', help='Invoice items (JSON format)')
    invoice_list = invoice_sub.add_parser('list', help='List invoices')
    invoice_list.add_argument('--type', choices=['input', 'output'], help='Filter by type')
    invoice_show = invoice_sub.add_parser('show', help='Show invoice')
    invoice_show.add_argument('id', help='Invoice ID')
    invoice_check = invoice_sub.add_parser('check', help='Check duplicate')
    invoice_check.add_argument('no', help='Invoice number')
    
    # bank command
    parser_bank = subparsers.add_parser('bank', help='Bank transactions')
    bank_sub = parser_bank.add_subparsers(dest='subcommand')
    bank_import = bank_sub.add_parser('import', help='Import transactions')
    bank_import.add_argument('--file', required=True, help='File path')
    bank_list = bank_sub.add_parser('list', help='List transactions')
    bank_list.add_argument('--limit', type=int, default=50, help='Limit')
    bank_match = bank_sub.add_parser('match', help='Match transaction')
    bank_match.add_argument('id', help='Transaction ID')
    bank_match.add_argument('--project-id', help='Related project ID')
    bank_match.add_argument('--invoice-id', help='Related invoice ID')
    bank_stats = bank_sub.add_parser('stats', help='Statistics')
    bank_stats.add_argument('--start-date', help='Start date')
    bank_stats.add_argument('--end-date', help='End date')
    
    # accounting command
    parser_accounting = subparsers.add_parser('accounting', help='Accounting')
    accounting_sub = parser_accounting.add_subparsers(dest='subcommand')
    accounting_voucher = accounting_sub.add_parser('voucher', help='Voucher management')
    voucher_sub = accounting_voucher.add_subparsers(dest='voucher_command')
    voucher_gen = voucher_sub.add_parser('generate', help='Generate voucher')
    voucher_gen.add_argument('--date', required=True, help='Voucher date')
    voucher_gen.add_argument('--description', required=True, help='Description')
    voucher_gen.add_argument('--entries', required=True, help='Entries (JSON format)')
    voucher_sub.add_parser('list', help='List vouchers')
    accounting_sub.add_parser('balance', help='Account balance')
    accounting_report = accounting_sub.add_parser('report', help='Generate report')
    accounting_report.add_argument('--type', choices=['profit', 'balance', 'cashflow'], required=True, help='Report type')
    accounting_report.add_argument('--period', required=True, help='Period (YYYY-MM or YYYY-QN)')
    
    # tax command
    parser_tax = subparsers.add_parser('tax', help='Tax management')
    tax_sub = parser_tax.add_subparsers(dest='subcommand')
    tax_vat = tax_sub.add_parser('vat', help='VAT')
    vat_sub = tax_vat.add_subparsers(dest='vat_command')
    vat_calc = vat_sub.add_parser('calculate', help='Calculate VAT')
    vat_calc.add_argument('--period', required=True, help='Period')
    vat_return = vat_sub.add_parser('return', help='Generate return form')
    vat_return.add_argument('--period', required=True, help='Period')
    tax_income = tax_sub.add_parser('income', help='Income tax')
    tax_income.add_argument('--period', required=True, help='Period')
    tax_income.add_argument('--type', choices=['corporate', 'personal'], default='corporate', help='Tax type')
    
    # archive command
    parser_archive = subparsers.add_parser('archive', help='Archive')
    archive_sub = parser_archive.add_subparsers(dest='subcommand')
    archive_project = archive_sub.add_parser('project', help='Archive project')
    archive_project.add_argument('id', help='Project ID')
    archive_contract = archive_sub.add_parser('contract', help='Archive contract')
    archive_contract.add_argument('id', help='Contract ID')
    archive_period = archive_sub.add_parser('period', help='Archive period')
    archive_period.add_argument('period', help='Period (YYYY-MM or YYYY-QN)')
    archive_sub.add_parser('list', help='List archives')
    
    # report command
    parser_report = subparsers.add_parser('report', help='Reports')
    report_sub = parser_report.add_subparsers(dest='subcommand')
    report_business = report_sub.add_parser('business', help='Business report')
    report_business.add_argument('--period', required=True, help='Period')
    report_tax = report_sub.add_parser('tax', help='Tax report')
    report_tax.add_argument('--period', required=True, help='Period')
    report_cashflow = report_sub.add_parser('cashflow', help='Cashflow report')
    report_cashflow.add_argument('--period', required=True, help='Period')
    
    # check command
    parser_check = subparsers.add_parser('check', help='Compliance check')
    check_sub = parser_check.add_subparsers(dest='subcommand')
    check_five = check_sub.add_parser('five-flow', help='Five-flow consistency check')
    check_five.add_argument('--project-id', help='Project ID')
    check_risk = check_sub.add_parser('tax-risk', help='Tax risk check')
    check_risk.add_argument('--period', required=True, help='Period')
    
    # upload command - 文件上传处理（核心改进）
    parser_upload = subparsers.add_parser('upload', help='Upload and parse file (bank/invoice/contract)')
    parser_upload.add_argument('file', help='File path to upload')
    parser_upload.add_argument('--type', choices=['bank', 'invoice', 'contract', 'auto'], 
                               default='auto', help='File type (auto=detect)')
    parser_upload.add_argument('--no-archive', action='store_true', help='Skip archiving')
    
    # archive-list command
    parser_archives = subparsers.add_parser('archives', help='List archived files')
    parser_archives.add_argument('--period', help='Filter by period (YYYY-MM)')
    
    # feedback command
    parser_feedback = subparsers.add_parser('feedback', help='User feedback')
    feedback_sub = parser_feedback.add_subparsers(dest='subcommand')
    feedback_add = feedback_sub.add_parser('add', help='Add issue')
    feedback_add.add_argument('issue', help='Issue description')
    feedback_add.add_argument('--context', default='', help='Context')
    feedback_list = feedback_sub.add_parser('list', help='List issues')
    feedback_list.add_argument('--limit', type=int, default=100, help='Limit')
    feedback_count = feedback_sub.add_parser('count', help='Show count')
    feedback_send = feedback_sub.add_parser('send', help='Send feedback email')
    feedback_clear = feedback_sub.add_parser('clear', help='Clear issues')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ensure data directory exists
    if args.command != 'init':
        ensure_data_dir()
    
    # Route to command handler
    command_map = {
        'init': cmd_init,
        'project': cmd_project,
        'contract': cmd_contract,
        'invoice': cmd_invoice,
        'bank': cmd_bank,
        'accounting': cmd_accounting,
        'tax': cmd_tax,
        'archive': cmd_archive,
        'report': cmd_report,
        'check': cmd_check,
        'upload': cmd_upload,
        'archives': cmd_archives,
        'feedback': cmd_feedback,
    }
    
    handler = command_map.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
