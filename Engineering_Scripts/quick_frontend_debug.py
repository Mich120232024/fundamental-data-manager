#!/usr/bin/env python3
"""
Quick Frontend Debug - Minimal Browser Testing
"""

import asyncio
from playwright.async_api import async_playwright

async def quick_debug():
    print("🚀 Quick Frontend Debug Starting...")
    
    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context()
        
        # Enable console logging
        def handle_console(msg):
            print(f"CONSOLE: {msg.text}")
        context.on('console', handle_console)
        
        page = await context.new_page()
        
        # Navigate to viewer
        print("📍 Loading Cosmos DB Viewer...")
        await page.goto("http://localhost:5001/viewer")
        
        # Wait and check
        await page.wait_for_timeout(3000)
        
        # Count containers
        containers = await page.query_selector_all(".container-item")
        print(f"✅ Found {len(containers)} containers")
        
        # Take screenshot
        await page.screenshot(path="quick_debug_screenshot.png")
        print("📸 Screenshot saved: quick_debug_screenshot.png")
        
        # Keep browser open for manual inspection
        print("🔍 Browser will stay open for manual inspection...")
        print("   Press Enter to close browser and exit")
        input()
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_debug())
