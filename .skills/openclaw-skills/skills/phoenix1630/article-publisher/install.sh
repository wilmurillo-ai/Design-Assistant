#!/bin/bash
echo "========================================"
echo "  Article Publisher Skill Installer"
echo "========================================"
echo ""
echo "Checking environment..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found. Please install Node.js 18+"
    echo "Download: https://nodejs.org/"
    exit 1
fi

echo "[OK] Node.js installed"
echo ""

# Install npm dependencies
echo "Installing npm dependencies..."
npm install --production
if [ $? -ne 0 ]; then
    echo "[ERROR] npm install failed"
    exit 1
fi
echo "[OK] Dependencies installed"
echo ""

# Check Playwright browser
echo "Checking Playwright browser..."
PLAYWRIGHT_CACHE="$HOME/.cache/ms-playwright"
if ls $PLAYWRIGHT_CACHE/chromium-* 1> /dev/null 2>&1; then
    echo "[OK] Chromium already installed, skipping download"
    exit 0
fi

echo ""
echo "Playwright browser not found. Choose download source:"
echo ""
echo "  [1] China Mirror (Recommended, faster in China)"
echo "  [2] Official Source (Outside China)"
echo "  [3] Skip (Install manually later)"
echo ""
read -p "Enter choice [1/2/3]: " choice

case $choice in
    1)
        echo ""
        echo "Downloading browser from China mirror..."
        PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright npx playwright install chromium
        ;;
    2)
        echo ""
        echo "Downloading browser from official source..."
        npx playwright install chromium
        ;;
    3)
        echo ""
        echo "Browser installation skipped."
        echo "You can install later with:"
        echo "  npm run install:browser:cn  (China mirror)"
        echo "  npm run install:browser      (Official)"
        ;;
    *)
        echo ""
        echo "Downloading browser from China mirror..."
        PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright npx playwright install chromium
        ;;
esac

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Usage:"
echo "  node test-publish.js zhihu     (Test Zhihu)"
echo "  node test-publish.js bilibili  (Test Bilibili)"
echo ""
