#!/usr/bin/env python3
"""
Test image file conversion with enhanced service
"""
import asyncio
import os
from PIL import Image
from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_image_conversion():
    service = EnhancedConversionService()
    
    # Create a test image with EXIF data
    print("Creating test image...")
    img = Image.new('RGB', (200, 200), color='blue')
    
    # Save with some basic info
    img.save('test_image.jpg', 'JPEG')
    
    print("Testing image conversion with enhanced service...")
    result = await service.convert_file_enhanced('test_image.jpg', 'test_image_output.md')
    
    print(f"Conversion status: {result.status}")
    print(f"Output file: {result.output_file}")
    
    if result.markdown_content:
        print("\n=== Markdown Content ===")
        print(result.markdown_content)
    else:
        print("No content generated")
    
    # Clean up
    if os.path.exists('test_image.jpg'):
        os.remove('test_image.jpg')
    if os.path.exists('converted/test_image_output.md'):
        os.remove('converted/test_image_output.md')
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_image_conversion())