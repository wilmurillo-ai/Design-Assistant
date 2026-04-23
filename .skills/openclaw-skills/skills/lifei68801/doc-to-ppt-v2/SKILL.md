---
name: doc-to-ppt-v2
version: 1.0.1
description: "Convert documents to PowerPoint slides. Local processing only."
license: MIT-0
author: lifei68801
tags: [ppt, document]
---

# Doc-to-PPT

Convert PDF, Word, Markdown to PowerPoint.

## Usage

```bash
python scripts/main.py input.pdf --output ./output
```

## Install

```bash
pip install playwright python-pptx pdfplumber python-docx
playwright install chromium
```

## Metadata

```yaml
metadata:
  openclaw:
    requires:
      bins: ["python3", "playwright"]
      pypi: ["playwright", "python-pptx", "pdfplumber", "python-docx"]
    permissions:
      - "file:read"
      - "file:write"
    behavior:
      network: none
      telemetry: none
      description: "Local document to PPT converter."
