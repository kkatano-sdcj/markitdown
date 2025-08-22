#!/usr/bin/env python3
"""
OpenAI API接続テストスクリプト
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

# Try to load from different locations
env_locations = [
    Path(__file__).parent / '.env',
    Path(__file__).parent.parent.parent / '.env',
    Path(__file__).parent.parent.parent / '.env.example'
]

for env_path in env_locations:
    if env_path.exists():
        print(f"Loading environment from: {env_path}")
        load_dotenv(env_path, override=True)
        break

# Test OpenAI API
from app.services.llm_client_service import LLMClientService
import asyncio

def test_api_key():
    """Test OpenAI API key configuration"""
    print("=" * 60)
    print("OpenAI API Key Test")
    print("=" * 60)
    
    # Check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    # Mask API key for display
    if api_key.startswith("sk-"):
        masked_key = f"{api_key[:7]}...{api_key[-4:]}"
        print(f"✅ API Key found: {masked_key}")
    else:
        print(f"⚠️  API Key found but format may be incorrect")
    
    # Initialize LLM client
    print("\nInitializing LLM Client...")
    llm_client = LLMClientService(api_key=api_key)
    
    # Check status
    status = llm_client.get_status()
    print(f"\nLLM Client Status:")
    print(f"  Available: {status['available']}")
    print(f"  Provider: {status.get('provider', 'N/A')}")
    print(f"  Model: {status.get('model', 'N/A')}")
    
    if not llm_client.is_available():
        print("\n❌ LLM Client not available - using mock service")
        return False
    
    print("\n✅ LLM Client initialized successfully with OpenAI")
    
    # Test API call
    print("\nTesting API call...")
    try:
        # Create a simple test image
        from PIL import Image, ImageDraw
        import tempfile
        
        # Create test image
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 40), "Test API", fill='black')
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            temp_path = tmp.name
        
        # Test image description
        description = llm_client.describe_image(
            temp_path,
            context="Test image for API validation"
        )
        
        print("\nAPI Response:")
        print("-" * 40)
        print(description[:200] + "..." if len(description) > 200 else description)
        print("-" * 40)
        
        # Clean up
        os.unlink(temp_path)
        
        if "Mock" in description or "mock" in description:
            print("\n⚠️  Received mock response - API may not be working")
            return False
        
        print("\n✅ API call successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ API call failed: {str(e)}")
        
        # Check if it's an authentication error
        if "api" in str(e).lower() and "key" in str(e).lower():
            print("\n⚠️  This appears to be an API key authentication issue.")
            print("Please check that your API key is valid and has the correct permissions.")
        
        return False

async def test_ai_conversion():
    """Test AI conversion with actual API"""
    from app.services.enhanced_conversion_service import EnhancedConversionService
    
    print("\n" + "=" * 60)
    print("Testing AI Conversion Mode with Real API")
    print("=" * 60)
    
    service = EnhancedConversionService()
    
    # Check if using real API
    if service.llm_client.get_status()['provider'] == 'OpenAI':
        print("✅ Using real OpenAI API")
    else:
        print("⚠️  Using mock API service")
    
    # Test with a simple image if it exists
    test_file = "test_paddle_text.png"
    if os.path.exists(test_file):
        print(f"\nTesting with: {test_file}")
        
        result = await service.convert_file_enhanced(
            test_file,
            "test_api_output.md",
            use_ai_mode=True
        )
        
        if result.status.value == 'completed':
            print("✅ Conversion completed")
            
            # Check output for AI content
            output_path = os.path.join("./converted", "test_api_output.md")
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    content = f.read()
                
                if "AI Image Analysis" in content or "AI Document Analysis" in content:
                    print("✅ AI analysis section found in output")
                    
                    # Check if it's real or mock
                    if "Mock" not in content and "mock" not in content:
                        print("✅ Real AI analysis detected")
                    else:
                        print("⚠️  Mock AI analysis detected")
        else:
            print(f"❌ Conversion failed: {result.error_message}")

if __name__ == "__main__":
    # Test API key
    api_working = test_api_key()
    
    if api_working:
        print("\n" + "🎉 " * 10)
        print("OpenAI API is properly configured and working!")
        print("🎉 " * 10)
        
        # Test AI conversion
        asyncio.run(test_ai_conversion())
    else:
        print("\n" + "⚠️ " * 10)
        print("OpenAI API is not properly configured.")
        print("AI mode will use mock responses.")
        print("⚠️ " * 10)
        
        print("\nTo enable real AI features:")
        print("1. Get an API key from https://platform.openai.com/api-keys")
        print("2. Set it in .env file: OPENAI_API_KEY=your-key-here")
        print("3. Restart the backend server")