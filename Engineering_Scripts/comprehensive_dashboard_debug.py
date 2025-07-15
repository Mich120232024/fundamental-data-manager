#!/usr/bin/env python3
"""
Comprehensive Dashboard Debug - Test All Functionality
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright

class DashboardDebugger:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_tests = []
        
    def log_error(self, test, error):
        self.errors.append({"test": test, "error": str(error), "timestamp": time.time()})
        print(f"❌ ERROR in {test}: {error}")
        
    def log_warning(self, test, warning):
        self.warnings.append({"test": test, "warning": str(warning), "timestamp": time.time()})
        print(f"⚠️  WARNING in {test}: {warning}")
        
    def log_success(self, test, details=""):
        self.passed_tests.append({"test": test, "details": details, "timestamp": time.time()})
        print(f"✅ PASSED {test}: {details}")

    async def setup_browser(self):
        """Setup browser with comprehensive debugging"""
        print("🌐 Setting up browser for comprehensive debugging...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            devtools=True,
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Capture all console messages
        self.context.on('console', lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        self.context.on('pageerror', lambda err: self.log_error("JavaScript", err))
        self.context.on('requestfailed', lambda req: self.log_error("Network", f"{req.method} {req.url} failed"))
        
        self.page = await self.context.new_page()

    async def test_basic_loading(self):
        """Test basic dashboard loading"""
        print("\n🧪 Testing Basic Dashboard Loading...")
        
        try:
            response = await self.page.goto("http://localhost:8000/professional-dashboard.html")
            if response.status != 200:
                self.log_error("Basic Loading", f"HTTP {response.status}")
                return False
                
            await self.page.wait_for_load_state("networkidle")
            
            title = await self.page.title()
            if "User Dashboard" not in title:
                self.log_warning("Basic Loading", f"Unexpected title: {title}")
            else:
                self.log_success("Basic Loading", f"Title: {title}")
                
            return True
            
        except Exception as e:
            self.log_error("Basic Loading", e)
            return False

    async def test_navigation_tabs(self):
        """Test all navigation tabs"""
        print("\n🧪 Testing Navigation Tabs...")
        
        try:
            tabs = await self.page.query_selector_all(".nav-item")
            self.log_success("Navigation", f"Found {len(tabs)} tabs")
            
            tab_names = []
            for tab in tabs:
                tab_text = await tab.inner_text()
                tab_data = await tab.get_attribute("data-tab")
                tab_names.append({"text": tab_text, "data-tab": tab_data})
                
            expected_tabs = ["overview", "mailbox", "cosmos", "graph", "agents", "manager", "workspace", "research", "documentation", "deepcontext"]
            
            found_tabs = [tab["data-tab"] for tab in tab_names]
            missing_tabs = set(expected_tabs) - set(found_tabs)
            
            if missing_tabs:
                self.log_error("Navigation", f"Missing tabs: {missing_tabs}")
            else:
                self.log_success("Navigation", f"All expected tabs present: {found_tabs}")
                
            return tab_names
            
        except Exception as e:
            self.log_error("Navigation", e)
            return []

    async def test_architecture_tab(self):
        """Comprehensive Architecture tab testing"""
        print("\n🧪 Testing Architecture Tab Functionality...")
        
        try:
            # Click Architecture tab
            arch_tab = await self.page.query_selector("[data-tab='research']")
            await arch_tab.click()
            await self.page.wait_for_timeout(2000)
            
            # Check if data loads
            await self.page.wait_for_selector(".file-category", timeout=10000)
            
            # Count categories
            categories = await self.page.query_selector_all(".file-category")
            category_count = len(categories)
            
            if category_count == 0:
                self.log_error("Architecture Categories", "No categories loaded")
                return False
            elif category_count < 9:
                self.log_warning("Architecture Categories", f"Only {category_count} categories, expected 9")
            else:
                self.log_success("Architecture Categories", f"Found {category_count} categories")
            
            # Test category names
            category_names = []
            for cat in categories[:5]:  # Test first 5
                header = await cat.query_selector(".category-header")
                if header:
                    name = await header.inner_text()
                    category_names.append(name.split('\n')[0])  # Get just the name part
                    
            self.log_success("Architecture Category Names", f"Categories: {category_names}")
            
            # Test file clicking
            file_items = await self.page.query_selector_all(".file-item")
            if file_items:
                first_file = file_items[0]
                file_name_elem = await first_file.query_selector(".file-item-name")
                file_name = await file_name_elem.inner_text()
                
                await first_file.click()
                await self.page.wait_for_timeout(2000)
                
                # Check iframe src
                iframe = await self.page.query_selector("#architecture-iframe")
                iframe_src = await iframe.get_attribute("src")
                
                if iframe_src and "architecture/raw" in iframe_src:
                    self.log_success("Architecture File Click", f"Clicked '{file_name}', iframe loaded: {iframe_src[:100]}...")
                else:
                    self.log_error("Architecture File Click", f"Iframe not loaded properly: {iframe_src}")
                    
                # Check viewer title
                viewer_title = await self.page.query_selector("#viewer-title")
                title_text = await viewer_title.inner_text()
                
                if file_name in title_text:
                    self.log_success("Architecture Viewer Title", f"Title updated to: {title_text}")
                else:
                    self.log_warning("Architecture Viewer Title", f"Title '{title_text}' doesn't match file '{file_name}'")
            else:
                self.log_error("Architecture Files", "No file items found")
                
            return True
            
        except Exception as e:
            self.log_error("Architecture Tab", e)
            return False

    async def test_documentation_tab(self):
        """Test Documentation tab"""
        print("\n🧪 Testing Documentation Tab...")
        
        try:
            # Click Documentation tab
            doc_tab = await self.page.query_selector("[data-tab='documentation']")
            await doc_tab.click()
            await self.page.wait_for_timeout(3000)
            
            # Check if content loads
            doc_categories = await self.page.query_selector("#doc-categories")
            if doc_categories:
                content = await doc_categories.inner_text()
                if "Loading" in content:
                    self.log_warning("Documentation", "Still showing loading message")
                else:
                    self.log_success("Documentation", "Content loaded")
            else:
                self.log_error("Documentation", "Doc categories element not found")
                
            return True
            
        except Exception as e:
            self.log_error("Documentation Tab", e)
            return False

    async def test_other_tabs(self):
        """Test other major tabs"""
        print("\n🧪 Testing Other Major Tabs...")
        
        tabs_to_test = [
            ("overview", "Overview"),
            ("cosmos", "Cosmos Explorer"), 
            ("agents", "Agent Shell"),
            ("mailbox", "Mailbox")
        ]
        
        for tab_data, tab_name in tabs_to_test:
            try:
                print(f"  Testing {tab_name}...")
                tab = await self.page.query_selector(f"[data-tab='{tab_data}']")
                await tab.click()
                await self.page.wait_for_timeout(2000)
                
                # Check if tab content appears
                tab_content = await self.page.query_selector(f"#{tab_data}")
                if tab_content:
                    display = await tab_content.evaluate("el => getComputedStyle(el).display")
                    if display != "none":
                        self.log_success(f"{tab_name} Tab", "Content visible")
                    else:
                        self.log_error(f"{tab_name} Tab", "Content hidden")
                else:
                    self.log_error(f"{tab_name} Tab", "Tab content element not found")
                    
            except Exception as e:
                self.log_error(f"{tab_name} Tab", e)

    async def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🧪 Testing API Endpoints...")
        
        endpoints = [
            "/api/v1/architecture/list",
            "/api/v1/architecture/health", 
            "/api/v1/agents/list",
            "/api/v1/docs/structure"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"http://localhost:8420{endpoint}"
                response = await self.page.evaluate(f"""
                    fetch('{url}')
                        .then(response => {{
                            if (response.ok) return response.json().then(data => ({{status: response.status, data}}));
                            else throw new Error(`HTTP ${{response.status}}`);
                        }})
                        .catch(err => ({{error: err.message}}))
                """)
                
                if "error" in response:
                    self.log_error(f"API {endpoint}", response["error"])
                else:
                    self.log_success(f"API {endpoint}", f"HTTP {response['status']}")
                    
            except Exception as e:
                self.log_error(f"API {endpoint}", e)

    async def capture_final_state(self):
        """Capture final state screenshots and data"""
        print("\n📸 Capturing Final Debug State...")
        
        timestamp = int(time.time())
        
        # Full page screenshot
        await self.page.screenshot(path=f"debug_full_{timestamp}.png", full_page=True)
        
        # Go back to Architecture tab for detailed screenshot
        arch_tab = await self.page.query_selector("[data-tab='research']")
        await arch_tab.click()
        await self.page.wait_for_timeout(2000)
        
        await self.page.screenshot(path=f"debug_architecture_{timestamp}.png", full_page=True)
        
        self.log_success("Screenshots", f"Saved debug_full_{timestamp}.png and debug_architecture_{timestamp}.png")

    async def generate_report(self):
        """Generate comprehensive debug report"""
        print("\n📋 Generating Debug Report...")
        
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.passed_tests) + len(self.errors) + len(self.warnings),
                "passed": len(self.passed_tests),
                "errors": len(self.errors),
                "warnings": len(self.warnings)
            },
            "passed_tests": self.passed_tests,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        report_file = f"dashboard_debug_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Debug Summary:")
        print(f"   ✅ Passed: {len(self.passed_tests)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   📄 Report: {report_file}")
        
        return report

    async def run_comprehensive_debug(self):
        """Run complete debug suite"""
        print("🚀 Starting Comprehensive Dashboard Debug")
        print("=" * 60)
        
        try:
            await self.setup_browser()
            
            # Run all tests
            await self.test_basic_loading()
            await self.test_navigation_tabs()
            await self.test_architecture_tab()
            await self.test_documentation_tab()
            await self.test_other_tabs()
            await self.test_api_endpoints()
            await self.capture_final_state()
            
            report = await self.generate_report()
            
            print("\n🎉 Comprehensive debug completed!")
            
            return report
            
        except Exception as e:
            self.log_error("Debug Suite", e)
        finally:
            if self.browser:
                await self.browser.close()
            await self.playwright.stop()

async def main():
    debugger = DashboardDebugger()
    await debugger.run_comprehensive_debug()

if __name__ == "__main__":
    asyncio.run(main())