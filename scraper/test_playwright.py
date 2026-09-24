import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to standard details page...")
        await page.goto("https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6IkhFNngxTWpENVE2dXlsSkJROFhXU2c9PSIsInZhbHVlIjoiM1B5aHgyREZ0enJvQUl4TGtFdEc4QT09IiwibWFjIjoiMzM5MGY4YTk1OTZmOWFhZTBmODQyM2ExODZmYWQwMWVhMDk5NGRiMWY2NWU3Y2JiMTU3MzhmYzBkOWMxYzEyNiIsInRhZyI6IiJ9", wait_until="networkidle")
        
        print("Page loaded. Looking for download buttons...")
        
        # Wait a bit for any dynamic content
        await page.wait_for_timeout(3000)
        
        # Setup listeners for dialogs (alerts) and downloads
        async def handle_dialog(dialog):
            print(f"ALERT POPUP: {dialog.message}")
            await dialog.dismiss()
        page.on("dialog", handle_dialog)
        
        buttons = await page.query_selector_all("button, a")
        target = None
        for b in buttons:
            text = await b.inner_text()
            if text and "Click to download" in text:
                target = b
                break
                
        if target:
            print("Found download button. Clicking it...")
            try:
                # Wait for download or just see what happens
                async with page.expect_download(timeout=5000) as download_info:
                    await target.click()
                download = await download_info.value
                print(f"SUCCESS: Download started! Filename: {download.suggested_filename}")
            except Exception as e:
                print(f"No download triggered. Error/Result: {e}")
                # check if URL changed or if a modal popped up
                print(f"Current URL after click: {page.url}")
                # Wait a bit for modal animation
                await page.wait_for_timeout(1000)
                
                # Check for any modal or overlay
                modals = await page.query_selector_all(".modal, .cdk-overlay-container, mat-dialog-container, swal2-container, p-dialog")
                for m in modals:
                    if await m.is_visible():
                        print("Found visible modal!")
                        print("Modal text:")
                        print(await m.inner_text())
                        
                # Check if a new tab opened
                if len(browser.contexts[0].pages) > 1:
                    new_page = browser.contexts[0].pages[-1]
                    print(f"A new tab was opened! URL: {new_page.url}")
                    print(await new_page.content())
        else:
            print("No download button found.")
            
        await browser.close()

asyncio.run(main())
