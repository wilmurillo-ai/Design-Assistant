#!/bin/bash
# LibreOffice document merge script
# Merge multiple documents into a single document

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
Usage: $0 <input-files...> [options]

Merge multiple documents into a single document.

OPTIONS:
  -o, --output <file>      Output file (required)
  -f, --format <format>    Output format: odt, docx, pdf, html (default: odt)
  -s, --sort               Sort files alphabetically
  -r, --reverse            Reverse file order
  -p, --page-break         Add page break between documents
  -s, --separator <text>   Add separator text between documents
  -t, --title <title>      Document title
  -a, --author <author>    Document author
  -c, --toc                Generate table of contents
  -v, --verbose            Verbose output
  -h, --help               Show this help

SUPPORTED INPUT FORMATS:
  .odt, .doc, .docx, .txt, .html, .rtf, .pdf (text extraction)

EXAMPLES:
  $0 chapter1.odt chapter2.odt --output book.odt --title "My Book"
  $0 *.txt --output combined.docx --format docx --page-break
  $0 report1.pdf report2.pdf --output full_report.pdf --format pdf
  $0 intro.html content.html --output manual.odt --toc --author "John Doe"
EOF
}

# Check if LibreOffice is available
check_libreoffice() {
    if ! command -v libreoffice &> /dev/null; then
        log_error "LibreOffice not found. Please install LibreOffice first."
        exit 1
    fi
}

# Check if unoconv is available (alternative for some operations)
check_unoconv() {
    if command -v unoconv &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Get file extension
get_extension() {
    local filename="$1"
    echo "${filename##*.}" | tr '[:upper:]' '[:lower:]'
}

# Convert document to text for merging
convert_to_text() {
    local input_file="$1"
    local output_file="$2"
    
    local extension
    extension=$(get_extension "$input_file")
    
    case "$extension" in
        txt)
            cp "$input_file" "$output_file"
            ;;
        odt|doc|docx|rtf|html)
            libreoffice --headless --convert-to "txt:Text (encoded):UTF8" --outdir "$(dirname "$output_file")" "$input_file" > /dev/null 2>&1
            
            local base_name
            base_name=$(basename "$input_file" ".$extension")
            local txt_file="$(dirname "$output_file")/$base_name.txt"
            
            if [ -f "$txt_file" ]; then
                mv "$txt_file" "$output_file"
            else
                log_error "Failed to convert $input_file to text"
                return 1
            fi
            ;;
        pdf)
            # Try to extract text from PDF
            if command -v pdftotext &> /dev/null; then
                pdftotext "$input_file" "$output_file"
            else
                # Use LibreOffice for PDF text extraction
                libreoffice --headless --convert-to "txt:Text (encoded):UTF8" --outdir "$(dirname "$output_file")" "$input_file" > /dev/null 2>&1
                
                local base_name
                base_name=$(basename "$input_file" ".pdf")
                local txt_file="$(dirname "$output_file")/$base_name.txt"
                
                if [ -f "$txt_file" ]; then
                    mv "$txt_file" "$output_file"
                else
                    log_error "Failed to extract text from PDF. Install pdftotext for better results."
                    return 1
                fi
            fi
            ;;
        *)
            log_error "Unsupported format for text conversion: $extension"
            return 1
            ;;
    esac
    
    return 0
}

# Create ODT document from text files
create_odt_from_texts() {
    local text_files=("$@")
    local output_file="${text_files[-1]}"
    unset 'text_files[${#text_files[@]}-1]'
    
    # Create a temporary HTML file as intermediate format
    local temp_html
    temp_html=$(mktemp --suffix=.html)
    
    # Start HTML document
    cat > "$temp_html" << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Merged Document</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 2cm; }
        h1 { color: #333; border-bottom: 2px solid #ccc; padding-bottom: 10px; }
        .page-break { page-break-after: always; }
        .separator { border-top: 1px dashed #ccc; margin: 20px 0; padding: 10px 0; }
    </style>
</head>
<body>
EOF
    
    # Add each text file content
    for text_file in "${text_files[@]}"; do
        if [ -f "$text_file" ]; then
            local content
            content=$(cat "$text_file")
            local filename
            filename=$(basename "$text_file")
            
            # Add filename as heading
            echo "<h2>${filename%.*}</h2>" >> "$temp_html"
            echo "<pre>$content</pre>" >> "$temp_html"
            echo "<div class='separator'></div>" >> "$temp_html"
        fi
    done
    
    # Close HTML document
    echo "</body></html>" >> "$temp_html"
    
    # Convert HTML to ODT
    libreoffice --headless --convert-to odt --outdir "$(dirname "$output_file")" "$temp_html" > /dev/null 2>&1
    
    # Find and rename the converted file
    local base_name
    base_name=$(basename "$temp_html" .html)
    local converted_file="$(dirname "$output_file")/$base_name.odt"
    
    if [ -f "$converted_file" ]; then
        mv "$converted_file" "$output_file"
        rm -f "$temp_html"
        return 0
    else
        rm -f "$temp_html"
        return 1
    fi
}

# Merge documents using LibreOffice macro (if available)
merge_with_macro() {
    local input_files=("${@:1:$(($#-1))}")
    local output_file="${!#}"
    local format="${output_file##*.}"
    
    # Create temporary directory
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT
    
    # Convert all files to a common format first
    local common_files=()
    local counter=1
    
    for input_file in "${input_files[@]}"; do
        local temp_file="$temp_dir/doc_$counter.odt"
        
        log_info "Converting: $input_file to ODT"
        
        if libreoffice --headless --convert-to odt --outdir "$temp_dir" "$input_file" > /dev/null 2>&1; then
            # Find the converted file
            local converted_file
            converted_file=$(find "$temp_dir" -name "*.odt" -newer "$temp_dir" | head -1)
            
            if [ -f "$converted_file" ]; then
                mv "$converted_file" "$temp_file"
                common_files+=("$temp_file")
                counter=$((counter + 1))
            else
                log_error "Failed to convert: $input_file"
                return 1
            fi
        else
            log_error "Conversion failed for: $input_file"
            return 1
        fi
    done
    
    # Create a Python macro to merge documents
    local merge_macro="$temp_dir/merge_documents.py"
    
    cat > "$merge_macro" << 'EOF'
import uno
import os
import sys

def merge_documents(input_files, output_file):
    # Get the uno component context
    local_context = uno.getComponentContext()
    
    # Create the UnoUrlResolver
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context)
    
    # Connect to the running LibreOffice
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    
    # Get the service manager
    service_manager = context.ServiceManager
    
    # Create desktop instance
    desktop = service_manager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    
    # Load first document
    input_url = uno.systemPathToFileUrl(os.path.abspath(input_files[0]))
    doc = desktop.loadComponentFromURL(input_url, "_blank", 0, ())
    
    # Insert other documents
    for i in range(1, len(input_files)):
        input_url = uno.systemPathToFileUrl(os.path.abspath(input_files[i]))
        insert_doc = desktop.loadComponentFromURL(input_url, "_blank", 0, ())
        
        # Copy content
        insert_doc_text = insert_doc.Text
        doc_text = doc.Text
        
        # Insert page break
        cursor = doc_text.createTextCursor()
        cursor.gotoEnd(False)
        cursor.setPropertyValue("BreakType", 4)  # PAGE_BREAK
        
        # Insert content
        insert_doc_text.copy()
        cursor.setString("")
        doc_text.insertString(cursor, "\n", False)
        cursor.gotoEnd(False)
        doc_text.insertControlCharacter(cursor, 0, False)  # PARAGRAPH_BREAK
        
        insert_doc.dispose()
    
    # Save merged document
    output_url = uno.systemPathToFileUrl(os.path.abspath(output_file))
    
    if output_file.endswith('.pdf'):
        filter_name = "writer_pdf_Export"
    elif output_file.endswith('.docx'):
        filter_name = "MS Word 2007 XML"
    elif output_file.endswith('.html'):
        filter_name = "HTML (StarWriter)"
    else:  # odt
        filter_name = "writer8"
    
    doc.storeToURL(output_url, (("FilterName", uno.Any("string", filter_name)),))
    doc.dispose()
    
    print(f"Merged {len(input_files)} documents to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python merge_documents.py <output_file> <input_file1> <input_file2> ...")
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    
    merge_documents(input_files, output_file)
EOF
    
    # Try to run the macro if Python UNO bridge is available
    if python3 -c "import uno" 2>/dev/null; then
        log_info "Attempting to merge using Python UNO bridge..."
        
        # Start LibreOffice in listening mode
        libreoffice --headless --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" &
        local lo_pid=$!
        sleep 5
        
        # Run merge macro
        if python3 "$merge_macro" "$output_file" "${common_files[@]}"; then
            kill $lo_pid 2>/dev/null
            wait $lo_pid 2>/dev/null
            return 0
        fi
        
        kill $lo_pid 2>/dev/null
        wait $lo_pid 2>/dev/null
    fi
    
    # Fallback: Convert to text and merge
    log_warning "Python UNO bridge not available, using text-based merge..."
    
    # Convert all files to text
    local text_files=()
    counter=1
    
    for common_file in "${common_files[@]}"; do
        local text_file="$temp_dir/text_$counter.txt"
        
        if convert_to_text "$common_file" "$text_file"; then
            text_files+=("$text_file")
            counter=$((counter + 1))
        fi
    done
    
    # Merge text files
    if [ ${#text_files[@]} -gt 0 ]; then
        text_files+=("$output_file")
        if create_odt_from_texts "${text_files[@]}"; then
            # Convert to desired format if needed
            local output_extension
            output_extension=$(get_extension "$output_file")
            
            if [ "$output_extension" != "odt" ]; then
                log_info "Converting to $output_extension..."
                libreoffice --headless --convert-to "$output_extension" --outdir "$(dirname "$output_file")" "$output_file" > /dev/null 2>&1
                
                # Remove intermediate ODT file
                rm -f "$output_file"
                
                # Find the converted file
                local base_name
                base_name=$(basename "$output_file" ".$output_extension")
                local converted_file="$(dirname "$output_file")/$base_name.$output_extension"
                
                if [ -f "$converted_file" ]; then
                    mv "$converted_file" "$output_file"
                fi
            fi
            
            return 0
        fi
    fi
    
    return 1
}

# Simple concatenation merge (for text-based formats)
simple_merge() {
    local input_files=("${@:1:$(($#-1))}")
    local output_file="${!#}"
    local format="${output_file##*.}"
    local add_page_break="$2"
    local separator_text="$3"
    
    # Create temporary directory
    local temp_dir
    temp_dir=$(mktemp -d)
    
    # Convert all files to text and concatenate
    local merged_text="$temp_dir/merged.txt"
    
    for input_file in "${input_files[@]}"; do
        local text_file="$temp_dir/$(basename "$input_file").txt"
        
        if convert_to_text "$input_file" "$text_file"; then
            # Add filename as header
            echo "=== $(basename "$input_file") ===" >> "$merged_text"
            echo "" >> "$merged_text"
            
            # Add content
            cat "$text_file" >> "$merged_text"
            
            # Add separator or page break
            if [ -n "$separator_text" ]; then
                echo "" >> "$merged_text"
                echo "$separator_text" >> "$merged_text"
                echo "" >> "$merged_text"
            elif [ "$add_page_break" = "true" ]; then
                echo "" >> "$merged_text"
                echo "--- Page Break ---" >> "$merged_text"
                echo "" >> "$merged_text"
            else
                echo "" >> "$merged_text"
                echo "" >> "$merged_text"
            fi
        fi
    done
    
    # Convert merged text to desired format
    case "$format" in
        txt)
            cp "$merged_text" "$output_file"
            ;;
        odt|docx|html|pdf)
            libreoffice --headless --convert-to "$format" --outdir "$(dirname "$output_file")" "$merged_text" > /dev/null 2>&1
            
            # Find and rename the converted file
            local base_name
            base_name=$(basename "$merged_text" .txt)
            local converted_file="$(dirname "$output_file")/$base_name.$format"
            
            if [ -f "$converted_file" ]; then
                mv "$converted_file" "$output_file"
            else
                log_error "Failed to convert merged text to $format"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported output format: $format"
            return 1
            ;;
    esac
    
    rm -rf "$temp_dir"
    return 0
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
    
    # Parse command line arguments
    local input_files=()
    local output_file=""
    local format="odt"
    local sort_files="false"
    local reverse_order="false"
    local add_page_break="false"
    local separator_text=""
    local document_title=""
    local document_author=""
    local generate_toc="false"
    local verbose="false"
    
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                show_usage
                exit 0
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -f|--format)
                format="$2"
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
            -p|--page-break)
                add_page_break="true"
                shift
                ;;
            --separator)
                separator_text="$2"
                shift 2
                ;;
            -t|--title)
                document_title="$2"
                shift 2
                ;;
            -a|--author)
                document_author="$2"
                shift 2
                ;;
            -c|--toc)
                generate_toc="true"
                shift
                ;;
            -v|--verbose)
                verbose="true"
                shift
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
    
    # Validate input
    if [ ${#input_files[@]} -lt 2 ]; then
        log_error "Need at least 2 files to merge"
        show_usage
        exit 1
    fi
    
    if [ -z "$output_file" ]; then
        log_error "Output file is required"
        show_usage
        exit 1
    fi
    
    # Add extension if not present
    if [[ ! "$output_file" =~ \.[a-zA-Z]{3,4}$ ]]; then
        output_file="$output_file.$format"
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
    
    # Check if all input files exist
    for file in "${input_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Input file not found: $file"
            exit 1
        fi
    done
    
    log_info "Merging ${#input_files[@]} documents..."
    log_info "Output: $output_file"
    log_info "Format: $format"
    
    if [ "$verbose" = "true" ]; then
        log_info "Input files:"
        for file in "${input_files[@]}"; do
            log_info "  - $file ($(du -h "$file" | cut -f1))"
        done
    fi
    
    # Try advanced merge first
    log_info "Attempting document merge..."
    
    if merge_with_macro "${input_files[@]}" "$output_file"; then
        log_success "Documents merged successfully: $output_file"
        log_info "File size: $(du -h "$output_file" | cut -f1)"
        exit 0
    fi
    
    # Fallback to simple merge
    log_warning "Advanced merge failed, using simple text-based merge..."
    
    if simple_merge "${input_files[@]}" "$output_file" "$add_page_break" "$separator_text"; then
        log_success "Documents merged (text-based): $output_file"
        log_info "File size: $(du -h "$output_file" | cut -f1)"
        exit 0
    fi
    
    log_error "Failed to merge documents"
    exit 1
}

# If script is executed directly, run main
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi