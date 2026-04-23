#!/usr/bin/env python3
"""Git 操作命令"""

import click
from pathlib import Path
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('-m', '--message', required=True, help='提交信息')
@click.option('-a', '--all', 'auto_add', is_flag=True, help='自动添加所有变更')
@click.option('--dry-run', is_flag=True, help='预览不执行')
def commit_cmd(skill_dir, message, auto_add, dry_run):
    """Git 提交"""
    skill_dir = Path(skill_dir).resolve()
    
    # 检查是否在 Git 仓库中
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=skill_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            console.print("[red]❌ 不在 Git 仓库中[/red]")
            return
    except FileNotFoundError:
        console.print("[red]❌ 未安装 Git[/red]")
        return
    
    console.print(f"[blue]📂 工作目录：{skill_dir}[/blue]")
    
    # 显示变更
    console.print("\n[bold]待提交的变更:[/bold]")
    result = subprocess.run(
        ['git', 'status', '--short'],
        cwd=skill_dir,
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        console.print(result.stdout)
    else:
        console.print("[yellow]⚠️  没有待提交的变更[/yellow]")
        return
    
    if dry_run:
        console.print("\n[yellow]🔍 干运行模式 - 不会实际提交[/yellow]")
        console.print(f"提交信息：{message}")
        return
    
    # 添加变更
    if auto_add:
        console.print("\n[bold]添加所有变更...[/bold]")
        subprocess.run(['git', 'add', '-A'], cwd=skill_dir, check=True)
    
    # 提交
    console.print(f"\n[bold]提交：{message}[/bold]")
    result = subprocess.run(
        ['git', 'commit', '-m', message],
        cwd=skill_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # 获取提交 hash
        result_hash = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=skill_dir,
            capture_output=True,
            text=True
        )
        commit_hash = result_hash.stdout.strip()
        
        console.print(Panel.fit(
            f"[bold green]✅ Git 提交成功[/bold green]\n\n"
            f"提交信息：{message}\n"
            f"Commit: [cyan]{commit_hash}[/cyan]",
            title="📝 Git 提交",
            border_style="green"
        ))
    else:
        console.print(f"[red]❌ 提交失败：{result.stderr}[/red]")


if __name__ == '__main__':
    commit_cmd()
