#!/usr/bin/env python3
"""
Test image file conversion with text content
"""
import asyncio
import os
from PIL import Image, ImageDraw, ImageFont
from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_image_with_text():
    service = EnhancedConversionService()
    
    # Create a test image with text
    print("Creating test image with text...")
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text to the image
    text = "Hello World!\nThis is a test image\nwith some text content"
    
    # Try to use a basic font
    try:
        # Try to use a larger font if available
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw text on image
    draw.text((20, 20), text, fill='black', font=font)
    
    # Add some shapes for visual interest
    draw.rectangle([20, 100, 100, 150], outline='red', width=2)
    draw.ellipse([120, 100, 200, 150], outline='blue', width=2)
    
    # Save the image
    img.save('test_image_with_text.jpg', 'JPEG')
    print("Test image created successfully")
    
    # Test conversion
    print("\nTesting image conversion with enhanced service...")
    result = await service.convert_file_enhanced('test_image_with_text.jpg', 'test_image_text_output.md')
    
    print(f"Conversion status: {result.status}")
    print(f"Output file: {result.output_file}")
    
    if result.markdown_content:
        print("\n=== Markdown Content ===")
        print(result.markdown_content)
        
        # Save to file for inspection
        with open('test_image_output.md', 'w') as f:
            f.write(result.markdown_content)
        print("\nOutput saved to test_image_output.md")
    else:
        print("No content generated")
    
    # Clean up
    if os.path.exists('test_image_with_text.jpg'):
        os.remove('test_image_with_text.jpg')
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_image_with_text())