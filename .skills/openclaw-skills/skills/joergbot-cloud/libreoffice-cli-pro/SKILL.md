---
name: libreoffice-cli-pro
description: "Comprehensive document conversion, creation and editing via LibreOffice CLI (Headless-Modus). Use for: PDF export, format conversion (doc↔odt↔pdf, xls↔ods↔xlsx, ppt↔odp↔pptx), text extraction, batch conversions, and integration with other skills. Includes wrapper scripts, health checks, and automation workflows."
emoji: 📄
---

# LibreOffice CLI Pro

Comprehensive LibreOffice 24.2+ management in headless mode with wrapper scripts, batch processing, and integration capabilities.

## Quick Start

### 1. Check Installation
```bash
./scripts/libreoffice-check.sh health
```

### 2. Convert Single Document
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

## Complete Script Reference

### libreoffice-check.sh
Health check and installation verification for LibreOffice.
```bash
# Comprehensive health check
./scripts/libreoffice-check.sh health

# Check specific components
./scripts/libreoffice-check.sh installed
./scripts/libreoffice-check.sh version
./scripts/libreoffice-check.sh headless
./scripts/libreoffice-check.sh conversion
./scripts/libreoffice-check.sh filters

# Installation help
./scripts/libreoffice-check.sh install-help
```

### libreoffice-convert.sh
Convert single documents between various formats.
```bash
# Basic conversion
./scripts/libreoffice-convert.sh document.docx pdf

# With quality settings
./scripts/libreoffice-convert.sh presentation.pptx pdf --quality high

# Specific output directory
./scripts/libreoffice-convert.sh spreadsheet.xlsx ods --output ./converted/

# Verbose output for debugging
./scripts/libreoffice-convert.sh report.odt docx --verbose
```

### libreoffice-batch.sh
Batch convert multiple documents with parallel processing.
```bash
# Convert all documents in directory
./scripts/libreoffice-batch.sh ./documents/ pdf

# Recursive conversion
./scripts/libreoffice-batch.sh ./project/ pdf --recursive

# Specific file pattern
./scripts/libreoffice-batch.sh . docx --pattern "*.odt"

# Parallel processing (4 threads)
./scripts/libreoffice-batch.sh ./large_collection/ pdf --threads 4

# Dry run (show what would be converted)
./scripts/libreoffice-batch.sh ./docs/ pdf --dry-run
```

### libreoffice-extract.sh
Extract text content from various document formats.
```bash
# Extract text to console
./scripts/libreoffice-extract.sh document.pdf

# Extract to file with specific format
./scripts/libreoffice-extract.sh report.docx --format txt --output extracted.txt

# Extract as HTML
./scripts/libreoffice-extract.sh manual.odt --format html --output manual.html

# Extract as JSON with metadata
./scripts/libreoffice-extract.sh data.pdf --format json --output data.json

# Extract with cleaning and line limit
./scripts/libreoffice-extract.sh long_document.pdf --clean --lines 100 --output summary.txt
```

### libreoffice-pdf.sh
PDF-specific operations including merge, split, optimize, and conversion.
```bash
# Merge documents into PDF
./scripts/libreoffice-pdf.sh merge chapter1.docx chapter2.odt --output book.pdf

# Split PDF into pages
./scripts/libreoffice-pdf.sh split document.pdf --output-dir ./pages

# Optimize PDF file size
./scripts/libreoffice-pdf.sh optimize large.pdf --compress 9 --remove-metadata

# Convert to PDF with quality settings
./scripts/libreoffice-pdf.sh convert presentation.pptx --output slides.pdf --quality high

# Show PDF information
./scripts/libreoffice-pdf.sh info document.pdf

# Extract content from PDF
./scripts/libreoffice-pdf.sh extract scanned.pdf --text --images --output-dir ./extracted
```

### libreoffice-merge.sh
Merge multiple documents into a single document.
```bash
# Merge ODT files
./scripts/libreoffice-merge.sh chapter1.odt chapter2.odt --output book.odt

# Merge different formats with page breaks
./scripts/libreoffice-merge.sh intro.docx content.odt appendix.rtf --output complete.pdf --page-break

# Merge with table of contents
./scripts/libreoffice-merge.sh *.md --output documentation.odt --toc --title "User Manual"

# Merge sorted alphabetically
./scripts/libreoffice-merge.sh *.txt --output combined.odt --sort --author "Documentation Team"
```

## Kernbefehle

### Konvertierung (--convert-to)

```bash
# Basis-Syntax
libreoffice --headless --convert-to <Zielformat[:Filter]> --outdir <Verzeichnis> <Datei(en)>

# PDF aus verschiedenen Formaten
libreoffice --headless --convert-to pdf *.odt
libreoffice --headless --convert-to pdf *.docx
libreoffice --headless --convert-to pdf:writer_pdf_Export --outdir ./output *.doc

# Office-Formate
libreoffice --headless --convert-to docx *.odt
libreoffice --headless --convert-to odt *.docx
libreoffice --headless --convert-to xlsx *.ods
libreoffice --headless --convert-to xlsx:"Calc MS Excel 2007 XML" *.csv
libreoffice --headless --convert-to pptx *.odp

# Text extrahieren
libreoffice --headless --convert-to "txt:Text (encoded):UTF8" *.pdf
libreoffice --headless --convert-to html *.odt
libreoffice --headless --convert-to epub *.doc
```

### Text-Anzeige (--cat)

```bash
# Textinhalt direkt auf Konsole ausgeben (kein Output-File)
libreoffice --headless --cat dokument.odt
libreoffice --headless --cat tabelle.xlsx
```

### Drucken (--print-to-file)

```bash
libreoffice --headless --print-to-file --outdir ./output *.odt
libreoffice --headless --print-to-file --printer-name "PDF" --outdir ./output *.doc
```

### Präsentationen anzeigen (--show)

```bash
libreoffice --show praesentation.odp  # startet Diashow
```

### Dokumente öffnen (--view)

```bash
libreoffice --view dokument.odt  # schreibgeschützt
```

## Format-Referenz

| Eingabe | → PDF | → Modern | → Text |
|---------|-------|----------|--------|
| .odt / .doc / .docx | pdf | docx / odt | txt, html, epub |
| .ods / .xls / .xlsx | pdf | xlsx / ods | csv, html |
| .odp / .ppt / .pptx | pdf | pptx / odp | html, png |
| .csv | pdf | xlsx / ods | - |
| .txt | pdf | odt / docx | - |
| .html | pdf | odt | txt |

## Wichtige Filter

- `writer_pdf_Export` — Writer→PDF mit Kontrolle
- `calc_pdf_Export` — Calc→PDF
- `impress_pdf_Export` — Impress→PDF
- `Text (encoded):UTF8` — UTF-8 Text-Export
- `MS Word 2007 XML` — docx (Writer)
- `Calc MS Excel 2007 XML` — xlsx (Calc)

## Flags

- `--headless` — Kein GUI (impliziert bei --convert-to)
- `--outdir <path>` — Ausgabeverzeichnis (sonst cwd)
- `--infilter=<filter>` — Eingabe-Filter erzwingen (z.B. für CSV-Encoding)
- `--convert-images-to <fmt>` — Bilder im Dokument konvertieren
- `-env:UserInstallation=file:///tmp/loprofile` — Eigenes Profil nutzen

## Beispiele

### CSV → Excel mit korrektem Encoding
```bash
libreoffice --headless --infilter="Text - txt - csv (StarCalc):44,34,0,1,1" \
  --convert-to xlsx:"Calc MS Excel 2007 XML" daten.csv --outdir ./export/
```

### Batch: Alle ODT → PDF
```bash
libreoffice --headless --convert-to pdf *.odt --outdir ./pdfs/
```

### HTML mit Bildkonvertierung
```bash
libreoffice --headless --convert-to "html:XHTML Writer File:UTF8" \
  --convert-images-to "jpg" bericht.docx
```

### Text aus PDF extrahieren
```bash
libreoffice --headless --cat dokument.pdf | head -100
```

### Mehrere Ordner gleichzeitig
```bash
find ./docs -name "*.doc" -exec \
  libreoffice --headless --convert-to pdf --outdir ./pdfs/ {} \;
```

## Reference Documentation

Complete reference documentation is available in the `references/` directory:

### Format Reference
`references/format-reference.md` - Complete format support matrix with conversion options, MIME types, and compatibility information.

### Filter Reference  
`references/filter-reference.md` - Detailed filter parameters, options syntax, JSON configuration, and advanced usage examples.

### Examples Collection
`references/examples.md` - Practical examples and real-world workflows including batch processing, automation, and integration patterns.

## Integration with Other Skills

### Joplin Notes Integration
```bash
#!/bin/bash
# Convert Joplin notes to PDF
joplin export --format md notes.md
./scripts/libreoffice-convert.sh notes.md pdf --output joplin_notes.pdf
```

### Gmail Attachment Processing
```bash
#!/bin/bash
# Process email attachments automatically
gog mail get <email_id> --save-attachments ./attachments
./scripts/libreoffice-batch.sh ./attachments/ pdf --pattern "*.docx"
```

### Web Content Conversion
```bash
#!/bin/bash
# Convert web articles to readable formats
web_fetch "https://example.com/article" --extractMode markdown > article.md
./scripts/libreoffice-convert.sh article.md pdf --quality high
```

### Automated Document Pipeline
```bash
#!/bin/bash
# Complete document processing pipeline
INPUT_DIR="./incoming"
PROCESSED_DIR="./processed"

# 1. Health check
./scripts/libreoffice-check.sh health

# 2. Batch convert to PDF
./scripts/libreoffice-batch.sh "$INPUT_DIR" pdf --recursive --output "$PROCESSED_DIR"

# 3. Extract text for search indexing
find "$PROCESSED_DIR" -name "*.pdf" | while read pdf; do
    ./scripts/libreoffice-extract.sh "$pdf" --output "${pdf%.pdf}.txt" --clean
done

# 4. Create combined index
./scripts/libreoffice-merge.sh "$PROCESSED_DIR"/*.pdf --output "$PROCESSED_DIR/index.pdf" --toc
```

## Tipps

- Java-Warnungen (`javaldx`) können ignoriert werden — Grundfunktionen gehen ohne Java
- Für parallele Konvertierungen: eigene Profile nutzen (`-env:UserInstallation=...`)
- CSV: `--infilter` nutzen um Trennzeichen/Encoding zu setzen
- Bei Fehlern: Dateiname ohne Leerzeichen/Sonderzeichen testen
- Use the reference documentation for advanced filter options and JSON configuration
- Check `examples.md` for complete automation workflows and integration patterns
