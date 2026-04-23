#!/bin/bash
# setup.sh - Install dependencies for md-to-image skill
# Idempotent: skips already-installed items
# Usage: setup.sh [--check-only]
set -e

CHECK_ONLY=false
[[ "$1" == "--check-only" ]] && CHECK_ONLY=true

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
FONT_DIR="$SKILL_DIR/fonts"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[✗]${NC} $1"; }

# --- Detect package manager ---
detect_pkg_mgr() {
    if command -v dnf &>/dev/null; then echo "dnf"
    elif command -v apt-get &>/dev/null; then echo "apt"
    elif command -v yum &>/dev/null; then echo "yum"
    elif command -v pacman &>/dev/null; then echo "pacman"
    elif command -v brew &>/dev/null; then echo "brew"
    else echo "unknown"
    fi
}

install_pkg() {
    local pkg="$1"
    if $CHECK_ONLY; then
        fail "$pkg not installed (check-only mode, skipping install)"
        return 1
    fi
    case "$PKG_MGR" in
        dnf)    sudo dnf install -y "$pkg" ;;
        apt)    sudo apt-get install -y "$pkg" ;;
        yum)    sudo yum install -y "$pkg" ;;
        pacman) sudo pacman -S --noconfirm "$pkg" ;;
        brew)   brew install "$pkg" ;;
        *)      fail "Unknown package manager. Install '$pkg' manually."; return 1 ;;
    esac
}

PKG_MGR=$(detect_pkg_mgr)
echo "Detected package manager: $PKG_MGR"
echo ""

# --- wkhtmltopdf (required) ---
if command -v wkhtmltoimage &>/dev/null; then
    info "wkhtmltoimage already installed: $(wkhtmltoimage --version 2>&1)"
else
    warn "Installing wkhtmltoimage..."
    install_pkg "wkhtmltopdf" && info "wkhtmltoimage installed" || fail "Failed to install wkhtmltoimage"
fi

# --- python3-pillow (required) ---
if python3 -c "from PIL import Image" 2>/dev/null; then
    info "Pillow already installed"
else
    warn "Installing python3-pillow..."
    case "$PKG_MGR" in
        dnf|yum) install_pkg "python3-pillow" ;;
        apt)     install_pkg "python3-pil" ;;
        *)       python3 -m pip install pillow 2>/dev/null || fail "Install Pillow manually: pip install pillow" ;;
    esac
    python3 -c "from PIL import Image" 2>/dev/null && info "Pillow installed" || fail "Pillow installation failed"
fi

# --- python3-mistune (required) ---
if python3 -c "import mistune" 2>/dev/null; then
    info "Mistune already installed: $(python3 -c 'import mistune; print(mistune.__version__)')"
else
    warn "Installing mistune..."
    case "$PKG_MGR" in
        dnf|yum) install_pkg "python3-mistune" ;;
        apt)     install_pkg "python3-mistune" 2>/dev/null || python3 -m pip install mistune || true ;;
        *)       python3 -m pip install mistune 2>/dev/null || true ;;
    esac
    python3 -c "import mistune" 2>/dev/null && info "Mistune installed" || fail "Mistune installation failed"
fi

# --- Custom font (optional) ---
# To use a custom font (e.g., Maple Mono), place .woff2 files in $FONT_DIR:
#   fonts/custom-400.woff2  (regular weight)
#   fonts/custom-700.woff2  (bold weight)
# The script auto-detects these files. Falls back to system fonts if absent.

# --- mermaid-cli (optional, for diagrams) ---
if command -v mmdc &>/dev/null; then
    info "Mermaid CLI already installed: $(mmdc --version 2>&1)"
else
    warn "Installing mermaid-cli (optional)..."
    npm install -g @mermaid-js/mermaid-cli 2>/dev/null && info "Mermaid CLI installed" || warn "Mermaid CLI install failed, diagrams will show as code"
fi

# --- pygments (optional, for syntax highlighting) ---
if python3 -c "import pygments" 2>/dev/null; then
    info "Pygments already installed"
else
    warn "Installing pygments (optional)..."
    case "$PKG_MGR" in
        dnf|yum) install_pkg "python3-pygments" 2>/dev/null || python3 -m pip install pygments 2>/dev/null || true ;;
        apt)     install_pkg "python3-pygments" 2>/dev/null || python3 -m pip install pygments 2>/dev/null || true ;;
        *)       python3 -m pip install pygments 2>/dev/null || true ;;
    esac
    if python3 -c "import pygments" 2>/dev/null; then
        info "Pygments installed (syntax highlighting enabled)"
    else
        warn "Pygments not available, code blocks will use monochrome style"
    fi
fi

echo ""
echo "Setup complete."
