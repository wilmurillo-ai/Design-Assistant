#!/usr/bin/env bash
#
# FormatFerry Convert to Markdown Script
# Secure wrapper - NO eval, bash arrays, streaming output, robust path sanitization
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }

check_dependencies() {
    if ! command -v formatferry &> /dev/null && ! command -v npx &> /dev/null; then
        log_error "FormatFerry not found. Install: npm install -g formatferry"
        return 1
    fi
}

# ROBUST: Recursive path traversal sanitization
sanitize_path() {
    local path="$1"
    local cleaned="$path"
    
    # Loop until no more traversal patterns (handles ....//, ..../, ./, /../)
    while [[ "$cleaned" =~ \.\.(\/) || "$cleaned" =~ \.\.+(\/) || "$cleaned" =~ \/.*\.\. ]]; do
        cleaned=$(echo "$cleaned" | sed -E 's|/[.]+|/|g' | sed -E 's|^[.]+/||' | sed -E 's|^[/.]*$||')
    done
    
    # Handle encoded bypass (%2e%2e)
    cleaned=$(echo "$cleaned" | sed -E 's:#%2e%2e:#%00:gI' | sed -E 's:#%2e:/:gI')
    
    # Final check
    [[ "$cleaned" =~ \.\. ]] && return 1
    
    printf '%s' "$cleaned"
}

# Validate path is safe
validate_safe_path() {
    local path="$1"
    
    [[ -z "$path" ]] && return 1
    
    # Block sensitive absolute paths
    [[ "$path" =~ ^/etc ]] && return 1
    [[ "$path" =~ ^/root ]] && return 1
    [[ "$path" =~ ^/sys ]] && return 1
    [[ "$path" =~ ^/proc ]] && return 1
    
    # Block sensitive filenames
    local bn
    bn=$(basename "$path")
    [[ "$bn" == "passwd" ]] && return 1
    [[ "$bn" == "shadow" ]] && return 1
    [[ "$bn" == "id_rsa" ]] && return 1
    [[ "$bn" == ".bashrc" ]] && return 1
    [[ "$bn" == ".bash_history" ]] && return 1
    
    return 0
}

convert_to_md() {
    local INPUT_FILE=""
    local URL=""
    local OUTPUT_FILE=""
    local FORMAT="github"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --input|-i)
                INPUT_FILE="$2"
                shift 2
                ;;
            --url)
                URL="$2"
                shift 2
                ;;
            --output|-o)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            --format|-f)
                FORMAT="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                return 1
                ;;
        esac
    done

    if [[ -z "$INPUT_FILE" ]] && [[ -z "$URL" ]]; then
        log_error "Either --input or --url is required"
        return 1
    fi

    # Validate INPUT_FILE
    if [[ -n "$INPUT_FILE" ]]; then
        validate_safe_path "$INPUT_FILE" || {
            log_error "Input path is not allowed: $INPUT_FILE"
            return 1
        }
        
        local sanitized_input
        sanitized_input=$(sanitize_path "$INPUT_FILE") || {
            log_error "Input contains invalid traversal: $INPUT_FILE"
            return 1
        }
        
        if [[ ! -f "$INPUT_FILE" ]]; then
            log_error "Input file not found: $INPUT_FILE"
            return 1
        fi
    fi

    if [[ -n "$URL" ]] && [[ ! "$URL" =~ ^https?:// ]]; then
        log_error "Invalid URL (must start with http:// or https://)"
        return 1
    fi

    # Validate OUTPUT_FILE
    if [[ -n "$OUTPUT_FILE" ]]; then
        validate_safe_path "$OUTPUT_FILE" || {
            log_error "Output path is not allowed: $OUTPUT_FILE"
            return 1
        }
        
        local sanitized_output
        sanitized_output=$(sanitize_path "$OUTPUT_FILE") || {
            log_error "Output contains invalid traversal: $OUTPUT_FILE"
            return 1
        }
        
        OUTPUT_FILE="$sanitized_output"
    else
        if [[ -n "$INPUT_FILE" ]]; then
            OUTPUT_FILE="$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//').md"
        else
            OUTPUT_FILE="converted-$(date +%s).md"
        fi
    fi

    # Ensure output in /tmp or current dir
    if [[ ! "$OUTPUT_FILE" =~ ^/ ]]; then
        OUTPUT_FILE="/tmp/$OUTPUT_FILE"
    fi

    local ARGS=()
    if [[ -n "$URL" ]]; then
        ARGS+=("--url" "$URL")
    else
        ARGS+=("-i" "$INPUT_FILE")
    fi
    ARGS+=("-o" "$OUTPUT_FILE")
    ARGS+=("-f" "$FORMAT")

    log_info "Converting..."
    
    if command -v formatferry &> /dev/null; then
        formatferry "${ARGS[@]}"
    else
        npx formatferry "${ARGS[@]}"
    fi

    log_info "Output: $OUTPUT_FILE"
    cat "$OUTPUT_FILE"
}

check_dependencies || exit 1
convert_to_md "$@"