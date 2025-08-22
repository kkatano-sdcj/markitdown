#!/bin/bash

echo "================================================"
echo "Tesseract OCR Installation Instructions"
echo "================================================"
echo ""
echo "To enable OCR functionality for image text extraction,"
echo "please run the following commands with administrator privileges:"
echo ""
echo "1. Update package list:"
echo "   sudo apt-get update"
echo ""
echo "2. Install Tesseract OCR:"
echo "   sudo apt-get install -y tesseract-ocr"
echo ""
echo "3. Install Japanese language support (optional):"
echo "   sudo apt-get install -y tesseract-ocr-jpn"
echo ""
echo "4. Verify installation:"
echo "   tesseract --version"
echo "   tesseract --list-langs"
echo ""
echo "================================================"
echo "Alternative: Install in user space (if available)"
echo "================================================"
echo ""
echo "If you cannot use sudo, you might try:"
echo "1. Download Tesseract AppImage (if available)"
echo "2. Use conda: conda install -c conda-forge tesseract"
echo "3. Build from source in your home directory"
echo ""
echo "================================================"
echo "Current Status:"
echo "================================================"

# Check if tesseract is installed
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract is installed!"
    echo "  Version: $(tesseract --version 2>&1 | head -1)"
    echo "  Languages available:"
    tesseract --list-langs 2>&1 | tail -n +2 | head -10
else
    echo "✗ Tesseract is NOT installed"
    echo "  Please install it using the commands above"
fi

echo ""
echo "Python packages status:"
if python3 -c "import pytesseract" 2>/dev/null; then
    echo "✓ pytesseract is installed"
else
    echo "✗ pytesseract is NOT installed - run: pip install pytesseract"
fi

if python3 -c "from PIL import Image" 2>/dev/null; then
    echo "✓ Pillow is installed"
else
    echo "✗ Pillow is NOT installed - run: pip install Pillow"
fi