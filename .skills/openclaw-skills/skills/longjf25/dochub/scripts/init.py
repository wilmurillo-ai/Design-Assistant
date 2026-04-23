"""
dochub 初始化主脚本
整合所有模块，完成文档知识库的初始化
"""
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Literal


# 命令行参数
args = None


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='dochub 文档知识库初始化工具')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='自动确认文档已脱敏（非交互模式）')
    parser.add_argument('--force', '-f', action='store_true',
                        help='强制覆盖所有已存在的 MD 文件')
    parser.add_argument('--skip-conflict', '-s', action='store_true',
                        help='遇到冲突时自动跳过（非交互模式）')
    return parser.parse_args()


# 转换模式：None=未设置, 'skip'=跳过, 'overwrite'=覆盖
convert_mode: Optional[Literal['skip', 'overwrite']] = None


def print_step(step_num: int, total: int, description: str):
    """
    打印步骤信息
    """
    print(f"\n{'=' * 60}")
    print(f"步骤 {step_num}/{total}: {description}")
    print('=' * 60)


def print_success(message: str):
    print(f"[OK] {message}")


def print_error(message: str):
    print(f"[ERROR] {message}")


def print_warning(message: str):
    print(f"[WARN] {message}")


def get_workspace() -> Path:
    """
    获取当前工作区路径
    """
    # 尝试从环境变量获取
    workspace = os.environ.get('WORKBUDDY_WORKSPACE')
    if workspace and Path(workspace).exists():
        return Path(workspace)
    
    # 默认使用当前目录
    return Path.cwd()


def confirm_desensitized() -> bool:
    """
    确认文档已脱敏
    返回 True 表示用户确认已脱敏，可以继续处理
    """
    global args
    
    print("\n" + "=" * 60)
    print("[!] 安全确认 - 需要用户输入")
    print("=" * 60)
    print("\n请确认 raw/ 文件夹内的文档已完成脱敏处理，")
    print("不含敏感个人信息、机密数据、商业机密等内容。")
    print("\n>>> 请在下方的输入框中回复 Y 或 N <<<")
    print("=" * 60)
    
    # 非交互模式：自动确认
    if args and args.yes:
        print("\n[自动确认] 通过 --yes 参数跳过安全确认")
        return True
    
    while True:
        choice = input("\n文档已脱敏？[Y/N]: ").strip().upper()
        if choice == 'Y':
            return True
        elif choice == 'N':
            print("\n[STOP] 用户未确认文档脱敏，操作已取消。")
            print("请先对文档进行脱敏处理后再试。")
            return False
        else:
            print("无效输入，请输入 Y 或 N")


# dochub 支持的文件格式
SUPPORTED_EXTS = {'.docx', '.xlsx'}


def check_unsupported_files(raw_dir: Path) -> list:
    """
    检查 raw 目录中的非支持格式文件
    返回不支持的文件列表
    """
    unsupported_files = []
    for file_path in raw_dir.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext not in SUPPORTED_EXTS:
                unsupported_files.append(file_path)
    return unsupported_files


def report_unsupported_files(unsupported_files: list) -> None:
    """
    报告不支持的文件，提示用户这些文件将被跳过
    """
    if not unsupported_files:
        return
    
    print("\n" + "=" * 60)
    print("[!] 检测到不支持的文件格式")
    print("=" * 60)
    print(f"\n发现 {len(unsupported_files)} 个不支持的文件：")
    
    # 按扩展名分组统计
    ext_count = {}
    for f in unsupported_files:
        ext = f.suffix.lower() or '(无扩展名)'
        ext_count[ext] = ext_count.get(ext, 0) + 1
        
    # 显示前10个文件
    for f in unsupported_files[:10]:
        print(f"  - {f.name}")
    if len(unsupported_files) > 10:
        print(f"  ... 还有 {len(unsupported_files) - 10} 个文件")
    
    print("\n格式统计:")
    for ext, count in sorted(ext_count.items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count} 个")
    
    print("\n[注意] dochub 仅支持 .docx 和 .xlsx 格式。")
    print("上述文件将被跳过，不会被处理。")
    print("如需处理这些文件，请先转换为 .docx 或 .xlsx 格式。")
    print("=" * 60)


def step1_move_to_raw(workspace: Path) -> dict:
    """
    步骤1: 将原始文档移动到 raw 文件夹
    """
    print_step(1, 5, "移动原始文档到 raw 文件夹")
    
    raw_dir = workspace / 'raw'
    
    # 收集所有要移动的文件和目录
    items_to_move = []
    exclude_names = {'raw', '_docs_md', 'update', 'dochub', '.workbuddy', '.git', '_docs_knowledge_base.md'}
    
    for item in workspace.iterdir():
        if item.name in exclude_names:
            continue
        
        # 跳过非目录项（忽略 .gitignore 等文件）
        if item.is_dir():
            items_to_move.append(item)
    
    if not items_to_move:
        print_warning("没有找到需要移动的原始文档目录")
        return {'success': True, 'moved': [], 'skipped': True}
    
    # 创建 raw 目录
    raw_dir.mkdir(exist_ok=True)
    
    moved = []
    errors = []
    
    for item in items_to_move:
        dest = raw_dir / item.name
        
        if dest.exists():
            # 如果目标已存在，添加后缀
            counter = 1
            while dest.exists():
                dest = raw_dir / f"{item.name}_{counter}"
                counter += 1
            print_warning(f"目标已存在，重命名为: {dest.name}")
        
        try:
            shutil.move(str(item), str(dest))
            moved.append((str(item), str(dest)))
            print_success(f"移动: {item.name} -> raw/{dest.name}")
        except Exception as e:
            errors.append((str(item), str(e)))
            print_error(f"移动失败 {item.name}: {e}")
    
    return {
        'success': len(errors) == 0,
        'moved': moved,
        'errors': errors
    }


def step2_normalize_names(raw_dir: Path) -> dict:
    """
    步骤2: 规范化文件名
    """
    print_step(2, 5, "规范化文件夹和文件名")
    
    # 导入并执行规范化模块
    script_path = Path(__file__).parent / 'normalize_names.py'
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(raw_dir)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("文件名规范化完成")
            # 解析输出
            output = result.stdout
            return {'success': True, 'output': output}
        else:
            print_error(f"规范化失败: {result.stderr}")
            return {'success': False, 'error': result.stderr}
    
    except Exception as e:
        print_error(f"执行规范化脚本失败: {e}")
        return {'success': False, 'error': str(e)}


def step3_check_unsupported(raw_dir: Path, unsupported_files: list) -> dict:
    """
    步骤3: 检查并报告不支持的文件格式
    仅提示用户，不执行任何转换
    """
    print_step(3, 5, "检查文件格式")
    
    if not unsupported_files:
        print_success("所有文件格式均支持（.docx/.xlsx）")
        return {'success': True, 'skipped': False, 'unsupported_count': 0}
    
    # 报告不支持的文件
    report_unsupported_files(unsupported_files)
    
    return {
        'success': True,
        'skipped': False,
        'unsupported_count': len(unsupported_files),
        'note': '不支持的文件已被跳过'
    }


def step4_convert_to_md(workspace: Path, raw_dir: Path, force: bool = False) -> dict:
    """
    步骤4: 使用 markitdown 转换为 MD 文档（仅处理 .docx/.xlsx）
    """
    global convert_mode
    
    print_step(4, 5, "将文档转换为 MD 格式")
    
    docs_md_dir = workspace / '_docs_md'
    docs_md_dir.mkdir(exist_ok=True)
    
    # 导入并执行 MD 转换模块
    script_path = Path(__file__).parent / 'convert_to_md.py'
    
    # 构建命令
    cmd = [sys.executable, str(script_path), str(raw_dir), str(docs_md_dir)]
    if force:
        cmd.append('--force')
    
    try:
        # 对于交互式询问模式，我们需要手动处理
        if not force:
            # 先检查有多少文件会冲突
            md_files = set()
            for f in docs_md_dir.rglob('*.md'):
                md_files.add(f.relative_to(docs_md_dir))
            
            # 检查源文件转换后的目标
            conflicts = []
            for src_file in raw_dir.rglob('*'):
                if src_file.is_file():
                    rel_path = src_file.relative_to(raw_dir)
                    md_path = rel_path.with_suffix('.md')
                    if md_path in md_files:
                        conflicts.append(str(rel_path))
            
            if conflicts:
                print_warning(f"发现 {len(conflicts)} 个已存在的 MD 文件")
                if convert_mode is None:
                    # 非交互模式：根据参数自动选择
                    if args and args.force:
                        print("\n[自动选择] 通过 --force 参数覆盖所有文件")
                        convert_mode = 'overwrite'
                        cmd.append('--force')
                    elif args and args.skip_conflict:
                        print("\n[自动选择] 通过 --skip-conflict 参数跳过冲突文件")
                        convert_mode = 'skip'
                    else:
                        print("\n" + "=" * 50)
                        print(">>> 需要用户输入 - 请选择操作方式 <<<")
                        print("=" * 50)
                        while True:
                            print("\n  [S] 跳过 - 保留现有文件，跳过已存在的文件")
                            print("  [O] 覆盖 - 删除现有文件，重新转换所有文件")
                            choice = input("\n请输入选择 (S/O): ").strip().upper()
                            
                            if choice == 'S':
                                convert_mode = 'skip'
                                break
                            elif choice == 'O':
                                convert_mode = 'overwrite'
                                cmd.append('--force')
                                break
                            else:
                                print("无效选择，请重新输入")
        
        print(f"\n源目录: {raw_dir}")
        print(f"输出目录: {docs_md_dir}")
        print("-" * 50)
        
        # 执行转换（实时输出进度）
        result = subprocess.run(
            cmd,
            stdout=None,  # 直接输出到终端
            stderr=subprocess.STDOUT,  # 错误也输出到终端
            cwd=str(workspace)
        )
        
        if result.returncode == 0:
            print_success("MD 文档转换完成")
            return {'success': True}
        else:
            print_error(f"MD 转换失败，返回码: {result.returncode}")
            return {'success': False, 'error': f"返回码: {result.returncode}"}
    
    except Exception as e:
        print_error(f"执行 MD 转换脚本失败: {e}")
        return {'success': False, 'error': str(e)}


def step5_generate_knowledge_base(workspace: Path, docs_md_dir: Path, raw_dir: Path) -> dict:
    """
    步骤5: 生成知识库概要与索引（合并为一个文档）
    """
    print_step(5, 5, "生成知识库概要与索引")
    
    kb_path = workspace / '_docs_knowledge_base.md'
    
    script_path = Path(__file__).parent / 'generate_knowledge_base.py'
    
    try:
        print(f"开始生成知识库文档...")
        print(f"  MD目录: {docs_md_dir}")
        print(f"  输出: {kb_path}")
        
        result = subprocess.run(
            [sys.executable, str(script_path), str(docs_md_dir), str(raw_dir), str(kb_path)],
            stdout=None,  # 直接输出到终端
            stderr=subprocess.STDOUT,  # 错误也输出到终端
            cwd=str(workspace)
        )
        
        if result.returncode == 0:
            print_success(f"知识库概要与索引已生成: {kb_path}")
            return {'success': True, 'output_path': str(kb_path)}
        else:
            print_error(f"生成知识库文档失败，返回码: {result.returncode}")
            return {'success': False, 'error': f"返回码: {result.returncode}"}
    
    except Exception as e:
        print_error(f"执行知识库生成脚本失败: {e}")
        return {'success': False, 'error': str(e)}


def init_knowledge_base(workspace: Path = None, force: bool = False) -> dict:
    """
    初始化知识库主流程
    
    Args:
        workspace: 工作区路径，默认当前目录
        force: 是否强制覆盖所有文件
        
    Returns:
        dict: 初始化结果
    """
    global convert_mode
    
    if workspace is None:
        workspace = get_workspace()
    
    print("\n" + "=" * 60)
    print("==> dochub 文档知识库初始化 <==")
    print("=" * 60)
    print(f"工作区: {workspace}")
    print(f"模式: {'强制覆盖' if force else '确认后转换'}")
    
    # 确保 raw 目录存在
    raw_dir = workspace / 'raw'
    raw_dir.mkdir(exist_ok=True)
    
    # 步骤0: 安全确认 - 确认文档已脱敏
    if not confirm_desensitized():
        return {
            'success': False,
            'cancelled': True,
            'reason': '用户未确认文档脱敏'
        }
    
    # 重置转换模式
    convert_mode = None
    
    # 创建 update 目录
    update_dir = workspace / 'update'
    update_dir.mkdir(exist_ok=True)
    print_success(f"创建 update 目录: {update_dir}")
    
    # 执行各步骤
    results = []
    
    # 步骤1: 移动到 raw
    result = step1_move_to_raw(workspace)
    results.append(('移动原始文档', result))
    if not result['success']:
        print_error("步骤1失败，初始化中止")
        return {'success': False, 'results': results}
    
    # 步骤2: 规范化名称
    result = step2_normalize_names(raw_dir)
    results.append(('规范化文件名', result))
    if not result['success']:
        print_warning("步骤2有错误，但继续执行")
    
    # 检查不支持的文件格式
    unsupported_files = check_unsupported_files(raw_dir)
    
    # 步骤3: 检查不支持的文件格式
    result = step3_check_unsupported(raw_dir, unsupported_files)
    results.append(('检查文件格式', result))
    
    # 步骤4: MD 转换
    result = step4_convert_to_md(workspace, raw_dir, force=force)
    results.append(('MD转换', result))
    
    docs_md_dir = workspace / '_docs_md'
    
    # 步骤5: 生成知识库概要与索引（合并）
    result = step5_generate_knowledge_base(workspace, docs_md_dir, raw_dir)
    results.append(('生成知识库概要与索引', result))
    
    # 总结
    print("\n" + "=" * 60)
    print("==> 初始化完成! <==")
    print("=" * 60)
    print(f"\n生成的文件:")
    print(f"  [DIR] _docs_md/ - MD 文档目录")
    print(f"  [FILE] _docs_knowledge_base.md - 知识库概要与索引")
    print(f"  [DIR] update/ - 增量更新目录")
    
    success_count = sum(1 for _, r in results if r.get('success', False))
    print(f"\n步骤完成: {success_count}/{len(results)}")
    
    return {
        'success': success_count == len(results),
        'results': results,
        'workspace': str(workspace)
    }


def main():
    global args
    args = parse_args()
    
    # 获取工作区路径
    workspace = None
    for arg in sys.argv[1:]:
        if not arg.startswith('-') and Path(arg).exists():
            workspace = Path(arg)
            break
    
    result = init_knowledge_base(workspace=workspace, force=args.force)
    
    if result.get('cancelled'):
        print("\n[STOP] 操作已取消")
        sys.exit(0)
    elif result['success']:
        print("\n[OK] 知识库初始化成功！")
        sys.exit(0)
    else:
        print("\n[WARN] 知识库初始化部分完成，请检查上述错误")
        sys.exit(1)


if __name__ == '__main__':
    main()
