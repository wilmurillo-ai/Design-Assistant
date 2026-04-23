"""
知识库概要与索引生成模块
合并文档概要（统计、目录树、关键词）和索引（文件清单）为一个文档
"""
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


def extract_keywords_from_md(md_path: Path, max_keywords: int = 5) -> List[str]:
    """
    从 MD 文档中提取关键词
    简单实现：从标题和前半部分内容提取高频词
    """
    try:
        # 只读取前 50KB 避免大文件处理过慢
        content = md_path.read_text(encoding='utf-8', errors='ignore')[:50000]
        
        # 移除 markdown 语法
        content = re.sub(r'[#*`\[\]()>_~\-]', '', content)
        
        # 提取中文字符序列作为候选关键词
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,}', content)
        
        # 简单统计词频
        word_freq = defaultdict(int)
        for i in range(min(len(chinese_words) - 1, 1000)):  # 限制处理数量
            # 提取二元组
            bigram = chinese_words[i] + chinese_words[i+1]
            if len(bigram) >= 4:  # 只保留4字及以上的词组
                word_freq[bigram] += 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 过滤停用词并返回前 N 个
        stopwords = {'的', '了', '是', '在', '和', '与', '为', '对', '等', '于', '以', '及', '或', '中', '后', '前', '时', '到', '将', '已', '本', '其', '此', '该', '各', '如', '所', '则', '但', '而', '又', '可', '会', '能', '要', '就', '也', '不', '还', '被', '把', '从', '由', '通过', '以及', '对于', '关于', '由于', '为了', '根据', '按照', '经过', '工作', '进行', '单位', '白云', '物流'}
        
        keywords = []
        for word, freq in sorted_words[:20]:  # 只处理前20个
            if word not in stopwords and freq >= 2:
                keywords.append(word)
                if len(keywords) >= max_keywords:
                    break
        
        return keywords
    
    except Exception as e:
        return []


def extract_title_from_md(md_path: Path) -> str:
    """
    从 MD 文档中提取标题
    """
    try:
        content = md_path.read_text(encoding='utf-8')
        
        # 查找第一个标题
        match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 如果没有标题，使用文件名
        return md_path.stem
    
    except Exception:
        return md_path.stem


def get_file_info(file_path: Path, base_dir: Path = None) -> dict:
    """
    获取文件详细信息
    """
    stat = file_path.stat()
    
    return {
        'name': file_path.name,
        'stem': file_path.stem,
        'suffix': file_path.suffix,
        'size': stat.st_size,
        'size_str': format_size(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
        'path': str(file_path.relative_to(base_dir)) if base_dir else str(file_path)
    }


def format_size(size: int) -> str:
    """
    格式化文件大小
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def build_directory_tree(categories: dict) -> str:
    """
    构建分类目录树
    """
    lines = []
    
    # 按大小排序
    sorted_cats = sorted(categories.items(), key=lambda x: x[1]['size'], reverse=True)
    
    for i, (cat, data) in enumerate(sorted_cats):
        # 使用 Unicode 图形字符构建树
        prefix = "└── " if i == len(sorted_cats) - 1 else "├── "
        lines.append(f"{prefix}📂 {cat}/ ({data['count']} 个文档, {format_size(data['size'])})")
        
        # 显示子文件（最多显示 5 个）
        files = data['files'][:5]
        for j, file_info in enumerate(files):
            is_last_file = (j == len(files) - 1)
            is_last_cat = (i == len(sorted_cats) - 1)
            
            if is_last_cat:
                file_prefix = "    "
            else:
                file_prefix = "│   "
            
            if is_last_file:
                file_prefix += "└── "
            else:
                file_prefix += "├── "
            
            lines.append(f"{file_prefix}📄 {file_info['name']}")
        
        # 如果文件超过 5 个，显示剩余数量
        if len(data['files']) > 5:
            remaining = len(data['files']) - 5
            if i == len(sorted_cats) - 1:
                lines.append(f"    ... 还有 {remaining} 个文件")
            else:
                lines.append(f"│   ... 还有 {remaining} 个文件")
    
    return '\n'.join(lines)


def get_raw_file_info(md_path: Path, raw_dir: Path, md_base_dir: Path) -> dict:
    """
    根据 MD 文件路径查找对应的原始文件信息
    """
    if not raw_dir or not raw_dir.exists():
        return None
    
    # 计算相对路径（基于 md_base_dir）
    try:
        rel_path = md_path.relative_to(md_base_dir)
    except ValueError:
        # 如果无法计算相对路径，使用文件名匹配
        rel_path = Path(md_path.name)
    
    raw_base = raw_dir / rel_path.with_suffix('')
    
    # 尝试多种扩展名
    supported_exts = ['.docx', '.doc', '.xlsx', '.xls', '.pdf', '.pptx', '.ppt']
    for ext in supported_exts:
        potential_raw = Path(str(raw_base) + ext)
        if potential_raw.exists():
            info = get_file_info(potential_raw, raw_dir)
            info['relative_path'] = str(potential_raw.relative_to(raw_dir))
            return info
    
    return None


def generate_knowledge_base(md_dir: str, raw_dir: str, output_path: str) -> dict:
    """
    生成知识库概要与索引（合并文档）
    
    Args:
        md_dir: MD 文档目录
        raw_dir: 原始文档目录（用于关联）
        output_path: 输出文件路径
        
    Returns:
        dict: 生成结果统计
    """
    md_path = Path(md_dir)
    raw_path = Path(raw_dir) if raw_dir else None
    
    if not md_path.exists():
        return {'success': False, 'error': f'MD 目录不存在: {md_dir}'}
    
    # 统计数据
    stats = {
        'total_files': 0,
        'total_size': 0,
        'by_category': defaultdict(lambda: {'count': 0, 'size': 0, 'files': []}),
        'by_type': defaultdict(lambda: {'count': 0, 'size': 0}),
        'keywords': defaultdict(int),
        'all_files': []
    }
    
    # 遍历所有 MD 文件
    md_files = list(md_path.rglob('*.md'))
    print(f"找到 {len(md_files)} 个 MD 文件待处理...")
    
    for idx, md_file in enumerate(md_files, 1):
        print(f"  [{idx}/{len(md_files)}] 处理: {md_file.name}")
        file_size = md_file.stat().st_size
        
        stats['total_files'] += 1
        stats['total_size'] += file_size
        
        # 计算相对路径和分类
        rel_path = md_file.relative_to(md_path)
        parts = rel_path.parts
        
        if len(parts) > 1:
            category = parts[0]
            sub_path = '/'.join(parts[1:])
        else:
            category = '根目录'
            sub_path = parts[0] if parts else ''
        
        # 提取标题和关键词
        title = extract_title_from_md(md_file)
        keywords = extract_keywords_from_md(md_file)
        
        # 获取原始文件信息
        raw_info = get_raw_file_info(md_file, raw_path, md_path) if raw_path else None
        
        file_info = {
            'name': md_file.name,
            'path': str(rel_path),
            'category': category,
            'title': title,
            'keywords': keywords,
            'size': file_size,
            'size_str': format_size(file_size),
            'modified': datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            'raw_info': raw_info
        }
        
        stats['all_files'].append(file_info)
        stats['by_category'][category]['count'] += 1
        stats['by_category'][category]['size'] += file_size
        stats['by_category'][category]['files'].append(file_info)
        
        # 统计文件类型
        ext = md_file.suffix
        stats['by_type'][ext]['count'] += 1
        stats['by_type'][ext]['size'] += file_size
        
        # 统计关键词
        for kw in keywords:
            stats['keywords'][kw] += 1
    
    print(f"  正在生成知识库内容...")
    
    # 生成知识库内容
    lines = []
    
    # 文档标题
    lines.append("# 知识库概要与索引\n")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ==================== 第一部分：概览 ====================
    print(f"  [1/6] 生成统计概览...")
    lines.append("---\n")
    lines.append("## 📊 文档统计概览\n")
    lines.append(f"| 统计项 | 数值 |")
    lines.append(f"|--------|------|")
    lines.append(f"| 总计文档 | {stats['total_files']} 个 |")
    lines.append(f"| 总大小 | {format_size(stats['total_size'])} |")
    lines.append(f"| 分类数 | {len(stats['by_category'])} 个 |")
    
    # 文档类型统计
    lines.append("\n### 文档类型分布\n")
    lines.append("| 类型 | 文档数 | 大小 |")
    lines.append("|------|--------|------|")
    for ext, data in sorted(stats['by_type'].items(), key=lambda x: x[1]['count'], reverse=True):
        lines.append(f"| {ext} | {data['count']} | {format_size(data['size'])} |")
    
    # ==================== 第二部分：分类目录树 ====================
    print(f"  [2/6] 生成分类目录树...")
    lines.append("\n---\n")
    lines.append("## 📁 分类目录树\n")
    tree = build_directory_tree(stats['by_category'])
    lines.append(tree)
    
    # ==================== 第三部分：高频关键词 ====================
    print(f"  [3/6] 生成高频关键词...")
    lines.append("\n---\n")
    lines.append("## 🔑 高频关键词\n")
    top_keywords = sorted(stats['keywords'].items(), key=lambda x: x[1], reverse=True)[:30]
    
    if top_keywords:
        # 以标签形式展示
        keyword_tags = [f"`{kw}`({freq})" for kw, freq in top_keywords]
        lines.append(" ".join(keyword_tags))
    else:
        lines.append("暂无关键词数据")
    
    # ==================== 第四部分：分类统计表 ====================
    print(f"  [4/6] 生成分类统计表...")
    lines.append("\n---\n")
    lines.append("## 📈 分类统计\n")
    lines.append("| 分类 | 文档数 | 大小 |")
    lines.append("|------|--------|------|")
    
    for cat, data in sorted(stats['by_category'].items(), key=lambda x: x[1]['size'], reverse=True):
        lines.append(f"| {cat} | {data['count']} | {format_size(data['size'])} |")
    
    # ==================== 第五部分：详细索引 ====================
    cat_count = len(stats['by_category'])
    print(f"  [5/6] 生成详细索引（共 {cat_count} 个分类）...")
    lines.append("\n---\n")
    lines.append("## 📝 文档详细索引\n")
    
    # 按分类组织展示
    cat_idx = 0
    for cat, data in sorted(stats['by_category'].items()):
        cat_idx += 1
        if cat_idx % 5 == 0 or cat_idx == cat_count:
            print(f"    处理分类 {cat_idx}/{cat_count}: {cat}")
        lines.append(f"\n### 📂 {cat}/\n")
        lines.append(f"*共 {data['count']} 个文档，总计 {format_size(data['size'])}*\n")
        lines.append("| 文件名 | 标题 | 关键词 | 大小 | 修改时间 | 原始文件 |")
        lines.append("|--------|------|--------|------|----------|----------|")
        
        for file_info in sorted(data['files'], key=lambda x: x['name']):
            keywords_str = ', '.join(file_info['keywords'][:3]) if file_info['keywords'] else '-'
            raw_file = file_info['raw_info']['name'] if file_info['raw_info'] else '-'
            lines.append(f"| {file_info['name']} | {file_info['title'][:40]} | {keywords_str} | {file_info['size_str']} | {file_info['modified']} | {raw_file} |")
    
    # 完整文件清单（按名称排序）
    print(f"  [6/6] 生成完整文件清单...")
    lines.append("\n---\n")
    lines.append("## 📋 完整文件清单（按名称排序）\n")
    lines.append("| 文件名 | 分类 | 标题 | 关键词 | 大小 |")
    lines.append("|--------|------|------|--------|------|")
    
    for file_info in sorted(stats['all_files'], key=lambda x: x['name']):
        keywords_str = ', '.join(file_info['keywords'][:3]) if file_info['keywords'] else '-'
        lines.append(f"| {file_info['name']} | {file_info['category']} | {file_info['title'][:30]} | {keywords_str} | {file_info['size_str']} |")
    
    # 写入文件
    print(f"  正在写入文件...")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  文件写入完成: {output_path}")
    
    return {
        'success': True,
        'total_files': stats['total_files'],
        'total_size': stats['total_size'],
        'categories': len(stats['by_category']),
        'output_path': output_path
    }


def main():
    if len(sys.argv) < 3:
        print("用法: python generate_knowledge_base.py <MD文档目录> <原始文档目录> <输出文件路径>")
        print("\n示例:")
        print("  python generate_knowledge_base.py ./_docs_md ./raw ./_docs_knowledge_base.md")
        sys.exit(1)
    
    md_dir = sys.argv[1]
    raw_dir = sys.argv[2]
    output_path = sys.argv[3]
    
    print(f"MD 文档目录: {md_dir}")
    print(f"原始文档目录: {raw_dir}")
    print(f"输出文件: {output_path}")
    print("-" * 50)
    
    result = generate_knowledge_base(md_dir, raw_dir, output_path)
    
    if result['success']:
        print(f"\n[OK] 知识库概要与索引生成成功！")
        print(f"  总计文档: {result['total_files']} 个")
        print(f"  总大小: {format_size(result['total_size'])}")
        print(f"  分类数: {result['categories']}")
        print(f"  输出文件: {result['output_path']}")
    else:
        print(f"\n[FAIL] 生成失败: {result['error']}")
        sys.exit(1)
    
    return result


if __name__ == '__main__':
    main()
