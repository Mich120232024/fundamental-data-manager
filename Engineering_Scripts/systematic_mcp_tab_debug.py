#!/usr/bin/env python3
"""
Systematic MCP-Based Dashboard Tab Debugging
Debug all errors one by one on each page as requested by user
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright

class SystematicTabDebugger:
    def __init__(self):
        self.errors_found = {}
        self.tabs_tested = {}
        self.console_logs = []
        self.screenshots_taken = []
        
    def log_tab_result(self, tab_name, status, details=""):
        self.tabs_tested[tab_name] = {"status": status, "details": details, "timestamp": time.time()}
        print(f"📊 {tab_name}: {status} - {details}")

    async def setup_browser(self):
        """Setup browser with comprehensive error catching"""
        print("🚀 Setting up MCP-based systematic debugging")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            devtools=True,
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Comprehensive error catching
        def log_console(msg):
            entry = {"type": msg.type, "text": msg.text, "timestamp": time.time()}
            self.console_logs.append(entry)
            if msg.type == "error":
                print(f"❌ CONSOLE ERROR: {msg.text}")
            else:
                print(f"📝 CONSOLE [{msg.type}]: {msg.text}")
                
        def log_js_error(error):
            error_info = {"error": str(error), "timestamp": time.time()}
            if "current_tab" in locals():
                if hasattr(self, 'current_tab'):
                    if self.current_tab not in self.errors_found:
                        self.errors_found[self.current_tab] = []
                    self.errors_found[self.current_tab].append(error_info)
            print(f"💥 JAVASCRIPT ERROR: {error}")
            
        self.context.on('console', log_console)
        self.context.on('pageerror', log_js_error)
        
        self.page = await self.context.new_page()

    async def test_tab_systematically(self, tab_name, tab_selector, expected_elements):
        """Test each tab systematically with MCP approach"""
        print(f"\n🔍 SYSTEMATIC DEBUG: {tab_name}")
        self.current_tab = tab_name
        
        try:
            # Step 1: Click tab
            print(f"👆 Clicking {tab_name} tab...")
            tab_element = await self.page.query_selector(tab_selector)
            if not tab_element:
                self.log_tab_result(tab_name, "❌ FAIL", "Tab selector not found")
                return False
                
            await tab_element.click()
            await self.page.wait_for_timeout(3000)
            
            # Step 2: Take screenshot
            timestamp = int(time.time())
            screenshot_path = f"mcp_debug_{tab_name}_{timestamp}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            self.screenshots_taken.append(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Step 3: Check expected elements
            elements_found = {}
            for element_name, selector in expected_elements.items():
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Check if element is visible
                        visible = await element.evaluate("el => getComputedStyle(el).display !== 'none'")
                        content = await element.text_content()
                        elements_found[element_name] = {
                            "exists": True,
                            "visible": visible,
                            "content_preview": content[:50] if content else ""
                        }
                    else:
                        elements_found[element_name] = {"exists": False, "visible": False}
                except Exception as e:
                    elements_found[element_name] = {"exists": False, "error": str(e)}
            
            # Step 4: Test interactions
            interactions_tested = {}
            if tab_name == "Cosmos Explorer":
                # Test container clicking
                containers = await self.page.query_selector_all(".container-item")
                if containers:
                    await containers[0].click()
                    await self.page.wait_for_timeout(2000)
                    interactions_tested["container_click"] = "✅ Clicked first container"
                    
                    # Test document clicking
                    documents = await self.page.query_selector_all(".list-item, .document-item")
                    if documents:
                        await documents[0].click()
                        await self.page.wait_for_timeout(2000)
                        interactions_tested["document_click"] = "✅ Clicked first document"
                    else:
                        interactions_tested["document_click"] = "❌ No documents found"
                else:
                    interactions_tested["container_click"] = "❌ No containers found"
                    
            elif tab_name == "Architecture":
                # Test file clicking  
                files = await self.page.query_selector_all(".file-item")
                if files:
                    await files[0].click()
                    await self.page.wait_for_timeout(2000)
                    interactions_tested["file_click"] = "✅ Clicked first file"
                else:
                    interactions_tested["file_click"] = "❌ No files found"
                    
            elif tab_name == "Documentation":
                # Test document clicking
                docs = await self.page.query_selector_all(".doc-item")
                if docs:
                    await docs[0].click()
                    await self.page.wait_for_timeout(2000)
                    interactions_tested["doc_click"] = "✅ Clicked first document"
                else:
                    interactions_tested["doc_click"] = "❌ No documents found"
            
            # Step 5: Check for errors specific to this tab
            tab_errors = []
            recent_console_errors = [log for log in self.console_logs[-20:] if log["type"] == "error"]
            if recent_console_errors:
                tab_errors = recent_console_errors
            
            # Step 6: Determine overall status
            critical_elements_working = sum(1 for elem in elements_found.values() if elem.get("exists") and elem.get("visible", True))
            total_critical_elements = len(expected_elements)
            
            if critical_elements_working == total_critical_elements and not tab_errors:
                status = "✅ WORKING"
                details = f"All {total_critical_elements} elements functional"
            elif critical_elements_working > total_critical_elements * 0.7:
                status = "⚠️ PARTIAL"
                details = f"{critical_elements_working}/{total_critical_elements} elements, {len(tab_errors)} errors"
            else:
                status = "❌ BROKEN"
                details = f"Only {critical_elements_working}/{total_critical_elements} elements working"
            
            self.log_tab_result(tab_name, status, details)
            
            # Step 7: Log detailed findings
            print(f"   🔧 Elements: {elements_found}")
            if interactions_tested:
                print(f"   🖱️ Interactions: {interactions_tested}")
            if tab_errors:
                print(f"   💥 Errors: {len(tab_errors)} errors found")
                
            return status.startswith("✅")
            
        except Exception as e:
            self.log_tab_result(tab_name, "❌ ERROR", f"Exception: {str(e)}")
            return False

    async def debug_all_tabs(self):
        """Debug all dashboard tabs systematically"""
        print("🎯 Starting systematic MCP debugging of all dashboard tabs")
        
        # Navigate to dashboard
        await self.page.goto("http://localhost:8000/professional-dashboard.html")
        await self.page.wait_for_load_state("networkidle")
        
        # Define all tabs with expected critical elements
        tabs_to_debug = {
            "Overview": {
                "selector": "[data-tab='overview']",
                "elements": {
                    "metrics_cards": ".card",
                    "system_status": ".status-dot",
                    "recent_activity": ".recent-activity"
                }
            },
            "Mailbox": {
                "selector": "[data-tab='mailbox']", 
                "elements": {
                    "message_list": "#message-list",
                    "message_viewer": "#message-viewer",
                    "folder_nav": ".folder-nav"
                }
            },
            "Cosmos Explorer": {
                "selector": "[data-tab='cosmos']",
                "elements": {
                    "container_list": ".container-list, .container-item",
                    "document_list": ".document-list",
                    "document_viewer": ".document-viewer"
                }
            },
            "Graph DB": {
                "selector": "[data-tab='graph']",
                "elements": {
                    "graph_container": "#graph-container",
                    "graph_controls": ".graph-controls",
                    "cytoscape": ".cytoscape"
                }
            },
            "Agent Shell": {
                "selector": "[data-tab='agents']",
                "elements": {
                    "agent_list": ".agent-list",
                    "agent_details": ".agent-details",
                    "file_explorer": ".file-explorer"
                }
            },
            "Manager": {
                "selector": "[data-tab='manager']",
                "elements": {
                    "dashboard_content": ".manager-dashboard",
                    "stats_display": ".stats-display"
                }
            },
            "Workspace": {
                "selector": "[data-tab='workspace']",
                "elements": {
                    "file_tree": ".file-tree",
                    "file_viewer": ".file-viewer"
                }
            },
            "Architecture": {
                "selector": "[data-tab='research']",
                "elements": {
                    "file_list": "#architecture-files",
                    "file_viewer": "#architecture-viewer", 
                    "iframe": "#architecture-iframe"
                }
            },
            "Documentation": {
                "selector": "[data-tab='documentation']",
                "elements": {
                    "doc_categories": "#doc-categories",
                    "doc_viewer": "#doc-viewer",
                    "search_input": "#doc-search"
                }
            },
            "Deep Context": {
                "selector": "[data-tab='deepcontext']",
                "elements": {
                    "agent_list": "#deepcontext-agents",
                    "context_content": "#deepcontext-content"
                }
            }
        }
        
        # Test each tab systematically
        working_tabs = 0
        for tab_name, config in tabs_to_debug.items():
            success = await self.test_tab_systematically(
                tab_name, 
                config["selector"], 
                config["elements"]
            )
            if success:
                working_tabs += 1
            
            # Brief pause between tabs
            await self.page.wait_for_timeout(1000)
        
        # Generate comprehensive report
        await self.generate_final_report(working_tabs, len(tabs_to_debug))

    async def generate_final_report(self, working_tabs, total_tabs):
        """Generate comprehensive debugging report"""
        print(f"\n📊 SYSTEMATIC MCP DEBUGGING COMPLETE")
        print(f"=" * 60)
        
        # Overall status
        success_rate = (working_tabs / total_tabs) * 100
        print(f"🎯 Overall Status: {working_tabs}/{total_tabs} tabs working ({success_rate:.1f}%)")
        
        # Tab by tab results
        print(f"\n📋 Tab Status Summary:")
        for tab_name, result in self.tabs_tested.items():
            print(f"   {result['status']} {tab_name}: {result['details']}")
        
        # Error summary
        total_errors = len([log for log in self.console_logs if log["type"] == "error"])
        print(f"\n💥 Errors Found: {total_errors} total console errors")
        
        # Recommendations
        print(f"\n🔧 Next Actions:")
        broken_tabs = [name for name, result in self.tabs_tested.items() if "❌" in result["status"]]
        if broken_tabs:
            print(f"   Priority Fix: {broken_tabs}")
        
        partial_tabs = [name for name, result in self.tabs_tested.items() if "⚠️" in result["status"]]
        if partial_tabs:
            print(f"   Improvements Needed: {partial_tabs}")
        
        # Save detailed report
        report = {
            "timestamp": time.time(),
            "working_tabs": working_tabs,
            "total_tabs": total_tabs,
            "success_rate": success_rate,
            "tab_results": self.tabs_tested,
            "console_logs": self.console_logs[-50:],  # Last 50 logs
            "screenshots": self.screenshots_taken
        }
        
        report_file = f"systematic_debug_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Detailed report: {report_file}")
        
        print(f"\n📸 Screenshots: {len(self.screenshots_taken)} screenshots taken")
        for screenshot in self.screenshots_taken:
            print(f"   - {screenshot}")

    async def run_systematic_debug(self):
        """Main entry point for systematic debugging"""
        try:
            await self.setup_browser()
            await self.debug_all_tabs()
        except Exception as e:
            print(f"❌ Critical error in systematic debugging: {e}")
        finally:
            if hasattr(self, 'browser'):
                await self.browser.close()
            await self.playwright.stop()

async def main():
    debugger = SystematicTabDebugger()
    await debugger.run_systematic_debug()

if __name__ == "__main__":
    asyncio.run(main())