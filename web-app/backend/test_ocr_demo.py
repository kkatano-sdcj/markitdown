#!/usr/bin/env python3
"""
Test OCR functionality with mock and real Tesseract
"""
import asyncio
import os
from PIL import Image, ImageDraw, ImageFont
from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_ocr_functionality():
    service = EnhancedConversionService()
    
    # Create test images with different characteristics
    print("Creating test images...")
    
    # 1. Red image with text
    img1 = Image.new('RGB', (400, 200), color='red')
    draw = ImageDraw.Draw(img1)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()
    draw.text((50, 50), "TEST IMAGE", fill='white', font=font)
    draw.text((50, 100), "Red Background", fill='white', font=font)
    img1.save('test_red.jpg')
    
    # 2. Blue image with text
    img2 = Image.new('RGB', (300, 150), color='blue')
    draw = ImageDraw.Draw(img2)
    draw.text((20, 30), "Blue Test\n日本語テスト", fill='white', font=font)
    img2.save('test_blue.png')
    
    # 3. Small image
    img3 = Image.new('RGB', (50, 50), color='green')
    img3.save('test_small.png')
    
    print("Test images created\n")
    
    # Test each image
    test_files = ['test_red.jpg', 'test_blue.png', 'test_small.png']
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Testing: {test_file}")
        print('='*60)
        
        result = await service.convert_file_enhanced(
            test_file, 
            f"{test_file}_output.md"
        )
        
        if result.status == "completed" and result.markdown_content:
            # Extract OCR section
            lines = result.markdown_content.split('\n')
            in_ocr_section = False
            ocr_lines = []
            
            for line in lines:
                if "## Text Content (OCR)" in line:
                    in_ocr_section = True
                elif in_ocr_section and line.startswith("## "):
                    break
                elif in_ocr_section:
                    ocr_lines.append(line)
            
            print("OCR Section:")
            print('\n'.join(ocr_lines[:30]))  # Show first 30 lines of OCR section
            
            # Save full output
            output_file = f"{test_file}_full.md"
            with open(output_file, 'w') as f:
                f.write(result.markdown_content)
            print(f"\nFull output saved to: {output_file}")
        else:
            print(f"Conversion failed: {result.error_message}")
    
    # Cleanup
    for test_file in test_files:
        if os.path.exists(test_file):
            os.remove(test_file)
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_ocr_functionality())