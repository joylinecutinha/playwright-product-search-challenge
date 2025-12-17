import json
import re
import time
import logging
import socket
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError, Error as PlaywrightError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("amazon-scraper")

def try_click(locator, label="(unknown)", timeout=2000):
    try:
        logger.info(f"click -> {label}")
        locator.click(timeout=timeout)
        logger.info(f"Success: clicked -> {label}")
        return True
    except PWTimeoutError:
        logger.info(f"Skip: not clickable / not found in time -> {label}")
        return False
    except PlaywrightError as e:
        logger.warning(f"Playwright error while clicking {label}: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error while clicking {label}: {e}")
        return False


def has_internet(host="www.amazon.de", port=443, timeout=3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

logger.info("Verifying internet connection")
if not has_internet():
    logger.error("No internet connection detected. Please connect to the internet and try again.")
    raise SystemExit(1)
logger.info("Internet connection looks OK.")


with sync_playwright() as p:
    browser = None
    page = None

    try:
        logger.info("Step 1: launch browser")
        # browser = p.chromium.launch(headless=False)
        try:
            browser = p.chromium.launch(channel="msedge", headless=False)
        except PlaywrightError:
            browser = p.chromium.launch(headless=False)  # fallback to Playwright's bundled Chromium

        logger.info("Step 2: open new page")
        page = browser.new_page()

        page.set_default_timeout(60000)

        logger.info("Step 3: goto https://www.amazon.de/")
        
        page.goto("https://www.amazon.de/", wait_until="domcontentloaded")
        logger.info("Success: page loaded ")
    
        # Optional banners
        try_click(page.get_by_role("button", name="Weiter shoppen"), label="Weiter shoppen", timeout=5000)
        try_click(page.locator("#sp-cc-accept"), label="Cookie accept (#sp-cc-accept)", timeout=5000)

        # Search for the book
        logger.info('Step 4: fill search box with "Harry Potter Buch"')
        page.locator("#twotabsearchtextbox").fill("Harry Potter Buch")

        logger.info("Step 5: press Enter to search")
        page.keyboard.press("Enter")

        page.wait_for_load_state("domcontentloaded")

        # Wait for results
        logger.info("Step 6: wait for product link selector a[href*='/dp/']")
        page.wait_for_selector('a[href*="/dp/"]')
        logger.info("Success: product links found")

        # Get the first product title link
        logger.info("Step 7: locate first product link")
        link = page.locator('a[href*="/dp/"]').filter(has_text=re.compile(r".+")).first

        # Find the surrounding result
        logger.info("Step 8: locate surrounding search result card")
        card = link.locator('xpath=ancestor::*[@data-component-type="s-search-result"][1]')

        # Extract title
        logger.info("Step 9: extract title")
       
        title = (link.get_attribute("title") or link.inner_text() or "").strip()
        if not title:
            logger.warning("Title extracted but empty")
            title = None
        else:
            logger.info(f"Success: title -> {title}")

        # Extract price 
        logger.info("Step 10: extract price ")
        price = None
        try:
            price = card.locator("span.a-price span.a-offscreen").first.inner_text().strip()
            logger.info(f"Success: price -> {price}")
        except PWTimeoutError:
            logger.info("Price not found in time (leaving as None)")
        except PlaywrightError as e:
            logger.warning(f"Playwright error while extracting price (leaving as None): {e}")
        except Exception as e:
            logger.warning(f"Unexpected error while extracting price (leaving as None): {e}")

        result = {"title": title, "price": price}
        logger.info("Step 11: print final JSON result")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        time.sleep(5)

    except PWTimeoutError as e:        
        if not has_internet():
            logger.error("No internet connection detected. Please connect to the internet and try again.")
            # raise SystemExit(1)
        else:
            logger.error(f"Timeout error occurred: {e}")
    except PlaywrightError as e:
        logger.error(f"Playwright error occurred: {e}")
        
    except Exception as e:
        logger.exception(f"Unexpected fatal error: {e}")

    finally:
        logger.info("Step 12: close browser")
        try:
            if browser:
                browser.close()
                logger.info("Success: browser closed")
        except Exception as e:
            logger.warning(f"Error while closing browser: {e}")
