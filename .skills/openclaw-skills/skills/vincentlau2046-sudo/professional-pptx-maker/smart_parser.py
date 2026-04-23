#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smart Parser for Professional PPTX Maker
Automatically detects structured data, tables, metrics, and trends from input content
"""

import re
import json
from typing import Dict, List, Any, Optional

class SmartParser:
    """Intelligent content parser that extracts structured data for professional presentations."""
    
    def __init__(self):
        self.content_type = None
        self.extracted_data = {}
        
    def parse_content(self, content: str) -> Dict[str, Any]:
        """
        Parse input content and extract structured data for professional presentation generation.
        
        Args:
            content (str): Input content (Markdown, plain text, or structured format)
            
        Returns:
            Dict containing extracted tables, charts, insights, and layout strategy
        """
        # Clean and normalize content
        cleaned_content = self._clean_content(content)
        
        # Detect content type
        self.content_type = self._detect_content_type(cleaned_content)
        
        # Extract all structured data
        extracted_data = {
            'content_type': self.content_type,
            'title': self._extract_title(cleaned_content),
            'tables': self._extract_tables(cleaned_content),
            'metrics': self._extract_key_metrics(cleaned_content),
            'trends': self._extract_trends(cleaned_content),
            'sections': self._extract_sections(cleaned_content),
            'insights': [],
            'layout_strategy': self._determine_layout_strategy()
        }
        
        # Generate professional insights based on extracted data
        extracted_data['insights'] = self._generate_insights(extracted_data)
        
        return extracted_data
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize input content."""
        # Remove extra whitespace and normalize line endings
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content.strip()
    
    def _detect_content_type(self, content: str) -> str:
        """Detect the type of content to determine appropriate processing strategy."""
        content_lower = content.lower()
        
        # Financial report detection
        financial_keywords = ['财报', '财务', '营收', '净利润', '毛利率', '现金流', '财年']
        if any(keyword in content_lower for keyword in financial_keywords):
            return 'financial_report'
        
        # Technical analysis detection  
        tech_keywords = ['架构', '技术', '性能', '对比', '分析', '系统', '平台']
        if any(keyword in content_lower for keyword in tech_keywords):
            return 'technical_analysis'
            
        # Market research detection
        market_keywords = ['市场', '趋势', '竞争', '份额', '用户', '需求']
        if any(keyword in content_lower for keyword in market_keywords):
            return 'market_research'
            
        return 'general_presentation'
    
    def _extract_title(self, content: str) -> str:
        """Extract presentation title from content."""
        # Look for H1 heading (# Title)
        h1_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Look for first line if no H1
        lines = content.split('\n')
        if lines:
            first_line = lines[0].strip()
            if first_line and not first_line.startswith(('#', '-', '*', '|')):
                return first_line
        
        return "Professional Presentation"
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract Markdown tables and convert to structured format."""
        tables = []
        
        # Find all Markdown tables (pipes with headers)
        table_pattern = r'(\|(?:[^\n]*\|)+\n\|(?:[-:\s|]+\|)+\n(?:\|(?:[^\n]*\|)+\n)+)'
        matches = re.finditer(table_pattern, content)
        
        for match in matches:
            table_text = match.group(1)
            table_data = self._parse_markdown_table(table_text)
            if table_data:
                tables.append({
                    'type': 'markdown_table',
                    'data': table_data,
                    'suggested_chart': self._suggest_chart_for_table(table_data)
                })
        
        return tables
    
    def _parse_markdown_table(self, table_text: str) -> Optional[List[List[str]]]:
        """Parse Markdown table into 2D array."""
        lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
        
        if len(lines) < 3:
            return None
            
        # Parse header
        header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        
        # Skip separator line (lines[1])
        data_rows = []
        for line in lines[2:]:
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(row) == len(header):
                data_rows.append(row)
        
        if not data_rows:
            return None
            
        return [header] + data_rows
    
    def _suggest_chart_for_table(self, table_data: List[List[str]]) -> str:
        """Suggest appropriate chart type based on table structure."""
        if not table_data or len(table_data) < 2:
            return 'none'
            
        header = table_data[0]
        first_row = table_data[1]
        
        # Check for time series data (quarters, months, years)
        time_indicators = ['q1', 'q2', 'q3', 'q4', '季度', '月', '年', '202', '2025', '2026']
        if any(indicator in str(cell).lower() for indicator in time_indicators for cell in header):
            return 'line_chart'
            
        # Check for percentage data
        if any('%' in str(cell) for row in table_data[1:] for cell in row):
            # If it's composition data (sums to ~100%)
            if len(table_data) == 2:  # Single row of percentages
                try:
                    percentages = [float(str(cell).replace('%', '').replace('+', '')) 
                                 for cell in table_data[1] if '%' in str(cell)]
                    if len(percentages) > 1 and abs(sum(percentages) - 100) < 10:
                        return 'pie_chart'
                except ValueError:
                    pass
            return 'column_chart'
            
        # Check for comparison data (multiple numeric columns)
        numeric_columns = 0
        for i, col in enumerate(header[1:], 1):
            try:
                float(str(table_data[1][i]).replace(',', '').replace('$', ''))
                numeric_columns += 1
            except (ValueError, IndexError):
                continue
                
        if numeric_columns >= 2:
            return 'column_chart'
            
        return 'none'
    
    def _extract_key_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key financial or performance metrics from content."""
        metrics = {}
        
        if self.content_type == 'financial_report':
            # Extract financial metrics using regex patterns
            patterns = {
                'revenue': r'(?:总营收|营收|收入)[：:]\s*([0-9,\.]+)',
                'profit': r'(?:净利润|利润)[：:]\s*([0-9,\.]+)',
                'margin': r'(?:毛利率|毛利)[：:]\s*([0-9,\.]+%)',
                'cash_flow': r'(?:现金流|现金)[：:]\s*([0-9,\.]+)',
                'growth_rate': r'(?:增长|同比)[：:]\s*(\+?[0-9,\.]+%)'
            }
            
            for metric_name, pattern in patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    # Take the first match and clean it
                    value = matches[0].replace(',', '')
                    try:
                        if '%' in value:
                            metrics[metric_name] = float(value.replace('%', ''))
                        else:
                            metrics[metric_name] = float(value)
                    except ValueError:
                        metrics[metric_name] = value
                        
        return metrics
    
    def _extract_trends(self, content: str) -> Dict[str, Any]:
        """Extract trend data for chart generation."""
        trends = {}
        
        if self.content_type == 'financial_report':
            # Look for quarterly data patterns
            quarterly_patterns = [
                r'(?:q1|q2|q3|q4|第一季度|第二季度|第三季度|第四季度).*?([0-9,\.]+)',
                r'(?:2025|2026|2027).*?([0-9,\.]+)'
            ]
            
            # This is a simplified approach - in practice, we'd need more sophisticated parsing
            # For now, we'll rely on table extraction for trend data
            pass
            
        return trends
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract section structure from content."""
        sections = []
        
        # Split by H2 headings (## Section)
        section_pattern = r'##\s+(.+?)\n((?:(?!##\s+).)*?)'
        matches = re.finditer(section_pattern, content, re.DOTALL)
        
        for match in matches:
            title = match.group(1).strip()
            content_section = match.group(2).strip()
            
            # Extract bullet points
            bullet_points = []
            for line in content_section.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    bullet_points.append(line[2:].strip())
                    
            sections.append({
                'title': title,
                'content': content_section,
                'bullet_points': bullet_points
            })
            
        return sections
    
    def _determine_layout_strategy(self) -> str:
        """Determine the best layout strategy based on content type."""
        strategies = {
            'financial_report': 'charts_and_tables_with_insights',
            'technical_analysis': 'architecture_diagrams_with_comparison',
            'market_research': 'trend_charts_with_competitive_analysis',
            'general_presentation': 'content_focused_with_key_points'
        }
        
        return strategies.get(self.content_type, 'content_focused_with_key_points')
    
    def _generate_insights(self, extracted_data: Dict[str, Any]) -> List[str]:
        """Generate professional insights based on extracted data."""
        insights = []
        
        if self.content_type == 'financial_report':
            metrics = extracted_data.get('metrics', {})
            
            # Revenue insight
            if 'revenue' in metrics and 'growth_rate' in metrics:
                insights.append(f"营收规模突破{metrics['revenue']:,.0f}亿，同比增长{metrics['growth_rate']}%，展现强劲增长势头")
            
            # Profit margin insight  
            if 'margin' in metrics:
                if metrics['margin'] > 70:
                    insights.append(f"毛利率高达{metrics['margin']:.1f}%，盈利能力处于行业领先水平")
                elif metrics['margin'] > 60:
                    insights.append(f"毛利率达到{metrics['margin']:.1f}%，盈利能力稳健")
                    
            # Cash flow insight
            if 'cash_flow' in metrics:
                insights.append(f"现金流充沛，为战略扩张和股东回报提供坚实基础")
                
        elif self.content_type == 'technical_analysis':
            insights.append("技术架构设计合理，性能指标达到行业领先水平")
            insights.append("核心技术创新驱动业务增长，竞争优势明显")
            
        elif self.content_type == 'market_research':
            insights.append("市场趋势明确，用户需求持续增长")
            insights.append("竞争格局清晰，市场份额有望进一步提升")
            
        # Add general insights if none generated
        if not insights:
            insights.append("核心指标表现优异，业务发展前景良好")
            
        return insights[:5]  # Limit to top 5 insights

def test_smart_parser():
    """Test the smart parser with sample content."""
    test_content = """
# 英伟达2026财年财报深度分析

## 财报数据整体分析
- 总营收：2159.38亿美元（同比+65.5%）
- GAAP净利润：1200.67亿美元（同比+64.8%）
- 毛利率：71.1%（创历史新高）

## 分季度财务趋势
| 季度 | 总营收 | 净利润 | 毛利率 |
|------|--------|--------|--------|
| Q1 | 440.62 | 187.75 | 70.1% |
| Q2 | 467.00 | 264.22 | 72.4% |
| Q3 | 570.06 | 319.10 | 73.4% |
| Q4 | 681.27 | 429.60 | 75.0% |
"""
    
    parser = SmartParser()
    result = parser.parse_content(test_content)
    
    print("Content Type:", result['content_type'])
    print("Title:", result['title'])
    print("Tables found:", len(result['tables']))
    print("Metrics:", result['metrics'])
    print("Insights:", result['insights'])
    
    return result

if __name__ == "__main__":
    test_smart_parser()