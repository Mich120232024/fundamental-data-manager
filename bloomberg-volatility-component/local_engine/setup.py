#!/usr/bin/env python3
"""
Setup script for Bloomberg Volatility Local Engine
"""

import subprocess
import sys
import os


def install_requirements():
    """Install required packages"""
    print("Installing requirements for Bloomberg Volatility Local Engine...")
    
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("\n✓ All requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error installing requirements: {e}")
        sys.exit(1)


def test_bloomberg_connection():
    """Test connection to Bloomberg API"""
    print("\nTesting Bloomberg API connection...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from api.bloomberg_client import BloombergAPIClient
        
        client = BloombergAPIClient()
        health = client.health_check()
        
        if health.get("success"):
            print("✓ API connection successful")
            print(f"  Bloomberg Terminal: {'Connected' if health['data']['bloomberg_terminal_running'] else 'Not Connected'}")
            print(f"  Server Time: {health['data']['server_time']}")
        else:
            print("✗ API connection failed")
            
    except Exception as e:
        print(f"✗ Cannot connect to Bloomberg API: {e}")
        print("  Make sure the API is running at http://20.172.249.92:8080")


def main():
    """Main setup function"""
    print("Bloomberg Volatility Local Engine Setup")
    print("=" * 40)
    
    # Install requirements
    install_requirements()
    
    # Test connection
    test_bloomberg_connection()
    
    print("\nSetup complete! You can now run:")
    print("  python examples/display_eurusd_surface.py")


if __name__ == "__main__":
    main()