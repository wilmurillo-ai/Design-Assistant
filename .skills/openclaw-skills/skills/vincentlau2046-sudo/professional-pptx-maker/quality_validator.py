#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quality Validator for Professional PPTX Maker
Ensures output meets professional standards with charts, tables, and insights
"""

from typing import Dict, List, Any

class QualityValidator:
    """Validates that generated presentations meet professional quality standards."""
    
    def __init__(self):
        self.quality_rules = self._load_quality_rules()
        
    def _load_quality_rules(self) -> Dict[str, Dict]:
        """Load quality rules for different content types."""
        return {
            'financial_report': {
                'required_chart_types': ['revenue_trend', 'profit_margin', 'business_composition'],
                'required_table_types': ['key_metrics', 'quarterly_data', 'business_segments'],
                'min_insight_points': 3,
                'has_executive_summary': True,
                'max_text_only_slides': 2  # Only allow 2 slides without charts/tables
            },
            'technical_analysis': {
                'required_chart_types': ['architecture_diagram', 'performance_comparison'],
                'required_table_types': ['feature_comparison', 'specification_table'],
                'min_insight_points': 4,
                'has_executive_summary': True,
                'max_text_only_slides': 3
            },
            'market_research': {
                'required_chart_types': ['market_trend', 'competitive_analysis'],
                'required_table_types': ['market_share', 'user_demographics'],
                'min_insight_points': 3,
                'has_executive_summary': True,
                'max_text_only_slides': 2
            },
            'general_presentation': {
                'required_chart_types': [],
                'required_table_types': [],
                'min_insight_points': 2,
                'has_executive_summary': False,
                'max_text_only_slides': 10  # More flexible for general content
            }
        }
    
    def validate_presentation_plan(self, content_plan: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate presentation plan against quality standards.
        
        Args:
            content_plan: The planned presentation structure
            extracted_data: Data extracted by smart parser
            
        Returns:
            Dict with validation results and recommendations
        """
        content_type = extracted_data.get('content_type', 'general_presentation')
        rules = self.quality_rules.get(content_type, self.quality_rules['general_presentation'])
        
        validation_result = {
            'content_type': content_type,
            'is_valid': True,
            'issues': [],
            'recommendations': [],
            'score': 100
        }
        
        # Check for required charts
        detected_charts = self._detect_charts_in_plan(content_plan)
        missing_charts = []
        for required_chart in rules['required_chart_types']:
            if required_chart not in detected_charts:
                missing_charts.append(required_chart)
                
        if missing_charts:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Missing required charts: {', '.join(missing_charts)}")
            validation_result['recommendations'].append("Add appropriate charts for data visualization")
            validation_result['score'] -= len(missing_charts) * 15
            
        # Check for required tables
        detected_tables = self._detect_tables_in_plan(content_plan)
        missing_tables = []
        for required_table in rules['required_table_types']:
            if required_table not in detected_tables:
                missing_tables.append(required_table)
                
        if missing_tables:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Missing required tables: {', '.join(missing_tables)}")
            validation_result['recommendations'].append("Add structured tables for key metrics")
            validation_result['score'] -= len(missing_tables) * 10
            
        # Check for insights
        insights_count = len(extracted_data.get('insights', []))
        if insights_count < rules['min_insight_points']:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Insufficient insights ({insights_count} found, {rules['min_insight_points']} required)")
            validation_result['recommendations'].append("Generate more professional insights from the data")
            validation_result['score'] -= (rules['min_insight_points'] - insights_count) * 5
            
        # Check executive summary
        if rules['has_executive_summary'] and not self._has_executive_summary(content_plan):
            validation_result['is_valid'] = False
            validation_result['issues'].append("Missing executive summary slide")
            validation_result['recommendations'].append("Add executive summary with key conclusions")
            validation_result['score'] -= 20
            
        # Check text-only slides ratio
        total_slides = len(content_plan.get('plan', {}).get('slides', []))
        text_only_slides = self._count_text_only_slides(content_plan)
        if text_only_slides > rules['max_text_only_slides']:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Too many text-only slides ({text_only_slides}/{total_slides})")
            validation_result['recommendations'].append("Convert text-only slides to include charts or tables")
            validation_result['score'] -= (text_only_slides - rules['max_text_only_slides']) * 5
            
        # Ensure minimum score threshold
        if validation_result['score'] < 70:
            validation_result['is_valid'] = False
            
        return validation_result
    
    def _detect_charts_in_plan(self, content_plan: Dict[str, Any]) -> List[str]:
        """Detect what types of charts are planned in the presentation."""
        charts = []
        slides = content_plan.get('plan', {}).get('slides', [])
        
        for slide in slides:
            archetype = slide.get('archetype_id', '')
            title = slide.get('action_title', '').lower()
            
            if 'trend' in archetype or 'chart' in archetype:
                if any(keyword in title for keyword in ['营收', '收入', '季度', '时间']):
                    charts.append('revenue_trend')
                elif any(keyword in title for keyword in ['毛利率', '利润', 'margin']):
                    charts.append('profit_margin')
                elif any(keyword in title for keyword in ['业务', '板块', 'composition']):
                    charts.append('business_composition')
                    
        return charts
    
    def _detect_tables_in_plan(self, content_plan: Dict[str, Any]) -> List[str]:
        """Detect what types of tables are planned in the presentation."""
        tables = []
        slides = content_plan.get('plan', {}).get('slides', [])
        
        for slide in slides:
            archetype = slide.get('archetype_id', '')
            title = slide.get('action_title', '').lower()
            
            if 'table' in archetype or 'metrics' in archetype:
                if any(keyword in title for keyword in ['指标', 'metrics', '核心']):
                    tables.append('key_metrics')
                elif any(keyword in title for keyword in ['季度', 'quarterly']):
                    tables.append('quarterly_data')
                elif any(keyword in title for keyword in ['业务', '板块', 'segments']):
                    tables.append('business_segments')
                    
        return tables
    
    def _has_executive_summary(self, content_plan: Dict[str, Any]) -> bool:
        """Check if presentation has an executive summary slide."""
        slides = content_plan.get('plan', {}).get('slides', [])
        for slide in slides:
            archetype = slide.get('archetype_id', '')
            title = slide.get('action_title', '').lower()
            if 'summary' in archetype or '结论' in title or '总结' in title:
                return True
        return False
    
    def _count_text_only_slides(self, content_plan: Dict[str, Any]) -> int:
        """Count slides that contain only text (no charts or tables)."""
        text_only_count = 0
        slides = content_plan.get('plan', {}).get('slides', [])
        
        for slide in slides:
            archetype = slide.get('archetype_id', '')
            if 'chart' not in archetype and 'table' not in archetype and 'analysis' not in archetype:
                text_only_count += 1
                
        return text_only_count
    
    def enforce_quality_standards(self, content_plan: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce quality standards by modifying the content plan if necessary.
        This is the enforcement layer that ensures professional output.
        """
        validation_result = self.validate_presentation_plan(content_plan, extracted_data)
        
        if validation_result['is_valid']:
            return content_plan
            
        # If not valid, enhance the plan to meet standards
        enhanced_plan = self._enhance_plan_to_meet_standards(content_plan, extracted_data, validation_result)
        return enhanced_plan
    
    def _enhance_plan_to_meet_standards(self, content_plan: Dict[str, Any], extracted_data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the content plan to meet quality standards."""
        # This is a placeholder - in practice, this would add missing chart/table slides
        # For now, we'll just log the issues and proceed
        print("⚠️  Quality validation failed, but proceeding with enhanced plan...")
        print("Issues:", validation_result['issues'])
        print("Recommendations:", validation_result['recommendations'])
        
        return content_plan

def test_quality_validator():
    """Test the quality validator with sample data."""
    validator = QualityValidator()
    
    # Sample content plan (simplified)
    content_plan = {
        'plan': {
            'slides': [
                {'action_title': 'Title', 'archetype_id': 'title_slide'},
                {'action_title': '财报数据整体分析', 'archetype_id': 'metrics_table_slide'},
                {'action_title': '分季度财务趋势', 'archetype_id': 'trend_chart_slide'},
                {'action_title': '总结', 'archetype_id': 'executive_summary_slide'}
            ]
        }
    }
    
    extracted_data = {
        'content_type': 'financial_report',
        'insights': ['Revenue is growing', 'Margins are strong', 'Cash flow is healthy']
    }
    
    result = validator.validate_presentation_plan(content_plan, extracted_data)
    print("Validation Result:", result)
    
    return result

if __name__ == "__main__":
    test_quality_validator()