# Bloomberg API Server Deployment Instructions

## 📦 Files to Copy to VM

Copy these files to `C:\Bloomberg\APIServer\` on the VM:

1. **bloomberg_api_server.py** - The main API server
2. **setup_bloomberg_service.ps1** - Windows service installer
3. **requirements.txt** - Python dependencies

## 🚀 Deployment Steps

### 1. Connect to VM via RDP
```
Server: 20.172.249.92
Username: bloombergadmin
Password: Ii89rra137+*
```

### 2. Create Directory
Open PowerShell as Administrator and run:
```powershell
New-Item -ItemType Directory -Force -Path "C:\Bloomberg\APIServer"
```

### 3. Copy Files
Copy the files listed above to `C:\Bloomberg\APIServer\`

### 4. Install Dependencies
```powershell
cd C:\Bloomberg\APIServer
pip install fastapi uvicorn[standard] python-multipart
```

### 5. Test the Server
First, test manually:
```powershell
cd C:\Bloomberg\APIServer
python bloomberg_api_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 6. Test API Access
Open a browser on the VM and go to:
- http://localhost:8080/docs - Should show Swagger UI
- http://localhost:8080/health - Should show health status

### 7. Install as Windows Service
Once manual test works, install as service:
```powershell
# Run as Administrator
cd C:\Bloomberg\APIServer
.\setup_bloomberg_service.ps1
```

### 8. Verify Service
```powershell
# Check if service is running
Get-ScheduledTask -TaskName "BloombergAPIServer"

# Check logs
Get-WinEvent -LogName Application | Where-Object {$_.Message -like "*Bloomberg*"} | Select-Object -First 10
```

## 🧪 Test from External Machine

Once the service is running, test from your local machine:

```python
from bloomberg_client import BloombergClient

client = BloombergClient("http://20.172.249.92:8080")
health = client.health_check()
print(health)
```

## 🔧 Troubleshooting

### API Server Won't Start
1. Check Bloomberg Terminal is running
2. Check Bloomberg Terminal is logged in
3. Check Python path: `where python`
4. Check BLPAPI installation: `python -c "import blpapi"`

### Can't Connect Externally
1. Check Windows Firewall on VM
2. Check NSG rules: `az network nsg rule list -g bloomberg-terminal-rg --nsg-name bloomberg-nsg`
3. Test from VM first: `curl http://localhost:8080/health`

### Service Not Running
1. Check Task Scheduler: `taskschd.msc`
2. Check Event Viewer for errors
3. Run manually to see errors: `python C:\Bloomberg\APIServer\bloomberg_api_server.py`