#!/usr/bin/env python3
"""
Test enhanced graph controls and filters
"""
import asyncio
import time
from playwright.async_api import async_playwright

async def test_graph_controls():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        print("🚀 Testing enhanced graph controls...")
        await page.goto('http://localhost:8420', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        
        # Navigate to Graph DB tab
        await page.click('text=Graph DB')
        await page.wait_for_timeout(2000)
        
        # Take screenshot of new controls
        screenshot_path = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/graph_controls_{int(time.time())}.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Graph controls screenshot: {screenshot_path}")
        
        # Test Hierarchy button
        print("🧪 Testing Hierarchy button...")
        await page.click('button:has-text("Hierarchy")')
        await page.wait_for_timeout(3000)
        
        # Take screenshot of hierarchy
        hierarchy_screenshot = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/graph_hierarchy_{int(time.time())}.png"
        await page.screenshot(path=hierarchy_screenshot)
        print(f"📸 Hierarchy screenshot: {hierarchy_screenshot}")
        
        # Test layout change
        print("🧪 Testing layout change...")
        await page.select_option('#graph-layout', 'circle')
        await page.click('button:has-text("Hierarchy")')  # Reload with new layout
        await page.wait_for_timeout(3000)
        
        # Test max nodes slider
        print("🧪 Testing max nodes slider...")
        slider = await page.query_selector('#max-nodes')
        if slider:
            await slider.fill('100')
            await page.wait_for_timeout(500)
        
        # Test Stats button
        print("🧪 Testing Stats button...")
        await page.click('button:has-text("Stats")')
        await page.wait_for_timeout(2000)
        
        # Take screenshot of stats modal
        stats_screenshot = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/graph_stats_{int(time.time())}.png"
        await page.screenshot(path=stats_screenshot)
        print(f"📸 Stats modal screenshot: {stats_screenshot}")
        
        # Close stats modal
        close_btn = await page.query_selector('.modal-close-btn')
        if close_btn:
            await close_btn.click()
            await page.wait_for_timeout(1000)
        
        # Test search functionality
        print("🧪 Testing search functionality...")
        search_input = await page.query_selector('#graph-search')
        if search_input:
            await search_input.fill('engineer')
            await page.click('button:has-text("Load Graph")')
            await page.wait_for_timeout(3000)
            
            search_screenshot = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/graph_search_{int(time.time())}.png"
            await page.screenshot(path=search_screenshot)
            print(f"📸 Search results screenshot: {search_screenshot}")
        
        print("✅ Graph controls testing completed!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_graph_controls())