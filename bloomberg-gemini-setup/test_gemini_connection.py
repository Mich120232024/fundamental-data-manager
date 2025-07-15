"""
Comprehensive Gemini API connection test for Bloomberg VM
Tests all major Gemini models and capabilities
"""

import os
import sys
import json
import time
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

# Configuration
API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

def test_basic_connection():
    """Test basic API connectivity"""
    print("\n" + "="*50)
    print("TEST 1: Basic Connection Test")
    print("="*50)
    
    try:
        genai.configure(api_key=API_KEY)
        
        # List available models
        models = genai.list_models()
        print("✓ Successfully connected to Gemini API")
        print(f"✓ Found {len(list(models))} available models")
        
        # Show first few models
        print("\nAvailable models:")
        for i, model in enumerate(genai.list_models()):
            if i < 5:  # Show first 5 models
                print(f"  - {model.name}")
        
        return True
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

def test_text_generation():
    """Test text generation capabilities"""
    print("\n" + "="*50)
    print("TEST 2: Text Generation Test")
    print("="*50)
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Simple test
        response = model.generate_content("What is 2+2? Answer with just the number.")
        print(f"✓ Simple math test: {response.text.strip()}")
        
        # Complex test
        complex_prompt = """
        Analyze the following FX data pattern and provide one key insight:
        EURUSD: 1.0850 -> 1.0890 (+0.37%)
        Volume: Increasing
        RSI: 65
        """
        response = model.generate_content(complex_prompt)
        print(f"✓ Complex analysis test completed")
        print(f"  Response preview: {response.text[:100]}...")
        
        return True
    except Exception as e:
        print(f"✗ Text generation failed: {str(e)}")
        return False

def test_streaming():
    """Test streaming responses"""
    print("\n" + "="*50)
    print("TEST 3: Streaming Response Test")
    print("="*50)
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(
            "Count from 1 to 5, with each number on a new line",
            stream=True
        )
        
        print("✓ Streaming test:")
        chunks_received = 0
        for chunk in response:
            chunks_received += 1
            print(f"  Chunk {chunks_received}: {chunk.text}", end='')
        
        print(f"\n✓ Received {chunks_received} streaming chunks")
        return True
    except Exception as e:
        print(f"✗ Streaming failed: {str(e)}")
        return False

def test_safety_settings():
    """Test content safety settings"""
    print("\n" + "="*50)
    print("TEST 4: Safety Settings Test")
    print("="*50)
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Test with different safety settings
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        response = model.generate_content(
            "Explain financial market volatility",
            safety_settings=safety_settings
        )
        
        print("✓ Content generated with safety settings")
        print(f"  Response length: {len(response.text)} characters")
        
        return True
    except Exception as e:
        print(f"✗ Safety settings test failed: {str(e)}")
        return False

def test_token_counting():
    """Test token counting functionality"""
    print("\n" + "="*50)
    print("TEST 5: Token Counting Test")
    print("="*50)
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        test_text = """
        The Bloomberg Terminal shows EURUSD at 1.0850 with increasing volume.
        Market sentiment appears bullish based on technical indicators.
        """
        
        token_count = model.count_tokens(test_text)
        print(f"✓ Token counting works")
        print(f"  Test text tokens: {token_count.total_tokens}")
        
        return True
    except Exception as e:
        print(f"✗ Token counting failed: {str(e)}")
        return False

def create_test_report(results):
    """Create a detailed test report"""
    report = {
        "test_date": datetime.now().isoformat(),
        "api_key_partial": API_KEY[:10] + "...",
        "test_results": results,
        "overall_status": "PASS" if all(results.values()) else "FAIL",
        "environment": {
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
            "genai_version": genai.__version__ if hasattr(genai, '__version__') else "unknown"
        }
    }
    
    # Save report
    report_path = "gemini_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Test report saved to: {report_path}")
    
    return report

def main():
    """Run all tests"""
    print("="*50)
    print("GEMINI API COMPREHENSIVE TEST SUITE")
    print("="*50)
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = {
        "basic_connection": test_basic_connection(),
        "text_generation": test_text_generation(),
        "streaming": test_streaming(),
        "safety_settings": test_safety_settings(),
        "token_counting": test_token_counting()
    }
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Create report
    report = create_test_report(results)
    
    if report["overall_status"] == "PASS":
        print("\n🎉 All tests passed! Gemini API is fully operational.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
    
    # Provide next steps
    print("\n" + "="*50)
    print("NEXT STEPS")
    print("="*50)
    print("1. If all tests passed, Gemini is ready for use")
    print("2. Integration example:")
    print("   python -c \"import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print(genai.GenerativeModel('gemini-pro').generate_content('Hello').text)\"")
    print("3. For Bloomberg integration, see the README.md file")

if __name__ == "__main__":
    main()