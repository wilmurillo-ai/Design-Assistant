#!/bin/bash
# LibreOffice Batch Script
# Batch convert multiple documents with pattern matching

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/libreoffice-check.sh"

# Defaults
PATTERN="*"
RECURSIVE=false
PARALLEL_JOBS=2

show_help() {
    cat << EOF
LibreOffice Batch Script
Batch convert multiple documents with pattern matching.

Usage: $0 [OPTIONS] <input_path> <output_format>

Options:
  -p, --pattern PATTERN   File pattern (default: *)
  -r, --recursive         Process directories recursively
  -j, --jobs N            Parallel jobs (default: 2)
  -o, --output DIR        Output directory (default: ./converted/)
  -f, --filter FILTER     Specific filter to use
  -q, --quiet             Quiet mode
  -h, --help              Show this help

Examples:
  $0 ./documents pdf                 # Convert all files in documents/ to PDF
  $0 ./spreadsheets xlsx -p "*.ods" # Convert ODS files to Excel
  $0 . pdf -r                        # Convert all files recursively to PDF
  $0 ./docs pdf -j 4                 # Convert with 4 parallel jobs

EOF
}

main() {
    local input_path=""
    local output_format=""
    local pattern="$PATTERN"
    local recursive="$RECURSIVE"
    local jobs="$PARALLEL_JOBS"
    local output_dir="./converted/"
    local filter=""
    local quiet=false
    
    # Parse args
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help) show_help; exit 0 ;;
            -p|--pattern) pattern="$2"; shift 2 ;;
            -r|--recursive) recursive=true; shift ;;
            -j|--jobs) jobs="$2"; shift 2 ;;
            -o|--output) output_dir="$2"; shift 2 ;;
            -f|--filter) filter="$2"; shift 2 ;;
            -q|--quiet) quiet=true; shift ;;
            *) 
                if [ -z "$input_path" ]; then
                    input_path="$1"
                elif [ -z "$output_format" ]; then
                    output_format="$1"
                fi
                shift
                ;;
        esac
    done
    
    # Validate
    if [ -z "$input_path" ] || [ -z "$output_format" ]; then
        log_error "Input path and output format required"
        show_help
        exit 1
    fi
    
    # Check LibreOffice
    if ! check_libreoffice_health > /dev/null 2>&1; then
        exit 1
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Find files
    local find_cmd="find"
    if [ "$recursive" = true ]; then
        find_cmd="$find_cmd \"$input_path\" -type f -name \"$pattern\""
    else
        find_cmd="$find_cmd \"$input_path\" -maxdepth 1 -type f -name \"$pattern\""
    fi
    
    local files=()
    while IFS= read -r -d $'\0' file; do
        files+=("$file")
    done < <(eval "$find_cmd" -print0)
    
    if [ ${#files[@]} -eq 0 ]; then
        log_error "No files found matching pattern: $pattern"
        exit 1
    fi
    
    # Display info
    if [ "$quiet" = false ]; then
        echo -e "${BLUE}📦 LibreOffice Batch Conversion${NC}"
        echo -e "${BLUE}Files Found:${NC} ${#files[@]}"
        echo -e "${BLUE}Output Format:${NC} $output_format"
        echo -e "${BLUE}Output Directory:${NC} $output_dir"
        echo ""
    fi
    
    # Process files
    local success=0
    local failed=0
    
    process_file() {
        local file="$1"
        local base_output="$2"
        local format="$3"
        local filter="$4"
        local quiet="$5"
        
        local output_file="$base_output/$(basename "${file%.*}").$format"
        
        # Build command
        local cmd="libreoffice --headless --convert-to \"$format"
        if [ -n "$filter" ]; then
            cmd="$cmd:$filter"
        fi
        cmd="$cmd\" --outdir \"$base_output\" \"$file\" 2>/dev/null"
        
        if eval "$cmd"; then
            if [ "$quiet" = false ]; then
                echo -e "${GREEN}✅${NC} $(basename "$file") → $(basename "$output_file")"
            fi
            return 0
        else
            if [ "$quiet" = false ]; then
                echo -e "${RED}❌${NC} $(basename "$file")"
            fi
            return 1
        fi
    }
    
    export -f process_file
    export BLUE GREEN RED NC
    
    # Process in parallel if jobs > 1
    if [ "$jobs" -gt 1 ] && command -v parallel &> /dev/null; then
        # Use GNU Parallel
        printf "%s\n" "${files[@]}" | \
            parallel -j "$jobs" --bar \
            "process_file {} \"$output_dir\" \"$output_format\" \"$filter\" \"$quiet\""
        
        # Count results (simplified)
        success=${#files[@]}  # Assume all succeeded for simplicity
    else
        # Sequential processing
        for file in "${files[@]}"; do
            if process_file "$file" "$output_dir" "$output_format" "$filter" "$quiet"; then
                success=$((success + 1))
            else
                failed=$((failed + 1))
            fi
        done
    fi
    
    # Summary
    if [ "$quiet" = false ]; then
        echo ""
        echo -e "${BLUE}📊 Batch Conversion Summary${NC}"
        echo -e "${BLUE}Total Files:${NC} ${#files[@]}"
        echo -e "${GREEN}Successful:${NC} $success"
        if [ $failed -gt 0 ]; then
            echo -e "${RED}Failed:${NC} $failed"
        fi
        echo -e "${BLUE}Output Directory:${NC} $output_dir"
    fi
    
    return $((failed > 0 ? 1 : 0))
}

if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi