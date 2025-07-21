#!/usr/bin/env python3
"""
Bloomberg API Diagnostic Script
This script helps diagnose Bloomberg Terminal API connectivity issues
"""

import sys
import os
import subprocess
import socket
from datetime import datetime

def check_bloomberg_processes():
    """Check if Bloomberg Terminal processes are running"""
    print("\n=== Checking Bloomberg Processes ===")
    processes = ['wintrv.exe', 'bbcomm.exe', 'blp.exe']
    found = False
    
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        for process in processes:
            if process.lower() in result.stdout.lower():
                print(f"✓ Found: {process}")
                found = True
        if not found:
            print("✗ No Bloomberg processes found")
    except Exception as e:
        print(f"✗ Error checking processes: {e}")
    
    return found

def check_bloomberg_api_path():
    """Check if Bloomberg API is installed"""
    print("\n=== Checking Bloomberg API Installation ===")
    paths = [
        r"C:\blp\API\Python",
        r"C:\blp\API\Python\blpapi",
        r"C:\blp\DAPI",
        r"C:\Program Files\Bloomberg\API",
        r"C:\Program Files (x86)\Bloomberg\API"
    ]
    
    found_paths = []
    for path in paths:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
            found_paths.append(path)
            # List contents
            try:
                contents = os.listdir(path)
                print(f"  Contents: {', '.join(contents[:5])}...")
            except:
                pass
        else:
            print(f"✗ Not found: {path}")
    
    return found_paths

def check_bloomberg_ports():
    """Check if Bloomberg API ports are open"""
    print("\n=== Checking Bloomberg API Ports ===")
    ports = {
        8194: "Bloomberg API Default",
        8195: "Bloomberg API Alternate",
        8196: "Bloomberg API Market Data"
    }
    
    for port, description in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✓ Port {port} ({description}): OPEN")
        else:
            print(f"✗ Port {port} ({description}): CLOSED")

def try_import_blpapi():
    """Try to import Bloomberg API"""
    print("\n=== Testing Bloomberg API Import ===")
    
    # Add all possible paths
    possible_paths = [
        r"C:\blp\API\Python",
        r"C:\blp\API\Python\blpapi",
        r"C:\blp\DAPI",
        r"C:\Program Files\Bloomberg\API\Python",
        r"C:\Program Files (x86)\Bloomberg\API\Python"
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)
    
    try:
        import blpapi
        print("✓ Successfully imported blpapi")
        print(f"  Version: {blpapi.__version__ if hasattr(blpapi, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import blpapi: {e}")
        return False

def test_bloomberg_connection():
    """Test actual Bloomberg connection"""
    print("\n=== Testing Bloomberg Connection ===")
    
    try:
        import blpapi
        
        # Session options
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost('localhost')
        sessionOptions.setServerPort(8194)
        
        print("Creating session...")
        session = blpapi.Session(sessionOptions)
        
        print("Starting session...")
        if not session.start():
            print("✗ Failed to start session")
            return False
        
        print("✓ Session started successfully")
        
        print("Opening service...")
        if not session.openService("//blp/refdata"):
            print("✗ Failed to open service")
            session.stop()
            return False
        
        print("✓ Service opened successfully")
        print("✓ Bloomberg Terminal connection is working!")
        
        session.stop()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def main():
    print("Bloomberg API Diagnostic Tool")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    # Run all checks
    processes_found = check_bloomberg_processes()
    api_paths = check_bloomberg_api_path()
    check_bloomberg_ports()
    api_imported = try_import_blpapi()
    
    if api_imported:
        connection_works = test_bloomberg_connection()
    else:
        connection_works = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Bloomberg Processes: {'✓ Running' if processes_found else '✗ Not found'}")
    print(f"Bloomberg API: {'✓ Installed' if api_paths else '✗ Not found'}")
    print(f"API Import: {'✓ Success' if api_imported else '✗ Failed'}")
    print(f"Terminal Connection: {'✓ Working' if connection_works else '✗ Failed'}")
    
    if not connection_works:
        print("\nRECOMMENDATIONS:")
        if not processes_found:
            print("1. Start Bloomberg Terminal")
        if not api_paths:
            print("2. Install Bloomberg API (contact Bloomberg support)")
        if not api_imported:
            print("3. Check Python paths and Bloomberg API installation")
        if processes_found and api_imported and not connection_works:
            print("4. Check if Bloomberg Terminal has API access enabled")
            print("5. Check Windows Firewall for port 8194")

if __name__ == "__main__":
    main()