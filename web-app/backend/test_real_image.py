#!/usr/bin/env python3
"""
Test with a real image file
"""
import asyncio
import os
import requests
from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_real_image():
    service = EnhancedConversionService()
    
    # Download a sample image with text
    print("Downloading sample image...")
    url = "https://via.placeholder.com/600x400/FF0000/FFFFFF?text=Sample+Image+With+Text"
    response = requests.get(url)
    
    with open('sample_image.png', 'wb') as f:
        f.write(response.content)
    print("Sample image downloaded")
    
    # Test conversion
    print("\nTesting image conversion...")
    result = await service.convert_file_enhanced('sample_image.png', 'sample_image_output.md')
    
    print(f"Conversion status: {result.status}")
    
    if result.markdown_content:
        print("\n=== Markdown Content Preview ===")
        # Show first 1500 characters
        print(result.markdown_content[:1500])
        if len(result.markdown_content) > 1500:
            print("\n... [Content truncated for display]")
        
        # Save full content
        with open('sample_image_full_output.md', 'w') as f:
            f.write(result.markdown_content)
        print("\nFull output saved to sample_image_full_output.md")
    
    # Clean up
    if os.path.exists('sample_image.png'):
        os.remove('sample_image.png')
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_real_image())