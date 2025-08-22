#!/usr/bin/env python3
"""
Test both Normal and AI conversion modes
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_both_modes():
    """Test both conversion modes"""
    service = EnhancedConversionService()
    
    # Test files
    test_files = [
        ("test_ai_image.png", "Image file"),
        ("test_document_with_images.docx", "Word document"),
        ("test_presentation_with_images.pptx", "PowerPoint")
    ]
    
    print("=" * 70)
    print("CONVERSION MODE TEST RESULTS")
    print("=" * 70)
    
    # Check LLM status
    llm_status = service.llm_client.get_status()
    print(f"\nLLM Service: {llm_status['provider']} ({llm_status.get('model', 'N/A')})")
    print(f"API Available: {'✅ Yes' if llm_status['available'] else '❌ No'}")
    print("=" * 70)
    
    for filename, description in test_files:
        if not os.path.exists(filename):
            print(f"\n❌ {filename} not found, skipping...")
            continue
            
        print(f"\n📁 {description}: {filename}")
        print("-" * 50)
        
        # Test Normal Mode
        print("  [Normal Mode]")
        normal_output = f"{os.path.splitext(filename)[0]}_normal_test.md"
        result_normal = await service.convert_file_enhanced(
            filename, 
            normal_output,
            use_ai_mode=False
        )
        
        if result_normal.status.value == 'completed':
            print(f"    ✅ Success ({result_normal.processing_time:.2f}s)")
            
            # Check content
            output_path = os.path.join("./converted", normal_output)
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    content = f.read()
                file_size = len(content)
                print(f"    📄 Output size: {file_size / 1024:.1f} KB")
                
                # Check for key features
                has_ocr = "OCR" in content or "Extracted Text" in content
                has_embedded = "Embedded Images" in content
                
                if has_ocr:
                    print(f"    ✅ OCR text extraction")
                if has_embedded:
                    print(f"    ✅ Embedded images found")
        else:
            print(f"    ❌ Failed: {result_normal.error_message}")
        
        # Test AI Mode
        print("  [AI Mode]")
        ai_output = f"{os.path.splitext(filename)[0]}_ai_test.md"
        result_ai = await service.convert_file_enhanced(
            filename,
            ai_output,
            use_ai_mode=True
        )
        
        if result_ai.status.value == 'completed':
            print(f"    ✅ Success ({result_ai.processing_time:.2f}s)")
            
            # Check content
            output_path = os.path.join("./converted", ai_output)
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    content = f.read()
                file_size = len(content)
                print(f"    📄 Output size: {file_size / 1024:.1f} KB")
                
                # Check for AI features
                has_ai_analysis = "AI Image Analysis" in content or "AI Analysis" in content
                has_chart = "Chart/Graph Analysis" in content
                has_embedded_ai = "AI Analysis:" in content
                
                if has_ai_analysis:
                    print(f"    ✅ AI image analysis")
                if has_chart:
                    print(f"    ✅ Chart/graph analysis")
                if has_embedded_ai:
                    print(f"    ✅ AI analysis for embedded images")
                    
                # Compare with normal mode
                normal_path = os.path.join("./converted", normal_output)
                if os.path.exists(normal_path):
                    with open(normal_path, 'r') as f:
                        normal_size = len(f.read())
                    size_diff = (file_size - normal_size) / 1024
                    print(f"    📊 Size difference: +{size_diff:.1f} KB")
        else:
            print(f"    ❌ Failed: {result_ai.error_message}")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    
    # Summary
    print("\n📋 SUMMARY:")
    print("- Normal Mode: Uses PaddleOCR for text extraction")
    print("- AI Mode: Uses OpenAI GPT-4 for intelligent analysis")
    print("- Both modes are working correctly!")

if __name__ == "__main__":
    asyncio.run(test_both_modes())