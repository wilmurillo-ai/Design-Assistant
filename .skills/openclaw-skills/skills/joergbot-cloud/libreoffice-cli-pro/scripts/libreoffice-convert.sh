#!/bin/bash
# LibreOffice Convert Script
# Convert single documents between formats with simplified interface

set -e

# Source the check script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/libreoffice-check.sh"

# Default configuration
OUTPUT_DIR="${LIBREOFFICE_OUTPUT_DIR:-./}"
LIBREOFFICE_CMD="${LIBREOFFICE_CMD:-libreoffice}"
TIMEOUT="${LIBREOFFICE_TIMEOUT:-300}"  # 5 minutes default

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
LibreOffice Convert Script
Convert single documents between formats with simplified interface.

Usage: $0 [OPTIONS] <input_file> <output_format>

Options:
  -o, --output DIR      Output directory (default: ./)
  -f, --filter FILTER   Specific filter to use (e.g., "writer_pdf_Export")
  -p, --profile DIR     Use custom LibreOffice profile directory
  -t, --timeout SEC     Timeout in seconds (default: 300)
  -q, --quiet           Quiet mode (minimal output)
  -k, --keep-profile    Keep temporary profile after conversion
  -s, --stdin           Read input from stdin (specify format with --input-format)
  --input-format FORMAT Input format when using stdin (required with --stdin)
  -h, --help            Show this help message

Output Formats:
  pdf      Portable Document Format
  docx     Microsoft Word 2007+
  odt      OpenDocument Text
  xlsx     Microsoft Excel 2007+
  ods      OpenDocument Spreadsheet
  pptx     Microsoft PowerPoint 2007+
  odp      OpenDocument Presentation
  txt      Plain Text
  html     HTML Document
  epub     EPUB eBook

Common Filters:
  writer_pdf_Export     Writer to PDF
  calc_pdf_Export       Calc to PDF
  impress_pdf_Export    Impress to PDF
  "Text (encoded):UTF8" UTF-8 Text export

Examples:
  $0 document.docx pdf                 # Convert Word to PDF
  $0 spreadsheet.ods xlsx              # Convert ODS to Excel
  $0 presentation.pptx pdf -o ./pdfs/  # Convert to PDF in specific directory
  $0 -s --input-format txt pdf < input.txt  # Convert stdin to PDF
  $0 data.csv xlsx --filter "Calc MS Excel 2007 XML"  # CSV to Excel with filter

Environment Variables:
  LIBREOFFICE_OUTPUT_DIR  Default output directory
  LIBREOFFICE_CMD         LibreOffice command (default: libreoffice)
  LIBREOFFICE_TIMEOUT     Timeout in seconds

EOF
}

# Parse command line arguments
parse_args() {
    local input_file=""
    local output_format=""
    local output_dir="$OUTPUT_DIR"
    local filter=""
    local profile_dir=""
    local timeout="$TIMEOUT"
    local quiet=false
    local keep_profile=false
    local use_stdin=false
    local input_format=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -f|--filter)
                filter="$2"
                shift 2
                ;;
            -p|--profile)
                profile_dir="$2"
                shift 2
                ;;
            -t|--timeout)
                timeout="$2"
                shift 2
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            -k|--keep-profile)
                keep_profile=true
                shift
                ;;
            -s|--stdin)
                use_stdin=true
                shift
                ;;
            --input-format)
                input_format="$2"
                shift 2
                ;;
            --)
                shift
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                # First argument is input file, second is output format
                if [ -z "$input_file" ]; then
                    input_file="$1"
                elif [ -z "$output_format" ]; then
                    output_format="$1"
                else
                    log_error "Unexpected argument: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Handle stdin mode
    if [ "$use_stdin" = true ]; then
        if [ -z "$input_format" ]; then
            log_error "Input format required when using stdin (--input-format)"
            show_help
            exit 1
        fi
        
        # Create temporary file for stdin content
        input_file="/tmp/libreoffice_stdin_$(date +%s).$input_format"
        cat - > "$input_file"
        
        # Mark for cleanup
        CLEANUP_FILES+=("$input_file")
    fi
    
    # Validate required arguments
    if [ -z "$input_file" ]; then
        log_error "Input file is required"
        show_help
        exit 1
    fi
    
    if [ -z "$output_format" ]; then
        log_error "Output format is required"
        show_help
        exit 1
    fi
    
    # Validate input file (unless using stdin)
    if [ "$use_stdin" = false ] && [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        exit 1
    fi
    
    # Create output directory if it doesn't exist
    mkdir -p "$output_dir"
    
    # Return values
    ARG_INPUT="$input_file"
    ARG_FORMAT="$output_format"
    ARG_OUTPUT_DIR="$output_dir"
    ARG_FILTER="$filter"
    ARG_PROFILE_DIR="$profile_dir"
    ARG_TIMEOUT="$timeout"
    ARG_QUIET="$quiet"
    ARG_KEEP_PROFILE="$keep_profile"
    ARG_USE_STDIN="$use_stdin"
}

# Get output filename
get_output_filename() {
    local input_file="$1"
    local output_format="$2"
    local output_dir="$3"
    
    local input_basename=$(basename "$input_file")
    local input_name="${input_basename%.*}"
    
    # Handle special characters in filename
    local safe_name=$(echo "$input_name" | tr -c '[:alnum:]._-' '_')
    
    echo "$output_dir/$safe_name.$output_format"
}

# Build LibreOffice command
build_libreoffice_command() {
    local input_file="$1"
    local output_format="$2"
    local output_dir="$3"
    local filter="$4"
    local profile_dir="$5"
    local timeout="$6"
    
    local output_file=$(get_output_filename "$input_file" "$output_format" "$output_dir")
    
    # Start building command
    local cmd="timeout $timeout $LIBREOFFICE_CMD --headless"
    
    # Add profile directory if specified
    if [ -n "$profile_dir" ]; then
        mkdir -p "$profile_dir"
        cmd="$cmd -env:UserInstallation=file://$profile_dir"
    else
        # Use temporary profile to avoid conflicts
        local temp_profile="/tmp/libreoffice_profile_$(date +%s)"
        mkdir -p "$temp_profile"
        cmd="$cmd -env:UserInstallation=file://$temp_profile"
        
        # Mark for cleanup unless keep_profile is true
        if [ "$ARG_KEEP_PROFILE" = false ]; then
            CLEANUP_DIRS+=("$temp_profile")
        fi
    fi
    
    # Add filter if specified
    local convert_to="$output_format"
    if [ -n "$filter" ]; then
        convert_to="$output_format:$filter"
    fi
    
    # Add conversion command
    cmd="$cmd --convert-to \"$convert_to\" --outdir \"$output_dir\" \"$input_file\""
    
    echo "$cmd"
}

# Main function
main() {
    # Arrays for cleanup
    CLEANUP_FILES=()
    CLEANUP_DIRS=()
    
    # Parse arguments
    parse_args "$@"
    
    # Check LibreOffice health
    if [ "$ARG_QUIET" = true ]; then
        if ! check_libreoffice_health > /dev/null 2>&1; then
            exit 1
        fi
    else
        if ! check_libreoffice_health; then
            exit 1
        fi
    fi
    
    # Display conversion info
    if [ "$ARG_QUIET" = false ]; then
        echo -e "${BLUE}📄 LibreOffice Document Conversion${NC}"
        echo -e "${BLUE}Input:${NC} $ARG_INPUT"
        echo -e "${BLUE}Output Format:${NC} $ARG_FORMAT"
        echo -e "${BLUE}Output Directory:${NC} $ARG_OUTPUT_DIR"
        if [ -n "$ARG_FILTER" ]; then
            echo -e "${BLUE}Filter:${NC} $ARG_FILTER"
        fi
        echo ""
    fi
    
    # Get output filename
    local output_file=$(get_output_filename "$ARG_INPUT" "$ARG_FORMAT" "$ARG_OUTPUT_DIR")
    
    # Check if output file already exists
    if [ -f "$output_file" ]; then
        if [ "$ARG_QUIET" = false ]; then
            log_warning "Output file already exists: $output_file"
            log_warning "It will be overwritten."
        fi
    fi
    
    # Build and execute command
    local libreoffice_cmd=$(build_libreoffice_command \
        "$ARG_INPUT" \
        "$ARG_FORMAT" \
        "$ARG_OUTPUT_DIR" \
        "$ARG_FILTER" \
        "$ARG_PROFILE_DIR" \
        "$ARG_TIMEOUT")
    
    if [ "$ARG_QUIET" = false ]; then
        log_info "Converting document..."
        debug_log "Command: $libreoffice_cmd"
    fi
    
    # Execute conversion
    if eval "$libreoffice_cmd" > /dev/null 2>&1; then
        if [ "$ARG_QUIET" = false ]; then
            log_success "✅ Conversion successful!"
            echo -e "${BLUE}Output File:${NC} $output_file"
            echo -e "${BLUE}File Size:${NC} $(du -h "$output_file" | cut -f1)"
        else
            echo "$output_file"
        fi
    else
        log_error "❌ Conversion failed"
        
        # Provide helpful error messages
        if [ ! -f "$ARG_INPUT" ]; then
            log_error "Input file not found or not readable"
        elif ! check_libreoffice_installed > /dev/null 2>&1; then
            log_error "LibreOffice not found or not working"
        else
            log_error "Possible issues:"
            log_error "  - Unsupported file format"
            log_error "  - Corrupted input file"
            log_error "  - Insufficient permissions"
            log_error "  - LibreOffice configuration issue"
        fi
        
        exit 1
    fi
    
    # Cleanup temporary files
    for file in "${CLEANUP_FILES[@]}"; do
        rm -f "$file" 2>/dev/null
    done
    
    # Cleanup temporary directories
    if [ "$ARG_KEEP_PROFILE" = false ]; then
        for dir in "${CLEANUP_DIRS[@]}"; do
            rm -rf "$dir" 2>/dev/null
        done
    fi
    
    # Additional tips
    if [ "$ARG_QUIET" = false ]; then
        echo ""
        echo -e "${BLUE}💡 Tips:${NC}"
        echo "  • View file: xdg-open \"$output_file\" 2>/dev/null || open \"$output_file\""
        echo "  • Batch conversion: Use libreoffice-batch.sh for multiple files"
        echo "  • Text extraction: Use libreoffice-extract.sh for text content"
        
        if [ -n "$ARG_FILTER" ]; then
            echo "  • Filter used: $ARG_FILTER"
        fi
    fi
}

# Cleanup on exit
cleanup() {
    # Cleanup temporary files
    for file in "${CLEANUP_FILES[@]}"; do
        rm -f "$file" 2>/dev/null
    done
    
    # Cleanup temporary directories (if not keeping profile)
    if [ "${ARG_KEEP_PROFILE:-false}" = false ]; then
        for dir in "${CLEANUP_DIRS[@]}"; do
            rm -rf "$dir" 2>/dev/null
        done
    fi
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi