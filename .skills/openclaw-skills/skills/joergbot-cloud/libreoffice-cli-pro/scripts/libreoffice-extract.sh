#!/bin/bash
# LibreOffice text extraction script
# Extract text content from various document formats

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 <input-file> [options]

Extract text content from documents using LibreOffice.

OPTIONS:
  -f, --format <format>    Output format: txt, html, md, json (default: txt)
  -o, --output <file>      Output file (default: stdout)
  -e, --encoding <enc>     Text encoding (default: UTF-8)
  -l, --lines <num>        Extract only first N lines
  -p, --pages <range>      Extract specific pages (e.g., 1-3,5,7-9)
  -c, --clean              Clean extracted text (remove extra whitespace)
  -v, --verbose            Verbose output
  -h, --help               Show this help

SUPPORTED INPUT FORMATS:
  .odt, .doc, .docx, .pdf, .txt, .html, .rtf, .epub, .xlsx, .ods, .pptx, .odp

EXAMPLES:
  $0 document.pdf --format txt --output extracted.txt
  $0 presentation.pptx --format html --pages 1-3
  $0 spreadsheet.xlsx --format json --clean
  $0 document.odt --lines 100 --encoding UTF-8
EOF
}

# Check if LibreOffice is available
check_libreoffice() {
    if ! command -v libreoffice &> /dev/null; then
        log_error "LibreOffice not found. Please install LibreOffice first."
        exit 1
    fi
}

# Get file extension
get_extension() {
    local filename="$1"
    echo "${filename##*.}" | tr '[:upper:]' '[:lower:]'
}

# Determine appropriate filter based on format
get_filter_for_format() {
    local format="$1"
    local encoding="${2:-UTF8}"
    
    case "$format" in
        txt)
            echo "txt:Text (encoded):$encoding"
            ;;
        html)
            echo "html:XHTML Writer File:UTF8"
            ;;
        md)
            echo "html:XHTML Writer File:UTF8"  # Convert to HTML then to Markdown
            ;;
        json)
            echo "txt:Text (encoded):$encoding"  # Base extraction, JSON formatting later
            ;;
        *)
            echo "txt:Text (encoded):$encoding"
            ;;
    esac
}

# Clean extracted text
clean_text() {
    local text="$1"
    
    # Remove multiple blank lines
    text=$(echo "$text" | sed '/^$/N;/^\n$/D')
    
    # Trim trailing whitespace
    text=$(echo "$text" | sed 's/[[:space:]]*$//')
    
    # Remove control characters (except newlines and tabs)
    text=$(echo "$text" | tr -d '\000-\010\013\014\016-\037')
    
    echo "$text"
}

# Convert HTML to Markdown (basic conversion)
html_to_markdown() {
    local html="$1"
    
    # Basic HTML to Markdown conversion
    echo "$html" | sed \
        -e 's/<h1>/# /g' -e 's/<\/h1>//g' \
        -e 's/<h2>/## /g' -e 's/<\/h2>//g' \
        -e 's/<h3>/### /g' -e 's/<\/h3>//g' \
        -e 's/<strong>\|<b>/**/g' -e 's/<\/strong>\|<\/b>/**/g' \
        -e 's/<em>\|<i>/*/g' -e 's/<\/em>\|<\/i>/*/g' \
        -e 's/<ul>//g' -e 's/<\/ul>//g' \
        -e 's/<li>/- /g' -e 's/<\/li>//g' \
        -e 's/<p>//g' -e 's/<\/p>/\n\n/g' \
        -e 's/<br[^>]*>/\n/g' \
        -e 's/<[^>]*>//g' | \
        sed -e 's/&lt;/</g' -e 's/&gt;/>/g' -e 's/&amp;/\&/g' \
            -e 's/&quot;/"/g' -e 's/&#39;/'\''/g'
}

# Format as JSON
format_as_json() {
    local text="$1"
    local filename="$2"
    local extension="$3"
    
    # Escape JSON special characters
    text=$(echo "$text" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/\\t/g' -e 's/\n/\\n/g' -e 's/\r/\\r/g')
    
    cat << EOF
{
  "filename": "$filename",
  "extension": "$extension",
  "content": "$text",
  "extracted_at": "$(date -Iseconds)",
  "character_count": ${#text},
  "line_count": $(echo "$text" | wc -l)
}
EOF
}

# Extract text from document
extract_text() {
    local input_file="$1"
    local format="$2"
    local encoding="$3"
    local output_file="$4"
    local clean="$5"
    local lines="$6"
    
    local extension
    extension=$(get_extension "$input_file")
    
    # Check if file exists
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        exit 1
    fi
    
    # Create temporary directory
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT
    
    log_info "Extracting text from: $input_file"
    
    # Get appropriate filter
    local filter
    filter=$(get_filter_for_format "$format" "$encoding")
    
    # Extract using LibreOffice
    if [ "$format" = "txt" ] || [ "$format" = "html" ]; then
        # Direct conversion for txt and html
        libreoffice --headless --convert-to "$filter" --outdir "$temp_dir" "$input_file" > /dev/null 2>&1
        
        # Find output file
        local base_name
        base_name=$(basename "$input_file" ".$extension")
        local output_path="$temp_dir/$base_name.$format"
        
        if [ -f "$output_path" ]; then
            local extracted_content
            extracted_content=$(cat "$output_path")
            
            # Apply cleaning if requested
            if [ "$clean" = "true" ]; then
                extracted_content=$(clean_text "$extracted_content")
            fi
            
            # Limit lines if requested
            if [ -n "$lines" ] && [ "$lines" -gt 0 ]; then
                extracted_content=$(echo "$extracted_content" | head -n "$lines")
            fi
            
            echo "$extracted_content"
            return 0
        else
            log_error "Extraction failed: output file not created"
            return 1
        fi
        
    elif [ "$format" = "md" ]; then
        # Extract as HTML then convert to Markdown
        libreoffice --headless --convert-to "html:XHTML Writer File:UTF8" --outdir "$temp_dir" "$input_file" > /dev/null 2>&1
        
        local base_name
        base_name=$(basename "$input_file" ".$extension")
        local html_path="$temp_dir/$base_name.html"
        
        if [ -f "$html_path" ]; then
            local html_content
            html_content=$(cat "$html_path")
            local markdown_content
            markdown_content=$(html_to_markdown "$html_content")
            
            # Apply cleaning if requested
            if [ "$clean" = "true" ]; then
                markdown_content=$(clean_text "$markdown_content")
            fi
            
            # Limit lines if requested
            if [ -n "$lines" ] && [ "$lines" -gt 0 ]; then
                markdown_content=$(echo "$markdown_content" | head -n "$lines")
            fi
            
            echo "$markdown_content"
            return 0
        else
            log_error "HTML extraction failed"
            return 1
        fi
        
    elif [ "$format" = "json" ]; then
        # Extract as text then format as JSON
        libreoffice --headless --convert-to "txt:Text (encoded):$encoding" --outdir "$temp_dir" "$input_file" > /dev/null 2>&1
        
        local base_name
        base_name=$(basename "$input_file" ".$extension")
        local txt_path="$temp_dir/$base_name.txt"
        
        if [ -f "$txt_path" ]; then
            local text_content
            text_content=$(cat "$txt_path")
            
            # Apply cleaning if requested
            if [ "$clean" = "true" ]; then
                text_content=$(clean_text "$text_content")
            fi
            
            # Limit lines if requested
            if [ -n "$lines" ] && [ "$lines" -gt 0 ]; then
                text_content=$(echo "$text_content" | head -n "$lines")
            fi
            
            format_as_json "$text_content" "$(basename "$input_file")" "$extension"
            return 0
        else
            log_error "Text extraction failed"
            return 1
        fi
        
    else
        log_error "Unsupported format: $format"
        return 1
    fi
}

# Main function
main() {
    # Check for required arguments
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    # Parse command line arguments
    local input_file=""
    local format="txt"
    local output_file=""
    local encoding="UTF8"
    local lines=""
    local pages=""
    local clean="false"
    local verbose="false"
    
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                show_usage
                exit 0
                ;;
            -f|--format)
                format="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -e|--encoding)
                encoding="$2"
                shift 2
                ;;
            -l|--lines)
                lines="$2"
                shift 2
                ;;
            -p|--pages)
                pages="$2"
                log_warning "Page extraction not yet implemented, extracting full document"
                shift 2
                ;;
            -c|--clean)
                clean="true"
                shift
                ;;
            -v|--verbose)
                verbose="true"
                shift
                ;;
            *)
                if [ -z "$input_file" ]; then
                    input_file="$1"
                else
                    log_error "Unknown argument: $1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Validate input file
    if [ -z "$input_file" ]; then
        log_error "No input file specified"
        show_usage
        exit 1
    fi
    
    # Check LibreOffice
    check_libreoffice
    
    # Validate format
    case "$format" in
        txt|html|md|json)
            # Valid format
            ;;
        *)
            log_error "Invalid format: $format. Supported formats: txt, html, md, json"
            exit 1
            ;;
    esac
    
    # Extract text
    local extracted_text
    if extracted_text=$(extract_text "$input_file" "$format" "$encoding" "$output_file" "$clean" "$lines"); then
        # Output to file or stdout
        if [ -n "$output_file" ]; then
            echo "$extracted_text" > "$output_file"
            log_success "Text extracted to: $output_file"
            
            if [ "$verbose" = "true" ]; then
                log_info "Character count: $(echo "$extracted_text" | wc -m)"
                log_info "Line count: $(echo "$extracted_text" | wc -l)"
            fi
        else
            echo "$extracted_text"
        fi
        return 0
    else
        log_error "Failed to extract text from $input_file"
        exit 1
    fi
}

# If script is executed directly, run main
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi