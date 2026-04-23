# LibreOffice Filter Reference

Complete reference of LibreOffice import/export filters with detailed parameters, options, and usage examples.

## Filter Categories

### 1. Text Document Filters
### 2. Spreadsheet Filters
### 3. Presentation Filters
### 4. Graphics Filters
### 5. Specialized Filters

## Text Document Filters

### Writer Filters (Text Documents)

#### Export Filters
| Filter Name | Format | Key Options | Usage |
|-------------|--------|-------------|-------|
| `writer8` | ODT (OpenDocument Text) | Default, no options | `--convert-to odt` |
| `MS Word 2007 XML` | DOCX | Compatibility mode | `--convert-to docx` |
| `MS Word 97` | DOC | Legacy support | `--convert-to doc` |
| `Rich Text Format` | RTF | Cross-platform | `--convert-to rtf` |
| `writer_pdf_Export` | PDF | Extensive options | `--convert-to pdf` |
| `XHTML Writer File` | HTML/XHTML | Modern HTML | `--convert-to html` |
| `EPUB` | EPUB | E-book format | `--convert-to epub` |
| `Text (encoded)` | TXT | Encoding control | `--convert-to txt` |
| `Text` | TXT | System encoding | `--convert-to txt:Text` |
| `DocBook` | XML | Documentation format | `--convert-to xml` |

#### Import Filters
| Filter Name | Format | Key Options | Usage |
|-------------|--------|-------------|-------|
| `writer8` | ODT | Default import | (automatic) |
| `MS Word 2007 XML` | DOCX | Modern Word | (automatic) |
| `MS Word 97` | DOC | Legacy Word | (automatic) |
| `Rich Text Format` | RTF | Cross-platform | (automatic) |
| `XHTML Writer File` | HTML | Web pages | (automatic) |
| `Text (encoded)` | TXT | Specific encoding | `--infilter="Text (encoded):UTF8"` |

### PDF Export Options (writer_pdf_Export)

#### Image Options
```json
{
  "ReduceImageResolution": {"type":"boolean","value":"true"},
  "MaxImageResolution": {"type":"long","value":"300"},
  "UseLosslessCompression": {"type":"boolean","value":"false"},
  "Quality": {"type":"long","value":"90"},
  "CompressionMode": {"type":"long","value":"0"}  // 0=auto, 1=JPEG, 2=Lossless
}
```

#### Document Options
```json
{
  "SelectPdfVersion": {"type":"long","value":"1"},  // 1=PDF 1.4, 2=PDF/A-1
  "ExportBookmarks": {"type":"boolean","value":"true"},
  "ExportNotes": {"type":"boolean","value":"false"},
  "ExportPlaceholders": {"type":"boolean","value":"false"},
  "ExportHiddenSlides": {"type":"boolean","value":"false"},
  "SinglePageSheets": {"type":"boolean","value":"false"}
}
```

#### Security Options
```json
{
  "EncryptFile": {"type":"boolean","value":"true"},
  "DocumentOpenPassword": {"type":"string","value":"mypassword"},
  "RestrictPermissions": {"type":"boolean","value":"true"},
  "PermissionPassword": {"type":"string","value":"adminpass"},
  "Printing": {"type":"long","value":"2"},  // 0=not allowed, 1=low res, 2=full
  "Changes": {"type":"long","value":"4"}    // 0=none, 4=fill forms, etc.
}
```

## Spreadsheet Filters

### Calc Filters (Spreadsheets)

#### Export Filters
| Filter Name | Format | Key Options | Usage |
|-------------|--------|-------------|-------|
| `calc8` | ODS (OpenDocument Spreadsheet) | Default | `--convert-to ods` |
| `Calc MS Excel 2007 XML` | XLSX | Modern Excel | `--convert-to xlsx` |
| `MS Excel 97` | XLS | Legacy Excel | `--convert-to xls` |
| `calc_pdf_Export` | PDF | Spreadsheet PDF | `--convert-to pdf` |
| `Text - txt - csv (StarCalc)` | CSV | Delimited text | `--convert-to csv` |
| `HTML (StarCalc)` | HTML | Web tables | `--convert-to html` |

#### Import Filters
| Filter Name | Format | Key Options | Usage |
|-------------|--------|-------------|-------|
| `calc8` | ODS | Default import | (automatic) |
| `Calc MS Excel 2007 XML` | XLSX | Modern Excel | (automatic) |
| `MS Excel 97` | XLS | Legacy Excel | (automatic) |
| `Text - txt - csv (StarCalc)` | CSV | Delimiter config | `--infilter="Text - txt - csv (StarCalc):44,34,0,1,1"` |

### CSV Filter Parameters
```
Text - txt - csv (StarCalc):field,text,charSet,firstRow,cellFormat

Parameters:
1. field    - Field delimiter ASCII code (44=comma, 59=semicolon, 9=tab)
2. text     - Text delimiter ASCII code (34=double quote, 39=single quote)
3. charSet  - Character set (0=system, 1=Windows-1252, 4=UTF-8, 12=UTF-16)
4. firstRow - First row number (usually 1)
5. cellFormat - Cell format (0=standard, 1=US, 2=system)
```

#### Examples:
```bash
# CSV with comma, double quotes, UTF-8
--infilter="Text - txt - csv (StarCalc):44,34,4,1,1"

# CSV with semicolon, single quotes, system encoding
--infilter="Text - txt - csv (StarCalc):59,39,0,1,1"

# TSV (tab-separated), double quotes, UTF-8
--infilter="Text - txt - csv (StarCalc):9,34,4,1,1"
```

## Presentation Filters

### Impress Filters (Presentations)

#### Export Filters
| Filter Name | Format | Key Options | Usage |
|-------------|--------|-------------|-------|
| `impress8` | ODP (OpenDocument Presentation) | Default | `--convert-to odp` |
| `Impress MS PowerPoint 2007 XML` | PPTX | Modern PowerPoint | `--convert-to pptx` |
| `MS PowerPoint 97` | PPT | Legacy PowerPoint | `--convert-to ppt` |
| `impress_pdf_Export` | PDF | Presentation PDF | `--convert-to pdf` |
| `impress_html_Export` | HTML | Web presentation | `--convert-to html` |

#### Import Filters
| Filter Name | Format | Key Options | Usage |
|-------------|--------|-------------|-------|
| `impress8` | ODP | Default import | (automatic) |
| `Impress MS PowerPoint 2007 XML` | PPTX | Modern PowerPoint | (automatic) |
| `MS PowerPoint 97` | PPT | Legacy PowerPoint | (automatic) |

### Presentation PDF Options
```json
{
  "SlidesRange": {"type":"string","value":"1-5,7,9-12"},
  "ExportNotesPages": {"type":"boolean","value":"true"},
  "ExportHandoutsPages": {"type":"boolean","value":"false"},
  "ExportOutlinePages": {"type":"boolean","value":"false"},
  "ExportOnlyNotesPages": {"type":"boolean","value":"false"},
  "ExportHiddenSlides": {"type":"boolean","value":"false"}
}
```

## Graphics Filters

### Draw Filters (Graphics)

#### Export Filters
| Filter Name | Format | Description | Usage |
|-------------|--------|-------------|-------|
| `draw8` | ODG (OpenDocument Graphics) | Native format | `--convert-to odg` |
| `draw_pdf_Export` | PDF | Vector PDF | `--convert-to pdf` |
| `SVG` | SVG | Scalable Vector Graphics | `--convert-to svg` |
| `EPS` | EPS | Encapsulated PostScript | `--convert-to eps` |
| `PNG` | PNG | Portable Network Graphics | `--convert-to png` |
| `JPEG` | JPG | JPEG image | `--convert-to jpg` |

#### Image Export Options
```json
{
  "Width": {"type":"long","value":"1920"},
  "Height": {"type":"long","value":"1080"},
  "Resolution": {"type":"long","value":"300"},
  "ImageFormat": {"type":"long","value":"1"},  // 1=PNG, 2=JPG, etc.
  "Quality": {"type":"long","value":"90"},
  "Compression": {"type":"long","value":"6"}
}
```

## Specialized Filters

### Database Filters
| Filter Name | Format | Description |
|-------------|--------|-------------|
| `dBase` | DBF | dBase database format |
| `ADO` | MDB | Microsoft Access |

### Math Filters
| Filter Name | Format | Description |
|-------------|--------|-------------|
| `math8` | ODF | OpenDocument Formula |
| `MathML` | XML | Mathematical Markup Language |

### Additional Text Filters
| Filter Name | Format | Description |
|-------------|--------|-------------|
| `AportisDoc` | PDB | Palm DOC format |
| `PocketWord` | PSW | Pocket Word format |
| `WordPerfect` | WPD | WordPerfect format |
| `LotusWordPro` | LWP | Lotus Word Pro |

## Filter Discovery

### List Available Filters
```bash
# List all export filters
libreoffice --headless --help | grep -A 200 "Filters:" | grep "^\s"

# List filters for specific format
libreoffice --headless --help | grep -i "pdf" | head -20

# Check filter capabilities
soffice --help | grep -B5 -A5 "convert-to"
```

### Filter Testing
```bash
# Test specific filter
libreoffice --headless --convert-to "pdf:writer_pdf_Export" test.odt

# Test with options
libreoffice --headless --convert-to "pdf:writer_pdf_Export:{\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"}}" test.odt

# Test import filter
libreoffice --headless --infilter="Text - txt - csv (StarCalc):44,34,4,1,1" --convert-to ods data.csv
```

## Advanced Filter Usage

### Chained Conversions
```bash
# DOCX → ODT → PDF (two-step conversion)
libreoffice --headless --convert-to odt document.docx
libreoffice --headless --convert-to pdf document.odt

# With specific filters
libreoffice --headless --convert-to "odt:writer8" document.docx
libreoffice --headless --convert-to "pdf:writer_pdf_Export:{\"Quality\":{\"type\":\"long\",\"value\":\"100\"}}" document.odt
```

### Batch Filter Application
```bash
# Apply same filter to multiple files
for file in *.docx; do
    libreoffice --headless --convert-to "pdf:writer_pdf_Export" "$file"
done

# With parallel processing
find . -name "*.odt" -print0 | xargs -0 -P4 -I{} libreoffice --headless --convert-to pdf {}
```

### Filter Options File
Create a JSON file with filter options:
```json
{
  "pdf_options": {
    "ReduceImageResolution": {"type":"boolean","value":"true"},
    "MaxImageResolution": {"type":"long","value":"150"},
    "ExportBookmarks": {"type":"boolean","value":"true"}
  }
}
```

Use it in script:
```bash
# Read options from file
options=$(cat pdf_options.json | jq -r '.pdf_options | tostring')

# Use in conversion
libreoffice --headless --convert-to "pdf:writer_pdf_Export:$options" document.odt
```

## Troubleshooting Filters

### Common Issues

1. **Filter Not Found**
   ```bash
   # Check if filter exists
   libreoffice --headless --help | grep -i "filter-name"
   
   # Install additional packages
   sudo apt install libreoffice-{writer,calc,impress,draw}
   ```

2. **Encoding Problems**
   ```bash
   # Force UTF-8 encoding
   --infilter="Text (encoded):UTF8"
   
   # Specify CSV encoding
   --infilter="Text - txt - csv (StarCalc):44,34,4,1,1"  # UTF-8
   ```

3. **Option Syntax Errors**
   ```bash
   # Test simple conversion first
   libreoffice --headless --convert-to pdf document.odt
   
   # Then add options gradually
   libreoffice --headless --convert-to "pdf:writer_pdf_Export:{\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"}}" document.odt
   ```

4. **Performance Issues**
   ```bash
   # Disable Java if not needed
   --norestore --nofirststartwizard --nologo --headless
   
   # Use separate user installation
   -env:UserInstallation=file:///tmp/loffice_$(date +%s)
   ```

### Debug Mode
```bash
# Enable verbose output
libreoffice --headless --convert-to pdf document.odt 2>&1 | tee conversion.log

# Check filter loading
strace -e openat libreoffice --headless --version 2>&1 | grep -i filter

# Profile conversion
time libreoffice --headless --convert-to pdf large_document.odt
```

## Filter Compatibility Matrix

### LibreOffice Version Support
| Filter | LO 24.2+ | LO 7.0-24.1 | LO 6.0-6.4 | Notes |
|--------|----------|-------------|------------|-------|
| MS Word 2007 XML | ✅ Full | ✅ Good | ⚠️ Basic | DOCX export/import |
| Calc MS Excel 2007 XML | ✅ Full | ✅ Good | ⚠️ Basic | XLSX export/import |
| Impress MS PowerPoint 2007 XML | ✅ Full | ✅ Good | ⚠️ Basic | PPTX export/import |
| EPUB export | ✅ Full | ✅ Good | ⚠️ Limited | E-book format |
| PDF/A export | ✅ Full | ✅ Good | ⚠️ Basic | Archival PDF |
| HTML5 export | ✅ Full | ⚠️ Basic | ❌ Limited | Modern web format |

### Cross-Platform Compatibility
| Filter | Linux | macOS | Windows | Notes |
|--------|-------|-------|---------|-------|
| All native filters | ✅ | ✅ | ✅ | Core functionality |
| MS Office filters | ✅ | ✅ | ✅ | Best on Windows |
| PDF export | ✅ | ✅ | ✅ | Consistent |
| HTML export | ✅ | ✅ | ✅ | Font differences |
| Java-dependent filters | ⚠️ | ⚠️ | ⚠️ | Requires Java |

## Best Practices

1. **Use Specific Filters**: Always specify the exact filter for critical conversions
2. **Test Import/Export**: Verify round-trip conversion for important documents
3. **Check Encoding**: Explicitly set encoding for text-based formats
4. **Validate Output**: Use tools like `pdftotext`, `file`, `xmllint` to check results
5. **Keep Backups**: Always keep original files before batch conversions
6. **Monitor Resources**: Large conversions may need increased memory limits
7. **Update Regularly**: Newer LibreOffice versions have better filter support