#!/usr/bin/env python3
"""
Professional PPTX Maker - Quality Stable Version
Enhanced with smart parsing, quality validation, and professional rendering
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Local imports
from template_extractor import TemplateExtractor
from operation_generator import ProfessionalOperationGenerator as OperationGenerator  
from pptx_renderer import ProfessionalPPTXRenderer as PPTXRenderer
from smart_parser import SmartParser
from quality_validator import QualityValidator

class ProfessionalPPTXMaker:
    """Quality stable PPTX generation pipeline with professional standards."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.input_file = config.get('input')
        self.output_file = config.get('output')
        self.template_file = config.get('template')
        self.theme = config.get('theme', 'finance')
        self.dry_run = config.get('dry_run', False)
        self.project_dir = config.get('project_dir', 'pptx_project')
        self.force_professional = config.get('force_professional', True)
        
    def run(self):
        """Execute complete PPTX generation pipeline with quality standards."""
        print("🚀 Starting professional PPTX generation pipeline...")
        
        # Step 1: Create project directory
        os.makedirs(self.project_dir, exist_ok=True)
        print(f"📁 Project directory: {self.project_dir}")
        
        # Step 2: Extract or create template
        if self.template_file and os.path.exists(self.template_file):
            print(f"🎨 Extracting template from: {self.template_file}")
            template_artifacts = self._extract_template()
        else:
            print(f"🎨 Creating default {self.theme} template")
            template_artifacts = self._create_default_template()
            
        manifest_path = os.path.join(self.project_dir, 'resolved_manifest.json')
        
        # Step 3: Load and analyze content with smart parser
        print(f"📄 Loading and analyzing content from: {self.input_file}")
        content_data = self._load_content()
        
        # Step 4: Generate operations with quality validation
        print("📋 Generating professional operations with quality validation...")
        operations = self._generate_operations(content_data, manifest_path)
        slides_json_path = os.path.join(self.project_dir, 'slides.json')
        
        # Step 5: Render PPTX
        if not self.dry_run:
            print("🎨 Rendering professional PPTX...")
            success = self._render_pptx(slides_json_path)
            if success:
                print(f"✅ Professional PPTX saved to: {self.output_file}")
            else:
                print("❌ PPTX rendering failed")
                return False
        else:
            print("✅ Dry run completed successfully!")
            
        return True
        
    def _extract_template(self) -> Dict[str, Any]:
        """Extract template contracts from existing PPTX file."""
        extractor = TemplateExtractor()
        return extractor.extract_template(
            self.template_file,
            self.project_dir
        )
        
    def _create_default_template(self) -> Dict[str, Any]:
        """Create default template for specified theme."""
        template_path = os.path.join(self.project_dir, 'default_template.pptx')
        
        if self.theme == 'tech_analysis':
            from templates.tech_analysis_template import create_tech_analysis_template
            template = create_tech_analysis_template()
            template.save(template_path)
        elif self.theme == 'tech_insight':
            from templates.tech_insight_template import create_tech_insight_template
            template = create_tech_insight_template()
            template.save(template_path)
        else:
            from templates.finance_template import create_finance_template
            template = create_finance_template()
            template.save(template_path)
        
        # Extract the created template
        extractor = TemplateExtractor()
        return extractor.extract_template(template_path, self.project_dir)
        
    def _load_content(self) -> Dict[str, Any]:
        """Load and parse content from input file using smart parser."""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Use smart parser for intelligent content extraction
        parser = SmartParser()
        parsed_data = parser.parse_content(content)
        
        # Set title and brief based on parsed data and theme
        self._title = parsed_data.get('title', 'Professional Presentation')
        if parsed_data.get('content_type') == 'financial_report':
            self._brief = "Financial analysis and performance report"
        elif self.theme == 'tech_analysis':
            self._brief = "Technology analysis and architecture report"
        elif self.theme == 'tech_insight':
            self._brief = "Technology insight and industry trend analysis"
        else:
            self._brief = "Professional analysis presentation"
            
        return {
            'title': self._title,
            'brief': self._brief,
            'sections': parsed_data.get('sections', []),
            'tables': parsed_data.get('tables', []),
            'metrics': parsed_data.get('metrics', {}),
            'insights': parsed_data.get('insights', []),
            'content_type': parsed_data.get('content_type', 'general_presentation')
        }
        
    def _generate_operations(self, content_data: Dict[str, Any], manifest_path: str) -> list:
        """Generate JSON operations based on content and template contract with quality validation."""
        generator = OperationGenerator()
        generator.load_template_contract(manifest_path)
        plan = generator.plan_content(content_data)
        
        # Quality validation - enforce professional standards
        validator = QualityValidator()
        validation_result = validator.validate_presentation_plan(plan, content_data)
        
        if not validation_result['is_valid']:
            print(f"⚠️  Quality validation warning (Score: {validation_result['score']}/100):")
            for issue in validation_result['issues']:
                print(f"   • {issue}")
            if validation_result['score'] < 50:
                print("   ⚠️  Low quality score - consider enhancing content structure")
        
        operations = generator.generate_operations()
        slides_json_path = os.path.join(self.project_dir, 'slides.json')
        generator.save_slides_json(slides_json_path)
        return operations
        
    def _render_pptx(self, slides_json_path: str) -> bool:
        """Render PPTX from operations."""
        base_template_path = os.path.join(self.project_dir, 'base_template.pptx')
        renderer = PPTXRenderer(base_template_path)
        renderer.load_operations(slides_json_path)
        success = renderer.execute_operations()
        if success:
            renderer.save(self.output_file)
        return success


def main():
    """Command line interface."""
    if len(sys.argv) < 3:
        print("Usage: python3 professional_main.py --input <file> --output <file.pptx>")
        print("Options: --theme <finance|tech_insight|tech_analysis> --template <file.pptx>")
        return
        
    config = {'theme': 'finance'}
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--input' and i + 1 < len(sys.argv):
            config['input'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            config['output'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--theme' and i + 1 < len(sys.argv):
            config['theme'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--template' and i + 1 < len(sys.argv):
            config['template'] = sys.argv[i + 1]
            i += 2
        else:
            i += 1
            
    if 'input' not in config or 'output' not in config:
        print("Error: --input and --output are required")
        return
        
    maker = ProfessionalPPTXMaker(config)
    success = maker.run()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()