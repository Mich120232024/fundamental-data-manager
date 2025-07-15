#!/usr/bin/env python3
"""
Quick MCP verification after fixing backend serving
"""
import asyncio
import time
from playwright.async_api import async_playwright

async def quick_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        print("🚀 Testing dashboard loading...")
        await page.goto('http://localhost:8420', wait_until='networkidle')
        await page.wait_for_timeout(3000)
        
        # Take screenshot
        screenshot_path = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/mcp_test_fixed_{int(time.time())}.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot: {screenshot_path}")
        
        # Check for navigation tabs
        nav_items = await page.query_selector_all('.nav-item')
        print(f"📊 Found {len(nav_items)} navigation items")
        
        if len(nav_items) >= 8:
            print("✅ Dashboard navigation loaded successfully")
            
            # Test clicking Cosmos Explorer
            await page.click('text=Cosmos Explorer')
            await page.wait_for_timeout(2000)
            
            containers = await page.query_selector_all('.list-item')
            print(f"📊 Found {len(containers)} containers in Cosmos Explorer")
            
            if len(containers) > 0:
                print("✅ Cosmos Explorer loads data successfully")
            else:
                print("❌ Cosmos Explorer not loading data")
                
        else:
            print("❌ Dashboard navigation not loading properly")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_test())