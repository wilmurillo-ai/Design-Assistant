#!/bin/bash
# LibreOffice PDF operations script
# PDF merge, split, optimize, and other PDF operations

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
Usage: $0 <command> [options]

PDF operations using LibreOffice.

COMMANDS:
  merge      Merge multiple documents into a single PDF
  split      Split PDF into individual pages
  optimize   Optimize/compress PDF file
  convert    Convert documents to PDF (alternative to libreoffice-convert.sh)
  info       Show PDF information
  extract    Extract text/images from PDF

OPTIONS BY COMMAND:

merge:
  $0 merge <input-files...> --output <output.pdf>
  Options:
    -o, --output <file>      Output PDF file (required)
    -s, --sort               Sort files alphabetically
    -r, --reverse            Reverse file order
    -q, --quality <level>    PDF quality: low, medium, high (default: medium)

split:
  $0 split <input.pdf> [options]
  Options:
    -o, --output-dir <dir>   Output directory (default: ./split_pages)
    -p, --pages <range>      Page range (e.g., 1-3,5,7-9)
    -f, --format <format>    Output format: pdf, png, jpg (default: pdf)

optimize:
  $0 optimize <input.pdf> [options]
  Options:
    -o, --output <file>      Output PDF file (default: <input>_optimized.pdf)
    -c, --compress <level>   Compression level: 1-9 (default: 6)
    -r, --remove-metadata    Remove metadata
    -i, --images             Optimize images only

convert:
  $0 convert <input-file> [options]
  Options:
    -o, --output <file>      Output PDF file
    -q, --quality <level>    PDF quality: low, medium, high
    -p, --password <pass>    PDF password protection

info:
  $0 info <input.pdf>

extract:
  $0 extract <input.pdf> [options]
  Options:
    -t, --text               Extract text only
    -i, --images             Extract images only
    -o, --output-dir <dir>   Output directory

EXAMPLES:
  $0 merge doc1.docx doc2.odt --output combined.pdf
  $0 split document.pdf --pages 1-5 --output-dir ./pages
  $0 optimize large.pdf --compress 9 --remove-metadata
  $0 convert presentation.pptx --output slides.pdf --quality high
  $0 info document.pdf
  $0 extract scanned.pdf --text --output-dir ./extracted
EOF
}

# Check if LibreOffice is available
check_libreoffice() {
    if ! command -v libreoffice &> /dev/null; then
        log_error "LibreOffice not found. Please install LibreOffice first."
        exit 1
    fi
}

# Check if pdftk is available (for advanced PDF operations)
check_pdftk() {
    if ! command -v pdftk &> /dev/null; then
        log_warning "pdftk not found. Some advanced PDF operations may be limited."
        return 1
    fi
    return 0
}

# Check if pdfinfo is available
check_pdfinfo() {
    if ! command -v pdfinfo &> /dev/null; then
        log_warning "pdfinfo not found. PDF information may be limited."
        return 1
    fi
    return 0
}

# Merge documents into PDF
merge_documents() {
    local input_files=("${@:1:$(($#-1))}")
    local output_file="${!#}"
    
    # Validate input files
    if [ ${#input_files[@]} -lt 2 ]; then
        log_error "Need at least 2 files to merge"
        return 1
    fi
    
    # Check if all input files exist
    for file in "${input_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Input file not found: $file"
            return 1
        fi
    done
    
    log_info "Merging ${#input_files[@]} documents into: $output_file"
    
    # Create temporary directory
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT
    
    # Convert each file to PDF first
    local pdf_files=()
    local counter=1
    
    for input_file in "${input_files[@]}"; do
        local base_name
        base_name=$(basename "$input_file")
        local pdf_file="$temp_dir/${counter}_${base_name%.*}.pdf"
        
        log_info "Converting: $input_file"
        
        if libreoffice --headless --convert-to pdf --outdir "$temp_dir" "$input_file" > /dev/null 2>&1; then
            # Find the converted PDF
            local converted_pdf
            converted_pdf=$(find "$temp_dir" -name "*.pdf" -newer "$temp_dir" | head -1)
            
            if [ -f "$converted_pdf" ]; then
                mv "$converted_pdf" "$pdf_file"
                pdf_files+=("$pdf_file")
                counter=$((counter + 1))
            else
                log_error "Failed to convert: $input_file"
                return 1
            fi
        else
            log_error "LibreOffice conversion failed for: $input_file"
            return 1
        fi
    done
    
    # Merge PDFs using pdftk if available
    if check_pdftk; then
        log_info "Merging PDFs using pdftk..."
        pdftk "${pdf_files[@]}" cat output "$output_file"
        
        if [ $? -eq 0 ] && [ -f "$output_file" ]; then
            log_success "PDFs merged successfully: $output_file"
            log_info "File size: $(du -h "$output_file" | cut -f1)"
            return 0
        fi
    fi
    
    # Fallback: Use LibreOffice to combine (convert all files at once)
    log_info "Using LibreOffice to merge documents..."
    
    # Create a temporary directory for merged output
    local merge_temp_dir
    merge_temp_dir=$(mktemp -d)
    
    # Convert all files at once to the same directory
    if libreoffice --headless --convert-to pdf --outdir "$merge_temp_dir" "${input_files[@]}" > /dev/null 2>&1; then
        # Get all converted PDFs
        local converted_pdfs=()
        while IFS= read -r pdf; do
            converted_pdfs+=("$pdf")
        done < <(find "$merge_temp_dir" -name "*.pdf" | sort)
        
        # Try to merge with pdftk again or just copy if only one
        if [ ${#converted_pdfs[@]} -eq 1 ]; then
            cp "${converted_pdfs[0]}" "$output_file"
            log_success "Single document converted to PDF: $output_file"
            return 0
        elif check_pdftk && [ ${#converted_pdfs[@]} -gt 1 ]; then
            pdftk "${converted_pdfs[@]}" cat output "$output_file"
            if [ -f "$output_file" ]; then
                log_success "PDFs merged successfully: $output_file"
                return 0
            fi
        else
            log_warning "Could not merge multiple PDFs. First PDF saved as: $output_file"
            cp "${converted_pdfs[0]}" "$output_file"
            return 0
        fi
    fi
    
    log_error "Failed to merge documents"
    return 1
}

# Split PDF into pages
split_pdf() {
    local input_file="$1"
    local output_dir="${2:-./split_pages}"
    local page_range="$3"
    local format="${4:-pdf}"
    
    # Validate input file
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        return 1
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    log_info "Splitting PDF: $input_file"
    log_info "Output directory: $output_dir"
    log_info "Format: $format"
    
    # Use pdftk for splitting if available
    if check_pdftk; then
        if [ -n "$page_range" ]; then
            log_info "Splitting pages: $page_range"
            pdftk "$input_file" cat "$page_range" output "$output_dir/split.pdf"
            
            if [ -f "$output_dir/split.pdf" ]; then
                log_success "Pages extracted to: $output_dir/split.pdf"
                return 0
            fi
        else
            # Split all pages
            pdftk "$input_file" burst output "$output_dir/page_%03d.pdf"
            
            local page_count
            page_count=$(find "$output_dir" -name "page_*.pdf" | wc -l)
            
            if [ "$page_count" -gt 0 ]; then
                log_success "Split $page_count pages to $output_dir"
                return 0
            fi
        fi
    fi
    
    # Fallback: Use LibreOffice to convert PDF to images or other formats
    log_warning "pdftk not available, using LibreOffice for conversion"
    
    case "$format" in
        pdf)
            log_error "PDF splitting requires pdftk. Please install pdftk."
            return 1
            ;;
        png|jpg|jpeg)
            log_info "Converting PDF pages to $format images..."
            
            # Convert PDF to images using LibreOffice
            libreoffice --headless --convert-to "$format" --outdir "$output_dir" "$input_file" > /dev/null 2>&1
            
            local image_count
            image_count=$(find "$output_dir" -name "*.$format" | wc -l)
            
            if [ "$image_count" -gt 0 ]; then
                log_success "Converted $image_count pages to $format images"
                return 0
            else
                log_error "Failed to convert PDF to images"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported format for splitting: $format"
            return 1
            ;;
    esac
}

# Optimize/compress PDF
optimize_pdf() {
    local input_file="$1"
    local output_file="${2:-${input_file%.*}_optimized.pdf}"
    local compress_level="${3:-6}"
    
    # Validate input file
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        return 1
    fi
    
    log_info "Optimizing PDF: $input_file"
    log_info "Output file: $output_file"
    log_info "Compression level: $compress_level"
    
    # Check for Ghostscript (gs) for PDF optimization
    if command -v gs &> /dev/null; then
        log_info "Using Ghostscript for PDF optimization..."
        
        local gs_options=()
        
        # Set compression level
        case "$compress_level" in
            1|2|3) gs_options+=("-dPDFSETTINGS=/screen") ;;   # Low quality
            4|5|6) gs_options+=("-dPDFSETTINGS=/ebook") ;;    # Medium quality
            7|8|9) gs_options+=("-dPDFSETTINGS=/printer") ;;  # High quality
            *) gs_options+=("-dPDFSETTINGS=/ebook") ;;
        esac
        
        # Additional optimization options
        gs_options+=("-dCompatibilityLevel=1.4")
        gs_options+=("-dPDFA=2")
        gs_options+=("-dNOPAUSE")
        gs_options+=("-dBATCH")
        gs_options+=("-dQUIET")
        
        # Run Ghostscript
        gs -sDEVICE=pdfwrite "${gs_options[@]}" \
           -sOutputFile="$output_file" \
           "$input_file" > /dev/null 2>&1
        
        if [ $? -eq 0 ] && [ -f "$output_file" ]; then
            local original_size
            original_size=$(du -h "$input_file" | cut -f1)
            local optimized_size
            optimized_size=$(du -h "$output_file" | cut -f1)
            
            log_success "PDF optimized successfully"
            log_info "Original size: $original_size"
            log_info "Optimized size: $optimized_size"
            return 0
        fi
    fi
    
    # Fallback: Use LibreOffice to re-convert (simple optimization)
    log_warning "Ghostscript not available, using LibreOffice for basic optimization..."
    
    # Convert PDF to PDF (re-save with LibreOffice)
    libreoffice --headless --convert-to pdf --outdir "$(dirname "$output_file")" "$input_file" > /dev/null 2>&1
    
    # Find the converted file
    local converted_file
    converted_file=$(find "$(dirname "$output_file")" -name "*.pdf" -newer "$input_file" | head -1)
    
    if [ -f "$converted_file" ] && [ "$converted_file" != "$input_file" ]; then
        mv "$converted_file" "$output_file"
        log_success "PDF re-saved (basic optimization): $output_file"
        return 0
    else
        log_error "Failed to optimize PDF"
        return 1
    fi
}

# Convert document to PDF
convert_to_pdf() {
    local input_file="$1"
    local output_file="${2:-${input_file%.*}.pdf}"
    local quality="${3:-medium}"
    
    # Validate input file
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        return 1
    fi
    
    log_info "Converting to PDF: $input_file"
    log_info "Output file: $output_file"
    log_info "Quality: $quality"
    
    # Set LibreOffice options based on quality
    local lo_options="--headless"
    
    case "$quality" in
        low)
            lo_options="$lo_options --convert-to pdf:writer_pdf_Export:{\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"},\"MaxImageResolution\":{\"type\":\"long\",\"value\":\"150\"}}"
            ;;
        high)
            lo_options="$lo_options --convert-to pdf:writer_pdf_Export:{\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"false\"},\"SelectPdfVersion\":{\"type\":\"long\",\"value\":\"1\"}}"
            ;;
        medium|*)
            lo_options="$lo_options --convert-to pdf"
            ;;
    esac
    
    # Convert using LibreOffice
    if libreoffice $lo_options --outdir "$(dirname "$output_file")" "$input_file" > /dev/null 2>&1; then
        # Find the converted file
        local converted_file
        converted_file=$(find "$(dirname "$output_file")" -name "*.pdf" -newer "$input_file" | head -1)
        
        if [ -f "$converted_file" ] && [ "$converted_file" != "$input_file" ]; then
            if [ "$converted_file" != "$output_file" ]; then
                mv "$converted_file" "$output_file"
            fi
            log_success "Converted to PDF: $output_file"
            log_info "File size: $(du -h "$output_file" | cut -f1)"
            return 0
        fi
    fi
    
    log_error "Failed to convert to PDF"
    return 1
}

# Show PDF information
show_pdf_info() {
    local input_file="$1"
    
    # Validate input file
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        return 1
    fi
    
    log_info "PDF Information: $input_file"
    echo "========================================"
    
    # Basic file info
    echo "File: $(basename "$input_file")"
    echo "Path: $(realpath "$input_file")"
    echo "Size: $(du -h "$input_file" | cut -f1)"
    echo "Modified: $(date -r "$input_file")"
    
    # Try to get PDF-specific info
    if check_pdfinfo; then
        echo ""
        echo "PDF Details:"
        pdfinfo "$input_file" 2>/dev/null | grep -E "^(Pages|Page size|Encrypted|PDF version|Creator|Producer):" || true
    fi
    
    # Try LibreOffice info
    echo ""
    echo "LibreOffice Analysis:"
    if file "$input_file" | grep -q "PDF document"; then
        echo "✓ Valid PDF document"
        
        # Try to extract metadata with exiftool if available
        if command -v exiftool &> /dev/null; then
            echo "Metadata available via exiftool"
        fi
    else
        echo "⚠ Not a recognized PDF file"
    fi
    
    echo "========================================"
}

# Extract content from PDF
extract_from_pdf() {
    local input_file="$1"
    local extract_text="$2"
    local extract_images="$3"
    local output_dir="${4:-./extracted}"
    
    # Validate input file
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        return 1
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    log_info "Extracting from PDF: $input_file"
    log_info "Output directory: $output_dir"
    
    # Extract text if requested
    if [ "$extract_text" = "true" ]; then
        log_info "Extracting text..."
        
        # Use pdftotext if available
        if command -v pdftotext &> /dev/null; then
            local text_file="$output_dir/$(basename "$input_file" .pdf).txt"
            pdftotext "$input_file" "$text_file"
            
            if [ -f "$text_file" ]; then
                log_success "Text extracted to: $text_file"
                log_info "Text size: $(wc -w < "$text_file") words"
            fi
        else
            # Use LibreOffice to extract text
            libreoffice --headless --convert-to "txt:Text (encoded):UTF8" --outdir "$output_dir" "$input_file" > /dev/null 2>&1
            
            local text_files
            text_files=$(find "$output_dir" -name "*.txt" -newer "$input_file")
            
            if [ -n "$text_files" ]; then
                log_success "Text extracted using LibreOffice"
            else
                log_warning "Text extraction may require pdftotext for better results"
            fi
        fi
    fi
    
    # Extract images if requested
    if [ "$extract_images" = "true" ]; then
        log_info "Extracting images..."
        
        # Use pdfimages if available
        if command -v pdfimages &> /dev/null; then
            local images_dir="$output_dir/images"
            mkdir -p "$images_dir"
            
            pdfimages -all "$input_file" "$images_dir/image"
            
            local image_count
            image_count=$(find "$images_dir" -name "image*" -type f | wc -l)
            
            if [ "$image_count" -gt 0 ]; then
                log_success "Extracted $image_count images to: $images_dir"
            fi
        else
            log_warning "pdfimages not available. Image extraction requires pdfimages tool."
        fi
    fi
    
    # If neither text nor images specified, extract both
    if [ "$extract_text" != "true" ] && [ "$extract_images" != "true" ]; then
        log_info "Extracting both text and images..."
        extract_from_pdf "$input_file" "true" "true" "$output_dir"
    fi
    
    log_success "Extraction complete. Files saved in: $output_dir"
}

# Main function
main() {
    # Check for required arguments
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    # Check LibreOffice
    check_libreoffice
    
    local command="$1"
    shift
    
    case "$command" in
        merge)
            # Parse merge options
            local input_files=()
            local output_file=""
            local sort_files="false"
            local reverse_order="false"
            local quality="medium"
            
            while [ $# -gt 0 ]; do
                case "$1" in
                    -o|--output)
                        output_file="$2"
                        shift 2
                        ;;
                    -s|--sort)
                        sort_files="true"
                        shift
                        ;;
                    -r|--reverse)
                        reverse_order="true"
                        shift
                        ;;
                    -q|--quality)
                        quality="$2"
                        shift 2
                        ;;
                    --)
                        shift
                        break
                        ;;
                    -*)
                        log_error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                    *)
                        input_files+=("$1")
                        shift
                        ;;
                esac
            done
            
            # Add any remaining arguments
            input_files+=("$@")
            
            if [ ${#input_files[@]} -lt 2 ]; then
                log_error "Need at least 2 files to merge"
                show_usage
                exit 1
            fi
            
            if [ -z "$output_file" ]; then
                log_error "Output file required for merge"
                show_usage
                exit 1
            fi
            
            # Sort files if requested
            if [ "$sort_files" = "true" ]; then
                IFS=$'\n' input_files=($(sort <<<"${input_files[*]}"))
                unset IFS
            fi
            
            # Reverse order if requested
            if [ "$reverse_order" = "true" ]; then
                local reversed_files=()
                for ((i=${#input_files[@]}-1; i>=0; i--)); do
                    reversed_files+=("${input_files[i]}")
                done
                input_files=("${reversed_files[@]}")
            fi
            
            merge_documents "${input_files[@]}" "$output_file"
            ;;
            
        split)
            # Parse split options
            local input_file=""
            local output_dir="./split_pages"
            local page_range=""
            local format="pdf"
            
            while [ $# -gt 0 ]; do
                case "$1" in
                    -o|--output-dir)
                        output_dir="$2"
                        shift 2
                        ;;
                    -p|--pages)
                        page_range="$2"
                        shift 2
                        ;;
                    -f|--format)
                        format="$2"
                        shift 2
                        ;;
                    -*)
                        log_error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                    *)
                        if [ -z "$input_file" ]; then
                            input_file="$1"
                        else
                            log_error "Multiple input files not supported for split"
                            show_usage
                            exit 1
                        fi
                        shift
                        ;;
                esac
            done
            
            if [ -z "$input_file" ]; then
                log_error "Input file required for split"
                show_usage
                exit 1
            fi
            
            split_pdf "$input_file" "$output_dir" "$page_range" "$format"
            ;;
            
        optimize)
            # Parse optimize options
            local input_file=""
            local output_file=""
            local compress_level="6"
            local remove_metadata="false"
            local optimize_images="false"
            
            while [ $# -gt 0 ]; do
                case "$1" in
                    -o|--output)
                        output_file="$2"
                        shift 2
                        ;;
                    -c|--compress)
                        compress_level="$2"
                        shift 2
                        ;;
                    -r|--remove-metadata)
                        remove_metadata="true"
                        shift
                        ;;
                    -i|--images)
                        optimize_images="true"
                        shift
                        ;;
                    -*)
                        log_error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                    *)
                        if [ -z "$input_file" ]; then
                            input_file="$1"
                        else
                            log_error "Multiple input files not supported for optimize"
                            show_usage
                            exit 1
                        fi
                        shift
                        ;;
                esac
            done
            
            if [ -z "$input_file" ]; then
                log_error "Input file required for optimize"
                show_usage
                exit 1
            fi
            
            if [ -z "$output_file" ]; then
                output_file="${input_file%.*}_optimized.pdf"
            fi
            
            optimize_pdf "$input_file" "$output_file" "$compress_level"
            ;;
            
        convert)
            # Parse convert options
            local input_file=""
            local output_file=""
            local quality="medium"
            local password=""
            
            while [ $# -gt 0 ]; do
                case "$1" in
                    -o|--output)
                        output_file="$2"
                        shift 2
                        ;;
                    -q|--quality)
                        quality="$2"
                        shift 2
                        ;;
                    -p|--password)
                        password="$2"
                        shift 2
                        ;;
                    -*)
                        log_error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                    *)
                        if [ -z "$input_file" ]; then
                            input_file="$1"
                        else
                            log_error "Multiple input files not supported for convert"
                            show_usage
                            exit 1
                        fi
                        shift
                        ;;
                esac
            done
            
            if [ -z "$input_file" ]; then
                log_error "Input file required for convert"
                show_usage
                exit 1
            fi
            
            convert_to_pdf "$input_file" "$output_file" "$quality"
            ;;
            
        info)
            if [ $# -lt 1 ]; then
                log_error "Input file required for info"
                show_usage
                exit 1
            fi
            show_pdf_info "$1"
            ;;
            
        extract)
            # Parse extract options
            local input_file=""
            local extract_text="false"
            local extract_images="false"
            local output_dir="./extracted"
            
            while [ $# -gt 0 ]; do
                case "$1" in
                    -t|--text)
                        extract_text="true"
                        shift
                        ;;
                    -i|--images)
                        extract_images="true"
                        shift
                        ;;
                    -o|--output-dir)
                        output_dir="$2"
                        shift 2
                        ;;
                    -*)
                        log_error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                    *)
                        if [ -z "$input_file" ]; then
                            input_file="$1"
                        else
                            log_error "Multiple input files not supported for extract"
                            show_usage
                            exit 1
                        fi
                        shift
                        ;;
                esac
            done
            
            if [ -z "$input_file" ]; then
                log_error "Input file required for extract"
                show_usage
                exit 1
            fi
            
            extract_from_pdf "$input_file" "$extract_text" "$extract_images" "$output_dir"
            ;;
            
        help|--help|-h)
            show_usage
            ;;
            
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# If script is executed directly, run main
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi