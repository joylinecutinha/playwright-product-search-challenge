
# Amazon.de find book by scraping

This is a small Playwright automation script that opens **Amazon Germany (amazon.de)**, searches for **“Harry Potter Buch”**, and prints the **title + price** of the **first** search result as JSON.

It’s written with real life issues in mind (banners pop up, clicks fail, internet drops, Edge might not exist on a machine), so it includes:
- clear logging to keep a track and see what step failed
- a safe `try_click()` helper
- an internet connection check before starting
- Microsoft Edge launch first, then a fallback to Chromium

---

## What it does

When you run the script, it:

1. Checks if you’re online 
2. Opens a browser.
3. Goes to `https://www.amazon.de/`.
4. Tries to close the common Amazon popups (like cookies / “Weiter shoppen”).
5. Types **Harry Potter Buch** into the search bar and hits Enter.
6. Waits until it can see product links.
7. Picks the **first** product, finds its matching “result card”, and extracts:
   - product **title**
   - product **price** (if available)
8. Prints the final result as formatted JSON.

---

## Libraries used

### External library 
- **Playwright for Python** (`playwright`)
  - What it’s used for: launching a real browser (Edge/Chromium), opening pages, clicking buttons, filling inputs, waiting for elements, and extracting text/attributes from the page.

Install:
```bash
pip install -r requirements.txt
playwright install msedge (optional)

