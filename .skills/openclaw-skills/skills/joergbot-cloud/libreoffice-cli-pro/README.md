# LibreOffice CLI Pro Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-blue)](https://clawhub.ai)
[![LibreOffice](https://img.shields.io/badge/LibreOffice-24.2+-green)](https://libreoffice.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive OpenClaw skill for document conversion, creation, and editing via LibreOffice CLI (headless mode). This skill provides wrapper scripts, batch processing, and integration patterns for LibreOffice document management.

## Features

- **Full LibreOffice CLI Integration** – Access all LibreOffice headless commands through OpenClaw
- **Wrapper Scripts** – Pre-built scripts for common document workflows
- **Batch Processing** – Convert multiple documents in parallel
- **Text Extraction** – Extract text from various document formats
- **PDF Operations** – Merge, split, and optimize PDFs
- **Error Handling** – Robust checks for LibreOffice installation and configuration
- **Multi-language Support** – Documentation in German and English
- **Integration Ready** – Works with other skills (Joplin, Gmail, Web Fetch)

## Quick Start

### 1. Check LibreOffice Installation
```bash
./scripts/libreoffice-check.sh health
```

### 2. Convert a Document
```bash
./scripts/libreoffice-convert.sh document.docx pdf
```

### 3. Batch Convert Documents
```bash
./scripts/libreoffice-batch.sh ./documents/ pdf --recursive
```

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `libreoffice-check.sh` | Health check and installation verification | `./libreoffice-check.sh health` |
| `libreoffice-convert.sh` | Convert single document between formats | `./libreoffice-convert.sh input.docx pdf` |
| `libreoffice-batch.sh` | Batch convert multiple documents | `./libreoffice-batch.sh ./docs/ pdf --recursive` |
| `libreoffice-extract.sh` | Extract text from documents | `./libreoffice-extract.sh document.pdf --format txt` |
| `libreoffice-pdf.sh` | PDF-specific operations | `./libreoffice-pdf.sh merge *.docx output.pdf` |
| `libreoffice-merge.sh` | Merge multiple documents | `./libreoffice-merge.sh *.odt combined.pdf` |

## Common Workflows

### Document Conversion
```bash
# Convert Word to PDF
./scripts/libreoffice-convert.sh report.docx pdf

# Convert ODT to DOCX
./scripts/libreoffice-convert.sh document.odt docx

# Convert Excel to PDF
./scripts/libreoffice-convert.sh data.xlsx pdf
```

### Batch Processing
```bash
# Convert all ODT files in folder to PDF
./scripts/libreoffice-batch.sh ./documents/ pdf

# Convert with specific pattern
./scripts/libreoffice-batch.sh ./spreadsheets/ xlsx --pattern "*.ods"

# Recursive conversion
./scripts/libreoffice-batch.sh ./projects/ pdf --recursive
```

### Text Extraction
```bash
# Extract text from PDF
./scripts/libreoffice-extract.sh document.pdf --format txt

# Extract as HTML
./scripts/libreoffice-extract.sh presentation.pptx --format html

# Extract with page limits
./scripts/libreoffice-extract.sh manual.pdf --format txt --pages 1-10
```

### PDF Operations
```bash
# Merge multiple documents into PDF
./scripts/libreoffice-pdf.sh merge chapter*.docx book.pdf

# Split PDF into single pages
./scripts/libreoffice-pdf.sh split document.pdf --pages 1-5

# Optimize PDF size
./scripts/libreoffice-pdf.sh optimize large.pdf compressed.pdf
```

## Integration with Other Skills

### Joplin → LibreOffice
```bash
# Save converted documents as Joplin notes
./scripts/libreoffice-convert.sh document.docx pdf | \
  joplin mknote "Converted Document"
```

### Gmail → LibreOffice
```bash
# Convert email attachments
# (Combine with gog skill)
```

### Web Fetch → LibreOffice
```bash
# Convert web pages to PDF
web_fetch --url https://example.com --extract-mode markdown | \
  ./scripts/libreoffice-convert.sh - pdf --stdin
```

## Prerequisites

1. **LibreOffice** installed (version 24.2+ recommended):
   ```bash
   # Ubuntu/Debian
   sudo apt install libreoffice
   
   # macOS
   brew install libreoffice
   
   # Windows: Download from https://libreoffice.org
   ```

2. **Headless mode support** – LibreOffice should support `--headless` flag

## Configuration

### Environment Variables
```bash
export LIBREOFFICE_PATH="/usr/bin/libreoffice"
export LIBREOFFICE_PROFILE_DIR="/tmp/libreoffice-profile"
export LIBREOFFICE_TIMEOUT=300
export LIBREOFFICE_MEMORY_LIMIT="2048M"
```

### LibreOffice Configuration for CLI
```bash
# Create separate profile for CLI operations
mkdir -p /tmp/libreoffice-profile
```

## Troubleshooting

### LibreOffice Not Found
```bash
Error: LibreOffice not found
```
**Solution:**
```bash
# Check installation
which libreoffice
# Install if missing
sudo apt install libreoffice
```

### Conversion Errors
```bash
Error: Conversion failed
```
**Solution:**
```bash
# Check file permissions
ls -la document.docx

# Try with different filter
./scripts/libreoffice-convert.sh document.docx pdf --filter "writer_pdf_Export"
```

### Memory Issues
```bash
Error: Out of memory
```
**Solution:**
```bash
# Increase memory limit
export LIBREOFFICE_MEMORY_LIMIT="4096M"

# Use separate profile
export LIBREOFFICE_PROFILE_DIR="/tmp/lo-profile-$(date +%s)"
```

## References

- `references/format-reference.md` – Format conversion table
- `references/filter-reference.md` – Filter options
- `references/examples.md` – Detailed examples
- [LibreOffice Documentation](https://help.libreoffice.org) – Official docs
- [ClawHub Skills](https://clawhub.ai) – More skills

## Development

### Project Structure
```
libreoffice-cli/
├── SKILL.md                    # Main skill documentation
├── README.md                   # ClawHub README
├── package.json                # ClawHub metadata
├── LICENSE                     # MIT License
├── scripts/                    # Wrapper scripts
│   ├── libreoffice-check.sh    # Health check
│   ├── libreoffice-convert.sh  # Single conversion
│   ├── libreoffice-batch.sh    # Batch conversion
│   ├── libreoffice-extract.sh  # Text extraction
│   ├── libreoffice-pdf.sh      # PDF operations
│   └── libreoffice-merge.sh    # Document merging
├── references/                 # Reference documentation
│   ├── format-reference.md     # Format table
│   ├── filter-reference.md     # Filter reference
│   └── examples.md             # Examples
└── examples/                   # Example files
```

### Adding New Scripts
1. Create script in `scripts/` directory
2. Include error handling with `libreoffice-check.sh`
3. Document in README.md and SKILL.md
4. Test with real LibreOffice installation

## License

MIT License – See [LICENSE](LICENSE) file.

---

**Happy Document Processing!** 📄