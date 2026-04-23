"""
文件名规范化模块
将所有文件夹和文件名规范化，只保留中文、英文、数字和中横线"-"
其余字符统一替换为"-"
"""
import os
import re
import sys
from pathlib import Path


def normalize_name(name: str) -> str:
    """
    规范化名称：只保留中文、英文、数字和中横线"-"
    其他所有字符替换为"-"
    """
    # 替换所有非允许字符为"-"
    # 允许：中文(\u4e00-\u9fa5)、英文(a-zA-Z)、数字(0-9)、中横线(-)
    pattern = r'[^a-zA-Z0-9\u4e00-\u9fa5-]'
    normalized = re.sub(pattern, '-', name)
    
    # 合并连续的中横线
    normalized = re.sub(r'-+', '-', normalized)
    
    # 移除首尾的中横线
    normalized = normalized.strip('-')
    
    return normalized


def normalize_path(path: str) -> str:
    """
    规范化路径中的各个部分
    """
    parts = path.split(os.sep)
    normalized_parts = [normalize_name(part) if part else part for part in parts]
    return os.sep.join(normalized_parts)


def normalize_directory(root_path: str) -> dict:
    """
    规范化目录下所有文件夹和文件的名称
    
    Args:
        root_path: 要规范化的根目录
        
    Returns:
        dict: {
            'renamed': [(原路径, 新路径), ...],
            'errors': [(路径, 错误信息), ...],
            'total': 处理的文件总数
        }
    """
    result = {
        'renamed': [],
        'errors': [],
        'total': 0
    }
    
    root = Path(root_path)
    if not root.exists():
        result['errors'].append((str(root), f"目录不存在: {root_path}"))
        return result
    
    # 遍历所有文件和目录（深度优先）
    all_items = list(root.rglob('*'))
    
    # 先处理目录（从深层到浅层，避免路径问题）
    dirs = [item for item in all_items if item.is_dir()]
    dirs.sort(key=lambda x: len(x.parts), reverse=True)
    
    for dir_path in dirs:
        parent = dir_path.parent
        old_name = dir_path.name
        new_name = normalize_name(old_name)
        
        if old_name != new_name and new_name:  # 名称有变化且新名称不为空
            new_path = parent / new_name
            try:
                # 检查新名称是否已存在
                if new_path.exists():
                    # 如果已存在，添加数字后缀
                    counter = 1
                    while new_path.exists():
                        new_path = parent / f"{new_name}-{counter}"
                        counter += 1
                
                dir_path.rename(new_path)
                result['renamed'].append((str(dir_path), str(new_path)))
                result['total'] += 1
            except Exception as e:
                result['errors'].append((str(dir_path), str(e)))
    
    # 再处理文件
    files = [item for item in all_items if item.is_file()]
    
    for file_path in files:
        parent = file_path.parent
        old_name = file_path.stem  # 文件名（不含扩展名）
        ext = file_path.suffix     # 扩展名
        
        new_name = normalize_name(old_name)
        
        if old_name != new_name and new_name:  # 名称有变化且新名称不为空
            new_path = parent / f"{new_name}{ext}"
            try:
                # 检查新名称是否已存在
                if new_path.exists():
                    counter = 1
                    while new_path.exists():
                        new_path = parent / f"{new_name}-{counter}{ext}"
                        counter += 1
                
                file_path.rename(new_path)
                result['renamed'].append((str(file_path), str(new_path)))
                result['total'] += 1
            except Exception as e:
                result['errors'].append((str(file_path), str(e)))
    
    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python normalize_names.py <目录路径>")
        sys.exit(1)
    
    root_path = sys.argv[1]
    
    print(f"开始规范化目录: {root_path}")
    print("-" * 50)
    
    result = normalize_directory(root_path)
    
    print(f"\n处理完成！")
    print(f"总计重命名: {result['total']} 项")
    print(f"成功: {len(result['renamed'])}")
    print(f"失败: {len(result['errors'])}")
    
    if result['renamed']:
        print("\n成功重命名:")
        for old, new in result['renamed']:
            print(f"  {old} -> {new}")
    
    if result['errors']:
        print("\n错误:")
        for path, error in result['errors']:
            print(f"  {path}: {error}")
    
    return result


if __name__ == '__main__':
    main()
