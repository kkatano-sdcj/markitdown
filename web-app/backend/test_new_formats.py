#!/usr/bin/env python3
"""
Test script for new file format support
"""
import asyncio
import json
import csv
import zipfile
import os
from app.services.enhanced_conversion_service import EnhancedConversionService

async def test_conversions():
    service = EnhancedConversionService()
    
    # Test JSON file
    print("Testing JSON conversion...")
    test_json = {"name": "Test", "items": [1, 2, 3], "nested": {"key": "value"}}
    with open("test.json", "w") as f:
        json.dump(test_json, f)
    
    result = await service.convert_file_enhanced("test.json", "test_json.md")
    print(f"JSON conversion: {result.status}")
    if result.markdown_content:
        print(result.markdown_content[:500])
    
    # Test CSV file
    print("\nTesting CSV conversion...")
    with open("test.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age", "City"])
        writer.writerow(["Alice", 30, "Tokyo"])
        writer.writerow(["Bob", 25, "Osaka"])
    
    result = await service.convert_file_enhanced("test.csv", "test_csv.md")
    print(f"CSV conversion: {result.status}")
    if result.markdown_content:
        print(result.markdown_content[:500])
    
    # Test ZIP file
    print("\nTesting ZIP conversion...")
    with zipfile.ZipFile("test.zip", "w") as zf:
        zf.writestr("file1.txt", "This is file 1")
        zf.writestr("file2.txt", "This is file 2")
    
    result = await service.convert_file_enhanced("test.zip", "test_zip.md")
    print(f"ZIP conversion: {result.status}")
    if result.markdown_content:
        print(result.markdown_content[:500])
    
    # Test YouTube URL
    print("\nTesting YouTube URL conversion...")
    result = await service.convert_file_enhanced(
        "",
        "test_youtube.md",
        is_url=True,
        url_content="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    print(f"YouTube URL conversion: {result.status}")
    if result.markdown_content:
        print(result.markdown_content[:500])
    
    # Clean up test files
    for file in ["test.json", "test.csv", "test.zip"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_conversions())