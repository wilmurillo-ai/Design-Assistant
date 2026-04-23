#!/usr/bin/env python3
"""发布管理命令（可选）"""

import click
from pathlib import Path
import subprocess
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()


def verify_prerequisites(skill_dir: Path) -> bool:
    """验证发布前置条件"""
    console.print("[bold]验证前置条件...[/bold]")
    
    # 1. 检查版本号一致性
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'
    origin_json = skill_dir / '.clawhub' / 'origin.json'
    
    versions = {}
    
    # 读取 SKILL.md 版本
    import re
    content = skill_md.read_text(encoding='utf-8')
    match = re.search(r'^version:\s*([\d\.]+)', content, re.MULTILINE)
    if match:
        versions['SKILL.md'] = match.group(1)
    
    # 读取 _meta.json 版本
    if meta_json.exists():
        data = json.loads(meta_json.read_text())
        versions['_meta.json'] = data.get('version', 'N/A')
    
    # 读取 origin.json 版本
    if origin_json.exists():
        data = json.loads(origin_json.read_text())
        versions['origin.json'] = data.get('installedVersion', 'N/A')
    
    # 检查一致性
    version_values = list(set(versions.values()))
    if len(version_values) > 1:
        console.print(f"[red]❌ 版本号不一致:[/red]")
        for file, ver in versions.items():
            console.print(f"   {file}: {ver}")
        return False
    
    console.print(f"[green]✅ 版本号一致：{version_values[0]}[/green]")
    
    # 2. 检查 ClawHub 是否可用
    try:
        result = subprocess.run(
            ['clawhub', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or 'Usage:' in result.stdout:
            console.print("[green]✅ ClawHub 已安装[/green]")
        else:
            console.print("[yellow]⚠️  ClawHub 可能未正确配置，尝试继续[/yellow]")
            return True  # 允许继续尝试
    except (FileNotFoundError, subprocess.TimeoutExpired):
        console.print("[yellow]⚠️  ClawHub 未找到，尝试继续[/yellow]")
        return True  # 允许继续尝试
    
    return True


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('--changelog', help='变更日志')
@click.option('--check', is_flag=True, help='仅验证前置条件')
@click.option('--dry-run', is_flag=True, help='预览不执行')
def publish_cmd(skill_dir, changelog, check, dry_run):
    """发布到 ClawHub（可选）"""
    skill_dir = Path(skill_dir).resolve()
    
    # 验证前置条件
    if not verify_prerequisites(skill_dir):
        console.print("\n[red]❌ 前置条件不满足，中止发布[/red]")
        return
    
    if check:
        console.print("\n[green]✅ 前置条件验证通过[/green]")
        return
    
    # 获取版本号
    import re
    skill_md = skill_dir / 'SKILL.md'
    content = skill_md.read_text(encoding='utf-8')
    match = re.search(r'^version:\s*([\d\.]+)', content, re.MULTILINE)
    version = match.group(1) if match else 'unknown'
    
    if dry_run:
        console.print(f"\n[yellow]🔍 干运行模式[/yellow]")
        console.print(f"   版本：{version}")
        console.print(f"   变更：{changelog or '自动生成'}")
        console.print(f"   命令：clawhub publish . --version {version}")
        return
    
    # 执行发布
    console.print(f"\n[bold]发布到 ClawHub...[/bold]")
    console.print(f"版本：{version}")
    
    cmd = ['clawhub', 'publish', '.', '--version', version]
    if changelog:
        cmd.extend(['--changelog', changelog])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=skill_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # 提取发布 ID（支持多种格式）
            import re
            patterns = [
                r'Published\s+\S+@\S+\s+\((\w+)\)',
                r'\((\w+)\)\s*$',
                r'publish\s+\S+\s+\((\w+)\)',
            ]
            publish_id = 'unknown'
            for pattern in patterns:
                match = re.search(pattern, result.stdout, re.MULTILINE)
                if match:
                    publish_id = match.group(1)
                    break
            
            # 保存发布记录
            publish_record = {
                'version': version,
                'publish_id': publish_id,
                'timestamp': datetime.now().isoformat(),
                'changelog': changelog or ''
            }
            
            record_file = skill_dir / '.publish_record.json'
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(publish_record, f, indent=2, ensure_ascii=False)
            
            console.print(Panel.fit(
                f"[bold green]✅ 发布成功[/bold green]\n\n"
                f"版本：{version}\n"
                f"发布 ID: [cyan]{publish_id}[/cyan]\n"
                f"记录：.publish_record.json",
                title="🚀 ClawHub 发布",
                border_style="green"
            ))
        else:
            console.print(f"[red]❌ 发布失败：{result.stderr}[/red]")
    
    except subprocess.TimeoutExpired:
        console.print("[red]❌ 发布超时（2 分钟）[/red]")
    except Exception as e:
        console.print(f"[red]❌ 发布失败：{e}[/red]")


if __name__ == '__main__':
    publish_cmd()
