#!/usr/bin/env python3
"""
Test PaddleOCR functionality with real text extraction
"""
import asyncio
import os
from PIL import Image, ImageDraw, ImageFont
from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_paddle_ocr():
    service = EnhancedConversionService()
    
    print("Creating test image with text...")
    
    # Create a test image with clear text
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a good font
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add various text elements
    draw.text((50, 30), "Welcome to MarkItDown", fill='black', font=font_large)
    draw.text((50, 100), "Image to Text Conversion", fill='blue', font=font_medium)
    draw.text((50, 150), "Features:", fill='black', font=font_medium)
    draw.text((80, 190), "• OCR Text Extraction", fill='gray', font=font_small)
    draw.text((80, 220), "• Multiple Languages Support", fill='gray', font=font_small)
    draw.text((80, 250), "• High Accuracy Recognition", fill='gray', font=font_small)
    draw.text((50, 300), "Test Date: 2025-08-14", fill='green', font=font_small)
    draw.text((50, 330), "Status: Active", fill='red', font=font_small)
    
    # Add a box with text
    draw.rectangle([400, 150, 550, 250], outline='blue', width=2)
    draw.text((420, 180), "SAMPLE", fill='blue', font=font_medium)
    draw.text((420, 210), "TEXT BOX", fill='blue', font=font_medium)
    
    # Save the image
    img.save('test_paddle_text.png')
    print("Test image created: test_paddle_text.png")
    
    # Test conversion with PaddleOCR
    print("\n" + "="*60)
    print("Testing OCR with PaddleOCR...")
    print("="*60)
    
    result = await service.convert_file_enhanced(
        'test_paddle_text.png',
        'test_paddle_output.md'
    )
    
    if result.status == "completed" and result.markdown_content:
        # Extract and display OCR section
        lines = result.markdown_content.split('\n')
        in_ocr = False
        ocr_lines = []
        
        for line in lines:
            if "## Text Content (OCR)" in line:
                in_ocr = True
            elif in_ocr and line.startswith("## "):
                break
            elif in_ocr:
                ocr_lines.append(line)
        
        print("\nOCR Results:")
        print("-" * 40)
        for line in ocr_lines:
            print(line)
        
        # Save full output
        with open('test_paddle_full_output.md', 'w') as f:
            f.write(result.markdown_content)
        print("\n" + "="*60)
        print("Full output saved to: test_paddle_full_output.md")
    else:
        print(f"Conversion failed: {result.error_message}")
    
    # Clean up
    if os.path.exists('test_paddle_text.png'):
        os.remove('test_paddle_text.png')
    
    print("="*60)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_paddle_ocr())