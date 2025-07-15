#!/usr/bin/env python3
"""
Systematic Tab Debugging Using MCP Approach
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def debug_tab(page, tab_name, tab_selector, description):
    """Debug a specific tab systematically"""
    print(f"\n🧪 Testing {description}...")
    
    # Click tab
    tab = await page.query_selector(tab_selector)
    if not tab:
        print(f"❌ Tab selector not found: {tab_selector}")
        return False
        
    await tab.click()
    await page.wait_for_timeout(3000)
    
    # Take screenshot
    timestamp = int(time.time())
    screenshot_path = f"debug_{tab_name}_{timestamp}.png"
    await page.screenshot(path=screenshot_path, full_page=True)
    print(f"📸 Screenshot: {screenshot_path}")
    
    # Check if tab is active
    is_active = await tab.evaluate("el => el.classList.contains('active')")
    print(f"   Active: {is_active}")
    
    # Check for loading states
    loading_elements = await page.query_selector_all(".loading")
    print(f"   Loading elements: {len(loading_elements)}")
    
    # Check for error messages
    error_elements = await page.query_selector_all(".error, .empty-state")
    print(f"   Error/empty elements: {len(error_elements)}")
    
    return True

async def systematic_debug():
    print("🚀 Starting Systematic Tab Debug with MCP Tools")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Console logging
        context.on('console', lambda msg: print(f"CONSOLE: [{msg.type}] {msg.text}"))
        context.on('pageerror', lambda err: print(f"❌ JS ERROR: {err}"))
        
        page = await context.new_page()
        
        # Navigate
        print("📍 Loading dashboard...")
        await page.goto("http://localhost:8000/professional-dashboard.html")
        await page.wait_for_load_state("networkidle")
        
        # Define tabs to test
        tabs = [
            ("overview", "[data-tab='overview']", "Overview Tab"),
            ("mailbox", "[data-tab='mailbox']", "Mailbox Tab"),
            ("cosmos", "[data-tab='cosmos']", "Cosmos Explorer Tab"),
            ("graph", "[data-tab='graph']", "Graph DB Tab"),
            ("agents", "[data-tab='agents']", "Agent Shell Tab"),
            ("manager", "[data-tab='manager']", "Manager Tab"),
            ("workspace", "[data-tab='workspace']", "Workspace Tab"),
            ("architecture", "[data-tab='research']", "Architecture Tab"),
            ("documentation", "[data-tab='documentation']", "Documentation Tab"),
            ("deepcontext", "[data-tab='deepcontext']", "Deep Context Tab")
        ]
        
        # Test each tab
        results = {}
        for tab_name, selector, description in tabs:
            try:
                success = await debug_tab(page, tab_name, selector, description)
                results[tab_name] = "✅ PASS" if success else "❌ FAIL"
            except Exception as e:
                print(f"❌ Error testing {tab_name}: {e}")
                results[tab_name] = f"❌ ERROR: {e}"
        
        # Summary
        print(f"\n📊 Test Results Summary:")
        for tab_name, result in results.items():
            print(f"   {tab_name:12} {result}")
        
        print(f"\n🔍 Screenshots saved for manual inspection")
        print(f"✅ Systematic debug completed")
        
        input("Press Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(systematic_debug())