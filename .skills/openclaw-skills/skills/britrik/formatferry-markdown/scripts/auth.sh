#!/usr/bin/env bash
#
# FormatFerry Auth Script
# Secure wrapper for authentication - no eval, safe argument handling
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*" >&2
}

# Authenticate with API key
auth_key() {
    local api_key="$1"

    if [[ -z "$api_key" ]]; then
        log_error "API key cannot be empty"
        return 1
    fi

    log_info "Authenticating with FormatFerry..."

    # Safe invocation - no eval
    if command -v formatferry &> /dev/null; then
        formatferry auth --api-key "$api_key"
    else
        npx formatferry auth --api-key "$api_key"
    fi
}

# Check auth status
auth_status() {
    log_info "Checking authentication status..."

    if command -v formatferry &> /dev/null; then
        formatferry auth --status
    else
        npx formatferry auth --status
    fi
}

main() {
    if [[ $# -eq 0 ]]; then
        log_error "Usage: $0 --key <api_key> | --status"
        return 1
    fi

    case "$1" in
        --key)
            if [[ -z "${2:-}" ]]; then
                log_error "API key required"
                return 1
            fi
            auth_key "$2"
            ;;
        --status)
            auth_status
            ;;
        *)
            log_error "Unknown option: $1"
            log_error "Usage: $0 --key <api_key> | --status"
            return 1
            ;;
    esac
}

main "$@"
