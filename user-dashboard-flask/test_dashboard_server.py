#!/usr/bin/env python3
"""
Test script to verify the dashboard server functionality
"""

import requests
import json
import sys
from pathlib import Path

def test_server():
    """Test if server is running and responsive"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Dashboard Server...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running at", base_url)
        else:
            print("❌ Server returned status code:", response.status_code)
            return False
    except requests.ConnectionError:
        print("❌ Server is not running. Start it with:")
        print("   cd backend && python app.py")
        return False
    except Exception as e:
        print("❌ Error connecting to server:", str(e))
        return False
    
    # Test 2: Check API endpoints
    print("\n2. Testing API endpoints...")
    
    # Test containers endpoint
    try:
        response = requests.get(f"{base_url}/api/containers")
        data = response.json()
        if data.get('success'):
            print(f"✅ Containers API working - Found {len(data.get('containers', []))} containers")
        else:
            print("❌ Containers API error:", data.get('error'))
    except Exception as e:
        print("❌ Error testing containers API:", str(e))
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/api/stats")
        data = response.json()
        if data.get('success'):
            stats = data.get('stats', {})
            print(f"✅ Stats API working - Total documents: {stats.get('totalDocuments', 0)}")
        else:
            print("❌ Stats API error:", data.get('error'))
    except Exception as e:
        print("❌ Error testing stats API:", str(e))
    
    # Test 3: Check new documentation endpoints
    print("\n3. Testing Documentation Hub endpoints...")
    
    # Test docs structure endpoint
    try:
        response = requests.get(f"{base_url}/api/docs/structure")
        data = response.json()
        if data.get('success'):
            structure = data.get('structure', {})
            stats = data.get('stats', {})
            print(f"✅ Docs structure API working")
            print(f"   - Categories: {stats.get('categories', 0)}")
            print(f"   - Total files: {stats.get('total_files', 0)}")
            print(f"   - Total size: {stats.get('total_size', 0)} bytes")
            
            # List categories
            if structure:
                print("   - Available categories:")
                for category, files in structure.items():
                    print(f"     • {category}: {len(files)} files")
        else:
            print("❌ Docs structure API error:", data.get('error'))
    except Exception as e:
        print("❌ Error testing docs structure API:", str(e))
    
    # Test docs content endpoint
    try:
        response = requests.get(f"{base_url}/api/docs/content?path=README.md")
        data = response.json()
        if data.get('success'):
            content_preview = data.get('content', '')[:100] + '...' if len(data.get('content', '')) > 100 else data.get('content', '')
            print(f"✅ Docs content API working - Successfully loaded README.md")
            print(f"   Preview: {content_preview}")
        else:
            print("❌ Docs content API error:", data.get('error'))
    except Exception as e:
        print("❌ Error testing docs content API:", str(e))
    
    print("\n" + "=" * 50)
    print("✨ Dashboard server test complete!")
    print("\nTo access the dashboard:")
    print(f"  1. Make sure server is running: cd backend && python app.py")
    print(f"  2. Open browser to: {base_url}")
    print(f"  3. Click on the 'Documentation Hub' tab to view docs")
    
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)