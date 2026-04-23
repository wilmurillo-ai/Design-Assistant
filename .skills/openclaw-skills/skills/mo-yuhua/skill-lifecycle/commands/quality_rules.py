#!/usr/bin/env python3
"""增强的质量扫描规则"""

import ast
import re
from pathlib import Path
from typing import List


class Issue:
    """质量问题"""
    def __init__(self, file: str, line: int, rule: str, message: str, severity: str = 'warning'):
        self.file = file
        self.line = line
        self.rule = rule
        self.message = message
        self.severity = severity


def check_magic_numbers(skill_dir: Path) -> List[Issue]:
    """检查魔数（未命名的硬编码数字）"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        if py_file.name.startswith('test_'):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Num):  # Python 3.8+
                    if isinstance(node.n, (int, float)) and node.n > 100:
                        # 忽略常见的合理数字
                        if node.n not in [100, 1000, 1024, 365]:
                            issues.append(Issue(
                                py_file.name, node.lineno, 'magic_number',
                                f'魔数：{node.n}，建议定义为常量', 'warning'
                            ))
        except (SyntaxError, AttributeError):
            pass
    
    return issues


def check_too_many_params(skill_dir: Path) -> List[Issue]:
    """检查函数参数过多"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    param_count = len(node.args.args)
                    if param_count > 7:
                        issues.append(Issue(
                            py_file.name, node.lineno, 'too_many_params',
                            f'函数 {node.name} 参数过多 ({param_count}个)，建议重构', 'warning'
                        ))
        except SyntaxError:
            pass
    
    return issues


def check_missing_docstrings(skill_dir: Path) -> List[Issue]:
    """检查缺少文档字符串"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        if py_file.name.startswith('test_'):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if node.name.startswith('_'):
                        continue  # 跳过私有方法
                    
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        issues.append(Issue(
                            py_file.name, node.lineno, 'missing_docstring',
                            f'{node.__class__.__name__} {node.name} 缺少文档字符串', 'info'
                        ))
        except SyntaxError:
            pass
    
    return issues


def check_unused_imports(skill_dir: Path) -> List[Issue]:
    """检查未使用的导入"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 简单检查：导入名是否在文件中出现
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    # 提取导入名
                    match = re.match(r'(?:from\s+\S+\s+)?import\s+(\w+)', line)
                    if match:
                        import_name = match.group(1)
                        # 统计出现次数（排除导入行本身）
                        count = content.count(import_name)
                        if count == 1:  # 只在导入行出现
                            issues.append(Issue(
                                py_file.name, i, 'unused_import',
                                f'未使用的导入：{import_name}', 'info'
                            ))
        except Exception:
            pass
    
    return issues


def check_hardcoded_paths(skill_dir: Path) -> List[Issue]:
    """检查硬编码路径"""
    issues = []
    
    patterns = [
        r'/home/\w+/',
        r'/Users/\w+/',
        r'C:\\Users\\',
        r'/tmp/\w+',
    ]
    
    for py_file in skill_dir.glob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 跳过注释和字符串中的路径
            if line.strip().startswith('#'):
                continue
            
            for pattern in patterns:
                if re.search(pattern, line):
                    issues.append(Issue(
                        py_file.name, i, 'hardcoded_path',
                        '硬编码路径，建议使用 Path 或配置', 'warning'
                    ))
                    break
    
    return issues


def check_large_file(skill_dir: Path) -> List[Issue]:
    """检查大文件"""
    issues = []
    
    for py_file in skill_dir.glob('*.py'):
        if py_file.name.startswith('test_'):
            continue
        
        line_count = len(py_file.read_text(encoding='utf-8').split('\n'))
        if line_count > 1000:
            issues.append(Issue(
                py_file.name, 1, 'large_file',
                f'文件过大 ({line_count}行)，建议拆分', 'warning'
            ))
    
    return issues


def check_circular_imports(skill_dir: Path) -> List[Issue]:
    """检查循环导入（简单版）"""
    issues = []
    imports_graph = {}
    
    # 构建导入图
    for py_file in skill_dir.glob('*.py'):
        module_name = py_file.stem
        imports_graph[module_name] = []
        
        content = py_file.read_text(encoding='utf-8')
        for line in content.split('\n'):
            if line.strip().startswith('from .') or line.strip().startswith('from commands'):
                match = re.search(r'from\s+(\S+)\s+import', line)
                if match:
                    imported = match.group(1).split('.')[-1]
                    imports_graph[module_name].append(imported)
    
    # 检测循环
    for module, imports in imports_graph.items():
        for imp in imports:
            if module in imports_graph.get(imp, []):
                issues.append(Issue(
                    f'{module}.py', 1, 'circular_import',
                    f'循环导入：{module} ↔ {imp}', 'error'
                ))
    
    return issues


# 导出所有检查函数
ALL_CHECKS = [
    ('magic_number', check_magic_numbers),
    ('too_many_params', check_too_many_params),
    ('missing_docstring', check_missing_docstrings),
    ('unused_import', check_unused_imports),
    ('hardcoded_path', check_hardcoded_paths),
    ('large_file', check_large_file),
    ('circular_import', check_circular_imports),
]
