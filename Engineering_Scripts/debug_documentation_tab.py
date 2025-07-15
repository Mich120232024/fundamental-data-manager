#!/usr/bin/env python3
"""
Documentation Tab Comprehensive Testing
"""

import asyncio
from playwright.async_api import async_playwright

async def test_documentation_tab():
    print("🚀 Testing Documentation Tab Functionality...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context()
        
        # Console logging
        context.on('console', lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        context.on('pageerror', lambda err: print(f"❌ JS ERROR: {err}"))
        
        page = await context.new_page()
        
        # Navigate to dashboard
        await page.goto("http://localhost:8000/professional-dashboard.html")
        await page.wait_for_timeout(3000)
        
        # Click Documentation tab
        print("👆 Clicking Documentation tab...")
        doc_tab = await page.query_selector("[data-tab='documentation']")
        await doc_tab.click()
        await page.wait_for_timeout(3000)
        
        # Check documentation structure
        print("\n📋 Checking Documentation Structure...")
        
        # Check header
        header = await page.query_selector(".documentation-header h3")
        if header:
            header_text = await header.inner_text()
            print(f"✅ Header found: {header_text}")
        
        # Check search input
        search_input = await page.query_selector("#doc-search")
        if search_input:
            print("✅ Search input found")
        else:
            print("❌ Search input missing")
        
        # Check category filter
        category_filter = await page.query_selector("#doc-category-filter")
        if category_filter:
            print("✅ Category filter found")
        else:
            print("❌ Category filter missing")
        
        # Check upload button
        upload_btn = await page.query_selector("button[onclick='uploadDocument()']")
        if upload_btn:
            print("✅ Upload button found")
        else:
            print("❌ Upload button missing")
        
        # Check categories container
        doc_categories = await page.query_selector("#doc-categories")
        if doc_categories:
            content = await doc_categories.inner_text()
            print(f"✅ Categories container found")
            print(f"📝 Content preview: {content[:100]}...")
        else:
            print("❌ Categories container missing")
        
        # Check viewer container
        doc_viewer = await page.query_selector("#doc-viewer")
        if doc_viewer:
            viewer_content = await doc_viewer.inner_text()
            print(f"✅ Viewer container found")
            print(f"📝 Viewer content: {viewer_content[:100]}...")
        else:
            print("❌ Viewer container missing")
        
        # Test API call
        print("\n🌐 Testing Documentation API...")
        try:
            response = await page.evaluate("""
                fetch('http://localhost:8420/api/v1/docs/structure')
                    .then(response => response.json())
                    .then(data => ({success: true, data}))
                    .catch(err => ({success: false, error: err.message}))
            """)
            
            if response.get('success'):
                print("✅ Documentation API working")
                data = response.get('data', {})
                if 'categories' in data:
                    categories = data['categories']
                    print(f"📁 Found {len(categories)} categories: {list(categories.keys())[:5]}")
                else:
                    print("⚠️  No categories in API response")
            else:
                print(f"❌ Documentation API failed: {response.get('error')}")
        except Exception as e:
            print(f"❌ API test failed: {e}")
        
        # Test search functionality
        print("\n🔍 Testing Search Functionality...")
        if search_input:
            await search_input.fill("test")
            await search_input.press("Enter")
            await page.wait_for_timeout(1000)
            print("✅ Search input tested")
        
        # Take screenshot
        timestamp = int(__import__('time').time())
        await page.screenshot(path=f"documentation_tab_debug_{timestamp}.png", full_page=True)
        print(f"📸 Screenshot saved: documentation_tab_debug_{timestamp}.png")
        
        print("\n🔍 Browser staying open for manual inspection...")
        print("   Check the Documentation tab functionality")
        print("   Ctrl+C to close")
        
        try:
            await page.wait_for_timeout(300000)  # 5 minutes
        except KeyboardInterrupt:
            print("👋 Closing browser...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_documentation_tab())