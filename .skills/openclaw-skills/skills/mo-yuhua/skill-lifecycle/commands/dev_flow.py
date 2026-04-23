#!/usr/bin/env python3
"""开发流程命令 - 核心流程（不含发布）"""

import click
from pathlib import Path
import subprocess
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

console = Console()

# 导入子命令
from commands.version import version_cmd
from commands.test import test_cmd
from commands.quality import scan_cmd
from commands.git_ops import commit_cmd


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('--bump', type=click.Choice(['major', 'minor', 'patch']), help='版本升级类型')
@click.option('--skip-test', is_flag=True, help='跳过测试')
@click.option('--skip-scan', is_flag=True, help='跳过质量扫描')
@click.option('--dry-run', is_flag=True, help='预览不执行')
def dev_flow(skill_dir, bump, skip_test, skip_scan, dry_run):
    """开发流程（不含发布）"""
    skill_dir = Path(skill_dir).resolve()
    
    console.print(Panel.fit(
        f"[bold blue]🔄 开发流程启动[/bold blue]\n\n"
        f"目录：{skill_dir}\n"
        f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        title="🚀 开始",
        border_style="blue"
    ))
    
    start_time = datetime.now()
    
    # 步骤 1: 版本升级
    console.print("\n[bold step]步骤 1/4: 版本升级[/bold step]")
    if bump:
        if dry_run:
            console.print("[yellow]🔍 干运行：跳过版本升级[/yellow]")
        else:
            try:
                version_cmd.callback(skill_dir, bump, None, dry_run)
            except SystemExit:
                pass
            except Exception as e:
                console.print(f"[red]❌ 版本升级失败：{e}[/red]")
                return
    else:
        console.print("[gray]⊘ 跳过：未指定 --bump[/gray]")
    
    # 步骤 2: 测试
    console.print("\n[bold step]步骤 2/4: 运行测试[/bold step]")
    if skip_test:
        console.print("[gray]⊘ 跳过：--skip-test[/gray]")
    else:
        if dry_run:
            console.print("[yellow]🔍 干运行：跳过测试[/yellow]")
        else:
            try:
                test_cmd.callback(skill_dir, None, False, False)
            except SystemExit as e:
                if e.code == 1:
                    console.print("\n[red]❌ 测试失败，中止流程[/red]")
                    return
            except Exception as e:
                console.print(f"[red]❌ 测试失败：{e}[/red]")
                return
    
    # 步骤 3: 质量扫描
    console.print("\n[bold step]步骤 3/4: 质量扫描[/bold step]")
    if skip_scan:
        console.print("[gray]⊘ 跳过：--skip-scan[/gray]")
    else:
        if dry_run:
            console.print("[yellow]🔍 干运行：跳过质量扫描[/yellow]")
        else:
            try:
                passed = scan_cmd.callback(skill_dir, False, False, False)
                if not passed:
                    console.print("\n[red]❌ 质量扫描失败，中止流程[/red]")
                    return
            except Exception as e:
                console.print(f"[red]❌ 质量扫描失败：{e}[/red]")
                return
    
    # 步骤 4: Git 提交
    console.print("\n[bold step]步骤 4/4: Git 提交[/bold step]")
    if dry_run:
        console.print("[yellow]🔍 干运行：跳过 Git 提交[/yellow]")
    else:
        # 检查是否有变更
        result = subprocess.run(
            ['git', 'status', '--short'],
            cwd=skill_dir,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            version = bump or '更新'
            message = f"📝 {version} 更新"
            
            try:
                commit_cmd.callback(skill_dir, message, True, dry_run)
            except Exception as e:
                console.print(f"[red]❌ Git 提交失败：{e}[/red]")
                return
        else:
            console.print("[gray]⊘ 跳过：没有待提交的变更[/gray]")
    
    # 完成
    elapsed = (datetime.now() - start_time).total_seconds()
    
    console.print("\n")
    console.print(Panel.fit(
        f"[bold green]✅ 开发流程完成[/bold green]\n\n"
        f"耗时：{elapsed:.1f}秒\n"
        f"💡 提示：如需发布到 ClawHub，运行 [cyan]sl-publish[/cyan]",
        title="🎉 完成",
        border_style="green"
    ))


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('--bump', type=click.Choice(['major', 'minor', 'patch']), help='版本升级类型')
@click.option('--skip-test', is_flag=True, help='跳过测试')
@click.option('--skip-scan', is_flag=True, help='跳过质量扫描')
@click.option('--no-publish', is_flag=True, help='跳过发布')
@click.option('--dry-run', is_flag=True, help='预览不执行')
def full_flow(skill_dir, bump, skip_test, skip_scan, no_publish, dry_run):
    """完整流程（含发布）"""
    skill_dir = Path(skill_dir).resolve()
    
    console.print(Panel.fit(
        f"[bold cyan]🚀 完整流程启动[/bold cyan]\n\n"
        f"目录：{skill_dir}\n"
        f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        title="🎯 开始",
        border_style="cyan"
    ))
    
    start_time = datetime.now()
    
    # 先执行开发流程
    console.print("\n[bold]=== 开发流程 ===[/bold]\n")
    
    if dry_run:
        console.print("[yellow]🔍 干运行：跳过开发流程[/yellow]")
    else:
        try:
            dev_flow.callback(skill_dir, bump, skip_test, skip_scan, dry_run)
        except Exception as e:
            console.print(f"[red]❌ 开发流程失败：{e}[/red]")
            return
    
    # 发布流程（可选）
    if no_publish:
        console.print("\n[gray]⊘ 跳过发布：--no-publish[/gray]")
    else:
        console.print("\n[bold]=== 发布流程 ===[/bold]\n")
        
        # 检查是否有 ClawHub 配置
        origin_json = skill_dir / '.clawhub' / 'origin.json'
        if not origin_json.exists():
            console.print("[yellow]⚠️  未配置 ClawHub，跳过发布[/yellow]")
            console.print("[gray]提示：如需发布，先配置 .clawhub/origin.json[/gray]")
        else:
            if dry_run:
                console.print("[yellow]🔍 干运行：跳过发布[/yellow]")
            else:
                from commands.publish import publish_cmd
                try:
                    changelog = f"v{bump} 更新" if bump else "定期更新"
                    publish_cmd.callback(skill_dir, changelog, False, dry_run)
                except Exception as e:
                    console.print(f"[yellow]⚠️  发布失败：{e}[/yellow]")
                    console.print("[gray]提示：可以稍后手动运行 sl-publish[/gray]")
    
    # 完成
    elapsed = (datetime.now() - start_time).total_seconds()
    
    console.print("\n")
    console.print(Panel.fit(
        f"[bold green]✅ 完整流程完成[/bold green]\n\n"
        f"耗时：{elapsed:.1f}秒",
        title="🎉 完成",
        border_style="green"
    ))


if __name__ == '__main__':
    dev_flow()
