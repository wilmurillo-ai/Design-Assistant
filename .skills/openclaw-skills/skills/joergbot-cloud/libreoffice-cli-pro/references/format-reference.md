# LibreOffice Format Reference

Complete reference of document formats supported by LibreOffice CLI with conversion options, filters, and usage examples.

## Supported Document Formats

### Text Documents
| Format | Extension | Description | Conversion Filters |
|--------|-----------|-------------|-------------------|
| OpenDocument Text | `.odt` | Native LibreOffice format | `writer8` (default) |
| Microsoft Word 97-2003 | `.doc` | Legacy Word format | `MS Word 97` |
| Microsoft Word 2007+ | `.docx` | Modern Word format | `MS Word 2007 XML` |
| Rich Text Format | `.rtf` | Cross-platform rich text | `Rich Text Format` |
| Plain Text | `.txt` | Unformatted text | `Text (encoded)` |
| HTML | `.html`, `.htm` | Web page format | `HTML (StarWriter)` |
| EPUB | `.epub` | E-book format | `EPUB` |
| PDF | `.pdf` | Portable Document Format | `writer_pdf_Export` |

### Spreadsheets
| Format | Extension | Description | Conversion Filters |
|--------|-----------|-------------|-------------------|
| OpenDocument Spreadsheet | `.ods` | Native LibreOffice format | `calc8` (default) |
| Microsoft Excel 97-2003 | `.xls` | Legacy Excel format | `MS Excel 97` |
| Microsoft Excel 2007+ | `.xlsx` | Modern Excel format | `Calc MS Excel 2007 XML` |
| CSV | `.csv` | Comma-separated values | `Text - txt - csv (StarCalc)` |
| PDF | `.pdf` | Portable Document Format | `calc_pdf_Export` |

### Presentations
| Format | Extension | Description | Conversion Filters |
|--------|-----------|-------------|-------------------|
| OpenDocument Presentation | `.odp` | Native LibreOffice format | `impress8` (default) |
| Microsoft PowerPoint 97-2003 | `.ppt` | Legacy PowerPoint format | `MS PowerPoint 97` |
| Microsoft PowerPoint 2007+ | `.pptx` | Modern PowerPoint format | `Impress MS PowerPoint 2007 XML` |
| PDF | `.pdf` | Portable Document Format | `impress_pdf_Export` |

## Conversion Matrix

### Text Document Conversions
```
.odt → .docx, .doc, .pdf, .txt, .html, .epub, .rtf
.docx → .odt, .pdf, .txt, .html, .epub, .rtf
.doc → .odt, .docx, .pdf, .txt, .html, .epub, .rtf
.txt → .odt, .docx, .pdf, .html, .rtf
.html → .odt, .docx, .pdf, .txt, .rtf
.pdf → .txt, .html (text extraction only)
```

### Spreadsheet Conversions
```
.ods → .xlsx, .xls, .pdf, .csv, .html
.xlsx → .ods, .pdf, .csv, .html
.xls → .ods, .xlsx, .pdf, .csv, .html
.csv → .ods, .xlsx, .xls, .pdf, .html
```

### Presentation Conversions
```
.odp → .pptx, .ppt, .pdf, .html
.pptx → .odp, .pdf, .html
.ppt → .odp, .pptx, .pdf, .html
```

## Filter Reference

### PDF Export Filters
| Filter | Application | Options |
|--------|-------------|---------|
| `writer_pdf_Export` | Writer (Text) | Image compression, security, metadata |
| `calc_pdf_Export` | Calc (Spreadsheets) | Sheet ranges, print ranges |
| `impress_pdf_Export` | Impress (Presentations) | Slides range, notes, handouts |
| `draw_pdf_Export` | Draw (Graphics) | Vector/bitmap export |

### Text Export Filters
| Filter | Description | Encoding Options |
|--------|-------------|------------------|
| `Text (encoded)` | Plain text with encoding | UTF8, ISO-8859-1, Windows-1252 |
| `Text` | Plain text (system encoding) | System default |
| `Text (StarWriter)` | LibreOffice text format | - |
| `HTML (StarWriter)` | HTML export | UTF8, XHTML options |
| `XHTML Writer File` | Modern XHTML export | UTF8, CSS styling |

### Office Format Filters
| Filter | Description | Compatibility |
|--------|-------------|---------------|
| `MS Word 2007 XML` | DOCX format | Word 2007+ |
| `MS Word 97` | DOC format | Word 97-2003 |
| `Calc MS Excel 2007 XML` | XLSX format | Excel 2007+ |
| `MS Excel 97` | XLS format | Excel 97-2003 |
| `Impress MS PowerPoint 2007 XML` | PPTX format | PowerPoint 2007+ |
| `MS PowerPoint 97` | PPT format | PowerPoint 97-2003 |

## Filter Options Syntax

### Basic Syntax
```bash
libreoffice --headless --convert-to "format:filter:options" input.file
```

### JSON Options Format
```bash
libreoffice --headless --convert-to "pdf:writer_pdf_Export:{
  \"ReduceImageResolution\": {\"type\":\"boolean\",\"value\":\"true\"},
  \"MaxImageResolution\": {\"type\":\"long\",\"value\":\"150\"},
  \"SelectPdfVersion\": {\"type\":\"long\",\"value\":\"1\"}
}" document.odt
```

### Common Options

#### PDF Options
```json
{
  "ReduceImageResolution": {"type":"boolean","value":"true"},
  "MaxImageResolution": {"type":"long","value":"150"},
  "Quality": {"type":"long","value":"90"},
  "UseLosslessCompression": {"type":"boolean","value":"false"},
  "SelectPdfVersion": {"type":"long","value":"1"},
  "ExportBookmarks": {"type":"boolean","value":"true"},
  "ExportNotes": {"type":"boolean","value":"false"}
}
```

#### Text Export Options
```json
{
  "Encoding": {"type":"string","value":"UTF8"},
  "LineBreak": {"type":"string","value":"CRLF"},
  "ParagraphBreak": {"type":"string","value":"CRLF"}
}
```

## Format Detection

### MIME Types
```
application/vnd.oasis.opendocument.text        → .odt
application/vnd.openxmlformats-officedocument.wordprocessingml.document → .docx
application/msword                             → .doc
text/plain                                     → .txt
text/html                                      → .html
application/pdf                                → .pdf
application/vnd.oasis.opendocument.spreadsheet → .ods
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet → .xlsx
application/vnd.ms-excel                       → .xls
text/csv                                       → .csv
application/vnd.oasis.opendocument.presentation → .odp
application/vnd.openxmlformats-officedocument.presentationml.presentation → .pptx
application/vnd.ms-powerpoint                  → .ppt
```

### File Command Output
```bash
file document.docx
# document.docx: Microsoft Word 2007+

file spreadsheet.ods
# spreadsheet.ods: OpenDocument Spreadsheet

file presentation.pdf
# presentation.pdf: PDF document, version 1.4
```

## Special Cases

### CSV Import/Export
```bash
# CSV with specific delimiter and encoding
libreoffice --headless --infilter="Text - txt - csv (StarCalc):44,34,0,1,1" \
  --convert-to xlsx:"Calc MS Excel 2007 XML" data.csv

# CSV export options
libreoffice --headless --convert-to "csv:Text - txt - csv (StarCalc):44,34,UTF8" \
  spreadsheet.ods
```

### HTML with Images
```bash
# Convert document to HTML with embedded images
libreoffice --headless --convert-to "html:XHTML Writer File:UTF8" \
  --convert-images-to "jpg" document.odt
```

### EPUB Export
```bash
# Export to EPUB format
libreoffice --headless --convert-to epub document.odt

# EPUB with metadata
libreoffice --headless --convert-to "epub:EPUB" \
  document.odt --outdir ./export
```

## Performance Tips

1. **Batch Processing**: Convert multiple files at once
2. **Profile Isolation**: Use `-env:UserInstallation` for parallel processing
3. **Memory Settings**: Adjust Java heap size if using Java features
4. **Filter Selection**: Use specific filters for better quality/speed
5. **Output Directory**: Specify `--outdir` to avoid cluttering current directory

## Troubleshooting

### Common Issues
1. **Encoding problems**: Specify `--infilter` for CSV/text files
2. **Format detection failures**: Use explicit filter names
3. **Large file handling**: Increase memory limits with `-env` options
4. **Missing filters**: Install additional LibreOffice packages

### Debug Commands
```bash
# List all available filters
libreoffice --headless --help | grep -A 100 "Filters"

# Test conversion with verbose output
libreoffice --headless --convert-to pdf --outdir ./test document.odt 2>&1

# Check file format
file --mime-type document.unknown
```

## Version Compatibility

### LibreOffice 24.2+
- Full support for all modern formats
- Improved PDF/A compliance
- Better DOCX/PPTX/XLSX compatibility
- Enhanced HTML/EPUB export

### LibreOffice 7.0+
- Good DOCX/PPTX/XLSX support
- Basic EPUB export
- Standard PDF features

### Legacy Versions (< 7.0)
- Limited modern format support
- May require additional filters
- Consider upgrading for best results