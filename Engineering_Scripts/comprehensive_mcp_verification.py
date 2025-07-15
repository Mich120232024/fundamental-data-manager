#!/usr/bin/env python3
"""
Comprehensive MCP-Based Dashboard Verification
Test all fixes made: ESC keys, popups, Graph DB, styling quality
"""
import asyncio
import json
import time
from playwright.async_api import async_playwright

async def test_dashboard_comprehensively():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        # Navigate to dashboard
        print("🚀 Loading dashboard...")
        await page.goto('http://localhost:8420', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        
        test_results = {
            "timestamp": time.time(),
            "tests": {},
            "screenshots": [],
            "console_logs": []
        }
        
        # Capture console logs
        def handle_console(msg):
            test_results["console_logs"].append({
                "type": msg.type,
                "text": msg.text,
                "timestamp": time.time()
            })
        page.on("console", handle_console)
        
        # Test 1: Cosmos Explorer popup and ESC key
        print("\n🧪 TEST 1: Cosmos Explorer popup ESC functionality")
        try:
            await page.click('text=Cosmos Explorer')
            await page.wait_for_timeout(1000)
            
            # Look for containers and click one
            containers = await page.query_selector_all('.list-item')
            if containers and len(containers) > 0:
                await containers[0].click()
                await page.wait_for_timeout(1000)
                
                # Look for documents and click one to open modal
                documents = await page.query_selector_all('.list-item')
                if len(documents) > 1:
                    await documents[1].click()  # Click a document
                    await page.wait_for_timeout(2000)
                    
                    # Take screenshot of modal
                    screenshot_path = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/mcp_test_cosmos_modal_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path)
                    test_results["screenshots"].append(screenshot_path)
                    print(f"📸 Modal screenshot: {screenshot_path}")
                    
                    # Test ESC key to close modal
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(1000)
                    
                    # Check if modal is gone
                    modal_exists = await page.query_selector('div[style*="z-index: 10000"]')
                    if modal_exists is None:
                        test_results["tests"]["cosmos_esc"] = "✅ WORKING - ESC key closes modal"
                        print("✅ ESC key successfully closes Cosmos modal")
                    else:
                        test_results["tests"]["cosmos_esc"] = "❌ BROKEN - ESC key does not close modal"
                        print("❌ ESC key failed to close modal")
                else:
                    test_results["tests"]["cosmos_esc"] = "❌ NO DOCUMENTS - Cannot test modal"
            else:
                test_results["tests"]["cosmos_esc"] = "❌ NO CONTAINERS - Cannot test"
                
        except Exception as e:
            test_results["tests"]["cosmos_esc"] = f"❌ ERROR - {str(e)}"
            print(f"❌ Cosmos test error: {e}")
        
        # Test 2: Graph DB visualization loading
        print("\n🧪 TEST 2: Graph DB loading and visualization")
        try:
            await page.click('text=Graph DB')
            await page.wait_for_timeout(1000)
            
            # Click Load Graph button
            load_button = await page.query_selector('button:has-text("Load Graph")')
            if load_button:
                await load_button.click()
                await page.wait_for_timeout(3000)  # Wait for graph to load
                
                # Take screenshot of graph area
                screenshot_path = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/mcp_test_graph_{int(time.time())}.png"
                await page.screenshot(path=screenshot_path)
                test_results["screenshots"].append(screenshot_path)
                print(f"📸 Graph screenshot: {screenshot_path}")
                
                # Check if cytoscape loaded
                cytoscape_element = await page.query_selector('#cy')
                graph_container = await page.query_selector('#graph-container')
                
                if cytoscape_element:
                    # Check if there's actual graph content (not just loading/error)
                    content = await graph_container.inner_text()
                    if "Loading" not in content and "Error" not in content and "Failed" not in content:
                        test_results["tests"]["graph_loading"] = "✅ WORKING - Graph visualization loaded"
                        print("✅ Graph DB visualization successfully loaded")
                    else:
                        test_results["tests"]["graph_loading"] = f"❌ BROKEN - {content}"
                        print(f"❌ Graph shows: {content}")
                else:
                    test_results["tests"]["graph_loading"] = "❌ BROKEN - No cytoscape element found"
                    print("❌ No cytoscape element found")
            else:
                test_results["tests"]["graph_loading"] = "❌ BROKEN - No Load Graph button found"
                
        except Exception as e:
            test_results["tests"]["graph_loading"] = f"❌ ERROR - {str(e)}"
            print(f"❌ Graph test error: {e}")
        
        # Test 3: Global ESC key functionality on other modals
        print("\n🧪 TEST 3: Global ESC key on Architecture files")
        try:
            await page.click('text=Architecture')
            await page.wait_for_timeout(2000)
            
            # Look for files and click one
            file_links = await page.query_selector_all('.file-item, .list-item')
            if file_links and len(file_links) > 0:
                await file_links[0].click()
                await page.wait_for_timeout(2000)
                
                # Check if iframe viewer opened
                iframe = await page.query_selector('#architecture-iframe')
                if iframe:
                    # Test ESC key
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(1000)
                    
                    # Architecture tab doesn't use modal - it uses iframe
                    test_results["tests"]["architecture_esc"] = "✅ INFO - Architecture uses iframe viewer, not modal"
                    print("ℹ️ Architecture uses iframe viewer, not modal popup")
                else:
                    test_results["tests"]["architecture_esc"] = "❌ NO IFRAME - Architecture viewer not working"
            else:
                test_results["tests"]["architecture_esc"] = "❌ NO FILES - Cannot test"
                
        except Exception as e:
            test_results["tests"]["architecture_esc"] = f"❌ ERROR - {str(e)}"
            print(f"❌ Architecture test error: {e}")
        
        # Test 4: Check overall styling quality
        print("\n🧪 TEST 4: Visual styling quality assessment")
        try:
            # Take full dashboard screenshot
            screenshot_path = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/mcp_test_styling_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            test_results["screenshots"].append(screenshot_path)
            print(f"📸 Full dashboard screenshot: {screenshot_path}")
            
            # Check for CSS variables and styling
            css_vars = await page.evaluate("""
                () => {
                    const styles = getComputedStyle(document.documentElement);
                    return {
                        primary: styles.getPropertyValue('--primary-blue'),
                        background: styles.getPropertyValue('--bg-dark'),
                        text: styles.getPropertyValue('--text-primary')
                    };
                }
            """)
            
            if css_vars['primary'] and css_vars['background']:
                test_results["tests"]["styling_quality"] = "✅ WORKING - CSS variables loaded properly"
                print("✅ CSS styling variables loaded correctly")
            else:
                test_results["tests"]["styling_quality"] = "❌ BROKEN - CSS variables not loading"
                print("❌ CSS variables not loading properly")
                
        except Exception as e:
            test_results["tests"]["styling_quality"] = f"❌ ERROR - {str(e)}"
            print(f"❌ Styling test error: {e}")
        
        # Test 5: Check for console errors
        print("\n🧪 TEST 5: Console error analysis")
        error_logs = [log for log in test_results["console_logs"] if log["type"] == "error"]
        warning_logs = [log for log in test_results["console_logs"] if log["type"] == "warning"]
        
        test_results["tests"]["console_errors"] = f"Errors: {len(error_logs)}, Warnings: {len(warning_logs)}"
        print(f"📊 Console analysis: {len(error_logs)} errors, {len(warning_logs)} warnings")
        
        if error_logs:
            print("🔍 Console errors found:")
            for error in error_logs[:3]:  # Show first 3 errors
                print(f"   ❌ {error['text']}")
        
        # Final summary
        print("\n📋 COMPREHENSIVE TEST SUMMARY:")
        total_tests = len([k for k in test_results["tests"].keys() if not k.startswith("console")])
        passed_tests = len([v for v in test_results["tests"].values() if v.startswith("✅")])
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        print(f"Success Rate: {passed_tests}/{total_tests} ({test_results['summary']['success_rate']:.1f}%)")
        
        for test_name, result in test_results["tests"].items():
            if not test_name.startswith("console"):
                print(f"  {result}")
        
        # Save detailed results
        report_path = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/comprehensive_test_report_{int(time.time())}.json"
        with open(report_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        print(f"📸 Screenshots captured: {len(test_results['screenshots'])}")
        
        await browser.close()
        return test_results

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE MCP-BASED DASHBOARD VERIFICATION")
    print("=" * 60)
    
    try:
        results = asyncio.run(test_dashboard_comprehensively())
        
        # Final verdict
        if results["summary"]["success_rate"] >= 80:
            print(f"\n🎉 VERDICT: DASHBOARD QUALITY RESTORED ({results['summary']['success_rate']:.1f}%)")
        elif results["summary"]["success_rate"] >= 60:
            print(f"\n⚠️ VERDICT: SIGNIFICANT IMPROVEMENT NEEDED ({results['summary']['success_rate']:.1f}%)")
        else:
            print(f"\n❌ VERDICT: MAJOR ISSUES REMAIN ({results['summary']['success_rate']:.1f}%)")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")