"""
Gemini Python SDK fallback for Bloomberg VM
Use this if the Gemini CLI doesn't work properly
"""

import os
import json
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

# Configuration
GEMINI_API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"
CONFIG_PATH = os.path.expanduser("~/.gemini/config.json")

def setup_gemini():
    """Set up Gemini API configuration"""
    # Configure API key
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Create config directory if it doesn't exist
    config_dir = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"Created config directory: {config_dir}")
    
    # Save config file
    config = {
        "api_key": GEMINI_API_KEY,
        "default_model": "gemini-pro",
        "models": {
            "pro": "gemini-pro",
            "pro-vision": "gemini-pro-vision",
            "ultra": "gemini-ultra"
        }
    }
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to: {CONFIG_PATH}")

def test_gemini():
    """Test Gemini API connection"""
    print("\n=== Testing Gemini API Connection ===")
    
    try:
        # Create model
        model = genai.GenerativeModel('gemini-pro')
        
        # Test query
        response = model.generate_content("Hello! Please confirm you're working by saying 'Gemini is operational'")
        
        print("✓ SUCCESS: Gemini API is working!")
        print(f"Response: {response.text}")
        
        # Test with a more complex query
        print("\n=== Testing Complex Query ===")
        complex_response = model.generate_content(
            "What are the key differences between REST and GraphQL APIs? Provide 3 bullet points."
        )
        print(f"Complex Response:\n{complex_response.text}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: Gemini API test failed")
        print(f"Error details: {str(e)}")
        return False

def create_cli_wrapper():
    """Create a simple CLI wrapper for Gemini"""
    wrapper_script = """#!/usr/bin/env python
# Simple Gemini CLI wrapper
import sys
import google.generativeai as genai

API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"
genai.configure(api_key=API_KEY)

def main():
    if len(sys.argv) < 2:
        print("Usage: gemini-cli <prompt>")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    model = genai.GenerativeModel('gemini-pro')
    
    try:
        response = model.generate_content(prompt)
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    wrapper_path = os.path.expanduser("~/gemini-cli.py")
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_script)
    
    # Make it executable on Unix systems
    if sys.platform != 'win32':
        os.chmod(wrapper_path, 0o755)
    
    print(f"\nCLI wrapper created: {wrapper_path}")
    print("Usage: python ~/gemini-cli.py 'Your prompt here'")

def main():
    """Main setup and test function"""
    print("=== Gemini Python SDK Setup ===")
    print(f"API Key: {GEMINI_API_KEY[:10]}...")
    
    # Set up configuration
    setup_gemini()
    
    # Test the connection
    success = test_gemini()
    
    if success:
        # Create CLI wrapper
        create_cli_wrapper()
        
        print("\n=== Setup Complete ===")
        print("Gemini is configured and working!")
        print("\nYou can now use:")
        print("1. This script for testing: python gemini_python_fallback.py")
        print("2. The CLI wrapper: python ~/gemini-cli.py 'Your prompt'")
        print("3. Direct Python SDK in your scripts")
    else:
        print("\n=== Setup Failed ===")
        print("Please check:")
        print("1. Internet connection")
        print("2. API key validity")
        print("3. Firewall settings")

if __name__ == "__main__":
    main()