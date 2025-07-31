"""
Playwright base class that doesn't use Django's LiveServerTestCase
This avoids hanging issues when Django server is not available
"""
import os
import asyncio
from pathlib import Path
from django.test import TransactionTestCase
from playwright.async_api import async_playwright

class PlaywrightTestBaseNoServer(TransactionTestCase):
    """
    Base test class for Playwright tests without LiveServer.
    Uses existing Django server or skips tests if not available.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up Playwright connection."""
        print("[NO-SERVER-BASE] Starting setUpClass", flush=True)
        super().setUpClass()
        
        # Run async setup
        asyncio.run(cls.async_class_setup())
    
    @classmethod
    async def async_class_setup(cls):
        """Async setup for Playwright."""
        print("[NO-SERVER-BASE] Starting async_class_setup", flush=True)
        
        # Initialize Playwright
        cls.playwright = await async_playwright().start()
        print("[NO-SERVER-BASE] Playwright started", flush=True)
        
        # Connect to Playwright server
        endpoint = os.environ.get('PW_TEST_CONNECT_WS_ENDPOINT', 'ws://playwright-server:3000/')
        print(f"[NO-SERVER-BASE] Connecting to: {endpoint}", flush=True)
        
        try:
            cls.browser = await cls.playwright.chromium.connect(endpoint)
            print(f"[NO-SERVER-BASE] Connected! Browser version: {cls.browser.version}", flush=True)
        except Exception as e:
            print(f"[NO-SERVER-BASE] Connection failed: {e}", flush=True)
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up Playwright."""
        asyncio.run(cls.async_class_teardown())
        super().tearDownClass()
    
    @classmethod
    async def async_class_teardown(cls):
        """Async teardown."""
        if hasattr(cls, 'browser'):
            await cls.browser.close()
        if hasattr(cls, 'playwright'):
            await cls.playwright.stop()
    
    def setUp(self):
        """Set up test instance."""
        print(f"[NO-SERVER-BASE] setUp for {self._testMethodName}", flush=True)
        super().setUp()
        
        # Create event loop
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        # Set up browser context and page
        self.loop.run_until_complete(self.async_setup_browser())
        print("[NO-SERVER-BASE] Browser setup complete", flush=True)
    
    async def async_setup_browser(self):
        """Create browser context and page."""
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        self.page = await self.context.new_page()
        
        # Screenshot directory
        self.screenshot_dir = Path("tests/screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test instance."""
        if hasattr(self, 'loop') and self.loop:
            self.loop.run_until_complete(self.async_teardown_browser())
        super().tearDown()
    
    async def async_teardown_browser(self):
        """Clean up browser resources."""
        if hasattr(self, 'page'):
            await self.page.close()
        if hasattr(self, 'context'):
            await self.context.close()
    
    def get_server_url(self):
        """Get Django server URL based on environment."""
        # Check if we're in CI
        if os.environ.get('CI'):
            return "http://localhost:8000"  # Default Django port
        else:
            # Local development
            return "http://localhost:8000"
    
    def take_screenshot(self, name):
        """Take a screenshot."""
        async def _take():
            path = self.screenshot_dir / f"{name}.png"
            await self.page.screenshot(path=str(path))
            print(f"[NO-SERVER-BASE] Screenshot saved: {path}", flush=True)
        
        self.loop.run_until_complete(_take())
    
    def goto(self, url):
        """Navigate to URL."""
        async def _goto():
            await self.page.goto(url, timeout=30000)
        
        self.loop.run_until_complete(_goto())