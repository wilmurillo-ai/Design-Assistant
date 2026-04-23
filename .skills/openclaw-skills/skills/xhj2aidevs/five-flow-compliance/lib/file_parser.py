# -*- coding: utf-8 -*-
"""
文件识别与解析模块

所有业务数据必须通过上传原始文件采集，禁止手动输入。
支持：银行流水(CSV/Excel/PDF)、发票(PDF/图片)、合同(PDF/Word/图片)
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import csv

# 尝试导入可选依赖
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


class FileParser:
    """文件解析器 - 支持银行流水、发票、合同等文件"""
    
    # 支持的文件类型
    FILE_TYPES = {
        'bank': {
            'extensions': ['.csv', '.xls', '.xlsx', '.pdf'],
            'description': '银行流水',
            'patterns': ['交易日期', '交易时间', '收入', '支出', '余额', '对方户名', '摘要']
        },
        'invoice': {
            'extensions': ['.pdf', '.jpg', '.jpeg', '.png', '.ofd'],
            'description': '发票',
            'patterns': ['发票代码', '发票号码', '价税合计', '购买方', '销售方']
        },
        'contract': {
            'extensions': ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'],
            'description': '合同',
            'patterns': ['合同', '甲方', '乙方', '金额', '签字']
        }
    }
    
    def __init__(self, data_dir: str = None):
        """初始化解析器
        
        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            # 默认使用 skills/five-flow-compliance/data
            skill_dir = Path(__file__).parent.parent
            data_dir = skill_dir / 'data'
        
        self.data_dir = Path(data_dir)
        self.archive_dir = self.data_dir / 'archive'
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def detect_file_type(self, file_path: str) -> Tuple[str, float]:
        """检测文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            (文件类型, 置信度)
        """
        ext = Path(file_path).suffix.lower()
        content_sample = self._read_file_sample(file_path)
        
        best_type = 'unknown'
        best_score = 0.0
        
        for file_type, config in self.FILE_TYPES.items():
            # 检查扩展名
            if ext not in config['extensions']:
                continue
            
            # 检查内容模式
            score = 0.0
            for pattern in config['patterns']:
                if pattern in content_sample:
                    score += 1.0
            
            score = score / len(config['patterns'])  # 归一化
            
            if score > best_score:
                best_score = score
                best_type = file_type
        
        return best_type, best_score
    
    def _read_file_sample(self, file_path: str, max_chars: int = 5000) -> str:
        """读取文件样本内容"""
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read(max_chars)
            elif ext in ['.xls', '.xlsx'] and HAS_PANDAS:
                df = pd.read_excel(file_path, nrows=10)
                return df.to_string()
            elif ext == '.pdf' and HAS_PDFPLUMBER:
                with pdfplumber.open(file_path) as pdf:
                    text = ''
                    for page in pdf.pages[:3]:  # 只读前3页
                        text += page.extract_text() or ''
                    return text[:max_chars]
            elif ext in ['.jpg', '.jpeg', '.png']:
                # 图片需要OCR，这里返回空，实际使用时调用OCR
                return ''
            else:
                # 尝试作为文本读取
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(max_chars)
        except Exception as e:
            return f'[读取失败: {e}]'
    
    def parse_bank_csv(self, file_path: str) -> List[Dict]:
        """解析银行流水CSV文件
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            交易记录列表
        """
        transactions = []
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # 检测是否有BOM
                    content = f.read()
                    if content.startswith('\ufeff'):
                        content = content[1:]
                
                # 解析CSV
                lines = content.strip().split('\n')
                if not lines:
                    continue
                
                # 检测表头
                header_line = lines[0]
                delimiter = ',' if ',' in header_line else '\t'
                
                reader = csv.DictReader(lines, delimiter=delimiter)
                
                for row in reader:
                    # 标准化字段名
                    record = self._normalize_bank_row(row)
                    if record:
                        transactions.append(record)
                
                if transactions:
                    break  # 成功解析，退出编码循环
                    
            except Exception as e:
                continue
        
        return transactions
    
    def _normalize_bank_row(self, row: Dict) -> Optional[Dict]:
        """标准化银行流水行数据"""
        # 常见字段名映射
        field_mapping = {
            '交易日期': 'date',
            '交易时间': 'time',
            '日期': 'date',
            '时间': 'time',
            '收入': 'income',
            '支出': 'expense',
            '借方': 'debit',
            '贷方': 'credit',
            '余额': 'balance',
            '对方户名': 'counterparty',
            '对方名称': 'counterparty',
            '摘要': 'summary',
            '备注': 'summary',
            '交易类型': 'type'
        }
        
        record = {}
        
        for key, value in row.items():
            # 清理键名
            clean_key = key.strip().replace('"', '').replace("'", '')
            
            # 映射到标准字段
            if clean_key in field_mapping:
                std_field = field_mapping[clean_key]
                record[std_field] = value.strip() if isinstance(value, str) else value
        
        # 验证必要字段
        if 'date' not in record:
            return None
        
        # 处理收入/支出
        if 'income' in record and 'expense' in record:
            income = self._parse_amount(record.get('income', 0))
            expense = self._parse_amount(record.get('expense', 0))
            record['amount'] = income if income > 0 else -expense
        elif 'credit' in record and 'debit' in record:
            credit = self._parse_amount(record.get('credit', 0))
            debit = self._parse_amount(record.get('debit', 0))
            record['amount'] = credit if credit > 0 else -debit
        
        return record if record else None
    
    def _parse_amount(self, value) -> float:
        """解析金额字符串"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if not value or not isinstance(value, str):
            return 0.0
        
        # 清理金额字符串
        clean = value.strip().replace(',', '').replace('￥', '').replace('¥', '')
        clean = clean.replace(' ', '').replace('"', '')
        
        try:
            return float(clean)
        except ValueError:
            return 0.0
    
    def archive_file(self, file_path: str, file_type: str) -> str:
        """归档原始文件
        
        Args:
            file_path: 原始文件路径
            file_type: 文件类型 (bank/invoice/contract)
            
        Returns:
            归档后的文件路径
        """
        # 按年月分类
        now = datetime.now()
        archive_subdir = self.archive_dir / f"{now.year}-{now.month:02d}"
        archive_subdir.mkdir(parents=True, exist_ok=True)
        
        # 生成归档文件名
        original_name = Path(file_path).stem
        ext = Path(file_path).suffix
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        archive_name = f"{file_type}_{original_name}_{timestamp}{ext}"
        
        archive_path = archive_subdir / archive_name
        
        # 复制文件到归档目录
        shutil.copy2(file_path, archive_path)
        
        return str(archive_path)
    
    def process_uploaded_file(self, file_path: str) -> Dict:
        """处理上传的文件（完整流程）
        
        Args:
            file_path: 上传的文件路径
            
        Returns:
            处理结果，包含：
            - file_type: 文件类型
            - confidence: 识别置信度
            - data: 解析出的数据
            - archive_path: 归档路径
        """
        # 1. 检测文件类型
        file_type, confidence = self.detect_file_type(file_path)
        
        # 2. 解析数据
        data = []
        if file_type == 'bank':
            ext = Path(file_path).suffix.lower()
            if ext == '.csv':
                data = self.parse_bank_csv(file_path)
            elif ext in ['.xls', '.xlsx'] and HAS_PANDAS:
                data = self._parse_bank_excel(file_path)
        elif file_type == 'invoice':
            data = self._parse_invoice(file_path)
        elif file_type == 'contract':
            data = self._parse_contract(file_path)
        
        # 3. 归档原始文件
        archive_path = self.archive_file(file_path, file_type)
        
        return {
            'file_type': file_type,
            'confidence': confidence,
            'data': data,
            'archive_path': archive_path,
            'data_count': len(data)
        }
    
    def _parse_bank_excel(self, file_path: str) -> List[Dict]:
        """解析银行流水Excel文件"""
        if not HAS_PANDAS:
            return []
        
        transactions = []
        
        try:
            df = pd.read_excel(file_path)
            
            for _, row in df.iterrows():
                record = self._normalize_bank_row(row.to_dict())
                if record:
                    transactions.append(record)
        except Exception as e:
            pass
        
        return transactions
    
    def _parse_invoice(self, file_path: str) -> List[Dict]:
        """解析发票文件（PDF/图片）
        
        注：实际使用时需要集成OCR服务
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf' and HAS_PDFPLUMBER:
            # 尝试从PDF提取文本
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ''
                    for page in pdf.pages:
                        text += page.extract_text() or ''
                    
                    # 简单的正则提取（实际需要更复杂的逻辑）
                    invoice_data = {
                        'raw_text': text,
                        'file_path': file_path
                    }
                    
                    # 提取发票号码
                    match = re.search(r'发票号码[：:]\s*(\d+)', text)
                    if match:
                        invoice_data['invoice_no'] = match.group(1)
                    
                    # 提取金额
                    match = re.search(r'价税合计[：:]\s*[\￥¥]?\s*([\d,\.]+)', text)
                    if match:
                        invoice_data['total_amount'] = self._parse_amount(match.group(1))
                    
                    return [invoice_data]
            except Exception as e:
                return [{'error': str(e), 'file_path': file_path}]
        
        # 图片需要OCR
        if ext in ['.jpg', '.jpeg', '.png']:
            return [{
                'note': '图片发票需要OCR识别',
                'file_path': file_path,
                'requires_ocr': True
            }]
        
        return []
    
    def _parse_contract(self, file_path: str) -> List[Dict]:
        """解析合同文件
        
        注：实际使用时需要集成OCR或更复杂的解析逻辑
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf' and HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ''
                    for page in pdf.pages:
                        text += page.extract_text() or ''
                    
                    return [{
                        'raw_text': text[:2000],  # 只保留前2000字符
                        'file_path': file_path
                    }]
            except Exception as e:
                return [{'error': str(e), 'file_path': file_path}]
        
        return [{'note': '需要解析', 'file_path': file_path}]
    
    def list_archives(self, year_month: str = None) -> List[Dict]:
        """列出归档文件
        
        Args:
            year_month: 年月筛选，格式 '2024-01'
        """
        archives = []
        
        if year_month:
            dirs = [self.archive_dir / year_month]
        else:
            dirs = [d for d in self.archive_dir.iterdir() if d.is_dir()]
        
        for dir_path in dirs:
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    # 解析文件名
                    name_parts = file_path.stem.split('_')
                    archives.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'type': name_parts[0] if name_parts else 'unknown',
                        'size': file_path.stat().st_size,
                        'mtime': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return archives


def main():
    """命令行测试"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python file_parser.py <文件路径>")
        print("\n支持的文件类型:")
        for file_type, config in FileParser.FILE_TYPES.items():
            print(f"  {file_type}: {config['description']} - {config['extensions']}")
        return
    
    file_path = sys.argv[1]
    parser = FileParser()
    
    print(f"\n处理文件: {file_path}")
    print("-" * 50)
    
    result = parser.process_uploaded_file(file_path)
    
    print(f"文件类型: {result['file_type']}")
    print(f"识别置信度: {result['confidence']:.2%}")
    print(f"解析数据条数: {result['data_count']}")
    print(f"归档路径: {result['archive_path']}")
    
    if result['data']:
        print("\n解析数据预览:")
        for i, item in enumerate(result['data'][:3]):
            print(f"  [{i+1}] {item}")


if __name__ == '__main__':
    main()
