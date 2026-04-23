#!/usr/bin/env python3
"""质量扫描命令"""

import click
from pathlib import Path
import re
import ast
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# 导入增强规则
from commands.quality_rules import ALL_CHECKS


class Issue:
    """质量问题"""
    def __init__(self, file: str, line: int, issue_type: str, message: str, severity: str = 'warning'):
        self.file = file
        self.line = line
        self.type = issue_type
        self.message = message
        self.severity = severity  # error, warning, info


def check_bare_except(skill_dir: Path) -> list:
    """检查裸 except"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        if py_file.name.startswith('test_'):
            continue
        
        content = py_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if re.match(r'\s*except\s*:', line):
                issues.append(Issue(
                    py_file.name, i, 'bare_except',
                    '裸 except 会掩盖所有异常', 'error'
                ))
    
    return issues


def check_sensitive_data(skill_dir: Path) -> list:
    """检查敏感信息"""
    issues = []
    patterns = [
        (r'sk[a-zA-Z0-9_-]{20,}', 'API Key'),
        (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
        (r'secret\s*=\s*["\'][^"\']+["\']', '硬编码密钥'),
        (r'api_key\s*=\s*["\'][^"\']+["\']', '硬编码 API Key'),
    ]
    
    for py_file in skill_dir.glob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        py_file.name, i, 'sensitive_data',
                        f'可能包含{desc}', 'error'
                    ))
    
    return issues


def check_long_functions(skill_dir: Path) -> list:
    """检查过长函数"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        if py_file.name.startswith('test_'):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'end_lineno'):
                        length = node.end_lineno - node.lineno
                        if length > 100:
                            issues.append(Issue(
                                py_file.name, node.lineno, 'long_function',
                                f'函数 {node.name} 过长 ({length} 行)', 'warning'
                            ))
        except SyntaxError:
            pass
    
    return issues


def check_print_in_production(skill_dir: Path) -> list:
    """检查生产代码中的 print"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        if py_file.name.startswith('test_') or py_file.name.startswith('check_'):
            continue
        
        content = py_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if re.match(r'\s*print\s*\(', line):
                # 排除 CLI 主入口文件
                if 'def main' in content or '__main__' in py_file.name:
                    continue
                issues.append(Issue(
                    py_file.name, i, 'print_statement',
                    '生产代码包含 print 语句', 'info'
                ))
    
    return issues


def check_documentation(skill_dir: Path) -> list:
    """检查文档完整性"""
    issues = []
    
    # 检查必要文件
    required_files = ['SKILL.md', 'README.md']
    for req_file in required_files:
        if not (skill_dir / req_file).exists():
            issues.append(Issue(
                req_file, 0, 'missing_doc',
                f'缺少必要文档：{req_file}', 'warning'
            ))
    
    return issues


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('--security', is_flag=True, help='仅扫描安全问题')
@click.option('--quality', is_flag=True, help='仅扫描代码质量')
@click.option('--report', is_flag=True, help='生成详细报告')
def scan_cmd(skill_dir, security, quality, report):
    """质量扫描"""
    skill_dir = Path(skill_dir).resolve()
    
    console.print(f"[blue]🔍 扫描目录：{skill_dir}[/blue]\n")
    
    all_issues = []
    
    # 安全检查
    if not quality:
        console.print("[bold]安全检查[/bold]")
        issues = check_sensitive_data(skill_dir)
        if issues:
            for issue in issues:
                console.print(f"  [red]❌[/red] {issue.file}:{issue.line} - {issue.message}")
        else:
            console.print("  [green]✅ 无安全问题[/green]")
        all_issues.extend(issues)
        console.print()
    
    # 代码质量检查
    if not security:
        console.print("[bold]代码质量检查[/bold]")
        
        issues = check_bare_except(skill_dir)
        if issues:
            for issue in issues:
                console.print(f"  [red]❌[/red] {issue.file}:{issue.line} - {issue.message}")
        else:
            console.print("  [green]✅ 无裸 except[/green]")
        all_issues.extend(issues)
        
        issues = check_long_functions(skill_dir)
        if issues:
            for issue in issues:
                console.print(f"  [yellow]⚠️[/yellow] {issue.file}:{issue.line} - {issue.message}")
        else:
            console.print("  [green]✅ 无过长函数[/green]")
        all_issues.extend(issues)
        
        issues = check_print_in_production(skill_dir)
        if issues:
            console.print(f"  [blue]ℹ️[/blue] 发现 {len(issues)} 处 print 语句（可能合理）")
        else:
            console.print("  [green]✅ 无生产代码 print[/green]")
        all_issues.extend(issues)
        
        issues = check_documentation(skill_dir)
        if issues:
            for issue in issues:
                console.print(f"  [yellow]⚠️[/yellow] {issue.file} - {issue.message}")
        else:
            console.print("  [green]✅ 文档完整[/green]")
        all_issues.extend(issues)
    
    console.print()
    
    # 运行增强检查
    console.print("[bold]增强检查[/bold]")
    for rule_name, check_func in ALL_CHECKS:
        issues = check_func(skill_dir)
        if issues:
            for issue in issues:
                symbol = "❌" if issue.severity == 'error' else "⚠️" if issue.severity == 'warning' else "ℹ️"
                console.print(f"  {symbol} {issue.file}:{issue.line} - {issue.message}")
        else:
            console.print(f"  [green]✅[/green] {rule_name}")
        all_issues.extend(issues)
    
    console.print()
    
    # 汇总
    error_count = sum(1 for i in all_issues if i.severity == 'error')
    warning_count = sum(1 for i in all_issues if i.severity == 'warning')
    info_count = sum(1 for i in all_issues if i.severity == 'info')
    
    table = Table(title="扫描结果汇总", box=box.ROUNDED)
    table.add_column("类型", style="cyan")
    table.add_column("数量", justify="right")
    table.add_column("状态")
    
    table.add_row("❌ 错误", str(error_count), "[green]需修复[/green]" if error_count == 0 else "[red]需修复[/red]")
    table.add_row("⚠️  警告", str(warning_count), "建议优化")
    table.add_row("ℹ️  提示", str(info_count), "可选优化")
    
    console.print(table)
    
    # 总结
    if error_count == 0:
        console.print(Panel.fit(
            f"[bold green]✅ 质量扫描通过[/bold green]\n\n"
            f"警告：{warning_count} | 提示：{info_count}",
            title="🎉 扫描完成",
            border_style="green"
        ))
        return True
    else:
        console.print(Panel.fit(
            f"[bold red]❌ 发现 {error_count} 个严重问题[/bold red]\n\n"
            f"警告：{warning_count} | 提示：{info_count}",
            title="⚠️  扫描失败",
            border_style="red"
        ))
        return False


if __name__ == '__main__':
    scan_cmd()
