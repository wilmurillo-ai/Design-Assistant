#!/usr/bin/env python3
"""测试执行命令"""

import click
from pathlib import Path
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('--test-file', help='运行特定测试文件')
@click.option('--coverage', is_flag=True, help='生成覆盖率报告')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def test_cmd(skill_dir, test_file, coverage, verbose):
    """运行测试"""
    skill_dir = Path(skill_dir).resolve()
    
    # 检查虚拟环境
    venv_python = skill_dir / '.venv' / 'bin' / 'python3'
    if not venv_python.exists():
        # 尝试父目录的虚拟环境
        venv_python = skill_dir.parent.parent / '.venvs' / skill_dir.name / 'bin' / 'python3'
    
    if not venv_python.exists():
        venv_python = sys.executable  # 使用当前 Python
        console.print("[yellow]⚠️  未找到虚拟环境，使用系统 Python[/yellow]")
    else:
        console.print(f"[green]✅ 使用虚拟环境：{venv_python}[/green]")
    
    # 发现测试文件
    test_files = []
    if test_file:
        test_files = [skill_dir / test_file]
    else:
        test_files = list(skill_dir.glob('test_*.py'))
    
    if not test_files:
        console.print("[yellow]⚠️  未找到测试文件 (test_*.py)[/yellow]")
        return
    
    console.print(f"[blue]📋 发现 {len(test_files)} 个测试文件[/blue]")
    
    # 运行测试
    results = []
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        console.print(f"\n[bold]运行：{test_file.name}[/bold]")
        
        cmd = [str(venv_python), str(test_file)]
        if verbose:
            cmd.append('-v')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                console.print("[green]✅ 通过[/green]")
                total_passed += 1
                results.append((test_file.name, 'PASS', None))
            else:
                console.print("[red]❌ 失败[/red]")
                if verbose:
                    console.print(result.stdout)
                    console.print(result.stderr)
                total_failed += 1
                results.append((test_file.name, 'FAIL', result.stderr))
        
        except subprocess.TimeoutExpired:
            console.print("[red]❌ 超时 (5 分钟)[/red]")
            total_failed += 1
            results.append((test_file.name, 'TIMEOUT', None))
        except Exception as e:
            console.print(f"[red]❌ 错误：{e}[/red]")
            total_failed += 1
            results.append((test_file.name, 'ERROR', str(e)))
    
    # 显示结果汇总
    console.print("\n")
    table = Table(title="测试结果汇总", box=box.ROUNDED)
    table.add_column("测试文件", style="cyan")
    table.add_column("状态", justify="center")
    table.add_column("备注", style="yellow")
    
    for name, status, note in results:
        status_style = "green" if status == 'PASS' else "red"
        table.add_row(name, f"[{status_style}]{status}[/{status_style}]", note or "")
    
    console.print(table)
    
    # 总结
    total = total_passed + total_failed
    pass_rate = (total_passed / total * 100) if total > 0 else 0
    
    if total_failed == 0:
        console.print(Panel.fit(
            f"[bold green]✅ 所有测试通过[/bold green]\n\n"
            f"总计：{total} 个测试\n"
            f"通过率：{pass_rate:.1f}%",
            title="🎉 测试完成",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]❌ {total_failed} 个测试失败[/bold red]\n\n"
            f"通过：{total_passed}/{total}\n"
            f"通过率：{pass_rate:.1f}%",
            title="⚠️  测试失败",
            border_style="red"
        ))
        sys.exit(1)


if __name__ == '__main__':
    test_cmd()
