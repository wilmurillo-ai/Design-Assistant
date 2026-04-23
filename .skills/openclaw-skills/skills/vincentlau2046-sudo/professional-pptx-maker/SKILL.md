# Professional PPTX Maker Skill (Quality Stable Version)

## Description
Creates professional PowerPoint presentations with **mandatory charts, tables, and expert commentary**. This is a quality-stable version that enforces professional standards.

## ✅ Quality Standards (Mandatory)
- **No large text blocks**: All content converted to structured layouts (cards, columns, tables, charts)
- **Charts required**: Automatic chart generation from structured data (tables → column/line/pie charts)
- **Tables required**: Structured data presented in professional formatted tables
- **Expert insights**: Every slide includes professional analysis and key takeaways
- **MECE principle**: Mutually exclusive, collectively exhaustive content organization
- **Professional layout**: Clear hierarchy, standardized theme color schemes
- **NO OVER-SIMPLIFICATION (MANDATORY)**: Prioritize retaining all core content, key metrics, technical details. Default to rich content output, only remove truly redundant information, no excessive simplification of technical documents

## 🎨 Templates & Themes

### Finance Template (Default)
- **Color scheme**: NVIDIA green (#76B900) on light gray background
- **Best for**: Financial reports, investment analysis, business performance
- **Charts**: Revenue trends, profit margins, business composition

### Technology Insight Template  
- **Color scheme**: Huawei red (#E02020) and orange (#FF6600) on white background
- **Best for**: Industry trends, market analysis, strategic insights
- **Layout**: Professional card-based design with emphasis on key points

### Technology Analysis Template
- **Color scheme**: Pure white background + dark red highlight (#8C1414)
- **Best for**: Technical architecture, performance analysis, system comparisons, technical reports
- **Features**: Optimized for technical diagrams, flow charts, performance charts, comparison tables, structured professional layout

### Technology Training Template
- **Color scheme**: Pure white background + dark red highlight (#8C1414)
- **Best for**: Technical training, operation guidance, process specification
- **Features**: Optimized for flow charts, architecture diagrams, data charts, clear structured presentation

## 🚀 Usage

```bash
# Create finance-themed presentation (default)
professional-pptx-maker --input content.md --output presentation.pptx --theme finance

# Create technology insight-themed presentation  
professional-pptx-maker --input content.md --output presentation.pptx --theme tech_insight

# Create technology analysis-themed presentation
professional-pptx-maker --input content.md --output presentation.pptx --theme tech_analysis

# Create technology training-themed presentation
professional-pptx-maker --input content.md --output presentation.pptx --theme tech_training

# Use existing template file
professional-pptx-maker --input content.md --output presentation.pptx --template custom.pptx
```

## 📋 Input Format Requirements

### For Best Results:
- Use **Markdown tables** for structured data
- Include **numerical metrics** with units and time periods  
- Use **H2 headings (##)** for section titles
- Use **bullet points (-)** for key items
- Include **percentage changes** and **growth rates**

### Example Input Structure:
```markdown
# Presentation Title

## Section 1: Key Metrics
| Metric | 2026 | 2025 | Change |
|--------|-------|------|--------|
| Revenue | 2159 | 1305 | +65.5% |

## Section 2: Quarterly Trends  
- Q1 revenue: $440M
- Q2 revenue: $467M  
- Q3 revenue: $570M
- Q4 revenue: $681M
```

## 🔧 Architecture Overview

### Four-Layer Professional Pipeline:
1. **Smart Parser**: Automatically detects tables, metrics, trends, and content type
2. **Professional Planner**: Creates optimal slide structure with charts/tables
3. **Quality Validator**: Enforces professional standards and provides feedback  
4. **Professional Renderer**: Generates PPTX with proper charts, tables, and styling

### Quality Validation Rules:
- **Financial Reports**: Must include revenue trend chart, margin chart, metrics table
- **Technical Analysis**: Must include architecture diagram, performance comparison
- **Minimum Insights**: 3+ professional insights for financial, 4+ for technical
- **Text Limit**: Maximum 2-3 text-only slides allowed

## 💻 Dependencies
- python-pptx
- Microsoft YaHei font (Chinese support)
- Poppins, Roboto fonts (English support)

## 📤 Output
Generates professional 16:9 PowerPoint presentations (.pptx) ready for executive presentations, with:
- **Professional charts** (column, line, pie charts)
- **Structured tables** with proper formatting  
- **Expert commentary** on every relevant slide
- **Executive summary** with key conclusions
- **Quality validation report** in console output

## 🎯 Professional Standards Compliance
This skill **guarantees** professional output quality by:
- **Rejecting poor input structure** with actionable feedback
- **Automatically converting** text to visual formats
- **Enforcing MECE principles** in content organization  
- **Providing quality scores** and improvement suggestions
- **Ensuring every output** meets executive presentation standards