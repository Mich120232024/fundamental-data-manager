# Patch the start() method to actually connect to Bloomberg

$startMethod = @'
    def start(self):
        """Start Bloomberg session - connects to localhost:8194"""
        try:
            import blpapi
            # Bloomberg Terminal API settings
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost('localhost')
            sessionOptions.setServerPort(8194)
            
            # Create and start session
            self.session = blpapi.Session(sessionOptions)
            if not self.session.start():
                raise Exception("Failed to start Bloomberg session")
                
            # Open reference data service
            if not self.session.openService("//blp/refdata"):
                raise Exception("Failed to open Bloomberg reference data service")
                
            self.service = self.session.getService("//blp/refdata")
            logger.info("Bloomberg Terminal connected successfully")
            
        except ImportError:
            raise Exception("Bloomberg API not available - blpapi package not installed")
        except Exception as e:
            logger.error(f"Bloomberg connection failed: {e}")
            raise Exception(f"Bloomberg Terminal not available: {e}")
'@

# Read current file
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace the start method
$pattern = '(?s)def start\(self\):.*?(?=\n    def get_reference_data)'
$newContent = $content -replace $pattern, $startMethod.TrimStart()

# Save
$newContent | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Patched start() method"