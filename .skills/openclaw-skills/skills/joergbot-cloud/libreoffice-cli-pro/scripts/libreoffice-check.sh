#!/bin/bash
# LibreOffice installation check script
# Usage: source this script or call functions directly

set -e

LIBREOFFICE_CHECK_DEBUG=${LIBREOFFICE_CHECK_DEBUG:-false}

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

debug_log() {
    if [ "$LIBREOFFICE_CHECK_DEBUG" = "true" ]; then
        echo -e "${YELLOW}[DEBUG]${NC} $1"
    fi
}

# Check if LibreOffice is installed
check_libreoffice_installed() {
    debug_log "Checking if LibreOffice is installed..."
    
    if command -v libreoffice &> /dev/null; then
        log_success "LibreOffice found: $(command -v libreoffice)"
        return 0
    else
        log_error "LibreOffice not found in PATH"
        return 1
    fi
}

# Get LibreOffice version
get_libreoffice_version() {
    if check_libreoffice_installed; then
        local version_output
        version_output=$(libreoffice --version 2>/dev/null | head -1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
        echo "$version_output"
    else
        echo "not-installed"
    fi
}

# Check LibreOffice version compatibility
check_libreoffice_version() {
    local min_version="${1:-24.2.0}"
    local current_version
    
    current_version=$(get_libreoffice_version)
    
    if [ "$current_version" = "not-installed" ]; then
        log_error "LibreOffice is not installed"
        return 1
    fi
    
    debug_log "Current LibreOffice version: $current_version, Minimum required: $min_version"
    
    # Simple version comparison
    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -1)" = "$min_version" ]; then
        log_success "LibreOffice version $current_version meets minimum requirement $min_version"
        return 0
    else
        log_error "LibreOffice version $current_version is below minimum requirement $min_version"
        return 1
    fi
}

# Check headless mode support
check_headless_support() {
    debug_log "Checking headless mode support..."
    
    if ! check_libreoffice_installed; then
        return 1
    fi
    
    # Test headless mode with a simple command
    if libreoffice --headless --version 2>&1 | grep -q "LibreOffice"; then
        log_success "LibreOffice headless mode is supported"
        return 0
    else
        log_error "LibreOffice headless mode test failed"
        return 1
    fi
}

# Check conversion capability
check_conversion_capability() {
    debug_log "Testing document conversion capability..."
    
    if ! check_headless_support; then
        return 1
    fi
    
    # Create a simple test document
    local test_file="/tmp/test_conversion_$(date +%s).txt"
    echo "Test document for LibreOffice conversion check" > "$test_file"
    
    # Try to convert it
    if libreoffice --headless --convert-to pdf --outdir /tmp "$test_file" 2>/dev/null; then
        log_success "Document conversion test passed"
        rm -f "$test_file" "/tmp/test_conversion_*.pdf" 2>/dev/null
        return 0
    else
        log_error "Document conversion test failed"
        rm -f "$test_file" 2>/dev/null
        return 1
    fi
}

# Check available filters
check_available_filters() {
    debug_log "Checking available filters..."
    
    if ! check_libreoffice_installed; then
        return 1
    fi
    
    # Common filters to check
    local filters=("pdf" "docx" "xlsx" "pptx" "txt" "html")
    local available_filters=()
    
    for filter in "${filters[@]}"; do
        if libreoffice --headless --help 2>&1 | grep -q "convert-to.*$filter"; then
            available_filters+=("$filter")
        fi
    done
    
    if [ ${#available_filters[@]} -gt 0 ]; then
        log_success "Available filters: ${available_filters[*]}"
        return 0
    else
        log_warning "No common filters detected (might be version specific)"
        return 0  # Not a critical error
    fi
}

# Comprehensive LibreOffice health check
check_libreoffice_health() {
    local overall_status=0
    local errors=0
    local warnings=0
    
    log_info "Starting LibreOffice health check..."
    
    # 1. Check installation
    if check_libreoffice_installed; then
        log_success "✓ LibreOffice is installed"
    else
        log_error "✗ LibreOffice is not installed"
        errors=$((errors + 1))
        overall_status=1
    fi
    
    # 2. Check version
    if check_libreoffice_version "24.2.0"; then
        log_success "✓ LibreOffice version is compatible"
    else
        log_error "✗ LibreOffice version is incompatible"
        errors=$((errors + 1))
        overall_status=1
    fi
    
    # 3. Check headless support
    if check_headless_support; then
        log_success "✓ LibreOffice headless mode is supported"
    else
        log_error "✗ LibreOffice headless mode not supported"
        errors=$((errors + 1))
        overall_status=1
    fi
    
    # 4. Check conversion capability
    if check_conversion_capability; then
        log_success "✓ Document conversion works"
    else
        log_error "✗ Document conversion failed"
        errors=$((errors + 1))
        overall_status=1
    fi
    
    # 5. Check available filters
    if check_available_filters; then
        log_success "✓ Common filters are available"
    else
        log_warning "⚠ Filter detection had issues"
        warnings=$((warnings + 1))
        overall_status=2
    fi
    
    # Summary
    echo ""
    if [ $errors -gt 0 ]; then
        log_error "❌ LibreOffice health check FAILED ($errors errors, $warnings warnings)"
        return 1
    elif [ $warnings -gt 0 ]; then
        log_warning "⚠️  LibreOffice health check WARNING ($warnings warnings)"
        return 0
    else
        log_success "✅ LibreOffice health check PASSED"
        return 0
    fi
}

# Installation instructions
show_installation_instructions() {
    cat << EOF

📝 LIBREOFFICE INSTALLATION INSTRUCTIONS

1. Install LibreOffice (if not already installed):
   - Ubuntu/Debian: sudo apt install libreoffice
   - Fedora: sudo dnf install libreoffice
   - macOS: brew install libreoffice
   - Windows: Download from https://libreoffice.org

2. Verify installation:
   libreoffice --version

3. Test headless mode:
   libreoffice --headless --version

4. Test conversion:
   echo "Test" > test.txt
   libreoffice --headless --convert-to pdf test.txt

For more information: https://libreoffice.org
EOF
}

# Main execution
main() {
    local action="${1:-health}"
    
    case "$action" in
        installed)
            check_libreoffice_installed
            ;;
        version)
            get_libreoffice_version
            ;;
        headless)
            check_headless_support
            ;;
        conversion)
            check_conversion_capability
            ;;
        filters)
            check_available_filters
            ;;
        health|check)
            check_libreoffice_health
            ;;
        install-help)
            show_installation_instructions
            ;;
        *)
            echo "Usage: $0 {health|installed|version|headless|conversion|filters|install-help}"
            exit 1
            ;;
    esac
}

# If script is executed directly, run main
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi

# Export functions for use in other scripts
export -f check_libreoffice_installed
export -f get_libreoffice_version
export -f check_libreoffice_version
export -f check_headless_support
export -f check_conversion_capability
export -f check_available_filters
export -f check_libreoffice_health