#!/usr/bin/env python3
"""
Fix urllib3 SSL Warning
This script provides solutions for the NotOpenSSLWarning
"""

import subprocess
import sys
import platform

def main():
    print("🔧 urllib3 SSL Warning Fix\n")
    
    print("The warning you're seeing:")
    print("'NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the ssl module is compiled with LibreSSL 2.8.3'")
    print("\nThis is because macOS uses LibreSSL instead of OpenSSL.\n")
    
    print("Here are your options:\n")
    
    print("Option 1: Suppress the warning (Recommended)")
    print("-" * 50)
    print("Add this to the top of your Python scripts:")
    print("\nimport warnings")
    print("warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')\n")
    
    print("\nOption 2: Downgrade urllib3")
    print("-" * 50)
    print("Run this command:")
    print("pip3 install 'urllib3<2.0'\n")
    
    print("\nOption 3: Create a startup file to suppress globally")
    print("-" * 50)
    print("Create ~/.pythonrc with the warning suppression:")
    
    response = input("\nWould you like me to create the global suppression file? (y/n): ")
    
    if response.lower() == 'y':
        pythonrc_content = """# Suppress urllib3 SSL warning on macOS
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')
"""
        
        import os
        pythonrc_path = os.path.expanduser("~/.pythonrc")
        
        with open(pythonrc_path, 'w') as f:
            f.write(pythonrc_content)
        
        print(f"\n✅ Created {pythonrc_path}")
        print("\nNow add this to your ~/.zshrc or ~/.bash_profile:")
        print("export PYTHONSTARTUP=~/.pythonrc")
        print("\nThen reload your shell or run:")
        print("source ~/.zshrc")
    
    print("\n✨ That's it! The warning is harmless and doesn't affect functionality.")

if __name__ == "__main__":
    main()