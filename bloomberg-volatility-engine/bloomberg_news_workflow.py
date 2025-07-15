#!/usr/bin/env python3
"""
Bloomberg News Workflow: Email → Terminal → Full Story Extraction
"""

import subprocess
import time

def create_bloomberg_news_workflow():
    """Create automated workflow for Bloomberg news extraction"""
    
    print("📧 Bloomberg News Extraction Workflow")
    print("=" * 60)
    
    workflow_script = r'''
Write-Host "Setting up Bloomberg News Extraction Workflow" -ForegroundColor Cyan

# Create the news extraction system
$newsWorkflow = @'
import sys
import os
import time
from datetime import datetime
import json
import re
sys.path.append(r"C:\blp\API\Python")

try:
    import blpapi
    import pyautogui  # For Terminal automation
    import win32com.client  # For Outlook integration
    import pyperclip  # For clipboard operations
except ImportError as e:
    print(f"Missing module: {e}")
    print("Installing required modules...")
    os.system("pip install pyautogui pywin32 pyperclip")

class BloombergNewsWorkflow:
    """Automated workflow for extracting Bloomberg news from email alerts"""
    
    def __init__(self):
        self.terminal_connected = False
        self.outlook = None
        self.setup_bloomberg_connection()
        self.setup_outlook_connection()
        
    def setup_bloomberg_connection(self):
        """Connect to Bloomberg Terminal"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost("localhost")
            sessionOptions.setServerPort(8194)
            
            self.session = blpapi.Session(sessionOptions)
            if self.session.start():
                self.terminal_connected = True
                print("✓ Connected to Bloomberg Terminal")
            else:
                print("✗ Failed to connect to Bloomberg Terminal")
        except Exception as e:
            print(f"Bloomberg connection error: {e}")
    
    def setup_outlook_connection(self):
        """Connect to Outlook for email monitoring"""
        try:
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            print("✓ Connected to Outlook")
        except Exception as e:
            print(f"✗ Outlook connection error: {e}")
    
    def monitor_bloomberg_emails(self):
        """Monitor Outlook for Bloomberg news alerts"""
        if not self.outlook:
            return []
        
        namespace = self.outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox
        
        # Filter for Bloomberg emails
        bloomberg_emails = []
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)  # Sort by newest first
        
        for message in messages:
            try:
                # Check if it's from Bloomberg
                if any(bloomberg_domain in str(message.SenderEmailAddress).lower() 
                       for bloomberg_domain in ['bloomberg.com', 'bloomberg.net', 'alert.bloomberg']):
                    
                    # Check if it's a news alert
                    subject = str(message.Subject)
                    if any(keyword in subject.lower() 
                           for keyword in ['alert', 'news', 'breaking', 'flash', 'urgent']):
                        
                        email_data = {
                            'subject': subject,
                            'body': str(message.Body),
                            'received': message.ReceivedTime,
                            'sender': str(message.SenderEmailAddress)
                        }
                        
                        # Extract story IDs or references
                        story_refs = self.extract_story_references(email_data)
                        if story_refs:
                            email_data['story_refs'] = story_refs
                            bloomberg_emails.append(email_data)
                        
                        # Only check last 10 emails
                        if len(bloomberg_emails) >= 10:
                            break
                            
            except Exception as e:
                print(f"Error processing email: {e}")
                
        return bloomberg_emails
    
    def extract_story_references(self, email_data):
        """Extract Bloomberg story IDs or references from email"""
        story_refs = []
        
        # Common patterns in Bloomberg emails
        patterns = [
            r'Story ID:\s*([A-Z0-9]+)',
            r'Reference:\s*([A-Z0-9]+)',
            r'bloomberg\.com/news/articles/([a-z0-9-]+)',
            r'First Word:\s*([A-Z][A-Z0-9]+)',
            r'NSN\s+([A-Z0-9]+)'
        ]
        
        text = email_data['subject'] + ' ' + email_data['body']
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            story_refs.extend(matches)
        
        return list(set(story_refs))  # Remove duplicates
    
    def open_story_in_terminal(self, story_ref):
        """Open story in Bloomberg Terminal using automation"""
        print(f"Opening story {story_ref} in Bloomberg Terminal...")
        
        try:
            # Bring Bloomberg Terminal to foreground
            # This assumes Terminal is already running
            pyautogui.hotkey('win', 'd')  # Show desktop
            time.sleep(0.5)
            
            # Click on Bloomberg Terminal (you may need to adjust coordinates)
            # Or use window title search
            terminal_windows = pyautogui.getWindowsWithTitle('Bloomberg')
            if terminal_windows:
                terminal_windows[0].activate()
                time.sleep(1)
                
                # Type news command
                pyautogui.write('N', interval=0.1)
                pyautogui.press('enter')
                time.sleep(2)
                
                # Search for story
                pyautogui.write(story_ref, interval=0.1)
                pyautogui.press('enter')
                time.sleep(3)
                
                # Copy the content (Ctrl+A, Ctrl+C)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.5)
                
                # Get from clipboard
                content = pyperclip.paste()
                
                return content
            else:
                print("Bloomberg Terminal window not found")
                return None
                
        except Exception as e:
            print(f"Terminal automation error: {e}")
            return None
    
    def save_news_content(self, story_ref, content):
        """Save extracted news content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bloomberg_news_{story_ref}_{timestamp}.json"
        
        data = {
            'story_ref': story_ref,
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'source': 'Bloomberg Terminal'
        }
        
        # Save to file
        filepath = os.path.join("C:\\Bloomberg\\NewsExtracted", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Saved news content to {filename}")
        return filepath
    
    def process_news_alerts(self):
        """Main workflow: Email → Terminal → Extract → Save"""
        print("\n📧 Checking for Bloomberg news alerts...")
        
        emails = self.monitor_bloomberg_emails()
        
        if not emails:
            print("No new Bloomberg news alerts found")
            return
        
        print(f"Found {len(emails)} Bloomberg news alerts")
        
        for email in emails:
            print(f"\n📨 Processing: {email['subject']}")
            
            for story_ref in email.get('story_refs', []):
                print(f"  → Story reference: {story_ref}")
                
                # Open in terminal and extract
                content = self.open_story_in_terminal(story_ref)
                
                if content:
                    # Save the content
                    filepath = self.save_news_content(story_ref, content)
                    
                    # Also save to database if configured
                    self.save_to_database(story_ref, content, email)
                else:
                    print(f"  ✗ Failed to extract content for {story_ref}")
    
    def save_to_database(self, story_ref, content, email_data):
        """Save to Cosmos DB or other database"""
        # This would connect to your Azure Cosmos DB
        print(f"  → Would save to database: {story_ref}")
        # Implementation depends on your database setup

# Alternative approach using Bloomberg MSG function
class BloombergMSGExtractor:
    """Extract news using Bloomberg MSG (message) function"""
    
    def __init__(self):
        self.setup_bloomberg()
    
    def setup_bloomberg(self):
        """Setup Bloomberg connection"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost("localhost")
            sessionOptions.setServerPort(8194)
            
            self.session = blpapi.Session(sessionOptions)
            if self.session.start() and self.session.openService("//blp/refdata"):
                self.refDataService = self.session.getService("//blp/refdata")
                print("✓ Bloomberg MSG service ready")
        except Exception as e:
            print(f"Bloomberg setup error: {e}")
    
    def get_msg_content(self, msg_number):
        """Get content using MSG function"""
        try:
            request = self.refDataService.createRequest("ReferenceDataRequest")
            request.append("securities", f"/msgnumber/{msg_number}")
            request.append("fields", "MSG_BODY")
            request.append("fields", "MSG_SUBJECT")
            request.append("fields", "MSG_TIME")
            
            self.session.sendRequest(request)
            
            # Process response
            while True:
                event = self.session.nextEvent(5000)
                for msg in event:
                    if msg.hasElement("securityData"):
                        # Extract message content
                        return self.parse_msg_response(msg)
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
        except Exception as e:
            print(f"MSG extraction error: {e}")
        
        return None

# Create HTTP endpoint for external access
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class NewsExtractionHandler(BaseHTTPRequestHandler):
    """HTTP handler for news extraction requests"""
    
    def do_POST(self):
        if self.path == '/extract-news':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            story_ref = data.get('story_ref')
            if story_ref:
                # Extract news content
                workflow = BloombergNewsWorkflow()
                content = workflow.open_story_in_terminal(story_ref)
                
                if content:
                    response = {
                        'status': 'success',
                        'story_ref': story_ref,
                        'content': content,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    response = {'status': 'error', 'message': 'Failed to extract content'}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == "__main__":
    print("Bloomberg News Extraction Workflow")
    print("=" * 50)
    
    # Start HTTP server for API access
    server = HTTPServer(('0.0.0.0', 8081), NewsExtractionHandler)
    print("✓ News extraction API running on port 8081")
    
    # Start workflow
    workflow = BloombergNewsWorkflow()
    
    # Process news alerts every 5 minutes
    while True:
        workflow.process_news_alerts()
        print("\nWaiting 5 minutes before next check...")
        time.sleep(300)  # 5 minutes
'@

# Save the workflow script
$workflowPath = "C:\Bloomberg\APIServer\bloomberg_news_workflow.py"
$newsWorkflow | Out-File -FilePath $workflowPath -Encoding UTF8
Write-Host "News workflow script created at: $workflowPath"

# Install required Python packages
Write-Host "`nInstalling required packages..."
C:\Python311\Scripts\pip.exe install pyautogui pywin32 pyperclip --quiet

# Create a simple test to check email
$emailTest = @'
import win32com.client

try:
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    inbox = namespace.GetDefaultFolder(6)
    
    print(f"Connected to Outlook. Inbox has {inbox.Items.Count} messages")
    
    # Check for Bloomberg emails
    bloomberg_count = 0
    for i, message in enumerate(inbox.Items):
        if i > 50:  # Only check last 50
            break
        try:
            if 'bloomberg' in str(message.SenderEmailAddress).lower():
                bloomberg_count += 1
        except:
            pass
    
    print(f"Found {bloomberg_count} Bloomberg emails in last 50 messages")
    
except Exception as e:
    print(f"Outlook test error: {e}")
'@

Write-Host "`nTesting Outlook connection..."
C:\Python311\python.exe -c $emailTest

Write-Host "`nWorkflow setup complete!" -ForegroundColor Green
Write-Host "`nThe workflow will:"
Write-Host "1. Monitor Outlook for Bloomberg news alerts"
Write-Host "2. Extract story references from emails"
Write-Host "3. Open stories in Bloomberg Terminal"
Write-Host "4. Copy and save the full content"
Write-Host "5. Store in local files and database"
'''

    # Execute workflow setup
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", workflow_script,
        "--no-wait"
    ]
    
    print("Setting up Bloomberg news extraction workflow...")
    subprocess.run(cmd, capture_output=True, text=True)
    
    print("\n📋 Workflow Overview:")
    print("=" * 60)
    print("""
📧 EMAIL MONITORING
   ↓
   Bloomberg sends news alert email
   ↓
🔍 EXTRACTION
   ↓
   System detects story ID/reference
   ↓
💻 TERMINAL AUTOMATION
   ↓
   Opens story in Bloomberg Terminal
   ↓
📄 CONTENT CAPTURE
   ↓
   Copies full article text
   ↓
💾 STORAGE
   ↓
   Saves to file/database
   ↓
🌐 API ACCESS
   ↓
   Available via HTTP endpoint
""")
    
    print("\n✅ Benefits of this approach:")
    print("1. Gets FULL news content (not just headlines)")
    print("2. Works with your existing Terminal access")
    print("3. Automated 24/7 monitoring")
    print("4. Stores everything locally")
    print("5. Can trigger alerts and analysis")
    
    print("\n🔧 Next steps:")
    print("1. Configure Outlook rules for Bloomberg emails")
    print("2. Test with a Bloomberg news alert")
    print("3. Set up database storage")
    print("4. Create news analysis pipeline")


if __name__ == "__main__":
    create_bloomberg_news_workflow()