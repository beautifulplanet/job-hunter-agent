import requests
from bs4 import BeautifulSoup

# Try playwright, fall back to requests
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def scrape_jd(url: str) -> str:
    """
    Scrapes the text content from a given URL.
    Tries Playwright first (for JS-rendered pages), falls back to requests.
    """
    # Try Playwright first (handles JS-heavy sites like LinkedIn)
    if HAS_PLAYWRIGHT:
        try:
            return _scrape_with_playwright(url)
        except Exception as e:
            print(f"  [WARN] Playwright scrape failed: {e}")
            print(f"  Falling back to requests...")

    # Fallback: simple HTTP request
    return _scrape_with_requests(url)


def _scrape_with_playwright(url: str) -> str:
    """Scrape using Playwright for JS-rendered content."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            # Wait for content to stabilize instead of fixed sleep
            page.wait_for_load_state("networkidle", timeout=10000)

            content = page.content()
            return _extract_text_from_html(content)
        except Exception as e:
            raise RuntimeError(f"Playwright error: {e}")
        finally:
            browser.close()


def _scrape_with_requests(url: str) -> str:
    """Scrape using requests (no JS rendering)."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return _extract_text_from_html(response.text)
    except Exception as e:
        print(f"  [ERROR] requests scrape failed: {e}")
        return ""


def _extract_text_from_html(html: str) -> str:
    """Extract clean text from HTML, removing nav/footer/script noise."""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try to find the main content area first
    main = soup.find("main") or soup.find("article") or soup.find(role="main")
    target = main if main else soup

    text = target.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text
