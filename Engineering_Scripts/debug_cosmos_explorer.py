#!/usr/bin/env python3
"""
Debug Cosmos Explorer - Navigation and Document Loading Issues
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_cosmos_explorer():
    print("🌌 Debugging Cosmos Explorer Tab")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Console logging
        console_logs = []
        errors = []
        
        def log_console(msg):
            entry = f"[{msg.type}] {msg.text}"
            console_logs.append(entry)
            print(f"CONSOLE: {entry}")
            
        def log_error(err):
            error_msg = str(err)
            errors.append(error_msg)
            print(f"❌ ERROR: {error_msg}")
            
        context.on('console', log_console)
        context.on('pageerror', log_error)
        
        page = await context.new_page()
        
        # Navigate to dashboard
        print("📍 Loading dashboard...")
        await page.goto("http://localhost:8000/professional-dashboard.html")
        await page.wait_for_load_state("networkidle")
        
        # Click Cosmos Explorer tab
        print("\n🌌 Clicking Cosmos Explorer tab...")
        cosmos_tab = await page.query_selector("[data-tab='cosmos']")
        await cosmos_tab.click()
        await page.wait_for_timeout(3000)
        
        # Check tab content structure
        cosmos_content = await page.evaluate("""
            const cosmosTab = document.getElementById('cosmos');
            return {
                tab_exists: !!cosmosTab,
                tab_visible: cosmosTab ? getComputedStyle(cosmosTab).display !== 'none' : false,
                tab_content: cosmosTab ? cosmosTab.textContent.substring(0, 200) : null
            }
        """)
        
        print(f"📊 Cosmos Tab Status:")
        print(f"   Tab exists: {cosmos_content['tab_exists']}")
        print(f"   Tab visible: {cosmos_content['tab_visible']}")
        print(f"   Content preview: {cosmos_content['tab_content']}...")
        
        # Check for container list
        containers = await page.query_selector_all(".container-item")
        print(f"📦 Found {len(containers)} container items")
        
        if containers:
            # Test clicking first container
            print("\n👆 Testing container navigation...")
            first_container = containers[0]
            container_name = await first_container.evaluate("el => el.textContent")
            print(f"   Clicking container: {container_name}")
            
            await first_container.click()
            await page.wait_for_timeout(3000)
            
            # Check if documents loaded
            documents = await page.query_selector_all(".document-item, .list-item")
            print(f"📄 Found {len(documents)} document items after click")
            
            if documents:
                # Test clicking first document
                print("\n👆 Testing document loading...")
                first_doc = documents[0]
                await first_doc.click()
                await page.wait_for_timeout(2000)
                
                # Check document viewer
                viewer_content = await page.evaluate("""
                    const viewer = document.querySelector('#document-viewer, #cosmos-viewer, .document-display');
                    return {
                        viewer_exists: !!viewer,
                        viewer_content: viewer ? viewer.textContent.substring(0, 100) : null
                    }
                """)
                
                print(f"📖 Document Viewer:")
                print(f"   Viewer exists: {viewer_content['viewer_exists']}")
                print(f"   Content: {viewer_content['viewer_content']}")
        
        # Check for loading states
        loading_elements = await page.query_selector_all(".loading")
        print(f"\n⏳ Loading elements found: {len(loading_elements)}")
        
        # Check for error states
        error_elements = await page.query_selector_all(".error, .empty-state")
        print(f"❌ Error/empty elements found: {len(error_elements)}")
        
        # Take screenshot
        timestamp = int(__import__('time').time())
        await page.screenshot(path=f"cosmos_debug_{timestamp}.png", full_page=True)
        print(f"\n📸 Screenshot: cosmos_debug_{timestamp}.png")
        
        # Summary
        print(f"\n📊 Debug Summary:")
        print(f"   Console logs: {len(console_logs)}")
        print(f"   Errors: {len(errors)}")
        
        if errors:
            print("\n❌ Errors found:")
            for error in errors[:3]:
                print(f"   - {error}")
                
        print("\n🔍 Browser staying open for manual inspection...")
        print("   - Check Cosmos tab navigation")
        print("   - Test container clicking")
        print("   - Test document loading")
        print("   Ctrl+C to close")
        
        try:
            await page.wait_for_timeout(300000)  # 5 minutes
        except KeyboardInterrupt:
            print("👋 Closing browser...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_cosmos_explorer())