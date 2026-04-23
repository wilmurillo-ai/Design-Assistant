#!/usr/bin/env python3
"""
skill-lifecycle - Skill 全生命周期管理工具

核心流程：版本管理 + 测试 + 质量扫描 + Git 提交
扩展流程：ClawHub 发布（可选）+ 知识提炼（可选）
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# 导入命令模块
from commands.version import version_cmd
from commands.test import test_cmd
from commands.quality import scan_cmd
from commands.git_ops import commit_cmd
from commands.publish import publish_cmd
from commands.config import config_cmd
from commands.batch import batch_dev
from commands.dev_flow import dev_flow, full_flow


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """🔄 skill-lifecycle - Skill 全生命周期管理工具"""
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold blue]skill-lifecycle[/bold blue] v0.1.0\n\n"
            "核心流程：[green]sl-dev --bump patch[/green]\n"
            "完整发布：[cyan]sl-full --bump patch[/cyan]\n\n"
            "运行 [bold]sl-dev --help[/bold] 或 [bold]sl-full --help[/bold] 查看详情",
            title="🔄 欢迎使用",
            border_style="blue"
        ))


# 核心命令
cli.add_command(version_cmd, name='version')
cli.add_command(test_cmd, name='test')
cli.add_command(scan_cmd, name='scan')
cli.add_command(commit_cmd, name='commit')
cli.add_command(config_cmd, name='config')

# 流程命令
cli.add_command(dev_flow, name='dev')
cli.add_command(full_flow, name='full')
cli.add_command(batch_dev, name='batch')

# 可选命令
cli.add_command(publish_cmd, name='publish')


def main():
    """主入口"""
    cli()


if __name__ == '__main__':
    main()
