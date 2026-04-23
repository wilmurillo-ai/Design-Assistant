#!/usr/bin/env python3
"""
代码解析器 - 使用 ast + 正则 解析多种编程语言（零外部依赖）

支持语言：
- Python (ast 内置，完整支持)
- JavaScript (正则，基础支持)
- Bash (正则，基础支持)

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import ast
import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# 日志配置
logger = logging.getLogger(__name__)


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"


@dataclass
class Parameter:
    """函数参数信息"""
    name: str
    type: Optional[str] = None
    default: Optional[str] = None
    description: Optional[str] = None


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    source_code: str = ""
    file_path: str = ""
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    source_code: str = ""
    file_path: str = ""
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """导入信息"""
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from: bool = False


@dataclass
class ParseTree:
    """解析结果"""
    file_path: str
    language: Language
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    module_docstring: Optional[str] = None
    source_code: str = ""
    error: Optional[str] = None


class CodeParser:
    """代码解析器（零外部依赖版本）"""

    def __init__(self, language: Language):
        self.language = language
        self.logger = logging.getLogger(f"{__name__}.{language.value}")

    # =========================================================================
    # 公开接口
    # =========================================================================

    def parse_file(self, file_path: str) -> ParseTree:
        """解析单个文件"""
        result = ParseTree(file_path=file_path, language=self.language)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                result.source_code = code
        except FileNotFoundError:
            result.error = f"File not found: {file_path}"
            return result

        if self.language == Language.PYTHON:
            self._parse_python(code, result)
        elif self.language == Language.JAVASCRIPT:
            self._parse_javascript_regex(code, result)
        elif self.language == Language.BASH:
            self._parse_bash_regex(code, result)

        self.logger.info(
            f"Parsed {file_path}: {len(result.functions)} functions, "
            f"{len(result.classes)} classes"
        )
        return result

    def parse_directory(self, dir_path: str, recursive: bool = True) -> List[ParseTree]:
        """解析整个目录"""
        results = []
        path = Path(dir_path)

        if not path.exists():
            self.logger.error(f"Directory not found: {dir_path}")
            return results

        ext_map = {
            Language.PYTHON: '.py',
            Language.JAVASCRIPT: '.js',
            Language.BASH: '.sh',
        }
        extension = ext_map.get(self.language)
        if not extension:
            return results

        files = list(path.rglob(f"*{extension}") if recursive else path.glob(f"*{extension}"))

        exclude_dirs = {'__pycache__', 'node_modules', '.git', 'venv', 'env', '.tox'}
        files = [f for f in files if not any(ex in f.parts for ex in exclude_dirs)]

        self.logger.info(f"Found {len(files)} {self.language.value} files in {dir_path}")

        for file in files:
            results.append(self.parse_file(str(file)))
        return results

    # =========================================================================
    # Python 解析（ast）
    # =========================================================================

    def _parse_python(self, code: str, result: ParseTree):
        """用 Python ast 模块解析代码"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            result.error = f"SyntaxError: {e}"
            return result

        # 模块 docstring
        result.module_docstring = ast.get_docstring(tree)

        lines = code.splitlines()
        result._lines = lines  # 缓存，供内部使用

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func = self._ast_function(node, lines, result.file_path)
                result.functions.append(func)
            elif isinstance(node, ast.ClassDef):
                cls = self._ast_class(node, lines, result.file_path)
                result.classes.append(cls)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.append(ImportInfo(
                        module=alias.name, alias=alias.asname
                    ))
            elif isinstance(node, ast.ImportFrom):
                names = [a.name for a in node.names]
                result.imports.append(ImportInfo(
                    module=(node.module or ""), names=names, is_from=True
                ))

        return result

    def _ast_function(self, node: ast.AST, lines: list, file_path: str) -> FunctionInfo:
        """从 ast.FunctionDef 提取函数信息"""
        docstring = ast.get_docstring(node) or None
        end_line = getattr(node, 'end_lineno', node.end_lineno) if hasattr(node, 'end_lineno') else node.lineno
        decorators = []
        if hasattr(node, 'decorator_list'):
            for d in node.decorator_list:
                decorators.append(ast.dump(d).split('(')[0].replace('ast.', ''))

        # 源代码
        start = node.lineno - 1
        source = '\n'.join(lines[start:end_line])

        # 参数
        params = []
        if hasattr(node, 'args'):
            args = node.args
            # 普通参数
            for arg in args.args:
                p = Parameter(name=arg.arg)
                if arg.annotation:
                    p.type = ast.unparse(arg.annotation)
                params.append(p)
            # *args
            if args.vararg:
                params.append(Parameter(name=f"*{args.vararg.arg}"))
            # **kwargs
            if args.kwarg:
                params.append(Parameter(name=f"**{args.kwarg.arg}"))
            # 默认值（从 defaults 对齐）
            defaults = args.defaults
            offset = len(args.args) - len(defaults)
            for i, default in enumerate(defaults):
                idx = offset + i
                if idx < len(params):
                    try:
                        params[idx].default = ast.unparse(default)
                    except Exception:
                        params[idx].default = "..."

        # 返回类型
        return_type = None
        if hasattr(node, 'returns') and node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                return_type = "..."

        return FunctionInfo(
            name=node.name,
            parameters=params,
            return_type=return_type,
            docstring=docstring,
            start_line=node.lineno,
            end_line=end_line or node.lineno,
            source_code=source,
            file_path=file_path,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    def _ast_class(self, node: ast.ClassDef, lines: list, file_path: str) -> ClassInfo:
        """从 ast.ClassDef 提取类信息"""
        docstring = ast.get_docstring(node) or None
        end_line = getattr(node, 'end_lineno', node.end_lineno) if hasattr(node, 'end_lineno') else node.lineno

        # 基类
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append("...")

        # 装饰器
        decorators = []
        for d in node.decorator_list:
            decorators.append(ast.dump(d).split('(')[0].replace('ast.', ''))

        # 源代码
        start = node.lineno - 1
        source = '\n'.join(lines[start:end_line])

        # 方法
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                m = self._ast_function(item, lines, file_path)
                m.is_method = True
                m.class_name = node.name
                methods.append(m)

        # 类属性（简单的 name=value 赋值）
        attributes = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        val = ast.unparse(item.value) if hasattr(ast, 'unparse') else "..."
                        attributes.append({"name": target.id, "value": val})

        return ClassInfo(
            name=node.name,
            docstring=docstring,
            methods=methods,
            attributes=attributes,
            start_line=node.lineno,
            end_line=end_line or node.lineno,
            source_code=source,
            file_path=file_path,
            decorators=decorators,
            base_classes=bases,
        )

    # =========================================================================
    # JavaScript 解析（正则）
    # =========================================================================

    def _parse_javascript_regex(self, code: str, result: ParseTree):
        """用正则解析 JavaScript（基础支持）"""
        lines = code.splitlines()

        # 函数：function name(...) / const name = (...) => / const name = function(...)
        func_pattern = re.compile(
            r'(?:function\s+(\w+)\s*\(([^)]*)\)|'
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>|'
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:function\s*)?\(([^)]*)\))'
        )
        for i, line in enumerate(lines, 1):
            for m in func_pattern.finditer(line):
                name = m.group(1) or m.group(3) or m.group(5)
                params_str = m.group(2) or m.group(4) or m.group(6) or ""
                params = []
                if params_str.strip():
                    for p in params_str.split(','):
                        p = p.strip()
                        if p:
                            # 去掉默认值
                            param_name = p.split('=')[0].strip().lstrip('...')
                            if param_name:
                                params.append(Parameter(name=param_name))
                result.functions.append(FunctionInfo(
                    name=name, parameters=params, start_line=i, end_line=i,
                    source_code=line.strip(), file_path=result.file_path
                ))

        # 类：class Name { ... } 或 class Name extends Base {
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?')
        for i, line in enumerate(lines, 1):
            m = class_pattern.search(line)
            if m:
                result.classes.append(ClassInfo(
                    name=m.group(1),
                    base_classes=[m.group(2)] if m.group(2) else [],
                    start_line=i, end_line=i,
                    file_path=result.file_path
                ))

    # =========================================================================
    # Bash 解析（正则）
    # =========================================================================

    def _parse_bash_regex(self, code: str, result: ParseTree):
        """用正则解析 Bash（基础支持）"""
        lines = code.splitlines()

        func_pattern = re.compile(r'^(?:function\s+)?(\w+)\s*\(\)\s*\{?$')
        for i, line in enumerate(lines, 1):
            m = func_pattern.match(line.strip())
            if m:
                result.functions.append(FunctionInfo(
                    name=m.group(1), start_line=i, end_line=i,
                    source_code=line.strip(), file_path=result.file_path
                ))


def detect_language(file_path: str) -> Optional[Language]:
    """检测文件语言"""
    ext = Path(file_path).suffix.lower()
    language_map = {
        '.py': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.sh': Language.BASH,
    }
    return language_map.get(ext)
