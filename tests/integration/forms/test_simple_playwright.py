"""
Simple Playwright test to verify the setup works
This avoids StaticLiveServerTestCase complexity
"""
import os
from django.test import TestCase
from playwright.sync_api import sync_playwright


class SimplePlaywrightTest(TestCase):
    """Simple test to verify Playwright works without LiveServer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Playwright."""
        super().setUpClass()
        print("[SIMPLE-TEST] Starting Playwright...", flush=True)
        
        cls.playwright = sync_playwright().start()
        endpoint = os.environ.get('PW_TEST_CONNECT_WS_ENDPOINT', 'ws://localhost:3000/')
        
        try:
            print(f"[SIMPLE-TEST] Connecting to {endpoint}...", flush=True)
            cls.browser = cls.playwright.chromium.connect(endpoint)
            print(f"[SIMPLE-TEST] Connected! Version: {cls.browser.version}", flush=True)
        except Exception as e:
            print(f"[SIMPLE-TEST] Connection failed: {e}", flush=True)
            cls.playwright.stop()
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up."""
        if hasattr(cls, 'browser'):
            cls.browser.close()
        if hasattr(cls, 'playwright'):
            cls.playwright.stop()
        super().tearDownClass()
    
    def test_playwright_works(self):
        """Test that Playwright can create pages."""
        print("[SIMPLE-TEST] Creating browser context...", flush=True)
        context = self.browser.new_context()
        
        print("[SIMPLE-TEST] Creating page...", flush=True)
        page = context.new_page()
        
        print("[SIMPLE-TEST] Navigating to example.com...", flush=True)
        page.goto("https://example.com", timeout=30000)
        
        title = page.title()
        print(f"[SIMPLE-TEST] Page title: {title}", flush=True)
        
        page.close()
        context.close()
        
        self.assertEqual(title, "Example Domain")
        print("[SIMPLE-TEST] ✅ Test passed!", flush=True)