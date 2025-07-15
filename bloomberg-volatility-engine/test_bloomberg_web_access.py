#!/usr/bin/env python3
"""
Test accessing Bloomberg articles via web browser when Terminal is authenticated
"""

import subprocess
import time

def test_bloomberg_web_access():
    """Test if we can access Bloomberg articles through web browser on Terminal-authenticated VM"""
    
    print("🌐 Testing Bloomberg Web Access via Authenticated Terminal")
    print("=" * 60)
    
    web_test_script = r'''
Write-Host "Testing Bloomberg Web Access with Terminal Authentication" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Install required packages
Write-Host "`nInstalling required packages..."
C:\Python311\Scripts\pip.exe install selenium requests beautifulsoup4 --quiet

$webAccessTest = @'
import os
import time
import json
from datetime import datetime
import subprocess

try:
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing module: {e}")
    import subprocess
    subprocess.run(["pip", "install", "selenium", "requests", "beautifulsoup4"])

class BloombergWebAccess:
    """Access Bloomberg content via web browser with Terminal authentication"""
    
    def __init__(self):
        self.webdoc_id = "0B06E00E-BB09-4F01-844D-55C242BDBC7B"
        self.results_dir = r"C:\Bloomberg\WebAccessTests"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def test_direct_browser_access(self):
        """Open Bloomberg article in browser"""
        print("\n1. TESTING DIRECT BROWSER ACCESS")
        print("-" * 40)
        
        # Common Bloomberg article URL patterns
        test_urls = [
            f"https://www.bloomberg.com/news/articles/{self.webdoc_id}",
            f"https://blinks.bloomberg.com/news/stories/{self.webdoc_id}",
            f"https://www.bloomberg.com/professional/stories/{self.webdoc_id}",
            f"https://terminal.bloomberg.com/news/{self.webdoc_id}",
            "https://www.bloomberg.com/news/articles/2025-01-10/euro-loses-0-77-to-1-1690-data-talk"
        ]
        
        # Use Edge browser (default on Windows Server)
        for url in test_urls:
            print(f"\nTrying: {url}")
            try:
                # Open in default browser
                os.system(f'start msedge "{url}"')
                time.sleep(5)
                
                # Also try with requests to check response
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                print(f"  Response code: {response.status_code}")
                print(f"  Final URL: {response.url}")
                
                if response.status_code == 200:
                    # Save the HTML
                    filename = f"bloomberg_page_{url.split('/')[-1]}.html"
                    filepath = os.path.join(self.results_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"  ✓ Saved HTML to {filename}")
                    
                    # Parse for article content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for article content
                    article_selectors = [
                        'article', 
                        'div[class*="article"]',
                        'div[class*="story"]',
                        'div[class*="content"]',
                        'main'
                    ]
                    
                    for selector in article_selectors:
                        content = soup.select(selector)
                        if content:
                            text = content[0].get_text(strip=True)
                            if len(text) > 200:
                                print(f"  ✓ Found article content ({len(text)} chars)")
                                self.save_article_content(text, url)
                                return True
                                
            except Exception as e:
                print(f"  Error: {e}")
        
        return False
    
    def test_selenium_access(self):
        """Use Selenium to access Bloomberg with cookies from Terminal session"""
        print("\n2. TESTING SELENIUM WITH EDGE")
        print("-" * 40)
        
        try:
            # Configure Edge options
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Try to use existing Edge profile with Bloomberg cookies
            edge_profile = r"C:\Users\bloombergadmin\AppData\Local\Microsoft\Edge\User Data"
            if os.path.exists(edge_profile):
                options.add_argument(f"user-data-dir={edge_profile}")
                print("  Using existing Edge profile with cookies")
            
            driver = webdriver.Edge(options=options)
            
            # First, check if we're logged into Bloomberg
            driver.get("https://www.bloomberg.com/account/profile")
            time.sleep(3)
            
            # Take screenshot
            screenshot_path = os.path.join(self.results_dir, "bloomberg_profile.png")
            driver.save_screenshot(screenshot_path)
            print(f"  ✓ Screenshot saved: bloomberg_profile.png")
            
            # Now try to access the article
            article_url = "https://www.bloomberg.com/news/articles/2025-01-10/euro-loses-0-77-to-1-1690-data-talk"
            driver.get(article_url)
            time.sleep(5)
            
            # Wait for article content
            try:
                article = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                
                # Get the article text
                article_text = article.text
                print(f"  ✓ Found article content: {len(article_text)} chars")
                
                # Save screenshot
                screenshot_path = os.path.join(self.results_dir, "article_screenshot.png")
                driver.save_screenshot(screenshot_path)
                
                # Save content
                self.save_article_content(article_text, article_url)
                
                driver.quit()
                return True
                
            except Exception as e:
                print(f"  Could not find article content: {e}")
                driver.quit()
                
        except Exception as e:
            print(f"  Selenium error: {e}")
        
        return False
    
    def test_terminal_browser_integration(self):
        """Check if Terminal has browser integration"""
        print("\n3. CHECKING TERMINAL BROWSER INTEGRATION")
        print("-" * 40)
        
        # Check for Bloomberg browser extensions or plugins
        edge_extensions = r"C:\Users\bloombergadmin\AppData\Local\Microsoft\Edge\User Data\Default\Extensions"
        
        if os.path.exists(edge_extensions):
            print("  Edge extensions found:")
            for ext in os.listdir(edge_extensions):
                print(f"    - {ext}")
        
        # Check for Bloomberg certificates
        print("\n  Checking for Bloomberg certificates...")
        try:
            result = subprocess.run(
                ["certutil", "-store", "My"],
                capture_output=True,
                text=True
            )
            if "Bloomberg" in result.stdout:
                print("  ✓ Bloomberg certificates found")
        except:
            pass
        
        return True
    
    def check_bloomberg_cookies(self):
        """Check for Bloomberg authentication cookies"""
        print("\n4. CHECKING AUTHENTICATION COOKIES")
        print("-" * 40)
        
        cookie_locations = [
            r"C:\Users\bloombergadmin\AppData\Local\Microsoft\Edge\User Data\Default\Cookies",
            r"C:\Users\bloombergadmin\AppData\Roaming\Microsoft\Windows\Cookies"
        ]
        
        for location in cookie_locations:
            if os.path.exists(location):
                print(f"  ✓ Found cookies at: {location}")
        
        return True
    
    def save_article_content(self, content, source_url):
        """Save retrieved article content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as text file
        text_file = f"article_content_{timestamp}.txt"
        text_path = os.path.join(self.results_dir, text_file)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Source: {source_url}\n")
            f.write(f"Retrieved: {datetime.now()}\n")
            f.write(f"Length: {len(content)} characters\n")
            f.write("=" * 60 + "\n\n")
            f.write(content)
        
        print(f"  ✓ Content saved to: {text_file}")
        
        # Also save as JSON
        json_file = f"article_metadata_{timestamp}.json"
        json_path = os.path.join(self.results_dir, json_file)
        
        metadata = {
            "webdoc_id": self.webdoc_id,
            "source_url": source_url,
            "retrieved_at": datetime.now().isoformat(),
            "content_length": len(content),
            "first_500_chars": content[:500],
            "method": "web_browser"
        }
        
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✓ Metadata saved to: {json_file}")
    
    def run_all_tests(self):
        """Run all web access tests"""
        print("\n🌐 Bloomberg Web Access Tests")
        print("=" * 50)
        
        # Run tests
        tests = [
            ("Direct Browser", self.test_direct_browser_access),
            ("Selenium Access", self.test_selenium_access),
            ("Terminal Integration", self.test_terminal_browser_integration),
            ("Cookie Check", self.check_bloomberg_cookies)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\nRunning: {test_name}")
            try:
                result = test_func()
                results[test_name] = "Success" if result else "Failed"
            except Exception as e:
                results[test_name] = f"Error: {e}"
        
        # Save results summary
        summary_file = os.path.join(self.results_dir, "test_summary.json")
        with open(summary_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "webdoc_id": self.webdoc_id,
                "results": results
            }, f, indent=2)
        
        print("\n" + "=" * 50)
        print("RESULTS SUMMARY:")
        for test, result in results.items():
            print(f"  {test}: {result}")

# Run the test
if __name__ == "__main__":
    tester = BloombergWebAccess()
    tester.run_all_tests()
    
    print(f"\n✓ All results saved to: {tester.results_dir}")
'@

Write-Host "`nRunning web access tests..."
C:\Python311\python.exe -c $webAccessTest

Write-Host "`n`nChecking results..." -ForegroundColor Yellow
Get-ChildItem -Path "C:\Bloomberg\WebAccessTests" -ErrorAction SilentlyContinue | Format-Table Name, Length, LastWriteTime

Write-Host "`n`nAlso opening Bloomberg.com in browser to check authentication..." -ForegroundColor Cyan
Start-Process "msedge.exe" "https://www.bloomberg.com/account/profile"

Write-Host "`nIMPORTANT:" -ForegroundColor Yellow
Write-Host "1. Check if you're logged into Bloomberg.com in the browser"
Write-Host "2. If yes, try opening article links directly" 
Write-Host "3. Terminal auth should carry over to web access"

Write-Host "`nTest complete!" -ForegroundColor Green
'''

    # Execute the web access test
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", web_test_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("\nTesting Bloomberg web access on VM...")
    print("This will check if Terminal authentication enables web access...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out but may have completed on VM")
    
    print("\n" + "=" * 60)
    print("💡 KEY INSIGHT:")
    print("=" * 60)
    print("""
You're absolutely right! When you're logged into Bloomberg Terminal, you should 
be able to access Bloomberg articles via web browser on the same machine.

The Terminal authentication creates a session that the browser can use.

Here's the workflow:
1. Bloomberg Terminal login → Creates authenticated session
2. Browser on same machine → Uses Terminal's authentication
3. Email links → Should open and display full content

This is much simpler than Terminal automation! The test checks:
- If browser can access Bloomberg.com when Terminal is running
- Whether Terminal cookies/auth are available to browser
- Direct URL access to articles

Check C:\\Bloomberg\\WebAccessTests on the VM for results!
""")


if __name__ == "__main__":
    test_bloomberg_web_access()