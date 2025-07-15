# Gemini CLI Setup for Bloomberg VM

This directory contains scripts to properly set up Gemini CLI on the Bloomberg VM (Windows Server 2022).

## Setup Instructions

### Step 1: Copy Files to Bloomberg VM

Copy this entire directory to the Bloomberg VM:
- Connect via RDP: `172.171.211.16`
- Username: `bloombergadmin`
- Copy to: `C:\Bloomberg\GeminiSetup\`

### Step 2: Install Google Cloud SDK (if not already installed)

1. Open PowerShell as Administrator
2. Navigate to the setup directory:
   ```powershell
   cd C:\Bloomberg\GeminiSetup
   ```
3. Run the installation script:
   ```powershell
   .\install_gemini_cli.ps1
   ```
4. Follow the installer prompts
5. **Restart PowerShell** after installation

### Step 3: Configure Gemini API Key

1. In PowerShell (regular user mode):
   ```powershell
   cd C:\Bloomberg\GeminiSetup
   .\setup_gemini_bloomberg_vm.ps1
   ```

2. This script will:
   - Set the GEMINI_API_KEY environment variable
   - Create configuration files in multiple locations
   - Create a test script on your Desktop

### Step 4: Verify Installation

1. Test Gemini CLI:
   ```powershell
   gemini --version
   gemini "Hello, are you working?"
   ```

2. If the CLI doesn't work, use the Python fallback:
   ```powershell
   # First install the Python package
   pip install google-generativeai
   
   # Then run the fallback script
   python gemini_python_fallback.py
   ```

## Files Included

1. **install_gemini_cli.ps1** - Installs Google Cloud SDK (includes gcloud and Gemini CLI)
2. **setup_gemini_bloomberg_vm.ps1** - Configures API key and creates config files
3. **gemini_python_fallback.py** - Python-based alternative if CLI fails
4. **README.md** - This file

## Configuration Details

- **API Key**: `AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4`
- **Config Locations**:
  - `%USERPROFILE%\.gemini\config.json`
  - `%USERPROFILE%\.config\gemini\config.json`
  - `%APPDATA%\gemini\config.json`

## Troubleshooting

### Issue: "gemini" command not found
- Make sure Google Cloud SDK is installed
- Restart PowerShell after installation
- Check if `gcloud` command works first

### Issue: API key not recognized
- Run `echo $env:GEMINI_API_KEY` to verify environment variable
- Check config files exist in the locations above
- Try the Python fallback method

### Issue: Network/Firewall errors
- Ensure the VM has internet access
- Check if `https://generativelanguage.googleapis.com` is accessible
- May need to configure proxy settings if behind corporate firewall

## Python Fallback Usage

If the Gemini CLI continues to have issues, use the Python SDK:

```python
import google.generativeai as genai

genai.configure(api_key="AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Your prompt here")
print(response.text)
```

## Integration with Bloomberg Terminal

Once Gemini is working, you can integrate it with your Bloomberg data pipeline:

```python
# Example: Analyze Bloomberg data with Gemini
import google.generativeai as genai
from bloomberg_api import get_market_data

# Get Bloomberg data
market_data = get_market_data("EURUSD Curncy")

# Analyze with Gemini
model = genai.GenerativeModel('gemini-pro')
prompt = f"Analyze this FX data and provide insights: {market_data}"
response = model.generate_content(prompt)
print(response.text)
```

## Support

If you encounter issues:
1. Check the PowerShell error messages
2. Verify network connectivity
3. Ensure all prerequisites are installed
4. Try the Python fallback method

—SOFTWARE_RESEARCH_ANALYST