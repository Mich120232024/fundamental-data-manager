#!/usr/bin/env python3
"""
Test keyboard shortcuts and UI improvements
"""
import asyncio
import time
from playwright.async_api import async_playwright

async def test_shortcuts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        print("🚀 Testing keyboard shortcuts...")
        await page.goto('http://localhost:8420', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        
        # Test ? for help
        print("🧪 Testing ? for help...")
        await page.keyboard.press('Shift+?')
        await page.wait_for_timeout(2000)
        
        # Take screenshot of help modal
        help_screenshot = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/keyboard_help_{int(time.time())}.png"
        await page.screenshot(path=help_screenshot)
        print(f"📸 Help modal screenshot: {help_screenshot}")
        
        # Close help modal with ESC
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(1000)
        
        # Test number keys for tab navigation
        print("🧪 Testing number keys for tabs...")
        await page.keyboard.press('4')  # Graph DB tab
        await page.wait_for_timeout(1500)
        
        # Test / for search focus
        print("🧪 Testing / for search...")
        await page.keyboard.press('/')
        await page.wait_for_timeout(1000)
        
        # Check if search is focused
        search_focused = await page.evaluate("""
            () => document.activeElement.id === 'graph-search'
        """)
        
        if search_focused:
            print("✅ Search input focused successfully")
            await page.keyboard.type("test search")
        else:
            print("❌ Search input not focused")
        
        # Test tab switching with numbers
        print("🧪 Testing quick tab switching...")
        for i in [1, 2, 3]:
            await page.keyboard.press(str(i))
            await page.wait_for_timeout(800)
        
        # Final screenshot
        final_screenshot = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/Scripts/final_state_{int(time.time())}.png"
        await page.screenshot(path=final_screenshot)
        print(f"📸 Final state screenshot: {final_screenshot}")
        
        print("✅ Keyboard shortcuts testing completed!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_shortcuts())