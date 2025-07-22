"""
Simple Playwright test to verify browser setup works
"""
import unittest
from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright


class SimplePlaywrightTest(LiveServerTestCase):
    """Simple test to verify Playwright works with Django"""
    
    @classmethod  
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        
        try:
            cls.browser = cls.playwright.chromium.launch(
                headless=True,
                executable_path='/usr/bin/google-chrome-stable',
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
        except Exception:
            # Fallback to default chromium
            cls.browser = cls.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browser'):
            cls.browser.close()
        if hasattr(cls, 'playwright'):
            cls.playwright.stop()
        super().tearDownClass()
    
    def test_browser_opens_page(self):
        """Test that browser can open a page"""
        context = self.browser.new_context()
        page = context.new_page()
        
        # Navigate to login page
        page.goto(f"{self.live_server_url}/login/")
        
        # Should see login form
        self.assertTrue(page.locator('input[name="email"]').is_visible())
        
        context.close()
    
    def test_home_redirects_to_login(self):
        """Test that home page redirects to login when not authenticated"""
        context = self.browser.new_context()
        page = context.new_page()
        
        # Navigate to home
        page.goto(f"{self.live_server_url}/")
        
        # Should be redirected to login
        page.wait_for_url(f"{self.live_server_url}/login/")
        self.assertIn('/login/', page.url)
        
        context.close()