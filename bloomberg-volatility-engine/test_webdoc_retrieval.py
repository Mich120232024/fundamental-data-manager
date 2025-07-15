#!/usr/bin/env python3
"""
Test retrieving a specific Bloomberg article using webdoc ID
Article: "Euro Loses 0.77% to $1.1690 -- Data Talk"
Webdoc ID: 0B06E00E-BB09-4F01-844D-55C242BDBC7B
"""

import subprocess
import time

def test_webdoc_retrieval():
    """Test if we can retrieve a Bloomberg article using webdoc ID on the Terminal"""
    
    print("🔍 Testing Bloomberg Article Retrieval")
    print("=" * 60)
    print("Article: Euro Loses 0.77% to $1.1690 -- Data Talk")
    print("Webdoc ID: 0B06E00E-BB09-4F01-844D-55C242BDBC7B")
    print("=" * 60)
    
    retrieval_script = r'''
Write-Host "Testing Bloomberg Article Retrieval via Webdoc ID" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Install required packages if not already installed
Write-Host "`nChecking Python packages..."
C:\Python311\Scripts\pip.exe install pyautogui pywin32 pyperclip pillow --quiet

$articleTest = @'
import sys
import os
import time
import json
from datetime import datetime

# Add Bloomberg API path
sys.path.append(r"C:\blp\API\Python")

try:
    import blpapi
    import pyautogui
    import pyperclip
    import win32gui
    import win32con
    from PIL import ImageGrab
except ImportError as e:
    print(f"Missing module: {e}")
    sys.exit(1)

class BloombergArticleRetriever:
    """Retrieve specific Bloomberg articles using Terminal automation"""
    
    def __init__(self):
        self.webdoc_id = "0B06E00E-BB09-4F01-844D-55C242BDBC7B"
        self.article_title = "Euro Loses 0.77% to $1.1690 -- Data Talk"
        
    def find_bloomberg_window(self):
        """Find Bloomberg Terminal window"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if 'bloomberg' in window_text.lower():
                    windows.append((hwnd, window_text))
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        for hwnd, title in windows:
            print(f"Found window: {title}")
            return hwnd
        
        return None
    
    def activate_bloomberg(self):
        """Bring Bloomberg Terminal to foreground"""
        hwnd = self.find_bloomberg_window()
        if hwnd:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(2)
                print("✓ Bloomberg Terminal activated")
                return True
            except Exception as e:
                print(f"Error activating window: {e}")
        return False
    
    def try_news_search(self):
        """Try to search for the article using NEWS function"""
        print("\n1. TRYING NEWS SEARCH")
        print("-" * 40)
        
        try:
            # Clear any existing input
            pyautogui.hotkey('esc')
            time.sleep(0.5)
            
            # Open NEWS function
            pyautogui.write('NEWS', interval=0.1)
            pyautogui.press('enter')
            time.sleep(3)
            
            # Search for article by title keywords
            pyautogui.write('Euro 0.77 Data Talk', interval=0.1)
            pyautogui.press('enter')
            time.sleep(5)
            
            # Take screenshot of results
            screenshot = ImageGrab.grab()
            screenshot.save(r"C:\Bloomberg\NewsSearch_Euro.png")
            print("✓ Screenshot saved: NewsSearch_Euro.png")
            
            # Try to copy any visible content
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            content = pyperclip.paste()
            if content and len(content) > 50:
                print("✓ Found news content")
                return content
            else:
                print("✗ No content found via NEWS search")
                
        except Exception as e:
            print(f"NEWS search error: {e}")
        
        return None
    
    def try_msg_function(self):
        """Try MSG function with webdoc ID"""
        print("\n2. TRYING MSG FUNCTION")
        print("-" * 40)
        
        try:
            # Clear and try MSG
            pyautogui.hotkey('esc')
            time.sleep(0.5)
            
            # Try MSG with webdoc ID
            pyautogui.write('MSG', interval=0.1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Enter webdoc ID
            pyautogui.write(self.webdoc_id, interval=0.1)
            pyautogui.press('enter')
            time.sleep(5)
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(r"C:\Bloomberg\MSG_Webdoc.png")
            print("✓ Screenshot saved: MSG_Webdoc.png")
            
            # Try to copy content
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            content = pyperclip.paste()
            if content and len(content) > 50:
                print("✓ Found content via MSG")
                return content
            else:
                print("✗ No content found via MSG")
                
        except Exception as e:
            print(f"MSG error: {e}")
        
        return None
    
    def try_direct_id_search(self):
        """Try searching directly with ID in various formats"""
        print("\n3. TRYING DIRECT ID SEARCHES")
        print("-" * 40)
        
        search_variations = [
            f"ID:{self.webdoc_id}",
            f"WEBDOC:{self.webdoc_id}",
            f"DOC:{self.webdoc_id}",
            self.webdoc_id
        ]
        
        for search_term in search_variations:
            try:
                print(f"Trying: {search_term}")
                
                pyautogui.hotkey('esc')
                time.sleep(0.5)
                
                # Try direct search
                pyautogui.write(search_term, interval=0.1)
                pyautogui.press('enter')
                time.sleep(3)
                
                # Check if anything loaded
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.5)
                
                content = pyperclip.paste()
                if content and len(content) > 100 and self.webdoc_id not in content:
                    print(f"✓ Found content with {search_term}")
                    return content
                    
            except Exception as e:
                print(f"Error with {search_term}: {e}")
        
        print("✗ No content found via direct ID search")
        return None
    
    def try_n_command(self):
        """Try N<GO> command for news"""
        print("\n4. TRYING N<GO> COMMAND")
        print("-" * 40)
        
        try:
            pyautogui.hotkey('esc')
            time.sleep(0.5)
            
            # N<GO> opens news
            pyautogui.write('N', interval=0.1)
            pyautogui.press('enter')
            time.sleep(3)
            
            # Search for Euro news
            pyautogui.write('EUR/USD 0.77%', interval=0.1)
            pyautogui.press('enter')
            time.sleep(5)
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(r"C:\Bloomberg\N_Command_Search.png")
            print("✓ Screenshot saved: N_Command_Search.png")
            
            # Try to find and click on article if visible
            # This would require OCR or specific coordinates
            
        except Exception as e:
            print(f"N command error: {e}")
        
        return None
    
    def save_results(self, content, method):
        """Save retrieved content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result = {
            "webdoc_id": self.webdoc_id,
            "article_title": self.article_title,
            "retrieval_method": method,
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content) if content else 0,
            "content": content[:1000] if content else None  # First 1000 chars
        }
        
        # Save to file
        filename = f"article_retrieval_test_{timestamp}.json"
        filepath = os.path.join(r"C:\Bloomberg\ArticleTests", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n✓ Results saved to: {filename}")
        
        # Also save full content if found
        if content:
            content_file = f"article_content_{timestamp}.txt"
            content_path = os.path.join(r"C:\Bloomberg\ArticleTests", content_file)
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Full content saved to: {content_file}")
    
    def run_test(self):
        """Run all retrieval methods"""
        print(f"\n🎯 Target Article: {self.article_title}")
        print(f"📋 Webdoc ID: {self.webdoc_id}")
        
        # Activate Bloomberg Terminal
        if not self.activate_bloomberg():
            print("✗ Could not activate Bloomberg Terminal")
            print("  Make sure Terminal is running and logged in")
            return
        
        # Try different methods
        methods = [
            ("NEWS_SEARCH", self.try_news_search),
            ("MSG_FUNCTION", self.try_msg_function),
            ("DIRECT_ID", self.try_direct_id_search),
            ("N_COMMAND", self.try_n_command)
        ]
        
        for method_name, method_func in methods:
            content = method_func()
            if content:
                print(f"\n✅ SUCCESS with {method_name}!")
                self.save_results(content, method_name)
                return
        
        print("\n❌ Could not retrieve article with any method")
        self.save_results(None, "NONE")

# Run the test
if __name__ == "__main__":
    print("Bloomberg Article Retrieval Test")
    print("=" * 50)
    
    retriever = BloombergArticleRetriever()
    retriever.run_test()
    
    print("\n" + "=" * 50)
    print("Test complete. Check C:\\Bloomberg\\ArticleTests for results")
'@

Write-Host "`nRunning article retrieval test..."
C:\Python311\python.exe -c $articleTest

Write-Host "`n`nChecking for saved files..." -ForegroundColor Yellow
Get-ChildItem -Path "C:\Bloomberg\ArticleTests" -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime | Format-Table

Write-Host "`nTest complete!" -ForegroundColor Green
'''

    # Execute the retrieval test
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", retrieval_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("\nExecuting Bloomberg article retrieval test on VM...")
    print("This will try multiple methods to retrieve the article...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out but may have completed on VM")
    
    print("\n" + "=" * 60)
    print("📋 RETRIEVAL METHODS TESTED:")
    print("=" * 60)
    print("""
1. NEWS SEARCH - Search for article by title keywords
2. MSG FUNCTION - Try to access via webdoc ID  
3. DIRECT ID - Various ID format searches
4. N COMMAND - News terminal command

The test saves:
- Screenshots of each attempt
- Any retrieved content
- JSON report with results

Check C:\\Bloomberg\\ArticleTests on the VM for:
- article_retrieval_test_*.json (test results)
- article_content_*.txt (full content if found)
- *.png screenshots of Terminal screens
""")


if __name__ == "__main__":
    test_webdoc_retrieval()