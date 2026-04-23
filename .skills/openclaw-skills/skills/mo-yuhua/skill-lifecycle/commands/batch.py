#!/usr/bin/env python3
"""批处理命令 - 支持一次处理多个 Skills"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

console = Console()

# 导入流程命令
from commands.dev_flow import dev_flow
from commands.version import version_cmd
from commands.test import test_cmd
from commands.quality import scan_cmd
from commands.git_ops import commit_cmd


def process_skill(skill_dir: Path, bump: str, skip_test: bool, skip_scan: bool) -> dict:
    """处理单个 Skill"""
    result = {
        'skill': skill_dir.name,
        'success': False,
        'error': None,
        'duration': 0
    }
    
    start = datetime.now()
    
    try:
        # 执行开发流程
        dev_flow.callback(str(skill_dir), bump, skip_test, skip_scan, False)
        result['success'] = True
    except Exception as e:
        result['error'] = str(e)
    
    result['duration'] = (datetime.now() - start).total_seconds()
    
    return result


@click.command()
@click.argument('skill_dirs', nargs=-1, type=click.Path(exists=True))
@click.option('--bump', type=click.Choice(['major', 'minor', 'patch']), required=True, help='版本升级类型')
@click.option('--skip-test', is_flag=True, help='跳过测试')
@click.option('--skip-scan', is_flag=True, help='跳过质量扫描')
@click.option('--jobs', '-j', type=int, default=4, help='并发数（默认 4）')
@click.option('--filter', 'pattern', help='文件名过滤（支持通配符）')
def batch_dev(skill_dirs, bump, skip_test, skip_scan, jobs, pattern):
    """批量执行开发流程"""
    if not skill_dirs:
        console.print("[red]❌ 请指定 Skills 目录[/red]")
        return
    
    # 解析目录
    skills = []
    for skill_dir in skill_dirs:
        path = Path(skill_dir)
        if path.is_dir() and (path / 'SKILL.md').exists():
            skills.append(path)
        elif '*' in str(path):
            # 通配符展开
            import glob
            for match in glob.glob(str(path)):
                match_path = Path(match)
                if match_path.is_dir() and (match_path / 'SKILL.md').exists():
                    skills.append(match_path)
    
    if not skills:
        console.print("[red]❌ 未找到有效的 Skills 目录[/red]")
        return
    
    # 应用过滤
    if pattern:
        import fnmatch
        skills = [s for s in skills if fnmatch.fnmatch(s.name, pattern)]
    
    console.print(Panel.fit(
        f"[bold blue]📦 批量处理启动[/bold blue]\n\n"
        f"Skills: {len(skills)} 个\n"
        f"版本升级：{bump}\n"
        f"并发数：{jobs}",
        title="🚀 开始",
        border_style="blue"
    ))
    
    # 执行批处理
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"处理 {len(skills)} 个 Skills...", total=len(skills))
        
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = {
                executor.submit(process_skill, skill_dir, bump, skip_test, skip_scan): skill_dir
                for skill_dir in skills
            }
            
            for future in as_completed(futures):
                skill_dir = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        console.print(f"[green]✅ {result['skill']} ({result['duration']:.1f}s)[/green]")
                    else:
                        console.print(f"[red]❌ {result['skill']}: {result['error']}[/red]")
                except Exception as e:
                    console.print(f"[red]❌ {skill_dir.name}: {e}[/red]")
                
                progress.update(task, advance=1)
    
    # 汇总
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    total_time = sum(r['duration'] for r in results)
    
    console.print("\n")
    console.print(Panel.fit(
        f"[bold green]✅ 批量处理完成[/bold green]\n\n"
        f"成功：{success_count}/{len(results)}\n"
        f"失败：{fail_count}\n"
        f"总耗时：{total_time:.1f}秒\n"
        f"平均：{total_time/len(results):.1f}秒/Skill",
        title="🎉 完成",
        border_style="green" if fail_count == 0 else "yellow"
    ))
    
    if fail_count > 0:
        console.print("\n[yellow]失败的 Skills:[/yellow]")
        for r in results:
            if not r['success']:
                console.print(f"  - {r['skill']}: {r['error']}")


if __name__ == '__main__':
    batch_dev()
