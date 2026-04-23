# Professional PPTX Maker v1.0.0

## Overview
Creates professional PowerPoint presentations with **mandatory charts, tables, and expert commentary**. This is a quality-stable version that enforces professional standards.

## Features
- **Smart Parsing**: Automatically detects tables, metrics, trends, and content type
- **Professional Planning**: Creates optimal slide structure with charts/tables  
- **Quality Validation**: Enforces professional standards and provides feedback
- **Professional Rendering**: Generates PPTX with proper charts, tables, and styling
- **Multiple Themes**: Finance, Technology Insight, and Technology Analysis templates

## Quality Standards (Mandatory)
- **No large text blocks**: All content converted to structured layouts
- **Charts required**: Automatic chart generation from structured data
- **Tables required**: Structured data presented in professional tables  
- **Expert insights**: Every slide includes professional analysis and key takeaways
- **MECE principle**: Mutually exclusive, collectively exhaustive organization
- **Professional layout**: Clear hierarchy, bright tech color schemes

## Installation
```bash
# Clone the repository
git clone https://github.com/vincentlau2046-sudo/professional-pptx-maker.git

# Install dependencies
pip install python-pptx
```

## Usage
```bash
python3 main.py --input content.md --output presentation.pptx --theme tech_insight
```

## Templates
- `finance`: Bright fintech theme (NVIDIA green)
- `tech_insight`: Technology insight theme (Huawei red/orange)  
- `tech_analysis`: Professional technology analysis theme (Tech blue)

## Version History
### v1.0.0 (2026-04-02)
- Initial stable release
- Four-layer professional pipeline
- Quality validation with mandatory standards
- Support for charts, tables, and professional layouts
- Three professional themes with Huawei-style design

## Dependencies
- python-pptx >= 0.6.21
- Microsoft YaHei font (Chinese support)
- Poppins, Roboto fonts (English support)

## License
MIT License