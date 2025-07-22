"""
Pytest configuration for Playwright tests
"""
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for the test session"""
    with sync_playwright() as p:
        # Try to use system Chrome first
        try:
            browser = p.chromium.launch(
                headless=True,
                executable_path='/usr/bin/google-chrome-stable',
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--window-size=1920,1080'
                ]
            )
        except Exception:
            # Fallback to default chromium
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions', 
                    '--window-size=1920,1080'
                ]
            )
        
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()