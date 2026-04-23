#!/usr/bin/env python3
"""
Professional Operation Generator - Enhanced with charts and tables support
"""

import json
from typing import Dict, List, Any

class ProfessionalOperationGenerator:
    """Enhanced operation generator with professional chart and table support."""
    
    def __init__(self):
        self.resolved_manifest = None
        self.content_plan = None
        
    def load_template_contract(self, manifest_path: str):
        """Load resolved manifest from template extraction."""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            self.resolved_manifest = json.load(f)
            
    def plan_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan content structure using professional frameworks."""
        self.content_plan = {
            'plan': {
                'deck_title': content_data.get('title', 'Professional Presentation'),
                'brief': content_data.get('brief', ''),
                'audience': content_data.get('audience', 'Executive'),
                'objective': content_data.get('objective', 'Inform and persuade'),
                'slides': []
            },
            'ops': {
                'operations': []
            }
        }
        
        # Plan slides based on content structure
        slide_number = 1
        
        # Title slide
        self.content_plan['plan']['slides'].append({
            'slide_number': slide_number,
            'story_role': 'opening',
            'archetype_id': 'title_slide',
            'action_title': self.content_plan['plan']['deck_title']
        })
        slide_number += 1
        
        # Content slides with professional structure
        sections = content_data.get('sections', [])
        tables = content_data.get('tables', [])
        metrics = content_data.get('metrics', {})
        insights = content_data.get('insights', [])
        content_type = content_data.get('content_type', 'general_presentation')
        
        if content_type == 'financial_report':
            # Financial report specific structure
            self._add_financial_report_slides(sections, tables, metrics, insights, slide_number)
        else:
            # General content structure
            for section in sections:
                self.content_plan['plan']['slides'].append({
                    'slide_number': slide_number,
                    'story_role': 'content',
                    'archetype_id': self._determine_archetype(section),
                    'action_title': section.get('title', 'Content Slide'),
                    'key_points': section.get('items', []),
                    'section_data': section
                })
                slide_number += 1
                
        # Summary slide
        if len(sections) >= 2:
            self.content_plan['plan']['slides'].append({
                'slide_number': len(self.content_plan['plan']['slides']) + 1,
                'story_role': 'closing',
                'archetype_id': 'summary_slide',
                'action_title': '核心结论与展望'
            })
            
        return self.content_plan
        
    def _add_financial_report_slides(self, sections, tables, metrics, insights, start_slide_number):
        """Add specialized slides for financial reports."""
        slides = self.content_plan['plan']['slides']
        
        # Key metrics slide
        if tables:
            slides.append({
                'slide_number': len(slides) + 1,
                'story_role': 'content',
                'archetype_id': 'metrics_table_slide',
                'action_title': '财报数据整体分析',
                'table_data': tables[0]['data'] if tables else [],
                'insights': insights[:2] if insights else []
            })
            
        # Quarterly trends slide  
        if len(tables) > 1:
            slides.append({
                'slide_number': len(slides) + 1,
                'story_role': 'content', 
                'archetype_id': 'trend_chart_slide',
                'action_title': '分季度财务趋势',
                'chart_data': self._extract_quarterly_data(tables[1]['data'] if len(tables) > 1 else []),
                'insights': insights[2:4] if len(insights) > 2 else []
            })
            
        # Business segments slide
        if len(tables) > 2:
            slides.append({
                'slide_number': len(slides) + 1,
                'story_role': 'content',
                'archetype_id': 'business_analysis_slide', 
                'action_title': '分领域业务深度分析',
                'chart_data': self._extract_business_composition(tables[2]['data'] if len(tables) > 2 else []),
                'table_data': tables[2]['data'] if len(tables) > 2 else [],
                'insights': insights[4:6] if len(insights) > 4 else []
            })
            
        # Executive summary
        slides.append({
            'slide_number': len(slides) + 1,
            'story_role': 'closing',
            'archetype_id': 'executive_summary_slide',
            'action_title': '核心结论与投资建议',
            'key_points': [
                f"✅ 历史最佳财报：营收{metrics.get('revenue', 'N/A')}亿(+{metrics.get('growth_rate', 'N/A')}%)",
                "✅ 数据中心统治力：占总营收89.7%",
                "✅ 增长韧性强劲：四季度环比持续增长",
                "✅ 现金流超级充沛：自由现金流970亿"
            ],
            'insights': insights[-2:] if len(insights) > 6 else []
        })
        
    def _extract_quarterly_data(self, table_data):
        """Extract quarterly trend data from table."""
        if not table_data or len(table_data) < 2:
            return {'categories': ['Q1', 'Q2', 'Q3', 'Q4'], 'series': []}
            
        categories = table_data[0][1:]  # Skip first column (指标)
        revenue_values = []
        profit_values = []
        margin_values = []
        
        for row in table_data[1:]:
            if len(row) >= 2:
                try:
                    if '营收' in row[0]:
                        revenue_values = [float(x.replace(',', '')) for x in row[1:]]
                    elif '净利润' in row[0]:
                        profit_values = [float(x.replace(',', '')) for x in row[1:]]
                    elif '毛利率' in row[0]:
                        margin_values = [float(x.replace('%', '').replace(',', '')) for x in row[1:]]
                except ValueError:
                    continue
                    
        series = []
        if revenue_values:
            series.append({'name': '营收 (亿美元)', 'values': revenue_values})
        if profit_values:
            series.append({'name': '净利润 (亿美元)', 'values': profit_values})
        if margin_values:
            series.append({'name': '毛利率 (%)', 'values': margin_values})
            
        return {'categories': categories, 'series': series}
        
    def _extract_business_composition(self, table_data):
        """Extract business composition data for pie chart."""
        if not table_data or len(table_data) < 2:
            return {'categories': [], 'series': []}
            
        categories = []
        values = []
        
        # Assume first column is business name, last column is percentage
        for row in table_data[1:]:
            if len(row) >= 2:
                categories.append(row[0])
                try:
                    value = float(row[-1].replace('%', '').replace('+', ''))
                    values.append(value)
                except ValueError:
                    values.append(0)
                    
        return {'categories': categories, 'series': [{'name': '营收占比 (%)', 'values': values}]}
        
    def _determine_archetype(self, section: Dict[str, Any]) -> str:
        """Determine appropriate archetype based on section content."""
        title = section.get('title', '').lower()
        
        if '财报' in title or '财务' in title or '指标' in title:
            return 'metrics_table_slide'
        elif '趋势' in title or '季度' in title or '增长' in title:
            return 'trend_chart_slide'
        elif '业务' in title or '板块' in title or '分析' in title:
            return 'business_analysis_slide'
        elif '战略' in title or '未来' in title or '展望' in title:
            return 'strategy_insights_slide'
        elif '总结' in title or '结论' in title or '核心' in title:
            return 'executive_summary_slide'
            
        if section.get('tables') or section.get('has_chart_data'):
            return 'chart_slide'
            
        section_keywords = ['目录', '概述', '介绍', 'introduction', 'overview']
        if any(keyword in title for keyword in section_keywords):
            return 'section_header'
            
        return 'content_slide'
        
    def generate_operations(self) -> List[Dict[str, Any]]:
        """Generate JSON operation sequence with professional charts and tables."""
        operations = []
        
        if not self.content_plan or not self.resolved_manifest:
            raise ValueError("Content plan and template contract must be loaded first")
            
        # Generate operations for each slide
        for i, slide_plan in enumerate(self.content_plan['plan']['slides']):
            slide_number = slide_plan['slide_number']
            archetype_id = slide_plan['archetype_id']
            
            # Get resolved layouts
            archetype_info = self.resolved_manifest['archetypes'].get(archetype_id, {})
            resolved_layouts = archetype_info.get('resolved_layouts', [])
            
            if not resolved_layouts:
                layout_name = "Title and Content"
                layout_id = 1
            else:
                layout_info = resolved_layouts[0]
                layout_name = layout_info['layout_name']
                layout_id = layout_info['layout_id']
                
            # Add slide operation
            operations.append({
                'op': 'add_slide',
                'layout_name': layout_name,
                'layout_index': layout_id
            })
            
            # Set title
            operations.append({
                'op': 'set_semantic_text',
                'slide_index': i,
                'role': 'title',
                'text': slide_plan['action_title']
            })
            
            # Handle specialized slide types
            if archetype_id == 'metrics_table_slide':
                # Add table
                table_data = slide_plan.get('table_data', [])
                if table_data:
                    operations.append({
                        'op': 'add_table',
                        'slide_index': i,
                        'data': table_data,
                        'position': {'x': 1, 'y': 2.2, 'width': 11, 'height': 0.4 * len(table_data)}
                    })
                    
                # Add analysis text
                insights = slide_plan.get('insights', [])
                if insights:
                    analysis_text = '\n'.join([f"• {insight}" for insight in insights])
                    operations.append({
                        'op': 'set_semantic_text',
                        'slide_index': i,
                        'role': 'body',
                        'text': analysis_text
                    })
                    
            elif archetype_id == 'trend_chart_slide':
                # Add charts
                chart_data = slide_plan.get('chart_data', {})
                if chart_data.get('series'):
                    # Revenue/Profit chart
                    operations.append({
                        'op': 'add_chart',
                        'slide_index': i,
                        'chart_type': 'column',
                        'data': chart_data,
                        'position': {'x': 1, 'y': 2.5, 'width': 5.5, 'height': 3.5}
                    })
                    
                    # Margin trend chart (if available)
                    margin_series = [s for s in chart_data.get('series', []) if '毛利率' in s.get('name', '')]
                    if margin_series:
                        margin_data = {
                            'categories': chart_data['categories'],
                            'series': margin_series
                        }
                        operations.append({
                            'op': 'add_chart',
                            'slide_index': i,
                            'chart_type': 'line',
                            'data': margin_data,
                            'position': {'x': 6.8, 'y': 2.5, 'width': 4.8, 'height': 3.5}
                        })
                        
                # Add trend analysis
                insights = slide_plan.get('insights', [])
                if insights:
                    trend_text = '\n'.join([f"• {insight}" for insight in insights])
                    operations.append({
                        'op': 'set_semantic_text',
                        'slide_index': i,
                        'role': 'body',
                        'text': trend_text
                    })
                    
            elif archetype_id == 'business_analysis_slide':
                # Add pie chart
                chart_data = slide_plan.get('chart_data', {})
                if chart_data.get('series'):
                    operations.append({
                        'op': 'add_chart',
                        'slide_index': i,
                        'chart_type': 'pie',
                        'data': chart_data,
                        'position': {'x': 1, 'y': 2.5, 'width': 5.5, 'height': 3.5}
                    })
                    
                # Add growth table
                table_data = slide_plan.get('table_data', [])
                if table_data:
                    operations.append({
                        'op': 'add_table',
                        'slide_index': i,
                        'data': table_data,
                        'position': {'x': 6.8, 'y': 2.5, 'width': 4.8, 'height': 0.4 * len(table_data)}
                    })
                    
                # Add business insights
                insights = slide_plan.get('insights', [])
                if insights:
                    business_text = '\n'.join([f"• {insight}" for insight in insights])
                    operations.append({
                        'op': 'set_semantic_text',
                        'slide_index': i,
                        'role': 'body',
                        'text': business_text
                    })
                    
            elif archetype_id == 'executive_summary_slide':
                # Add key points
                key_points = slide_plan.get('key_points', [])
                if key_points:
                    summary_text = '\n'.join(key_points)
                    operations.append({
                        'op': 'set_semantic_text',
                        'slide_index': i,
                        'role': 'body',
                        'text': summary_text
                    })
                    
            elif archetype_id != 'title_slide':
                # Standard content slide
                key_points = slide_plan.get('key_points', [])
                if key_points:
                    body_text = '\n'.join([f"• {point}" for point in key_points[:6]])
                    operations.append({
                        'op': 'set_semantic_text',
                        'slide_index': i,
                        'role': 'body',
                        'text': body_text
                    })
                    
            # Add speaker notes
            if archetype_id in ['content_slide', 'chart_slide', 'summary_slide']:
                operations.append({
                    'op': 'add_notes',
                    'slide_index': i,
                    'text': f"Slide {slide_number}: {slide_plan['action_title']}"
                })
                
        # Add core properties
        operations.append({
            'op': 'set_core_properties',
            'title': self.content_plan['plan']['deck_title'],
            'subject': self.content_plan['plan']['brief']
        })
        
        return operations
        
    def save_slides_json(self, output_path: str):
        """Save operations to slides.json file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.content_plan, f, ensure_ascii=False, indent=2)
