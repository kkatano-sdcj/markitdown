#!/usr/bin/env python3
"""Test script for PPTX conversion with markitdown"""

from markitdown import MarkItDown
import os

def test_markitdown_pptx():
    """Test if markitdown can handle PPTX files"""
    try:
        # Initialize MarkItDown
        md = MarkItDown()
        print("✓ MarkItDown initialized successfully")
        
        # Check if pptx converter is available
        converters = [type(c).__name__ for c in md._converters]
        print(f"Available converters: {converters}")
        
        if "PptxConverter" in converters:
            print("✓ PptxConverter is available")
        else:
            print("✗ PptxConverter is NOT available")
            
        # Try to import python-pptx directly
        try:
            import pptx
            print("✓ python-pptx module is importable")
        except ImportError as e:
            print(f"✗ python-pptx import error: {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_markitdown_pptx()
    exit(0 if success else 1)