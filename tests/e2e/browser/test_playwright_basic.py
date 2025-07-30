"""
Simple Playwright test to verify browser setup works

NOTE: Currently experiencing Docker container networking issues where Chrome
cannot connect to the Django LiveServer despite the server being accessible
via HTTP requests. This is a known limitation with Chrome in Docker containers.

Status: Infrastructure ready, networking configuration needs investigation.
The core test logic and cleanup is implemented correctly.
"""
import unittest
import os
from tests.playwright_base import PlaywrightTestBase

# Fix Django async context issues
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


class SimplePlaywrightTest(PlaywrightTestBase):
    """Simple test to verify Playwright works with Django"""
    
    def test_browser_opens_page(self):
        """Test that browser can open a page"""
        context = None
        try:
            context = self.browser.new_context()
            page = context.new_page()
            
            # Set a page timeout to prevent hanging
            page.set_default_timeout(10000)
            
            # Fix localhost issue in Docker containers
            # Replace localhost with 127.0.0.1 for Chrome compatibility in containers
            server_url = self.live_server_url.replace('localhost', '127.0.0.1')
            print(f"Live server URL: {server_url}")
            
            # Navigate to home page (which contains login form)
            page.goto(f"{server_url}/")
            
            # Wait for page to load
            page.wait_for_load_state('domcontentloaded')
            
            # Should see login form elements on home page
            # Login form uses 'email' and 'password' fields
            login_email = page.locator('input[name="email"]')
            login_password = page.locator('input[name="password"]')
            
            # Wait for elements to be visible with shorter timeout
            try:
                login_email.wait_for(state="visible", timeout=3000)
                login_password.wait_for(state="visible", timeout=3000)
                
                self.assertTrue(login_email.is_visible())
                self.assertTrue(login_password.is_visible())
            except Exception as e:
                # Take screenshot for debugging
                page.screenshot(path='test_failure_screenshot.png')
                print(f"Page content: {page.content()[:500]}")
                raise e
        finally:
            if context:
                context.close()
    
    def test_home_shows_login_form(self):
        """Test that home page shows login form for unauthenticated users"""
        context = None
        try:
            context = self.browser.new_context()
            page = context.new_page()
            
            # Set a page timeout to prevent hanging
            page.set_default_timeout(10000)
            
            # Fix localhost issue in Docker containers
            server_url = self.live_server_url.replace('localhost', '127.0.0.1')
            
            # Navigate to home
            page.goto(f"{server_url}/")
            
            # Wait for page to load
            page.wait_for_load_state('domcontentloaded')
            
            # Should see both login and registration forms
            login_form = page.locator('form').first  # Login form is typically first
            registration_form = page.locator('form').nth(1)  # Registration form second
            
            self.assertTrue(login_form.is_visible())
            self.assertTrue(registration_form.is_visible())
        finally:
            if context:
                context.close()