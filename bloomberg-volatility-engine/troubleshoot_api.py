#!/usr/bin/env python3
"""
Troubleshoot Bloomberg API Server deployment
"""

import subprocess
import json

def run_azure_command(cmd, description):
    """Run Azure CLI command and return result"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout.strip().startswith('{') else result.stdout
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def troubleshoot():
    """Troubleshoot the Bloomberg API server"""
    
    print("🔍 Bloomberg API Server Troubleshooting")
    print("=" * 50)
    
    RG = "bloomberg-terminal-rg"
    VM = "bloomberg-vm-02"
    
    # 1. Check VM status
    vm_status = run_azure_command(
        ["az", "vm", "show", "-g", RG, "-n", VM, "--query", "powerState", "-o", "tsv"],
        "Checking VM power state"
    )
    print(f"VM Status: {vm_status}")
    
    # 2. Check if Python process is running
    check_process = r'''
$procs = Get-Process python* -ErrorAction SilentlyContinue
if ($procs) {
    Write-Host "Python processes found:"
    $procs | ForEach-Object { Write-Host "  PID: $($_.Id), Path: $($_.Path)" }
} else {
    Write-Host "No Python processes found"
}

# Check if port 8080 is listening
$tcp = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($tcp) {
    Write-Host "Port 8080 is listening: $($tcp.State)"
} else {
    Write-Host "Port 8080 is NOT listening"
}

# Check firewall rules
$rules = Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*8080*" -or $_.DisplayName -like "*Bloomberg*"}
Write-Host "Firewall rules found: $($rules.Count)"
'''
    
    result = subprocess.run([
        "az", "vm", "run-command", "invoke",
        "-g", RG, "-n", VM,
        "--command-id", "RunPowerShellScript",
        "--scripts", check_process,
        "--query", "value[0].message",
        "-o", "tsv"
    ], capture_output=True, text=True, timeout=45)
    
    print("\nProcess and Port Check:")
    print(result.stdout if result.stdout else "No output")
    
    # 3. Try to start the server again with better error handling
    start_server = r'''
$path = "C:\Bloomberg\APIServer"
$logFile = "$path\server_log.txt"

# Check if directory exists
if (Test-Path $path) {
    Write-Host "API directory exists"
    
    # Check for Python script
    if (Test-Path "$path\api_server.py") {
        Write-Host "API server script found"
        
        # Try to start with output capture
        Write-Host "Attempting to start server..."
        
        # Create a batch file to run the server
        @"
@echo off
cd /d C:\Bloomberg\APIServer
echo Starting server at %date% %time% >> server_log.txt
C:\Python311\python.exe api_server.py >> server_log.txt 2>&1
"@ | Out-File -FilePath "$path\run_server.bat" -Encoding ASCII
        
        # Start using the batch file
        Start-Process -FilePath "$path\run_server.bat" -WorkingDirectory $path -WindowStyle Hidden
        
        Start-Sleep -Seconds 5
        
        # Check if it started
        $proc = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*python*"}
        if ($proc) {
            Write-Host "Python process started: PID $($proc.Id)"
        } else {
            Write-Host "Failed to start Python process"
            
            # Check log file
            if (Test-Path $logFile) {
                Write-Host "Log file contents:"
                Get-Content $logFile -Tail 20
            }
        }
    } else {
        Write-Host "API server script NOT found!"
    }
} else {
    Write-Host "API directory does NOT exist!"
}
'''
    
    print("\n\nAttempting to restart server...")
    result = subprocess.run([
        "az", "vm", "run-command", "invoke",
        "-g", RG, "-n", VM,
        "--command-id", "RunPowerShellScript",
        "--scripts", start_server,
        "--query", "value[0].message",
        "-o", "tsv"
    ], capture_output=True, text=True, timeout=45)
    
    print(result.stdout if result.stdout else "No output")
    
    # 4. Test internal connectivity
    test_internal = '''
# Test localhost connection
try {
    $response = Invoke-WebRequest -Uri http://localhost:8080/health -TimeoutSec 5 -UseBasicParsing
    Write-Host "Localhost test SUCCESS: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Localhost test FAILED: $_"
}
'''
    
    print("\n\nTesting internal connectivity...")
    result = subprocess.run([
        "az", "vm", "run-command", "invoke",
        "-g", RG, "-n", VM,
        "--command-id", "RunPowerShellScript",
        "--scripts", test_internal,
        "--query", "value[0].message",
        "-o", "tsv"
    ], capture_output=True, text=True, timeout=30)
    
    print(result.stdout if result.stdout else "No output")
    
    print("\n\n📋 Summary:")
    print("If the server is running internally but not accessible externally:")
    print("1. Windows Firewall may be blocking despite rules")
    print("2. NSG rules may need to be re-applied")
    print("3. The VM's internal IP might have changed")
    print("\nNext steps:")
    print("- RDP to the VM and check if http://localhost:8080 works")
    print("- Run 'netstat -an | findstr 8080' to verify listening")
    print("- Check Windows Firewall advanced settings")


if __name__ == "__main__":
    troubleshoot()