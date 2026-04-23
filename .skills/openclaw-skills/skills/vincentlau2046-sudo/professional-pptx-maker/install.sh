#!/bin/bash
# Install Professional PPTX Maker v1.0.0

echo "Installing Professional PPTX Maker v1.0.0..."

# Create skills directory if not exists
mkdir -p ~/.openclaw/workspace/skills/professional-pptx-maker

# Copy all files
cp -r ./* ~/.openclaw/workspace/skills/professional-pptx-maker/

# Create symlink in bin directory
ln -sf ~/.openclaw/workspace/skills/professional-pptx-maker/professional-pptx-maker ~/.openclaw/bin/professional-pptx-maker

# Set executable permissions
chmod +x ~/.openclaw/bin/professional-pptx-maker

echo "✅ Professional PPTX Maker v1.0.0 installed successfully!"
echo "Usage: professional-pptx-maker --input content.md --output output.pptx --theme tech_insight"