#!/usr/bin/env python3
"""
Test Fixed Documentation Viewer
"""

import asyncio
from playwright.async_api import async_playwright

async def test_fixed_docs():
    print("🧪 Testing FIXED Documentation Viewer")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless for quick test
        page = await browser.new_page()
        
        await page.goto("http://localhost:8000/professional-dashboard.html")
        await page.wait_for_timeout(2000)
        
        # Go to Documentation tab
        await page.click("[data-tab='documentation']")
        await page.wait_for_timeout(3000)
        
        # Click first document
        first_doc = await page.query_selector(".doc-item")
        if first_doc:
            await first_doc.click()
            await page.wait_for_timeout(2000)
            
            # Check viewer content
            viewer_content = await page.evaluate("""
                const viewer = document.getElementById('doc-viewer');
                return {
                    title: viewer.querySelector('.doc-title')?.textContent,
                    meta: viewer.querySelector('.doc-meta')?.textContent,
                    content_preview: viewer.querySelector('.doc-content pre')?.textContent.substring(0, 100)
                }
            """)
            
            print("📄 Document Viewer Results:")
            print(f"   Title: {viewer_content['title']}")
            print(f"   Meta: {viewer_content['meta']}")
            print(f"   Content preview: {viewer_content['content_preview']}")
            
            if viewer_content['title'] and viewer_content['title'] != 'undefined':
                print("✅ SUCCESS: Real content is loading!")
            else:
                print("❌ STILL BROKEN: Shows undefined")
        else:
            print("❌ No documents found")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fixed_docs())