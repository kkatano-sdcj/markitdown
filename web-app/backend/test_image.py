#!/usr/bin/env python3
"""
Test image file conversion
"""
import os
from PIL import Image
from markitdown import MarkItDown

# Create a simple test image
img = Image.new('RGB', (100, 100), color='red')
img.save('test_image.png')

# Test with markitdown
md = MarkItDown()

print("Testing image conversion with markitdown...")
try:
    result = md.convert('test_image.png')
    print(f"Success! Content length: {len(result.text_content) if result.text_content else 0}")
    print("Content preview:")
    if result.text_content:
        print(result.text_content[:500])
    else:
        print("No content returned")
except Exception as e:
    print(f"Error: {e}")

# Clean up
os.remove('test_image.png')
print("\nTest completed!")