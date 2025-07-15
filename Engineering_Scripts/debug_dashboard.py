#!/usr/bin/env python3
"""
Dashboard Debug - Browser Testing for Architecture Tab Issue
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_dashboard():
    print("🚀 Dashboard Debug Starting...")
    
    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context()
        
        # Enable console logging
        def handle_console(msg):
            print(f"CONSOLE: {msg.text}")
        context.on('console', handle_console)
        
        page = await context.new_page()
        
        # Navigate to dashboard
        print("📍 Loading User Dashboard...")
        await page.goto("http://localhost:8000/professional-dashboard.html")
        
        # Wait for page to load
        await page.wait_for_timeout(3000)
        
        # Click on Architecture tab
        print("👆 Clicking Architecture tab...")
        arch_tab = await page.query_selector("[data-tab='research']")
        if arch_tab:
            await arch_tab.click()
            await page.wait_for_timeout(2000)
            print("✅ Architecture tab clicked")
        
        # Check if categories are visible
        categories = await page.query_selector_all(".file-category")
        print(f"✅ Found {len(categories)} file categories")
        
        # Check if files are visible
        file_items = await page.query_selector_all(".file-item")
        print(f"✅ Found {len(file_items)} file items")
        
        # Try clicking first file if it exists
        if file_items:
            print("👆 Clicking first file...")
            await file_items[0].click()
            await page.wait_for_timeout(2000)
            
            # Check iframe src
            iframe = await page.query_selector("#architecture-iframe")
            if iframe:
                iframe_src = await iframe.get_attribute("src")
                print(f"📄 Iframe src: {iframe_src}")
        
        # Take screenshot
        timestamp = int(__import__('time').time())
        screenshot_path = f"dashboard_debug_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        print("🔍 Browser will stay open for manual inspection...")
        print("   Check console for any errors")
        print("   Ctrl+C to close")
        
        try:
            await page.wait_for_timeout(300000)  # 5 minutes
        except KeyboardInterrupt:
            print("👋 Closing browser...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_dashboard())