#!/usr/bin/env python3
"""
Comprehensive Browser-Based Frontend Debugging for Cosmos DB Viewer
"""

import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright
import time

class CosmosViewerDebugger:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.browser = None
        self.page = None
        self.debug_log = []

    async def setup_browser(self, headless=False):
        """Initialize browser with debugging capabilities"""
        print("🌐 Starting browser for debugging...")
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with debugging enabled
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            devtools=True,
            args=[
                '--enable-logging',
                '--log-level=0',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with extended timeout
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        
        # Enable console logging
        context.on('console', self.handle_console_message)
        context.on('pageerror', self.handle_page_error)
        context.on('requestfailed', self.handle_request_failed)
        
        self.page = await context.new_page()
        print("✅ Browser initialized with debugging")

    def handle_console_message(self, msg):
        """Capture console messages"""
        entry = {
            'type': 'console',
            'level': msg.type,
            'text': msg.text,
            'timestamp': time.time()
        }
        self.debug_log.append(entry)
        print(f"📟 CONSOLE [{msg.type.upper()}]: {msg.text}")

    def handle_page_error(self, error):
        """Capture JavaScript errors"""
        entry = {
            'type': 'javascript_error',
            'error': str(error),
            'timestamp': time.time()
        }
        self.debug_log.append(entry)
        print(f"❌ JS ERROR: {error}")

    def handle_request_failed(self, request):
        """Capture failed network requests"""
        entry = {
            'type': 'network_error',
            'url': request.url,
            'method': request.method,
            'failure': request.failure,
            'timestamp': time.time()
        }
        self.debug_log.append(entry)
        print(f"🌐 NETWORK FAIL: {request.method} {request.url} - {request.failure}")

    async def test_viewer_loading(self):
        """Test if the viewer loads properly"""
        print("\n🧪 Testing Cosmos DB Viewer Loading...")
        
        try:
            # Navigate to viewer
            print(f"📍 Navigating to {self.base_url}/viewer")
            response = await self.page.goto(f"{self.base_url}/viewer", wait_until="networkidle")
            
            print(f"✅ Page loaded with status: {response.status}")
            
            # Check page title
            title = await self.page.title()
            print(f"📄 Page title: {title}")
            
            # Wait for initial JavaScript to execute
            await self.page.wait_for_timeout(2000)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load viewer: {e}")
            return False

    async def check_containers_loading(self):
        """Check if containers are loading in the sidebar"""
        print("\n🧪 Testing Container Loading...")
        
        try:
            # Wait for container list to load
            print("⏳ Waiting for container list...")
            
            # Check if loading message appears first
            loading_selector = ".loading"
            try:
                await self.page.wait_for_selector(loading_selector, timeout=5000)
                print("✅ Loading message appeared")
            except:
                print("ℹ️ No loading message found")
            
            # Wait for containers to appear
            container_selector = ".container-item"
            await self.page.wait_for_selector(container_selector, timeout=10000)
            
            # Count containers
            containers = await self.page.query_selector_all(container_selector)
            print(f"✅ Found {len(containers)} containers")
            
            # Get container details
            for i, container in enumerate(containers[:5]):  # Show first 5
                name = await container.query_selector(".container-name")
                count = await container.query_selector(".container-count")
                
                if name and count:
                    name_text = await name.inner_text()
                    count_text = await count.inner_text()
                    print(f"   📁 {name_text}: {count_text}")
            
            return True
            
        except Exception as e:
            print(f"❌ Container loading failed: {e}")
            return False

    async def test_container_interaction(self):
        """Test clicking on a container to load documents"""
        print("\n🧪 Testing Container Interaction...")
        
        try:
            # Find first container
            container = await self.page.query_selector(".container-item")
            if not container:
                print("❌ No containers found to click")
                return False
            
            # Get container name
            name_elem = await container.query_selector(".container-name")
            container_name = await name_elem.inner_text() if name_elem else "unknown"
            
            print(f"👆 Clicking on container: {container_name}")
            await container.click()
            
            # Wait for documents to load
            await self.page.wait_for_timeout(3000)
            
            # Check if documents appeared
            documents = await self.page.query_selector_all(".document-item")
            print(f"✅ Container clicked, found {len(documents)} documents")
            
            return True
            
        except Exception as e:
            print(f"❌ Container interaction failed: {e}")
            return False

    async def test_api_connectivity(self):
        """Test API endpoints directly from browser"""
        print("\n🧪 Testing API Connectivity...")
        
        api_tests = [
            "/api/containers",
            "/api/stats",
            "/api/containers/messages/documents?limit=1"
        ]
        
        for endpoint in api_tests:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"🌐 Testing: {endpoint}")
                
                # Use browser to fetch API
                response = await self.page.evaluate(f"""
                    fetch('{url}')
                        .then(r => r.json())
                        .then(data => {{
                            return {{
                                success: true,
                                status: 200,
                                data: data
                            }};
                        }})
                        .catch(err => {{
                            return {{
                                success: false,
                                error: err.message
                            }};
                        }})
                """)
                
                if response.get('success'):
                    print(f"   ✅ API working")
                else:
                    print(f"   ❌ API failed: {response.get('error')}")
                    
            except Exception as e:
                print(f"   ❌ API test failed: {e}")

    async def capture_debug_info(self):
        """Capture comprehensive debug information"""
        print("\n📊 Capturing Debug Information...")
        
        try:
            # Get all console logs from debug panel
            debug_entries = await self.page.evaluate("""
                Array.from(document.querySelectorAll('.debug-entry')).map(entry => ({
                    timestamp: entry.querySelector('.timestamp')?.textContent || '',
                    content: entry.textContent || '',
                    className: entry.className
                }))
            """)
            
            print(f"📋 Found {len(debug_entries)} debug entries")
            for entry in debug_entries[-10:]:  # Show last 10
                print(f"   {entry['timestamp']}: {entry['content'][:100]}...")
            
            # Get network requests
            network_info = await self.page.evaluate("""
                performance.getEntriesByType('navigation').map(entry => ({
                    name: entry.name,
                    duration: entry.duration,
                    loadEventEnd: entry.loadEventEnd
                }))
            """)
            
            print(f"🌐 Page load time: {network_info[0]['duration']:.2f}ms")
            
        except Exception as e:
            print(f"❌ Debug info capture failed: {e}")

    async def take_screenshots(self):
        """Take screenshots for visual debugging"""
        print("\n📸 Taking Debug Screenshots...")
        
        try:
            screenshots_dir = Path(__file__).parent / "debug_screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            timestamp = int(time.time())
            
            # Full page screenshot
            await self.page.screenshot(
                path=screenshots_dir / f"viewer_full_{timestamp}.png",
                full_page=True
            )
            print(f"✅ Full page screenshot saved")
            
            # Sidebar screenshot
            sidebar = await self.page.query_selector(".sidebar")
            if sidebar:
                await sidebar.screenshot(
                    path=screenshots_dir / f"sidebar_{timestamp}.png"
                )
                print(f"✅ Sidebar screenshot saved")
            
            # Main content screenshot
            main = await self.page.query_selector(".main")
            if main:
                await main.screenshot(
                    path=screenshots_dir / f"main_content_{timestamp}.png"
                )
                print(f"✅ Main content screenshot saved")
                
            print(f"📁 Screenshots saved to: {screenshots_dir}")
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")

    async def save_debug_report(self):
        """Save comprehensive debug report"""
        report_path = Path(__file__).parent / f"debug_report_{int(time.time())}.json"
        
        # Get page metrics
        metrics = await self.page.evaluate("""
            ({
                url: window.location.href,
                userAgent: navigator.userAgent,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                containers: Array.from(document.querySelectorAll('.container-item')).length,
                documents: Array.from(document.querySelectorAll('.document-item')).length,
                errors: window.jsErrors || []
            })
        """)
        
        report = {
            'timestamp': time.time(),
            'debug_log': self.debug_log,
            'page_metrics': metrics,
            'status': 'completed'
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📋 Debug report saved: {report_path}")

    async def run_complete_debug(self, headless=False):
        """Run complete debugging suite"""
        print("🚀 Starting Complete Frontend Debug Session")
        print("=" * 50)
        
        try:
            await self.setup_browser(headless=headless)
            
            # Run all tests
            tests = [
                self.test_viewer_loading(),
                self.test_api_connectivity(),
                self.check_containers_loading(),
                self.test_container_interaction(),
                self.capture_debug_info(),
                self.take_screenshots(),
                self.save_debug_report()
            ]
            
            for test in tests:
                await test
                await self.page.wait_for_timeout(1000)  # Brief pause between tests
            
            print("\n🎉 Complete debug session finished!")
            print("📋 Check debug_report_*.json for detailed results")
            print("📸 Check debug_screenshots/ for visual evidence")
            
        except Exception as e:
            print(f"❌ Debug session failed: {e}")
        
        finally:
            if self.browser:
                await self.browser.close()
            await self.playwright.stop()

async def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Debug Cosmos DB Viewer Frontend')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--url', default='http://localhost:5001', help='Base URL to test')
    
    args = parser.parse_args()
    
    debugger = CosmosViewerDebugger(args.url)
    await debugger.run_complete_debug(headless=args.headless)

if __name__ == "__main__":
    asyncio.run(main())
