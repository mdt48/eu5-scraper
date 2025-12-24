"""Debug script to test forum page loading with Playwright."""
import asyncio
from playwright.async_api import async_playwright


async def test_forum_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to False to see what happens
        page = await browser.new_page()

        url = "https://forum.paradoxplaza.com/forum/index.php?threads/1887357"
        print(f"Loading: {url}")

        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(5000)  # Wait 5 seconds

        # Get page title
        title = await page.title()
        print(f"Page title: {title}")

        # Try different selectors
        selectors_to_try = [
            "article.message--post",
            ".message-body",
            ".bbWrapper",
            "article",
            "[class*='message']",
            ".p-body-content",
        ]

        for selector in selectors_to_try:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"✓ Found: {selector}")
                    text = await element.inner_text()
                    print(f"  Content preview: {text[:100]}...")
                else:
                    print(f"✗ Not found: {selector}")
            except Exception as e:
                print(f"✗ Error with {selector}: {e}")

        # Get page HTML for inspection
        html = await page.content()
        print(f"\nHTML length: {len(html)} characters")
        print(f"HTML preview:\n{html[:500]}\n...")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_forum_page())
