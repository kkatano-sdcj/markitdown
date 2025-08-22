#!/usr/bin/env python3
"""
Debug AI conversion mode
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.services.enhanced_conversion_service import EnhancedConversionService
from app.services.llm_client_service import LLMClientService

async def debug_test():
    print("=" * 60)
    print("AI Conversion Debug Test")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"\n1. Environment Check:")
    if api_key:
        print(f"   ✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print(f"   ❌ No API key in environment")
    
    # Initialize service
    print(f"\n2. Service Initialization:")
    service = EnhancedConversionService()
    
    # Check LLM client
    print(f"\n3. LLM Client Status:")
    print(f"   Type: {type(service.llm_client).__name__}")
    print(f"   Available: {service.llm_client.is_available()}")
    status = service.llm_client.get_status()
    print(f"   Provider: {status.get('provider', 'N/A')}")
    print(f"   Model: {status.get('model', 'N/A')}")
    
    # Test conversion with AI mode
    print(f"\n4. Testing AI Conversion:")
    
    result = await service.convert_file_enhanced(
        'test_ai_image.png',
        'debug_ai_output.md',
        use_ai_mode=True
    )
    
    print(f"   Status: {result.status.value}")
    
    if result.status.value == 'completed':
        # Check output
        output_path = './converted/debug_ai_output.md'
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                content = f.read()
            
            # Check for AI sections
            has_ai_analysis = "AI Image Analysis" in content
            has_chart_analysis = "Chart/Graph Analysis" in content
            
            print(f"   ✅ File created: debug_ai_output.md")
            print(f"   AI Analysis Section: {'✅ Found' if has_ai_analysis else '❌ Not found'}")
            print(f"   Chart Analysis: {'✅ Found' if has_chart_analysis else '❌ Not found'}")
            
            if has_ai_analysis:
                # Extract AI content
                import re
                ai_match = re.search(r'## AI Image Analysis.*?(?=##|\Z)', content, re.DOTALL)
                if ai_match:
                    print(f"\n5. AI Analysis Content:")
                    print("-" * 40)
                    print(ai_match.group()[:500])
                    print("-" * 40)
        else:
            print(f"   ❌ Output file not found")
    else:
        print(f"   ❌ Conversion failed: {result.error_message}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_test())