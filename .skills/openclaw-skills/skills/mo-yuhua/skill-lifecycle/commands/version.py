#!/usr/bin/env python3
"""版本管理命令"""

import click
from pathlib import Path
import re
import json
from rich.console import Console
from rich.panel import Panel

console = Console()


def parse_version(version_str: str) -> tuple:
    """解析版本号"""
    parts = version_str.split('.')
    if len(parts) != 3:
        raise ValueError(f"无效版本号：{version_str}")
    return tuple(map(int, parts))


def bump_version(version: str, bump_type: str) -> str:
    """升级版本号"""
    major, minor, patch = parse_version(version)
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"无效的升级类型：{bump_type}")


def update_file_version(file_path: Path, new_version: str) -> bool:
    """更新文件中的版本号"""
    if not file_path.exists():
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    if file_path.suffix == '.md':
        # SKILL.md: version: 2.7.5
        pattern = r'^version:\s*[\d\.]+'
        replacement = f'version: {new_version}'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    elif file_path.suffix == '.json':
        # JSON 文件
        try:
            data = json.loads(content)
            updated = False
            
            if 'version' in data:
                data['version'] = new_version
                updated = True
            if 'installedVersion' in data:
                data['installedVersion'] = new_version
                updated = True
            
            if updated:
                content = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
            else:
                return False
        except json.JSONDecodeError:
            return False
    else:
        return False
    
    file_path.write_text(content, encoding='utf-8')
    return True


@click.command()
@click.argument('skill_dir', default='.', type=click.Path(exists=True))
@click.option('--bump', type=click.Choice(['major', 'minor', 'patch']), help='升级类型')
@click.option('--set', 'set_version', help='直接设置版本号')
@click.option('--dry-run', is_flag=True, help='预览不执行')
def version_cmd(skill_dir, bump, set_version, dry_run):
    """版本管理"""
    skill_dir = Path(skill_dir).resolve()
    
    # 找到 SKILL.md
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        console.print("[red]❌ 未找到 SKILL.md[/red]")
        return
    
    # 读取当前版本
    content = skill_md.read_text(encoding='utf-8')
    match = re.search(r'^version:\s*([\d\.]+)', content, re.MULTILINE)
    if not match:
        console.print("[red]❌ SKILL.md 中未找到版本号[/red]")
        return
    
    current_version = match.group(1)
    
    # 计算新版本
    if set_version:
        new_version = set_version
    elif bump:
        new_version = bump_version(current_version, bump)
    else:
        console.print(f"[blue]📊 当前版本：{current_version}[/blue]")
        return
    
    # 验证版本号格式
    try:
        parse_version(new_version)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        return
    
    if dry_run:
        console.print("[yellow]🔍 干运行模式[/yellow]")
        console.print(f"   当前版本：{current_version}")
        console.print(f"   新版本：{new_version}")
        return
    
    # 更新所有文件
    files_to_update = [
        skill_dir / 'SKILL.md',
        skill_dir / '_meta.json',
        skill_dir / '.clawhub' / 'origin.json',
    ]
    
    updated_count = 0
    for file_path in files_to_update:
        if update_file_version(file_path, new_version):
            console.print(f"[green]✅ 更新：{file_path.name}[/green]")
            updated_count += 1
        else:
            if file_path.exists():
                console.print(f"[yellow]⚠️  跳过：{file_path.name} (无版本字段)[/yellow]")
            else:
                console.print(f"[gray]⊘ 不存在：{file_path.name}[/gray]")
    
    console.print(Panel.fit(
        f"[bold green]版本升级完成[/bold green]\n\n"
        f"{current_version} → [bold]{new_version}[/bold]\n"
        f"更新文件：{updated_count}",
        title="📦 版本管理",
        border_style="green"
    ))


if __name__ == '__main__':
    version_cmd()
