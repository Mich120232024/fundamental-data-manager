# Bloomberg API Server Auto-Start Setup

## Option 1: Task Scheduler (Recommended)

### Create Scheduled Task on VM

1. Copy `startup_and_monitoring.ps1` to `C:\Bloomberg\APIServer\`

2. Create scheduled task:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Bloomberg\APIServer\startup_and_monitoring.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "BloombergAPIMonitor" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Monitors and maintains Bloomberg API Server"
```

3. Start the task immediately:
```powershell
Start-ScheduledTask -TaskName "BloombergAPIMonitor"
```

## Option 2: Windows Service

### Create Windows Service

1. Install NSSM (Non-Sucking Service Manager):
```powershell
# Download NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "C:\temp\nssm.zip"
Expand-Archive -Path "C:\temp\nssm.zip" -DestinationPath "C:\temp\"
Copy-Item "C:\temp\nssm-2.24\win64\nssm.exe" -Destination "C:\Windows\System32\"
```

2. Create service:
```powershell
nssm install BloombergAPI "C:\Python311\python.exe" "C:\Bloomberg\APIServer\real_bloomberg_api.py"
nssm set BloombergAPI AppDirectory "C:\Bloomberg\APIServer"
nssm set BloombergAPI DisplayName "Bloomberg API Server"
nssm set BloombergAPI Description "Provides REST API access to Bloomberg Terminal"
nssm set BloombergAPI Start SERVICE_AUTO_START
```

3. Start service:
```powershell
nssm start BloombergAPI
```

## Option 3: Startup Script

### Add to Windows Startup

1. Create batch file `C:\Bloomberg\APIServer\start_api.bat`:
```batch
@echo off
cd /d C:\Bloomberg\APIServer
start /B C:\Python311\python.exe real_bloomberg_api.py
```

2. Add to startup folder:
```powershell
Copy-Item "C:\Bloomberg\APIServer\start_api.bat" -Destination "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\"
```

## Monitoring Commands

### Check if running:
```powershell
# Check scheduled task
Get-ScheduledTask -TaskName "BloombergAPIMonitor" | Select-Object TaskName, State

# Check service
Get-Service -Name "BloombergAPI" -ErrorAction SilentlyContinue

# Check process
Get-Process python* | Where-Object {$_.Path -like "*Bloomberg*"}

# Check API health
Invoke-RestMethod -Uri "http://localhost:8080/health"
```

### View logs:
```powershell
Get-Content "C:\Bloomberg\APIServer\monitor.log" -Tail 50
```

### Manual restart:
```powershell
# Restart scheduled task
Restart-ScheduledTask -TaskName "BloombergAPIMonitor"

# Restart service
Restart-Service -Name "BloombergAPI"

# Kill and restart manually
Get-Process python* | Stop-Process -Force
cd C:\Bloomberg\APIServer
Start-Process C:\Python311\python.exe -ArgumentList "real_bloomberg_api.py" -WindowStyle Hidden
```

## Azure CLI Commands

### Deploy monitoring script:
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts @startup_and_monitoring.ps1
```

### Check status remotely:
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-ScheduledTask -TaskName 'BloombergAPIMonitor' | Select-Object State"
```

## Important Notes

1. **Bloomberg Terminal** must be running and logged in
2. **Auto-logon** should be configured for the Windows user
3. **Monitor script** checks health every 5 minutes
4. **Logs** are written to `C:\Bloomberg\APIServer\monitor.log`
5. **Scheduled task** survives reboots better than services