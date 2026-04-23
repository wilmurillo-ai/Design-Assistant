# LibreOffice CLI Examples

Practical examples and real-world usage scenarios for LibreOffice CLI operations.

## Basic Examples

### 1. Health Check
```bash
# Check LibreOffice installation
./scripts/libreoffice-check.sh health

# Check version compatibility
./scripts/libreoffice-check.sh version

# Test conversion capability
./scripts/libreoffice-check.sh conversion
```

### 2. Single Document Conversion
```bash
# Convert DOCX to PDF
./scripts/libreoffice-convert.sh document.docx pdf

# Convert ODT to DOCX
./scripts/libreoffice-convert.sh report.odt docx

# Convert XLSX to ODS
./scripts/libreoffice-convert.sh data.xlsx ods

# Convert PPT to PDF with specific quality
./scripts/libreoffice-convert.sh presentation.ppt pdf --quality high
```

### 3. Batch Conversion
```bash
# Convert all DOCX files in current directory to PDF
./scripts/libreoffice-batch.sh . pdf

# Convert ODT files in subdirectories
./scripts/libreoffice-batch.sh ./documents/ pdf --recursive

# Convert specific file types
./scripts/libreoffice-batch.sh . odt --pattern "*.docx"

# Convert with parallel processing (4 threads)
./scripts/libreoffice-batch.sh . pdf --threads 4
```

## Text Extraction Examples

### 1. Basic Text Extraction
```bash
# Extract text from PDF to console
./scripts/libreoffice-extract.sh document.pdf

# Extract text to file
./scripts/libreoffice-extract.sh report.docx --output extracted.txt

# Extract as HTML
./scripts/libreoffice-extract.sh manual.odt --format html --output manual.html

# Extract as JSON with metadata
./scripts/libreoffice-extract.sh data.pdf --format json --output data.json
```

### 2. Advanced Extraction
```bash
# Extract first 100 lines
./scripts/libreoffice-extract.sh long_document.pdf --lines 100

# Extract with UTF-8 encoding
./scripts/libreoffice-extract.sh document.txt --encoding UTF-8

# Clean extracted text (remove extra whitespace)
./scripts/libreoffice-extract.sh scanned.pdf --clean --output clean.txt

# Extract specific pages (requires pdftk)
./scripts/libreoffice-extract.sh book.pdf --pages 1-5,10-15
```

### 3. Batch Text Extraction
```bash
# Extract text from all PDFs in directory
for pdf in *.pdf; do
    ./scripts/libreoffice-extract.sh "$pdf" --output "${pdf%.pdf}.txt"
done

# Extract from multiple formats
find . -name "*.docx" -o -name "*.odt" -o -name "*.pdf" | while read file; do
    ./scripts/libreoffice-extract.sh "$file" --output "${file%.*}.txt"
done
```

## PDF Operations Examples

### 1. PDF Creation and Conversion
```bash
# Convert document to PDF
./scripts/libreoffice-pdf.sh convert document.docx --output document.pdf

# Convert with high quality
./scripts/libreoffice-pdf.sh convert presentation.pptx --output slides.pdf --quality high

# Convert with password protection
./scripts/libreoffice-pdf.sh convert confidential.docx --output secure.pdf --password "secret123"
```

### 2. PDF Merging
```bash
# Merge multiple documents into one PDF
./scripts/libreoffice-pdf.sh merge chapter1.docx chapter2.odt --output book.pdf

# Merge all DOCX files in directory
./scripts/libreoffice-pdf.sh merge *.docx --output combined.pdf

# Merge with sorted filenames
./scripts/libreoffice-pdf.sh merge *.odt --output sorted.pdf --sort

# Merge in reverse order
./scripts/libreoffice-pdf.sh merge intro.odt content.odt appendix.odt --output reverse.pdf --reverse
```

### 3. PDF Splitting
```bash
# Split PDF into individual pages
./scripts/libreoffice-pdf.sh split document.pdf --output-dir ./pages

# Split specific pages
./scripts/libreoffice-pdf.sh split report.pdf --pages 1-5 --output-dir ./executive_summary

# Split and convert to images
./scripts/libreoffice-pdf.sh split presentation.pdf --format png --output-dir ./slides
```

### 4. PDF Optimization
```bash
# Optimize PDF file size
./scripts/libreoffice-pdf.sh optimize large.pdf --compress 9

# Optimize with metadata removal
./scripts/libreoffice-pdf.sh optimize document.pdf --remove-metadata --output optimized.pdf

# Optimize images only
./scripts/libreoffice-pdf.sh optimize scanned.pdf --images --output scanned_optimized.pdf
```

### 5. PDF Information and Extraction
```bash
# Show PDF information
./scripts/libreoffice-pdf.sh info document.pdf

# Extract text from PDF
./scripts/libreoffice-pdf.sh extract scanned.pdf --text --output-dir ./extracted_text

# Extract images from PDF
./scripts/libreoffice-pdf.sh extract catalog.pdf --images --output-dir ./product_images

# Extract both text and images
./scripts/libreoffice-pdf.sh extract magazine.pdf --text --images --output-dir ./magazine_content
```

## Document Merging Examples

### 1. Basic Document Merging
```bash
# Merge ODT files
./scripts/libreoffice-merge.sh chapter1.odt chapter2.odt --output book.odt

# Merge different formats
./scripts/libreoffice-merge.sh intro.docx content.odt appendix.rtf --output complete.odt

# Merge to PDF
./scripts/libreoffice-merge.sh *.txt --output report.pdf --format pdf
```

### 2. Advanced Merging Options
```bash
# Merge with page breaks
./scripts/libreoffice-merge.sh part1.odt part2.odt --output combined.odt --page-break

# Merge with custom separator
./scripts/libreoffice-merge.sh *.txt --output merged.odt --separator "--- Next Document ---"

# Merge with table of contents
./scripts/libreoffice-merge.sh *.odt --output manual.odt --toc --title "User Manual"

# Merge sorted alphabetically
./scripts/libreoffice-merge.sh *.md --output documentation.odt --sort --author "Documentation Team"
```

### 3. Text-Based Merging
```bash
# Merge text files
./scripts/libreoffice-merge.sh file1.txt file2.txt file3.txt --output combined.txt

# Merge log files with timestamps
./scripts/libreoffice-merge.sh log_*.txt --output full_log.odt --separator "$(date)"

# Merge CSV data into spreadsheet
./scripts/libreoffice-merge.sh data1.csv data2.csv --output dataset.ods --format ods
```

## Real-World Workflows

### 1. Document Processing Pipeline
```bash
#!/bin/bash
# Process incoming documents: convert, extract, organize

INPUT_DIR="./incoming"
PROCESSED_DIR="./processed"
EXTRACTED_DIR="./extracted"

# 1. Check LibreOffice health
./scripts/libreoffice-check.sh health || exit 1

# 2. Convert all documents to PDF
./scripts/libreoffice-batch.sh "$INPUT_DIR" pdf --recursive --output "$PROCESSED_DIR"

# 3. Extract text from all PDFs
find "$PROCESSED_DIR" -name "*.pdf" | while read pdf; do
    base=$(basename "$pdf" .pdf)
    ./scripts/libreoffice-extract.sh "$pdf" --output "$EXTRACTED_DIR/$base.txt" --clean
done

# 4. Merge extracted text for analysis
./scripts/libreoffice-merge.sh "$EXTRACTED_DIR"/*.txt --output "$PROCESSED_DIR/combined_analysis.odt" --toc
```

### 2. Report Generation
```bash
#!/bin/bash
# Generate monthly report from data sources

# 1. Convert data sources to consistent format
./scripts/libreoffice-convert.sh sales_data.xlsx sales_data.ods
./scripts/libreoffice-convert.sh customer_feedback.docx feedback.odt

# 2. Extract key information
./scripts/libreoffice-extract.sh sales_data.ods --format json --output sales_summary.json
./scripts/libreoffice-extract.sh feedback.odt --output feedback.txt --lines 50

# 3. Create report sections
echo "# Monthly Sales Report" > report.md
cat sales_summary.json | jq '.content' >> report.md
echo "" >> report.md
echo "# Customer Feedback" >> report.md
cat feedback.txt >> report.md

# 4. Convert to final formats
./scripts/libreoffice-convert.sh report.md report.pdf --quality high
./scripts/libreoffice-convert.sh report.md report.docx
```

### 3. Archive Preparation
```bash
#!/bin/bash
# Prepare documents for long-term archiving

ARCHIVE_DIR="./archive_$(date +%Y%m)"
mkdir -p "$ARCHIVE_DIR"

# 1. Convert all documents to PDF/A (archival format)
find . -name "*.docx" -o -name "*.odt" -o -name "*.xlsx" | while read file; do
    ./scripts/libreoffice-convert.sh "$file" pdf --quality high --output "$ARCHIVE_DIR"
done

# 2. Optimize PDFs for storage
find "$ARCHIVE_DIR" -name "*.pdf" | while read pdf; do
    ./scripts/libreoffice-pdf.sh optimize "$pdf" --compress 9 --remove-metadata
done

# 3. Create index document
./scripts/libreoffice-merge.sh "$ARCHIVE_DIR"/*.pdf --output "$ARCHIVE_DIR/index.odt" --toc --title "Archive Index"
```

### 4. Email Attachment Processing
```bash
#!/bin/bash
# Process email attachments automatically

ATTACHMENT_DIR="./attachments"
PROCESSED_DIR="./processed"

# Process each attachment
for file in "$ATTACHMENT_DIR"/*; do
    # Convert to PDF if not already
    if [[ "$file" != *.pdf ]]; then
        ./scripts/libreoffice-convert.sh "$file" pdf --output "$PROCESSED_DIR"
    else
        cp "$file" "$PROCESSED_DIR"
    fi
    
    # Extract text for search indexing
    ./scripts/libreoffice-extract.sh "$file" --output "$PROCESSED_DIR/$(basename "$file").txt"
done

# Merge related documents
./scripts/libreoffice-merge.sh "$PROCESSED_DIR"/*.pdf --output "$PROCESSED_DIR/combined.pdf"
```

## Integration Examples

### 1. With Joplin Notes
```bash
#!/bin/bash
# Convert Joplin export to readable formats

JOPLIN_EXPORT="./joplin_export.json"
OUTPUT_DIR="./joplin_docs"

# Extract notes from Joplin export
jq -r '.items[] | select(.type_==1) | .title + "\n" + .body' "$JOPLIN_EXPORT" > notes.txt

# Split into individual notes
csplit -z notes.txt '/^===/' '{*}'

# Convert each note to PDF
for note in xx*; do
    ./scripts/libreoffice-convert.sh "$note" pdf --output "$OUTPUT_DIR"
done

# Create index
./scripts/libreoffice-merge.sh "$OUTPUT_DIR"/*.pdf --output "$OUTPUT_DIR/joplin_notes_index.pdf" --toc
```

### 2. With Gmail Integration
```bash
#!/bin/bash
# Process email attachments and save to Drive

# Fetch emails with attachments
gog mail search "has:attachment" --max-results 10 | while read email_id; do
    # Download attachments
    gog mail get "$email_id" --save-attachments ./attachments
    
    # Process each attachment
    for attachment in ./attachments/*; do
        # Convert to PDF
        ./scripts/libreoffice-convert.sh "$attachment" pdf --output ./processed
        
        # Upload to Google Drive
        gog drive upload "./processed/$(basename "$attachment").pdf" --folder "Processed Attachments"
    done
done
```

### 3. With Web Content
```bash
#!/bin/bash
# Convert web articles to readable formats

URL="https://example.com/article"
OUTPUT_FILE="article.pdf"

# Fetch web content
web_fetch "$URL" --extractMode markdown > article.md

# Convert to PDF
./scripts/libreoffice-convert.sh article.md pdf --output "$OUTPUT_FILE" --quality high

# Extract key points
./scripts/libreoffice-extract.sh "$OUTPUT_FILE" --lines 20 --output summary.txt
```

## Performance Optimization Examples

### 1. Parallel Processing
```bash
#!/bin/bash
# Convert large number of documents in parallel

INPUT_DIR="./documents"
OUTPUT_DIR="./converted"
THREADS=4

# Create function for parallel processing
convert_file() {
    local file="$1"
    ./scripts/libreoffice-convert.sh "$file" pdf --output "$OUTPUT_DIR"
}
export -f convert_file

# Process files in parallel
find "$INPUT_DIR" -name "*.docx" | parallel -j "$THREADS" convert_file
```

### 2. Memory Management
```bash
#!/bin/bash
# Process large documents with memory limits

# Set LibreOffice memory limits
export OOO_FORCE_DESKTOP=gnome
export SAL_USE_VCLPLUGIN=gen
export URE_BOOTSTRAP=vnd.sun.star.pathname:/usr/lib/libreoffice/program/fundamentalrc

# Process with separate user installations
for file in large_*.odt; do
    INSTALL_DIR="/tmp/lo_$(date +%s)"
    libreoffice -env:UserInstallation="file://$INSTALL_DIR" \
                --headless --convert-to pdf "$file"
    rm -rf "$INSTALL_DIR"
done
```

### 3. Batch Processing with Error Handling
```bash
#!/bin/bash
# Robust batch processing with logging and retries

LOG_FILE="./conversion.log"
ERROR_DIR="./failed"
MAX_RETRIES=3

process_file() {
    local file="$1"
    local retry=0
    
    while [ $retry -lt $MAX_RETRIES ]; do
        if ./scripts/libreoffice-convert.sh "$file" pdf 2>> "$LOG_FILE"; then
            echo "SUCCESS: $file" >> "$LOG_FILE"
            return 0
        else
            retry=$((retry + 1))
            echo "RETRY $retry: $file" >> "$LOG_FILE"
            sleep 2
        fi
    done
    
    echo "FAILED: $file" >> "$LOG_FILE"
    mv "$file" "$ERROR_DIR/"
    return 1
}

export -f process_file
find . -name "*.docx" -exec bash -c 'process_file "$0"' {} \;
```

## Troubleshooting Examples

### 1. Debug Conversion Issues
```bash
#!/bin/bash
# Debug problematic document conversions

PROBLEM_FILE="problematic.docx"
DEBUG_DIR="./debug"

# 1. Check file integrity
file "$PROBLEM_FILE"
md5sum "$PROBLEM_FILE"

# 2. Try different conversion methods
./scripts/libreoffice-convert.sh "$PROBLEM_FILE" pdf --verbose 2>&1 | tee "$DEBUG_DIR/conversion.log"

# 3. Try intermediate conversion
./scripts/libreoffice-convert.sh "$PROBLEM_FILE" odt --output "$DEBUG_DIR/intermediate.odt"
./scripts/libreoffice-convert.sh "$DEBUG_DIR/intermediate.odt" pdf

# 4. Extract and rebuild
./scripts/libreoffice-extract.sh "$PROBLEM_FILE" --output "$DEBUG_DIR/extracted.txt"
./scripts/libreoffice-convert.sh "$DEBUG_DIR/extracted.txt" pdf
```

### 2. Handle Encoding Problems
```bash
#!/bin/bash
# Fix document encoding issues

PROBLEM_FILE="weird_encoding.txt"

# Try different encodings
for encoding in UTF-8 ISO-8859-1 Windows-1252 UTF-16; do
    echo "Trying encoding: $encoding"
    iconv -f "$encoding" -t UTF-8 "$PROBLEM_FILE" > "test_$encoding.txt" 2>/dev/null
    if [ $? -eq 0 ]; then
        ./scripts/libreoffice-convert.sh "test_$encoding.txt" pdf && break
    fi
done

# Use LibreOffice with specific infilter
libreoffice --headless --infilter="Text (encoded):UTF8" \
            --convert-to pdf "$PROBLEM_FILE"
```

### 3. Repair Corrupted Documents
```bash
#!/bin/bash
# Attempt to repair corrupted Office documents

CORRUPTED_FILE="corrupted.docx"
REPAIR_DIR="./repair_attempts"

# 1. Extract as much as possible
./scripts/libreoffice-extract.sh "$CORRUPTED_FILE" --output "$REPAIR_DIR/extracted.txt"

# 2. Try different LibreOffice versions/options
libreoffice --headless --norestore --convert-to pdf "$CORRUPTED_FILE"

# 3. Use recovery mode
libreoffice --headless --safe-mode --convert-to pdf "$CORRUPTED_FILE"

# 4. Convert to intermediate format
libreoffice --headless --convert-to odt "$CORRUPTED_FILE"
libreoffice --headless --convert-to pdf "${CORRUPTED_FILE%.*}.odt"
```

## Automation Examples

### 1. Cron Job for Daily Processing
```bash
#!/bin/bash
# Daily document processing cron job

# Add to crontab: 0 2 * * * /path/to/daily_processing.sh

LOG_DIR="/var/log/libreoffice_processing"
PROCESSING_DIR="/home/user/documents_to_process"
ARCHIVE_DIR="/home/user/processed_archive/$(date +%Y-%m-%d)"

mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"

# Process new documents
./scripts/libreoffice-batch.sh "$PROCESSING_DIR"