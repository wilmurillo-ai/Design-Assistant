#!/usr/bin/env python3
"""配置文件管理命令"""

import click
from pathlib import Path
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()

DEFAULT_CONFIG = {
    'version': '1.0',
    'versioning': {
        'auto_bump': 'patch',
        'files': [
            'SKILL.md',
            '_meta.json',
            '.clawhub/origin.json'
        ]
    },
    'scan': {
        'rules': {
            'bare_except': 'error',
            'sensitive_data': 'error',
            'long_function': 'warning',
            'print_statement': 'info',
            'missing_doc': 'warning'
        },
        'ignore': [
            'test_*.py',
            '__pycache__/',
            '*.pyc'
        ]
    },
    'test': {
        'timeout': 300,
        'parallel': True,
        'min_coverage': 0
    },
    'git': {
        'auto_commit': True,
        'commit_template': '📝 {version} 更新'
    },
    'publish': {
        'auto_publish': False,
        'changelog_auto': True
    }
}


def get_config_path() -> Path:
    """获取配置文件路径"""
    # 优先查找当前目录
    local_config = Path('.skill-lifecycle.yaml')
    if local_config.exists():
        return local_config
    
    # 查找用户主目录
    home_config = Path.home() / '.skill-lifecycle' / 'config.yaml'
    if home_config.exists():
        return home_config
    
    # 返回默认路径（用于创建）
    return local_config


def load_config(config_path: Path = None) -> dict:
    """加载配置"""
    if config_path is None:
        config_path = get_config_path()
    
    if not config_path.exists():
        return DEFAULT_CONFIG
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 合并默认配置
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)
    
    return merged


def save_config(config: dict, config_path: Path):
    """保存配置"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


@click.group()
def config_cmd():
    """配置管理"""
    pass


@config_cmd.command()
@click.option('--output', '-o', type=click.Path(), help='输出路径')
def init(output):
    """初始化配置文件"""
    if output:
        config_path = Path(output)
    else:
        config_path = Path('.skill-lifecycle.yaml')
    
    if config_path.exists():
        console.print(f"[yellow]⚠️  配置文件已存在：{config_path}[/yellow]")
        if not click.confirm("是否覆盖？"):
            return
    
    save_config(DEFAULT_CONFIG, config_path)
    
    console.print(Panel.fit(
        f"[bold green]✅ 配置文件已创建[/bold green]\n\n"
        f"路径：{config_path.absolute()}\n\n"
        f"[dim]提示：编辑后运行 sl-config validate 验证[/dim]",
        title="🔧 配置初始化",
        border_style="green"
    ))


@config_cmd.command()
def edit():
    """编辑配置文件"""
    config_path = get_config_path()
    
    if not config_path.exists():
        console.print("[yellow]⚠️  配置文件不存在，先运行 sl-config init[/yellow]")
        return
    
    # 使用默认编辑器打开
    import subprocess
    editor = subprocess._optim_args_from_interpreter_flags()  # 获取系统默认编辑器
    
    try:
        subprocess.run([editor, str(config_path)])
        console.print("[green]✅ 配置已保存[/green]")
    except Exception as e:
        console.print(f"[red]❌ 编辑失败：{e}[/red]")
        console.print(f"[dim]请手动编辑：{config_path}[/dim]")


@config_cmd.command()
def validate():
    """验证配置文件"""
    config_path = get_config_path()
    
    if not config_path.exists():
        console.print("[yellow]⚠️  配置文件不存在[/yellow]")
        return
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 验证基本结构
        required_keys = ['versioning', 'scan', 'test', 'git']
        missing = [k for k in required_keys if k not in config]
        
        if missing:
            console.print(f"[red]❌ 缺少必需的配置项：{missing}[/red]")
            return
        
        console.print(Panel.fit(
            f"[bold green]✅ 配置验证通过[/bold green]\n\n"
            f"文件：{config_path}\n"
            f"版本：{config.get('version', '1.0')}",
            title="✅ 验证成功",
            border_style="green"
        ))
    
    except yaml.YAMLError as e:
        console.print(f"[red]❌ YAML 语法错误：{e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ 验证失败：{e}[/red]")


@config_cmd.command()
def show():
    """显示当前配置"""
    config_path = get_config_path()
    
    if not config_path.exists():
        console.print("[yellow]⚠️  未找到配置文件，使用默认配置[/yellow]")
        config = DEFAULT_CONFIG
    else:
        config = load_config(config_path)
    
    console.print(f"[bold]配置文件:[/bold] {config_path}")
    console.print("\n[yellow]=== 版本管理 ===[/yellow]")
    console.print(f"自动升级：{config['versioning']['auto_bump']}")
    console.print(f"同步文件：{', '.join(config['versioning']['files'])}")
    
    console.print("\n[yellow]=== 质量扫描 ===[/yellow]")
    for rule, level in config['scan']['rules'].items():
        console.print(f"  {rule}: {level}")
    
    console.print("\n[yellow]=== 测试 ===[/yellow]")
    console.print(f"超时：{config['test']['timeout']}秒")
    console.print(f"并行：{config['test']['parallel']}")
    
    console.print("\n[yellow]=== Git ===[/yellow]")
    console.print(f"自动提交：{config['git']['auto_commit']}")
    console.print(f"提交模板：{config['git']['commit_template']}")


if __name__ == '__main__':
    config_cmd()
