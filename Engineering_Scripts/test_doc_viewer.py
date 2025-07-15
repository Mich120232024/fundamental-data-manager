#!/usr/bin/env python3
"""
Test Documentation Viewer - Click Documents to See Content
"""

import asyncio
from playwright.async_api import async_playwright

async def test_doc_viewer():
    print("🧪 Testing Documentation Viewer - Real Content")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
        # Console logging
        page.on('console', lambda msg: print(f"CONSOLE: {msg.text}"))
        
        await page.goto("http://localhost:8000/professional-dashboard.html")
        await page.wait_for_timeout(3000)
        
        # Go to Documentation tab
        print("📚 Clicking Documentation tab...")
        await page.click("[data-tab='documentation']")
        await page.wait_for_timeout(4000)
        
        # Wait for categories to load
        await page.wait_for_selector(".doc-category", timeout=10000)
        print("✅ Categories loaded")
        
        # Click first document
        print("👆 Clicking first document...")
        first_doc = await page.query_selector(".doc-category .doc-item")
        if first_doc:
            doc_name = await first_doc.text_content()
            print(f"   Clicking: {doc_name}")
            await first_doc.click()
            await page.wait_for_timeout(3000)
            
            # Check viewer content
            viewer = await page.query_selector("#doc-viewer")
            if viewer:
                content = await viewer.text_content()
                print(f"📄 Viewer content preview: {content[:100]}...")
                
                if "Loading" in content:
                    print("⚠️  Still loading...")
                elif "Select a document" in content:
                    print("❌ No content loaded - still showing placeholder")
                else:
                    print("✅ Real content displayed!")
            else:
                print("❌ Viewer not found")
        else:
            print("❌ No documents found to click")
        
        # Take screenshot
        timestamp = int(__import__('time').time())
        await page.screenshot(path=f"doc_viewer_test_{timestamp}.png", full_page=True)
        print(f"📸 Screenshot: doc_viewer_test_{timestamp}.png")
        
        input("Press Enter to close...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_doc_viewer())