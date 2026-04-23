#!/usr/bin/env bash
#
# FormatFerry Convert Script
# Secure wrapper - no eval, bash arrays, robust path sanitization
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

check_formatferry() {
    if ! command -v formatferry &> /dev/null && ! command -v npx &> /dev/null; then
        log_error "FormatFerry not found. Install: npm install -g formatferry"
        return 1
    fi
}

# Recursive path traversal sanitization
sanitize_path() {
    local path="$1"
    local cleaned="$path"
    
    while [[ "$cleaned" =~ \.\.(\/) || "$cleaned" =~ \.\.+(\/) || "$cleaned" =~ \/.*\.\. ]]; do
        cleaned=$(echo "$cleaned" | sed -E 's|/[.]+|/|g' | sed -E 's|^[.]+/||' | sed -E 's|^[/.]*$||')
    done
    
    cleaned=$(echo "$cleaned" | sed -E 's:#%2e%2e:#%00:gI' | sed -E 's:#%2e:/:gI')
    [[ "$cleaned" =~ \.\. ]] && return 1
    
    printf '%s' "$cleaned"
}

validate_safe_path() {
    local path="$1"
    [[ -z "$path" ]] && return 1
    
    [[ "$path" =~ ^/etc ]] && return 1
    [[ "$path" =~ ^/root ]] && return 1
    [[ "$path" =~ ^/sys ]] && return 1
    [[ "$path" =~ ^/proc ]] && return 1
    
    local bn
    bn=$(basename "$path")
    [[ "$bn" == "passwd" ]] && return 1
    [[ "$bn" == "shadow" ]] && return 1
    [[ "$bn" == "id_rsa" ]] && return 1
    [[ "$bn" == ".bashrc" ]] && return 1
    
    return 0
}

convert_file() {
    local input_file="$1"
    local output_file="${2:-}"
    local format="${3:-github}"

    validate_safe_path "$input_file" || {
        log_error "Input path not allowed: $input_file"
        return 1
    }
    
    [[ ! -f "$input_file" ]] && {
        log_error "Input file not found: $input_file"
        return 1
    }

    if [[ -z "$output_file" ]]; then
        output_file="$(basename "$input_file" | sed 's/\.[^.]*$//').md"
    fi

    validate_safe_path "$output_file" || {
        log_error "Output path not allowed: $output_file"
        return 1
    }
    
    local sanitized
    sanitized=$(sanitize_path "$output_file") || {
        log_error "Output contains traversal: $output_file"
        return 1
    }
    
    output_file="$sanitized"
    [[ ! "$output_file" =~ ^/ ]] && output_file="/tmp/$output_file"

    local ARGS=()
    ARGS+=("-i" "$input_file")
    ARGS+=("-o" "$output_file")
    ARGS+=("-f" "$format")

    log_info "Converting: $input_file → $output_file"

    if command -v formatferry &> /dev/null; then
        formatferry "${ARGS[@]}"
    else
        npx formatferry "${ARGS[@]}"
    fi

    log_info "Done: $output_file"
    echo "$output_file"
}

convert_url() {
    local url="$1"
    local output_file="${2:-}"
    local format="${3:-github}"

    [[ ! "$url" =~ ^https?:// ]] && {
        log_error "Invalid URL: $url"
        return 1
    }

    if [[ -z "$output_file" ]]; then
        output_file="converted-$(date +%s).md"
    fi

    validate_safe_path "$output_file" || {
        log_error "Output path not allowed: $output_file"
        return 1
    }
    
    local sanitized
    sanitized=$(sanitize_path "$output_file") || {
        log_error "Output contains traversal: $output_file"
        return 1
    }
    
    output_file="$sanitized"
    [[ ! "$output_file" =~ ^/ ]] && output_file="/tmp/$output_file"

    local ARGS=()
    ARGS+=("--url" "$url")
    ARGS+=("--output" "$output_file")
    ARGS+=("-f" "$format")

    log_info "Fetching: $url → $output_file"

    if command -v formatferry &> /dev/null; then
        formatferry "${ARGS[@]}"
    else
        npx formatferry "${ARGS[@]}"
    fi

    log_info "Done: $output_file"
    echo "$output_file"
}

main() {
    [[ $# -eq 0 ]] && {
        log_error "Usage: $0 --file <input> [--output <file>] [--format <format>]"
        log_error "   or: $0 --url <url> [--output <file>] [--format <format>]"
        return 1
    }

    check_formatferry || return 1

    local mode="" input="" output="" format="github"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --file) mode="file"; input="$2"; shift 2 ;;
            --url) mode="url"; input="$2"; shift 2 ;;
            --output) output="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            *) log_error "Unknown: $1"; return 1 ;;
        esac
    done

    [[ -z "$mode" ]] || [[ -z "$input" ]] && {
        log_error "Missing required argument"
        return 1
    }

    case "$mode" in
        file) convert_file "$input" "$output" "$format" ;;
        url) convert_url "$input" "$output" "$format" ;;
        *) log_error "Invalid mode: $mode"; return 1 ;;
    esac
}

main "$@"