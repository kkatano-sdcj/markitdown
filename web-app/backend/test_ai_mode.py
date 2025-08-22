#!/usr/bin/env python3
"""
Test AI conversion mode functionality
"""
import asyncio
import os
from app.services.enhanced_conversion_service import EnhancedConversionService
from app.services.llm_client_service import LLMClientService

async def test_ai_mode():
    """Test AI mode with different file types"""
    
    # Initialize service
    service = EnhancedConversionService()
    
    print("=" * 60)
    print("Testing AI Conversion Mode")
    print("=" * 60)
    
    # Check LLM client status
    llm_status = service.llm_client.get_status()
    print(f"\nLLM Client Status:")
    print(f"  Available: {llm_status['available']}")
    print(f"  Provider: {llm_status['provider']}")
    print(f"  Model: {llm_status.get('model', 'N/A')}")
    print(f"  Capabilities: {', '.join(llm_status.get('capabilities', []))}")
    
    # Test files
    test_files = [
        ("test_document_with_images.docx", "Word document with embedded images"),
        ("test_presentation_with_images.pptx", "PowerPoint with images"),
        ("test_paddle_text.png", "Image file")
    ]
    
    for filename, description in test_files:
        if os.path.exists(filename):
            print(f"\n{'='*40}")
            print(f"Testing: {description}")
            print(f"File: {filename}")
            print(f"{'='*40}")
            
            # Test Normal Mode
            print("\n[Normal Mode]")
            output_normal = f"{os.path.splitext(filename)[0]}_normal.md"
            result_normal = await service.convert_file_enhanced(
                filename, 
                output_normal,
                use_ai_mode=False
            )
            print(f"  Status: {result_normal.status.value}")
            if result_normal.status.value == 'completed':
                print(f"  Output: {result_normal.output_file}")
                print(f"  Processing time: {result_normal.processing_time:.2f}s")
            
            # Test AI Mode
            print("\n[AI Mode]")
            output_ai = f"{os.path.splitext(filename)[0]}_ai.md"
            result_ai = await service.convert_file_enhanced(
                filename,
                output_ai,
                use_ai_mode=True
            )
            print(f"  Status: {result_ai.status.value}")
            if result_ai.status.value == 'completed':
                print(f"  Output: {result_ai.output_file}")
                print(f"  Processing time: {result_ai.processing_time:.2f}s")
                
                # Compare file sizes
                normal_size = os.path.getsize(os.path.join("./converted", output_normal))
                ai_size = os.path.getsize(os.path.join("./converted", output_ai))
                print(f"  Normal mode size: {normal_size / 1024:.2f} KB")
                print(f"  AI mode size: {ai_size / 1024:.2f} KB")
                print(f"  Size difference: {(ai_size - normal_size) / 1024:.2f} KB")
    
    # Test YouTube URL
    print(f"\n{'='*40}")
    print("Testing: YouTube URL conversion")
    print(f"{'='*40}")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Normal mode
    print("\n[Normal Mode - YouTube]")
    result_yt_normal = await service.convert_file_enhanced(
        "",
        "youtube_normal.md",
        is_url=True,
        url_content=test_url,
        use_ai_mode=False
    )
    print(f"  Status: {result_yt_normal.status.value}")
    
    # AI mode
    print("\n[AI Mode - YouTube]")
    result_yt_ai = await service.convert_file_enhanced(
        "",
        "youtube_ai.md",
        is_url=True,
        url_content=test_url,
        use_ai_mode=True
    )
    print(f"  Status: {result_yt_ai.status.value}")
    
    print("\n" + "="*60)
    print("AI Mode Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_ai_mode())