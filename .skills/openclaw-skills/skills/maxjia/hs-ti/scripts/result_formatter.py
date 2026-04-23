import json
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class ResultFormatter:
    """结果格式化器"""
    
    @staticmethod
    def format_text(result: Dict[str, Any], language: str = 'en') -> str:
        """格式化为文本"""
        if 'error' in result:
            return f"Error: {result['error']}"
        
        data = result.get('data', {})
        response_time = result.get('response_time_ms', 0)
        
        texts = {
            'en': {
                'result': 'Result',
                'threat_type': 'Threat Type',
                'credibility': 'Credibility',
                'response_time': 'Response Time',
                'malicious': 'Malicious',
                'benign': 'Benign',
                'unknown': 'Unknown'
            },
            'cn': {
                'result': '结果',
                'threat_type': '威胁类型',
                'credibility': '可信度',
                'response_time': '响应时间',
                'malicious': '恶意',
                'benign': '良性',
                'unknown': '未知'
            }
        }
        
        t = texts.get(language, texts['en'])
        
        result_str = data.get('result', 'unknown')
        if result_str == 'malicious':
            result_str = t['malicious']
        elif result_str == 'benign':
            result_str = t['benign']
        else:
            result_str = t['unknown']
        
        output = [
            f"{t['result']}: {result_str}",
            f"{t['threat_type']}: {', '.join(data.get('threat_type', []))}",
            f"{t['credibility']}: {data.get('credibility', 0)}",
            f"{t['response_time']}: {response_time}ms"
        ]
        
        return '\n'.join(output)
    
    @staticmethod
    def format_json(result: Dict[str, Any]) -> str:
        """格式化为JSON"""
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @staticmethod
    def format_table(results: List[Dict[str, Any]], language: str = 'en') -> str:
        """格式化为表格"""
        if not results:
            return "No results"
        
        texts = {
            'en': {
                'ioc': 'IOC',
                'type': 'Type',
                'result': 'Result',
                'threat_type': 'Threat Type',
                'credibility': 'Credibility',
                'response_time': 'Response Time (ms)'
            },
            'cn': {
                'ioc': 'IOC',
                'type': '类型',
                'result': '结果',
                'threat_type': '威胁类型',
                'credibility': '可信度',
                'response_time': '响应时间(ms)'
            }
        }
        
        t = texts.get(language, texts['en'])
        
        headers = [t['ioc'], t['type'], t['result'], t['threat_type'], 
                  t['credibility'], t['response_time']]
        
        rows = []
        for item in results:
            ioc = item.get('ioc', '')
            ioc_type = item.get('ioc_type', '')
            result_data = item.get('result', {})
            data = result_data.get('data', {})
            
            result_str = data.get('result', 'unknown')
            threat_type = ', '.join(data.get('threat_type', []))
            credibility = data.get('credibility', 0)
            response_time = item.get('response_time_ms', 0)
            
            rows.append([ioc, ioc_type, result_str, threat_type, 
                        str(credibility), str(response_time)])
        
        col_widths = [
            max(len(str(row[i])) for row in [headers] + rows)
            for i in range(len(headers))
        ]
        
        separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
        
        table_lines = [separator]
        
        header_line = '|' + '|'.join(
            f' {headers[i].ljust(col_widths[i])} ' 
            for i in range(len(headers))
        ) + '|'
        table_lines.append(header_line)
        table_lines.append(separator)
        
        for row in rows:
            row_line = '|' + '|'.join(
                f' {str(row[i]).ljust(col_widths[i])} ' 
                for i in range(len(row))
            ) + '|'
            table_lines.append(row_line)
        
        table_lines.append(separator)
        
        return '\n'.join(table_lines)
    
    @staticmethod
    def format_batch_results(batch_result: Dict[str, Any], language: str = 'en') -> str:
        """格式化批量查询结果"""
        texts = {
            'en': {
                'query_results': 'Query Results',
                'batch_stats': 'Batch Statistics',
                'total_stats': 'Total Statistics',
                'avg': 'Average',
                'max': 'Maximum',
                'min': 'Minimum',
                'median': 'Median',
                'total_calls': 'Total Calls'
            },
            'cn': {
                'query_results': '查询结果',
                'batch_stats': '批量统计',
                'total_stats': '累计统计',
                'avg': '平均',
                'max': '最大',
                'min': '最小',
                'median': '中位数',
                'total_calls': '总调用次数'
            }
        }
        
        t = texts.get(language, texts['en'])
        
        output = []
        
        results = batch_result.get('results', [])
        if results:
            output.append(f"\n{t['query_results']}:")
            output.append(ResultFormatter.format_table(results, language))
        
        batch_stats = batch_result.get('batch_stats', {})
        if batch_stats:
            output.append(f"\n{t['batch_stats']}:")
            output.append(f"  {t['avg']}: {batch_stats.get('batch_avg_ms', 0)}ms")
            output.append(f"  {t['max']}: {batch_stats.get('batch_max_ms', 0)}ms")
            output.append(f"  {t['min']}: {batch_stats.get('batch_min_ms', 0)}ms")
            output.append(f"  {t['median']}: {batch_stats.get('batch_median_ms', 0)}ms")
        
        total_stats = batch_result.get('total_stats', {})
        if total_stats:
            output.append(f"\n{t['total_stats']}:")
            output.append(f"  {t['total_calls']}: {total_stats.get('total_calls', 0)}")
            output.append(f"  {t['avg']}: {total_stats.get('total_avg_ms', 0)}ms")
            output.append(f"  {t['max']}: {total_stats.get('total_max_ms', 0)}ms")
            output.append(f"  {t['min']}: {total_stats.get('total_min_ms', 0)}ms")
            output.append(f"  {t['median']}: {total_stats.get('total_median_ms', 0)}ms")
        
        return '\n'.join(output)


class ResultExporter:
    """结果导出器"""
    
    @staticmethod
    def export_csv(results: List[Dict[str, Any]], filename: str, 
                   language: str = 'en') -> None:
        """导出为CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            texts = {
                'en': ['IOC', 'Type', 'Result', 'Threat Type', 
                       'Credibility', 'Response Time (ms)', 'Success', 'Error'],
                'cn': ['IOC', '类型', '结果', '威胁类型', 
                       '可信度', '响应时间(ms)', '成功', '错误']
            }
            
            headers = texts.get(language, texts['en'])
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for result in results:
                ioc = result.get('ioc', '')
                ioc_type = result.get('ioc_type', '')
                result_data = result.get('result', {})
                data = result_data.get('data', {})
                
                writer.writerow([
                    ioc,
                    ioc_type,
                    data.get('result', ''),
                    str(data.get('threat_type', [])),
                    data.get('credibility', ''),
                    result.get('response_time_ms', ''),
                    result.get('success', ''),
                    result.get('error', '')
                ])
    
    @staticmethod
    def export_json(results: List[Dict[str, Any]], filename: str, 
                     batch_stats: Optional[Dict] = None,
                     total_stats: Optional[Dict] = None) -> None:
        """导出为JSON"""
        export_data = {
            'export_time': datetime.now().isoformat(),
            'results': results
        }
        
        if batch_stats:
            export_data['batch_stats'] = batch_stats
        
        if total_stats:
            export_data['total_stats'] = total_stats
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_html(results: List[Dict[str, Any]], filename: str, 
                    language: str = 'en', 
                    batch_stats: Optional[Dict] = None,
                    total_stats: Optional[Dict] = None) -> None:
        """导出为HTML报告"""
        texts = {
            'en': {
                'title': 'Hillstone Threat Intelligence Report',
                'export_time': 'Export Time',
                'query_results': 'Query Results',
                'batch_stats': 'Batch Statistics',
                'total_stats': 'Total Statistics',
                'ioc': 'IOC',
                'type': 'Type',
                'result': 'Result',
                'threat_type': 'Threat Type',
                'credibility': 'Credibility',
                'response_time': 'Response Time (ms)',
                'success': 'Success',
                'error': 'Error',
                'avg': 'Average',
                'max': 'Maximum',
                'min': 'Minimum',
                'median': 'Median',
                'total_calls': 'Total Calls'
            },
            'cn': {
                'title': '云瞻威胁情报报告',
                'export_time': '导出时间',
                'query_results': '查询结果',
                'batch_stats': '批量统计',
                'total_stats': '累计统计',
                'ioc': 'IOC',
                'type': '类型',
                'result': '结果',
                'threat_type': '威胁类型',
                'credibility': '可信度',
                'response_time': '响应时间(ms)',
                'success': '成功',
                'error': '错误',
                'avg': '平均',
                'max': '最大',
                'min': '最小',
                'median': '中位数',
                'total_calls': '总调用次数'
            }
        }
        
        t = texts.get(language, texts['en'])
        
        html = f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .malicious {{
            color: #d32f2f;
            font-weight: bold;
        }}
        .benign {{
            color: #388e3c;
            font-weight: bold;
        }}
        .unknown {{
            color: #757575;
        }}
        .stats {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .export-time {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{t['title']}</h1>
        <p class="export-time">{t['export_time']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>{t['query_results']}</h2>
        <table>
            <thead>
                <tr>
                    <th>{t['ioc']}</th>
                    <th>{t['type']}</th>
                    <th>{t['result']}</th>
                    <th>{t['threat_type']}</th>
                    <th>{t['credibility']}</th>
                    <th>{t['response_time']}</th>
                    <th>{t['success']}</th>
                    <th>{t['error']}</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in results:
            ioc = result.get('ioc', '')
            ioc_type = result.get('ioc_type', '')
            result_data = result.get('result', {})
            data = result_data.get('data', {})
            
            result_str = data.get('result', 'unknown')
            result_class = result_str
            threat_type = ', '.join(data.get('threat_type', []))
            credibility = data.get('credibility', 0)
            response_time = result.get('response_time_ms', 0)
            success = result.get('success', False)
            error = result.get('error', '')
            
            html += f"""                <tr>
                    <td>{ioc}</td>
                    <td>{ioc_type}</td>
                    <td class="{result_class}">{result_str}</td>
                    <td>{threat_type}</td>
                    <td>{credibility}</td>
                    <td>{response_time}</td>
                    <td>{'Yes' if success else 'No'}</td>
                    <td>{error}</td>
                </tr>
"""
        
        html += """            </tbody>
        </table>
"""
        
        if batch_stats:
            html += f"""
        <h2>{t['batch_stats']}</h2>
        <div class="stats">
            <p><strong>{t['avg']}:</strong> {batch_stats.get('batch_avg_ms', 0)}ms</p>
            <p><strong>{t['max']}:</strong> {batch_stats.get('batch_max_ms', 0)}ms</p>
            <p><strong>{t['min']}:</strong> {batch_stats.get('batch_min_ms', 0)}ms</p>
            <p><strong>{t['median']}:</strong> {batch_stats.get('batch_median_ms', 0)}ms</p>
        </div>
"""
        
        if total_stats:
            html += f"""
        <h2>{t['total_stats']}</h2>
        <div class="stats">
            <p><strong>{t['total_calls']}:</strong> {total_stats.get('total_calls', 0)}</p>
            <p><strong>{t['avg']}:</strong> {total_stats.get('total_avg_ms', 0)}ms</p>
            <p><strong>{t['max']}:</strong> {total_stats.get('total_max_ms', 0)}ms</p>
            <p><strong>{t['min']}:</strong> {total_stats.get('total_min_ms', 0)}ms</p>
            <p><strong>{t['median']}:</strong> {total_stats.get('total_median_ms', 0)}ms</p>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    @staticmethod
    def export_markdown(results: List[Dict[str, Any]], filename: str, 
                        language: str = 'en',
                        batch_stats: Optional[Dict] = None,
                        total_stats: Optional[Dict] = None) -> None:
        """导出为Markdown报告"""
        texts = {
            'en': {
                'title': '# Hillstone Threat Intelligence Report',
                'export_time': 'Export Time',
                'query_results': '## Query Results',
                'batch_stats': '## Batch Statistics',
                'total_stats': '## Total Statistics',
                'ioc': 'IOC',
                'type': 'Type',
                'result': 'Result',
                'threat_type': 'Threat Type',
                'credibility': 'Credibility',
                'response_time': 'Response Time (ms)',
                'success': 'Success',
                'error': 'Error',
                'avg': 'Average',
                'max': 'Maximum',
                'min': 'Minimum',
                'median': 'Median',
                'total_calls': 'Total Calls'
            },
            'cn': {
                'title': '# 云瞻威胁情报报告',
                'export_time': '导出时间',
                'query_results': '## 查询结果',
                'batch_stats': '## 批量统计',
                'total_stats': '## 累计统计',
                'ioc': 'IOC',
                'type': '类型',
                'result': '结果',
                'threat_type': '威胁类型',
                'credibility': '可信度',
                'response时间': '响应时间(ms)',
                'success': '成功',
                'error': '错误',
                'avg': '平均',
                'max': '最大',
                'min': '最小',
                'median': '中位数',
                'total_calls': '总调用次数'
            }
        }
        
        t = texts.get(language, texts['en'])
        
        markdown = f"""{t['title']}

**{t['export_time']}**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{t['query_results']}

| {t['ioc']} | {t['type']} | {t['result']} | {t['threat_type']} | {t['credibility']} | {t['response_time']} | {t['success']} | {t['error']} |
|-----------|------------|-------------|-------------------|------------------|---------------------|------------|------------|
"""
        
        for result in results:
            ioc = result.get('ioc', '')
            ioc_type = result.get('ioc_type', '')
            result_data = result.get('result', {})
            data = result_data.get('data', {})
            
            result_str = data.get('result', 'unknown')
            threat_type = ', '.join(data.get('threat_type', []))
            credibility = data.get('credibility', 0)
            response_time = result.get('response_time_ms', 0)
            success = result.get('success', False)
            error = result.get('error', '')
            
            markdown += f"| {ioc} | {ioc_type} | {result_str} | {threat_type} | {credibility} | {response_time} | {'Yes' if success else 'No'} | {error} |\n"
        
        if batch_stats:
            markdown += f"""
{t['batch_stats']}

- **{t['avg']}**: {batch_stats.get('batch_avg_ms', 0)}ms
- **{t['max']}**: {batch_stats.get('batch_max_ms', 0)}ms
- **{t['min']}**: {batch_stats.get('batch_min_ms', 0)}ms
- **{t['median']}**: {batch_stats.get('batch_median_ms', 0)}ms
"""
        
        if total_stats:
            markdown += f"""
{t['total_stats']}

- **{t['total_calls']}**: {total_stats.get('total_calls', 0)}
- **{t['avg']}**: {total_stats.get('total_avg_ms', 0)}ms
- **{t['max']}**: {total_stats.get('total_max_ms', 0)}ms
- **{t['min']}**: {total_stats.get('total_min_ms', 0)}ms
- **{t['median']}**: {total_stats.get('total_median_ms', 0)}ms
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
