#!/usr/bin/env python3
"""
Test Documentation Tab API Loading
"""

import asyncio
from playwright.async_api import async_playwright

async def test_doc_api():
    print("🧪 Testing Documentation API Loading...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context()
        
        # Capture console messages
        context.on('console', lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        context.on('pageerror', lambda err: print(f"❌ JS ERROR: {err}"))
        
        page = await context.new_page()
        
        # Navigate and wait
        await page.goto("http://localhost:8000/professional-dashboard.html")
        await page.wait_for_timeout(3000)
        
        # Click Documentation tab
        print("👆 Clicking Documentation tab...")
        doc_tab = await page.query_selector("[data-tab='documentation']")
        await doc_tab.click()
        await page.wait_for_timeout(5000)  # Wait longer for loading
        
        # Check what's in the categories div
        categories_content = await page.evaluate("""
            const categoriesDiv = document.getElementById('doc-categories');
            return {
                exists: !!categoriesDiv,
                innerHTML: categoriesDiv ? categoriesDiv.innerHTML : null,
                textContent: categoriesDiv ? categoriesDiv.textContent : null
            }
        """)
        
        print(f"📋 Categories div status:")
        print(f"   Exists: {categories_content['exists']}")
        print(f"   Content: {categories_content['textContent']}")
        
        # Manually test the API call
        print("\n🌐 Testing API call manually...")
        api_result = await page.evaluate("""
            fetch('http://localhost:8420/api/v1/docs/structure')
                .then(response => {
                    console.log('API Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('API Data received:', data);
                    return {success: true, data: data};
                })
                .catch(err => {
                    console.error('API Error:', err);
                    return {success: false, error: err.message};
                })
        """)
        
        if api_result['success']:
            print("✅ API call successful")
            data = api_result['data']
            print(f"   Categories: {len(data.get('categories', []))}")
        else:
            print(f"❌ API call failed: {api_result['error']}")
        
        # Manually call loadDocumentation
        print("\n🔄 Manually calling loadDocumentation...")
        result = await page.evaluate("""
            loadDocumentation().then(() => {
                const categoriesDiv = document.getElementById('doc-categories');
                return {
                    innerHTML: categoriesDiv.innerHTML,
                    textContent: categoriesDiv.textContent
                };
            }).catch(err => {
                console.error('loadDocumentation error:', err);
                return {error: err.message};
            })
        """)
        
        print(f"📋 After manual loadDocumentation:")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"   Content: {result['textContent'][:200]}...")
        
        # Take screenshot
        timestamp = int(__import__('time').time())
        await page.screenshot(path=f"doc_api_test_{timestamp}.png", full_page=True)
        print(f"📸 Screenshot: doc_api_test_{timestamp}.png")
        
        input("Press Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_doc_api())