"""
MD 文档转换模块
使用 markitdown 将文档转换为 MD 格式
支持跳过/覆盖确认机制（首次询问后自动应用）
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Literal


# 转换模式：None=未设置, 'skip'=跳过, 'overwrite'=覆盖
convert_mode: Optional[Literal['skip', 'overwrite']] = None


def get_markitdown_cmd(input_path: str, output_path: str) -> list:
    """
    获取 markitdown 转换命令
    """
    return [
        sys.executable, '-m', 'markitdown',
        '--output', output_path,
        input_path
    ]


def convert_file(input_path: str, output_path: str, force: bool = False) -> dict:
    """
    转换单个文件为 MD 格式
    
    Args:
        input_path: 输入文件路径
        output_path: 输出 MD 文件路径
        force: 是否强制覆盖
        
    Returns:
        dict: {'success': bool, 'skipped': bool, 'error': str}
    """
    global convert_mode
    
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    # 检查输入文件是否存在
    if not input_file.exists():
        return {'success': False, 'skipped': False, 'error': f'输入文件不存在: {input_path}'}
    
    # 检查输出文件是否存在
    if output_file.exists():
        if not force:
            if convert_mode is None:
                # 首次遇到重复文件，询问用户
                while True:
                    print(f"\n目标文件已存在: {output_path}")
                    print("请选择操作方式：")
                    print("  [S] 跳过 - 保留现有文件，跳过此文件")
                    print("  [O] 覆盖 - 删除现有文件，重新转换")
                    choice = input("请输入选择 (S/O): ").strip().upper()
                    
                    if choice == 'S':
                        convert_mode = 'skip'
                        break
                    elif choice == 'O':
                        convert_mode = 'overwrite'
                        break
                    else:
                        print("无效选择，请重新输入")
            
            if convert_mode == 'skip':
                return {'success': True, 'skipped': True, 'error': None}
            # convert_mode == 'overwrite' 时继续执行覆盖逻辑
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 执行转换
    try:
        cmd = get_markitdown_cmd(str(input_file), str(output_file))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            return {'success': True, 'skipped': False, 'error': None}
        else:
            return {'success': False, 'skipped': False, 'error': result.stderr or '转换失败'}
    
    except subprocess.TimeoutExpired:
        return {'success': False, 'skipped': False, 'error': '转换超时（5分钟）'}
    except Exception as e:
        return {'success': False, 'skipped': False, 'error': str(e)}


def convert_directory(source_dir: str, output_dir: str, force: bool = False) -> dict:
    """
    批量转换目录下的所有支持文档为 MD 格式
    
    Args:
        source_dir: 源目录路径
        output_dir: 输出目录路径
        force: 是否强制覆盖所有文件
        
    Returns:
        dict: 转换统计结果
    """
    global convert_mode
    
    # 重置转换模式
    if force:
        convert_mode = 'overwrite'
    else:
        convert_mode = None
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    result = {
        'total': 0,
        'success': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }
    
    # 支持的文件扩展名（dochub 仅支持 .docx 和 .xlsx）
    supported_exts = {'.docx', '.xlsx'}
    
    # 先收集所有要处理的文件
    all_files = [f for f in source_path.rglob('*') 
                 if f.is_file() and f.suffix.lower() in supported_exts]
    total_files = len(all_files)
    
    print(f"发现 {total_files} 个文件待转换...")
    
    # 遍历所有文件
    for idx, file_path in enumerate(all_files, 1):
        result['total'] += 1
        
        # 计算相对路径
        rel_path = file_path.relative_to(source_path)
        
        # 构建输出路径（将扩展名改为 .md）
        md_rel_path = rel_path.with_suffix('.md')
        md_output_path = output_path / md_rel_path
        
        print(f"\n[{idx}/{total_files}] 转换: {rel_path}")
        
        conv_result = convert_file(str(file_path), str(md_output_path), force=force)
        
        if conv_result['skipped']:
            result['skipped'] += 1
            print(f"  -> 已跳过")
        elif conv_result['success']:
            result['success'] += 1
            print(f"  -> 成功: {md_output_path}")
        else:
            result['failed'] += 1
            result['errors'].append({
                'file': str(rel_path),
                'error': conv_result['error']
            })
            print(f"  -> 失败: {conv_result['error']}")
    
    return result


def main():
    if len(sys.argv) < 3:
        print("用法: python convert_to_md.py <源目录> <输出目录> [--force]")
        print("  --force: 强制覆盖所有已存在的 MD 文件")
        print("\n支持的格式: .docx, .xlsx （其他格式将被跳过）")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_dir = sys.argv[2]
    force = '--force' in sys.argv
    
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print(f"模式: {'强制覆盖' if force else '询问确认'}")
    print("-" * 50)
    
    result = convert_directory(source_dir, output_dir, force=force)
    
    print("\n" + "=" * 50)
    print("转换完成！")
    print(f"总计: {result['total']}")
    print(f"成功: {result['success']}")
    print(f"跳过: {result['skipped']}")
    print(f"失败: {result['failed']}")
    
    if result['errors']:
        print("\n失败文件:")
        for item in result['errors']:
            print(f"  {item['file']}: {item['error']}")
    
    return result


if __name__ == '__main__':
    main()
