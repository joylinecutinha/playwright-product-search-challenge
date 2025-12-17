from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("http://www.amazon.de/", wait_until="domcontentloaded")
    try:
        page.get_by_role("button", name="Weiter shoppen").click(timeout=5000)
        page.wait_for_load_state("domcontentloaded")
    except PWTimeoutError:
        # Button not shown -> continue normally
        pass
    search = page.locator("#twotabsearchtextbox")
    search.click()
    search.fill("Harry Potter Buch")
    search.press("Enter")
    print("Title:", page.title())
    input("Press Enter to close the browser...")
    # page.screenshot(path="shot.png")
    browser.close()