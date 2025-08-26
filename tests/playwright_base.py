import os
import tempfile
from pathlib import Path
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, TransactionTestCase
from django.db import transaction
from django.contrib.auth import get_user_model
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from pacientes.models import Paciente
from processos.models import Doenca, Medicamento, Processo
import datetime
from tests.test_base import UniqueDataGenerator

# Using Playwright Async API to work properly with asyncio event loops

# Import container utilities for debugging and process management
try:
    from .container_utils import ContainerProcessManager, PlaywrightContainerDebugger
except ImportError:
    # Fallback if container_utils not available
    class ContainerProcessManager:
        @staticmethod
        def cleanup_chrome_processes():
            return True

        @staticmethod
        def monitor_resources():
            return True

    class PlaywrightContainerDebugger:
        def __init__(self, test_instance):
            pass

        def health_check_before_test(self):
            return True


User = get_user_model()

# Fix for Django async context issues with Playwright
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


class PlaywrightTestBase(StaticLiveServerTestCase):
    """
    Base test class for Playwright tests in Django.
    Optimized for Docker container environments and official Playwright images.
    """

    # Django server is running in separate web container

    # Override to make live server accessible from other containers
    host = "0.0.0.0"

    @property
    def live_server_url(self):
        """Override to use container network-accessible URL."""
        # Return URL that Playwright server container can access
        # Use the web service name instead of localhost
        return f"http://web:{self.server_thread.port}"

    @classmethod
    async def async_class_setup(cls):
        """Async setup for Playwright - called from setUpClass"""
        print("[SETUP] Initializing Playwright with Async API...")

        # Initialize Playwright in async mode
        cls.playwright = await async_playwright().start()
        print("[OK] Playwright async API initialized successfully")

        # Connect to Playwright server running in playwright-server container
        playwright_server_endpoint = os.environ.get(
            "PW_TEST_CONNECT_WS_ENDPOINT", "ws://playwright-server:3000/"
        )
        
        print(f"[CONNECT] Connecting to Playwright server at {playwright_server_endpoint}")
        
        try:
            # Connect to the Playwright server using the standard connect method
            cls.browser = await cls.playwright.chromium.connect(playwright_server_endpoint)
            print("[OK] Successfully connected to Playwright server")
            
            # Test the connection by getting browser version
            try:
                browser_version = cls.browser.version
                print(f"[DEBUG] Connected browser version: {browser_version}")
            except Exception as version_error:
                print(f"[WARN] Could not get browser version: {version_error}")
                
        except Exception as connection_error:
            print(f"[ERROR] Playwright server connection failed: {connection_error}")
            print(f"[DEBUG] Attempted endpoint: {playwright_server_endpoint}")
            raise Exception(f"Failed to connect to Playwright server: {connection_error}")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Run the async setup
        import asyncio

        asyncio.run(cls.async_class_setup())

    @classmethod
    async def async_class_teardown(cls):
        """Async teardown for Playwright - called from tearDownClass"""
        import asyncio
        
        # Proper teardown sequence per official Playwright documentation
        try:
            if hasattr(cls, "browser") and cls.browser:
                print("[TEARDOWN] Closing browser connection...")
                # Add delay before browser.close() to prevent CancelledError
                await asyncio.sleep(0.1)
                await cls.browser.close()
                print("[OK] Browser closed successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Browser close cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Browser cleanup failed: {e}")
            
        try:
            if hasattr(cls, "playwright") and cls.playwright:
                print("[TEARDOWN] Stopping Playwright...")
                await cls.playwright.stop()
                print("[OK] Playwright stopped successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Playwright stop cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Playwright cleanup failed: {e}")

    @classmethod
    def tearDownClass(cls):
        # Run async cleanup
        import asyncio

        try:
            asyncio.run(cls.async_class_teardown())
        except Exception as e:
            print(f"Warning: Teardown failed: {e}")
            # Continue with teardown even if cleanup fails
        super().tearDownClass()

    def setUp(self):
        super().setUp()

        # Create an async test utility
        import asyncio

        # Python 3.11+ compatible event loop handling
        # Official Python pattern for handling "no current event loop" RuntimeError
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                # Create and set new event loop as recommended by Python docs
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                raise
        
        # Alternative pattern (for reference):
        # try:
        #     self.loop = asyncio.get_running_loop()
        # except RuntimeError:
        #     self.loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(self.loop)

        # Create a new context for each test to ensure isolation
        self.context = None
        self.page = None
        
        # Initialize browser context and page for the test
        self.setup_browser()

    async def async_setup_browser(self):
        """Set up browser context and page for the test"""
        # Create new context for test isolation
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )

        # Enable request/response interception for debugging
        self.context.on("request", lambda request: print(f"Request: {request.url}"))
        self.context.on(
            "response",
            lambda response: print(f"Response: {response.url} - {response.status}"),
        )

        # Create new page
        self.page = await self.context.new_page()

        # Set up screenshot directory for failed tests
        screenshot_dir = Path("tests/screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        self.screenshot_dir = screenshot_dir

        print(f"[SETUP] Browser context and page ready for {self.__class__.__name__}")

    def setup_browser(self):
        """Synchronous wrapper for async browser setup"""
        return self.loop.run_until_complete(self.async_setup_browser())

    async def async_teardown_browser(self):
        """Clean up browser context and page after the test"""
        import asyncio
        
        # Proper teardown sequence: page -> context
        try:
            if self.page:
                print("[TEARDOWN] Closing page...")
                await self.page.close()
                print("[OK] Page closed successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Page close cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Page cleanup failed: {e}")
            
        try:
            if self.context:
                print("[TEARDOWN] Closing context...")
                await asyncio.sleep(0.1)  # Small delay before context close
                await self.context.close()
                print("[OK] Context closed successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Context close cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Context cleanup failed: {e}")

    def teardown_browser(self):
        """Synchronous wrapper for async browser teardown"""
        return self.loop.run_until_complete(self.async_teardown_browser())

    def tearDown(self):
        # Clean up browser resources
        if hasattr(self, "context") and self.context:
            self.teardown_browser()
        super().tearDown()

    async def async_navigate_to(self, url):
        """Navigate to a URL with error handling"""
        if not self.page:
            await self.async_setup_browser()

        print(f"[NAV] Navigating to: {url}")
        try:
            response = await self.page.goto(url, wait_until="networkidle")
            if response:
                print(f"[NAV] Response status: {response.status}")
            return response
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            # Take screenshot on navigation failure
            await self.async_take_screenshot(f"navigation_failed_{self._testMethodName}")
            raise

    def navigate_to(self, url):
        """Synchronous wrapper for navigation"""
        return self.loop.run_until_complete(self.async_navigate_to(url))

    async def async_take_screenshot(self, name: str):
        """Take a screenshot with the given name"""
        if not self.page:
            print("[WARN] No page available for screenshot")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        screenshot_path = self.screenshot_dir / filename

        try:
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"[SCREENSHOT] Saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            return None

    def take_screenshot(self, name: str):
        """Synchronous wrapper for taking screenshots"""
        return self.loop.run_until_complete(self.async_take_screenshot(name))

    async def async_wait_for_page_load(self):
        """Wait for the page to fully load."""
        if not self.page:
            await self.async_setup_browser()
        # Add timeout to prevent infinite wait
        await self.page.wait_for_load_state("networkidle", timeout=30000)

    def wait_for_page_load(self):
        """Synchronous wrapper for waiting for page load"""
        return self.loop.run_until_complete(self.async_wait_for_page_load())

    async def async_login_user(self, email: str, password: str):
        """Helper method to log in a user."""
        if not self.page:
            await self.async_setup_browser()
            
        # Use the proper live server URL for container communication
        server_url = self.live_server_url
        print(f"[DEBUG] Connecting to Django server: {server_url}")

        try:
            await self.page.goto(f"{server_url}/", timeout=30000, wait_until="networkidle")
            print("[OK] Successfully connected to Django server")
        except Exception as e:
            print(f"[ERROR] Failed to connect to Django server: {e}")
            # Take screenshot for debugging
            try:
                await self.async_take_screenshot("connection_failed")
            except BaseException:
                pass
            raise

        await self.page.wait_for_load_state("domcontentloaded")

        # Fill login form (on home page)
        # The form uses 'username' field for email
        await self.page.fill('input[name="username"]', email)
        await self.page.fill('input[name="password"]', password)

        # Click login submit button (look for specific login form button)
        login_button = self.page.locator('button[type="submit"]').first
        await login_button.click()

        # Wait for navigation and full page reload after login
        await self.page.wait_for_load_state("networkidle")

    def login_user(self, email: str, password: str):
        """Synchronous wrapper for user login"""
        return self.loop.run_until_complete(self.async_login_user(email, password))


class PlaywrightFormTestBase(PlaywrightTestBase):
    """Base class for testing forms and complex interactions."""

    async def async_fill_form_field(self, selector: str, value: str):
        """Fill a form field and wait for it to be updated."""
        if not self.page:
            await self.async_setup_browser()
        await self.page.fill(selector, value)
        await self.page.wait_for_timeout(100)  # Small delay for form updates

    def fill_form_field(self, selector: str, value: str):
        """Synchronous wrapper for filling form fields"""
        return self.loop.run_until_complete(self.async_fill_form_field(selector, value))

    async def async_select_dropdown_option(self, selector: str, value: str):
        """Select an option from a dropdown."""
        if not self.page:
            await self.async_setup_browser()
        await self.page.select_option(selector, value)
        await self.page.wait_for_timeout(100)

    def select_dropdown_option(self, selector: str, value: str):
        """Synchronous wrapper for selecting dropdown options"""
        return self.loop.run_until_complete(self.async_select_dropdown_option(selector, value))

    async def async_submit_form_and_wait(self, form_selector: str = "form"):
        """Submit a form and wait for the response."""
        if not self.page:
            await self.async_setup_browser()
        await self.page.click(f'{form_selector} button[type="submit"]')
        await self.page.wait_for_load_state("networkidle")

    def submit_form_and_wait(self, form_selector: str = "form"):
        """Synchronous wrapper for form submission"""
        return self.loop.run_until_complete(self.async_submit_form_and_wait(form_selector))

    async def async_assert_form_error(self, message: str):
        """Assert that a form error message is displayed."""
        if not self.page:
            await self.async_setup_browser()
        error_locator = self.page.locator(f'text="{message}"')
        is_visible = await error_locator.is_visible()
        assert is_visible, f"Form error '{message}' not found"

    def assert_form_error(self, message: str):
        """Synchronous wrapper for asserting form errors"""
        return self.loop.run_until_complete(self.async_assert_form_error(message))

    async def async_assert_success_message(self, message: str):
        """Assert that a success message is displayed."""
        if not self.page:
            await self.async_setup_browser()
        success_locator = self.page.locator(f'text="{message}"')
        is_visible = await success_locator.is_visible()
        assert is_visible, f"Success message '{message}' not found"

    def assert_success_message(self, message: str):
        """Synchronous wrapper for asserting success messages"""
        return self.loop.run_until_complete(self.async_assert_success_message(message))


class PlaywrightNavigationTestBase(PlaywrightTestBase):
    """Base class for testing navigation and workflow."""

    async def async_click_link_and_wait(self, selector: str):
        """Click a link and wait for navigation."""
        if not self.page:
            await self.async_setup_browser()
        await self.page.click(selector)
        await self.page.wait_for_load_state("networkidle")

    def click_link_and_wait(self, selector: str):
        """Synchronous wrapper for clicking links"""
        return self.loop.run_until_complete(self.async_click_link_and_wait(selector))

    async def async_assert_page_title(self, expected_title: str):
        """Assert the page title matches expected."""
        if not self.page:
            await self.async_setup_browser()
        actual_title = await self.page.title()
        assert actual_title == expected_title, f"Expected title '{expected_title}', got '{actual_title}'"

    def assert_page_title(self, expected_title: str):
        """Synchronous wrapper for asserting page title"""
        return self.loop.run_until_complete(self.async_assert_page_title(expected_title))

    async def async_assert_url_contains(self, url_fragment: str):
        """Assert the current URL contains the given fragment."""
        if not self.page:
            await self.async_setup_browser()
        current_url = self.page.url
        assert url_fragment in current_url, f"URL fragment '{url_fragment}' not found in '{current_url}'"

    def assert_url_contains(self, url_fragment: str):
        """Synchronous wrapper for asserting URL contents"""
        return self.loop.run_until_complete(self.async_assert_url_contains(url_fragment))

    async def async_navigate_to_section(self, section_name: str):
        """Navigate to a specific section via menu/navigation."""
        if not self.page:
            await self.async_setup_browser()
        nav_link = self.page.locator(f'a:has-text("{section_name}")')
        is_visible = await nav_link.is_visible()
        if is_visible:
            await nav_link.click()
            await self.page.wait_for_load_state("networkidle")
        else:
            raise AssertionError(f"Navigation link '{section_name}' not found")

    def navigate_to_section(self, section_name: str):
        """Synchronous wrapper for section navigation"""
        return self.loop.run_until_complete(self.async_navigate_to_section(section_name))


class PlaywrightLiveServerTestBase(TransactionTestCase):
    """
    Playwright test base that bypasses StaticLiveServerTestCase hanging issues.
    Uses TransactionTestCase for database isolation and assumes server is already running.
    """

    # Server configuration - assumes Django server is already running
    # This avoids the hanging issue with StaticLiveServerTestCase in CI
    server_port = 8001
    
    @classmethod
    def setUpClass(cls):
        import sys
        print(f"[PLAYWRIGHT-CLASS-SETUP] Starting setUpClass for {cls.__name__}", flush=True)
        sys.stdout.flush()
        
        # Since we're not using StaticLiveServerTestCase, we don't need to call super().setUpClass()
        # which is where the hanging occurs
        print("[PLAYWRIGHT-CLASS-SETUP] Skipping StaticLiveServerTestCase setup to avoid hang", flush=True)
        
        # Set the host for container access
        cls.host = "0.0.0.0"
        
        # CRITICAL: Set allowed hosts for Django's server
        from django.conf import settings
        settings.ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'web', '0.0.0.0']

        # Run the async setup
        import asyncio

        print("[PLAYWRIGHT-CLASS-SETUP] Running async_class_setup...")
        try:
            asyncio.run(cls.async_class_setup())
            print("[PLAYWRIGHT-CLASS-SETUP] async_class_setup complete")
        except Exception as e:
            print(f"[PLAYWRIGHT-CLASS-SETUP] ERROR in async_class_setup: {e}")
            raise

    @classmethod
    async def async_class_setup(cls):
        """Async setup for Playwright - called from setUpClass"""
        print("[SETUP] Initializing Playwright with Async API...")

        # Initialize Playwright in async mode
        cls.playwright = await async_playwright().start()
        print("[OK] Playwright async API initialized successfully")

        # Connect to Playwright server running in playwright-server container
        playwright_server_endpoint = os.environ.get(
            "PW_TEST_CONNECT_WS_ENDPOINT", "ws://playwright-server:3000/"
        )
        
        print(f"[CONNECT] Connecting to Playwright server at {playwright_server_endpoint}")
        
        print(f"[DEBUG] CI env var: {os.environ.get('CI')}")
        print(f"[DEBUG] Comparing endpoint: {playwright_server_endpoint} == ws://localhost:3000/")
        
        try:
            # In CI, launch Chrome browser directly instead of connecting to server
            if os.environ.get("CI") == "true":
                print("[CI] Detected CI environment, launching Chrome browser directly")
                print("[CI] Launching Chromium (Chrome) with special CI flags...")
                cls.browser = await cls.playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                )
                print("[OK] Chrome browser launched successfully")
            else:
                # Not in CI, connect to the Playwright server
                cls.browser = await cls.playwright.chromium.connect(playwright_server_endpoint)
                print("[OK] Successfully connected to Playwright server")
            
            # Test the connection by getting browser version
            try:
                browser_version = cls.browser.version
                print(f"[DEBUG] Connected browser version: {browser_version}")
            except Exception as version_error:
                print(f"[WARN] Could not get browser version: {version_error}")
                
        except Exception as connection_error:
            print(f"[ERROR] Playwright server/browser setup failed: {connection_error}")
            print(f"[DEBUG] Attempted endpoint: {playwright_server_endpoint}")
            raise Exception(f"Failed to setup Playwright browser: {connection_error}")

        # Health checks
        try:
            manager = ContainerProcessManager()
            debugger = PlaywrightContainerDebugger(None)

            print("[HEALTH] Performing container health checks...")
            manager.cleanup_chrome_processes()
            manager.monitor_resources()
            debugger.health_check_before_test()
            print("[OK] Container health checks completed")
        except Exception as e:
            print(f"[WARN]  Health check error: {e}")

    @classmethod
    async def async_class_teardown(cls):
        """Async teardown for Playwright - called from tearDownClass"""
        import asyncio
        
        # Proper teardown sequence per official Playwright documentation
        try:
            if hasattr(cls, "browser") and cls.browser:
                print("[TEARDOWN] Closing browser connection...")
                # Add delay before browser.close() to prevent CancelledError
                await asyncio.sleep(0.1)
                await cls.browser.close()
                print("[OK] Browser closed successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Browser close cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Browser cleanup failed: {e}")
            
        try:
            if hasattr(cls, "playwright") and cls.playwright:
                print("[TEARDOWN] Stopping Playwright...")
                await cls.playwright.stop()
                print("[OK] Playwright stopped successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Playwright stop cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Playwright cleanup failed: {e}")

    @classmethod
    def tearDownClass(cls):
        # Run async cleanup
        import asyncio

        try:
            asyncio.run(cls.async_class_teardown())
        except Exception as e:
            print(f"Warning: Teardown failed: {e}")
            # Continue with teardown even if cleanup fails
        # Don't call super() since we're not using StaticLiveServerTestCase

    def setUp(self):
        print(f"[PLAYWRIGHT-BASE-SETUP] Starting setUp for {self.__class__.__name__}", flush=True)
        print(f"[PLAYWRIGHT-BASE-SETUP] Using TransactionTestCase setUp (no server startup)", flush=True)
        import sys
        sys.stdout.flush()
        
        # Call TransactionTestCase setUp instead of StaticLiveServerTestCase
        # This avoids the hanging server startup
        try:
            super().setUp()
            print("[PLAYWRIGHT-BASE-SETUP] Parent setUp complete", flush=True)
            sys.stdout.flush()
        except Exception as e:
            print(f"[PLAYWRIGHT-BASE-SETUP] ERROR in parent setUp: {e}", flush=True)
            raise

        print("[PLAYWRIGHT-BASE-SETUP] Point 1: After parent setUp", flush=True)
        sys.stdout.flush()
        
        # Create a new browser context and page for each test
        print("[PLAYWRIGHT-BASE-SETUP] Point 2: About to import asyncio...", flush=True)
        sys.stdout.flush()
        
        import asyncio

        print("[PLAYWRIGHT-BASE-SETUP] Point 3: asyncio imported successfully", flush=True)
        sys.stdout.flush()
        
        print("[PLAYWRIGHT-BASE-SETUP] Point 4: Setting up event loop...", flush=True)
        sys.stdout.flush()
        
        # Python 3.11+ compatible event loop handling
        # Official Python pattern for handling "no current event loop" RuntimeError
        try:
            print("[PLAYWRIGHT-BASE-SETUP] Point 5: Attempting to get event loop...", flush=True)
            sys.stdout.flush()
            self.loop = asyncio.get_event_loop()
            print("[PLAYWRIGHT-BASE-SETUP] Point 6: Got existing event loop", flush=True)
            sys.stdout.flush()
        except RuntimeError as ex:
            print(f"[PLAYWRIGHT-BASE-SETUP] Point 7: RuntimeError: {ex}", flush=True)
            sys.stdout.flush()
            if "There is no current event loop in thread" in str(ex):
                # Create and set new event loop as recommended by Python docs
                print("[PLAYWRIGHT-BASE-SETUP] Point 8: Creating new event loop", flush=True)
                sys.stdout.flush()
                self.loop = asyncio.new_event_loop()
                print("[PLAYWRIGHT-BASE-SETUP] Point 9: Setting event loop", flush=True)
                sys.stdout.flush()
                asyncio.set_event_loop(self.loop)
                print("[PLAYWRIGHT-BASE-SETUP] Point 10: Event loop set", flush=True)
                sys.stdout.flush()
            else:
                raise
        
        print("[PLAYWRIGHT-BASE-SETUP] Point 11: Event loop setup complete", flush=True)
        sys.stdout.flush()
        
        print("[PLAYWRIGHT-BASE-SETUP] Point 12: About to run async_setup_page...", flush=True)
        sys.stdout.flush()
        try:
            print("[PLAYWRIGHT-BASE-SETUP] Point 13: Calling run_until_complete...", flush=True)
            sys.stdout.flush()
            self.loop.run_until_complete(self.async_setup_page())
            print("[PLAYWRIGHT-BASE-SETUP] Point 14: async_setup_page complete", flush=True)
            sys.stdout.flush()
        except Exception as e:
            print(f"[PLAYWRIGHT-BASE-SETUP] Point 15: ERROR in async_setup_page: {e}", flush=True)
            sys.stdout.flush()
            raise
        
        print("[PLAYWRIGHT-BASE-SETUP] Point 16: setUp fully complete", flush=True)
        sys.stdout.flush()

    async def async_setup_page(self):
        """Create a new page for the test"""
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A1: Starting async_setup_page", flush=True)
        import sys
        sys.stdout.flush()
        
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A2: Checking browser instance...", flush=True)
        print(f"[PLAYWRIGHT-ASYNC-SETUP] Has browser attr: {hasattr(self, 'browser')}", flush=True)
        print(f"[PLAYWRIGHT-ASYNC-SETUP] Has class browser attr: {hasattr(self.__class__, 'browser')}", flush=True)
        sys.stdout.flush()
        
        if not hasattr(self.__class__, 'browser') or not self.__class__.browser:
            print("[PLAYWRIGHT-ASYNC-SETUP] ERROR: No browser instance available on class!", flush=True)
            raise Exception("Browser not initialized. Check class setup.")
        
        # Use class browser instance
        browser = self.__class__.browser
        
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A3: Browser instance found", flush=True)
        print(f"[PLAYWRIGHT-ASYNC-SETUP] Browser type: {type(browser)}", flush=True)
        print(f"[PLAYWRIGHT-ASYNC-SETUP] Browser is_connected: {browser.is_connected() if hasattr(browser, 'is_connected') else 'N/A'}", flush=True)
        
        # Test if browser is still responsive
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A3.1: Testing browser responsiveness...", flush=True)
        try:
            # Try to get browser version as a simple connectivity test
            if hasattr(browser, 'version'):
                print(f"[PLAYWRIGHT-ASYNC-SETUP] Browser version: {browser.version}", flush=True)
        except Exception as e:
            print(f"[PLAYWRIGHT-ASYNC-SETUP] WARNING: Browser version check failed: {e}", flush=True)
        
        sys.stdout.flush()
        
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A4: Creating new browser context...", flush=True)
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A4.1: About to call browser.new_context()", flush=True)
        import os
        print(f"[PLAYWRIGHT-ASYNC-SETUP] Playwright server endpoint: {os.environ.get('PW_TEST_CONNECT_WS_ENDPOINT', 'Not set')}", flush=True)
        sys.stdout.flush()
        try:
            # Add timeout to prevent infinite hang
            import asyncio
            print("[PLAYWRIGHT-ASYNC-SETUP] Point A4.2: Creating context with 30s timeout...", flush=True)
            print("[PLAYWRIGHT-ASYNC-SETUP] Trying minimal context creation first...", flush=True)
            sys.stdout.flush()
            
            # Try creating context with minimal options
            try:
                # In CI environments, browser.newContext() can hang due to GPU issues
                # Try with a very short timeout first
                self.context = await asyncio.wait_for(
                    browser.new_context(),  # No viewport or other options
                    timeout=5.0
                )
                print("[PLAYWRIGHT-ASYNC-SETUP] Point A5: Minimal context created successfully", flush=True)
                # Now try to set viewport
                await self.context.set_viewport_size({"width": 1280, "height": 720})
                print("[PLAYWRIGHT-ASYNC-SETUP] Viewport size set", flush=True)
            except asyncio.TimeoutError:
                print("[PLAYWRIGHT-ASYNC-SETUP] Minimal context also timed out", flush=True)
                # Try using a page directly from browser
                print("[PLAYWRIGHT-ASYNC-SETUP] Attempting to get default context...", flush=True)
                contexts = browser.contexts
                if contexts:
                    print(f"[PLAYWRIGHT-ASYNC-SETUP] Found {len(contexts)} existing contexts", flush=True)
                    self.context = contexts[0]
                else:
                    # Last resort: try launching a new browser instance
                    print("[PLAYWRIGHT-ASYNC-SETUP] No contexts available, trying to launch new browser", flush=True)
                    try:
                        # Get playwright instance from class
                        playwright = self.__class__.playwright
                        print("[PLAYWRIGHT-ASYNC-SETUP] Launching new browser instance...", flush=True)
                        # Launch Chrome with CI-specific flags
                        print("[PLAYWRIGHT-ASYNC-SETUP] Launching Chrome browser with CI flags...", flush=True)
                        new_browser = await playwright.chromium.launch(
                            headless=True,
                            args=[
                                '--no-sandbox',
                                '--disable-setuid-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-gpu',
                                '--disable-web-security',
                                '--disable-features=IsolateOrigins,site-per-process'
                            ]
                        )
                        print("[PLAYWRIGHT-ASYNC-SETUP] New browser launched, creating context...", flush=True)
                        self.context = await new_browser.new_context(
                            viewport={"width": 1280, "height": 720}
                        )
                        print("[PLAYWRIGHT-ASYNC-SETUP] Context created on new browser", flush=True)
                        # Store the new browser instance
                        self._local_browser = new_browser
                    except Exception as launch_error:
                        print(f"[PLAYWRIGHT-ASYNC-SETUP] Failed to launch new browser: {launch_error}", flush=True)
                        raise Exception("No contexts available and cannot create new one")
            
            sys.stdout.flush()
        except asyncio.TimeoutError:
            print("[PLAYWRIGHT-ASYNC-SETUP] ERROR: Timeout creating context after 30s", flush=True)
            print("[PLAYWRIGHT-ASYNC-SETUP] This suggests the Playwright server connection is broken", flush=True)
            sys.stdout.flush()
            raise Exception("Timeout creating browser context - Playwright server may be unreachable")
        except Exception as e:
            print(f"[PLAYWRIGHT-ASYNC-SETUP] ERROR creating context: {e}", flush=True)
            print(f"[PLAYWRIGHT-ASYNC-SETUP] Error type: {type(e).__name__}", flush=True)
            sys.stdout.flush()
            raise
        
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A6: Creating new page...", flush=True)
        sys.stdout.flush()
        try:
            self.page = await self.context.new_page()
            print("[PLAYWRIGHT-ASYNC-SETUP] Point A7: Page created", flush=True)
            sys.stdout.flush()
        except Exception as e:
            print(f"[PLAYWRIGHT-ASYNC-SETUP] ERROR creating page: {e}", flush=True)
            sys.stdout.flush()
            raise

        print("[PLAYWRIGHT-ASYNC-SETUP] Point A8: Setting up screenshot directory...", flush=True)
        sys.stdout.flush()
        
        # Set up screenshot directory
        from pathlib import Path
        screenshot_dir = Path("tests/screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        self.screenshot_dir = screenshot_dir
        
        print("[PLAYWRIGHT-ASYNC-SETUP] Point A9: async_setup_page complete", flush=True)
        sys.stdout.flush()

    def tearDown(self):
        # Clean up the page and context
        import asyncio

        if hasattr(self, "context") and self.context:
            asyncio.run(self.async_cleanup_page())
        super().tearDown()

    async def async_cleanup_page(self):
        """Clean up page and context"""
        import asyncio
        
        # Proper teardown sequence: page -> context -> local browser (if any)
        try:
            if hasattr(self, "page") and self.page:
                print("[TEARDOWN] Closing page...")
                await self.page.close()
                print("[OK] Page closed successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Page close cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Page cleanup failed: {e}")
            
        try:
            if hasattr(self, "context") and self.context:
                print("[TEARDOWN] Closing context...")
                await asyncio.sleep(0.1)  # Small delay before context close
                await self.context.close()
                print("[OK] Context closed successfully")
        except asyncio.exceptions.CancelledError:
            print("[WARN] Context close cancelled during teardown (expected)")
        except Exception as e:
            print(f"[WARN] Context cleanup failed: {e}")
            
        # Clean up local browser if we created one
        try:
            if hasattr(self, "_local_browser") and self._local_browser:
                print("[TEARDOWN] Closing local browser instance...")
                await self._local_browser.close()
                print("[OK] Local browser closed successfully")
        except Exception as e:
            print(f"[WARN] Local browser cleanup failed: {e}")

    async def async_navigate_to(self, url):
        """Navigate to a URL with error handling"""
        print(f"[NAV] Navigating to: {url}")
        try:
            response = await self.page.goto(url, wait_until="networkidle")
            if response:
                print(f"[NAV] Response status: {response.status}")
            return response
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            # Take screenshot on navigation failure
            await self.async_take_screenshot(f"navigation_failed_{self._testMethodName}")
            raise

    def navigate_to(self, url):
        """Synchronous wrapper for navigation"""
        return self.loop.run_until_complete(self.async_navigate_to(url))

    async def async_take_screenshot(self, name: str):
        """Take a screenshot with the given name"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        screenshot_path = self.screenshot_dir / filename

        try:
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"[SCREENSHOT] Saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            return None

    def take_screenshot(self, name: str):
        """Synchronous wrapper for taking screenshots"""
        return self.loop.run_until_complete(self.async_take_screenshot(name))

    @property
    def live_server_url(self):
        """Return URL for the already-running Django server"""
        # Assume Django server is already running on port 8001
        # This bypasses StaticLiveServerTestCase's server startup
        if os.environ.get('CI'):
            # In CI, Django should be running on the host
            return f"http://localhost:{self.server_port}"
        else:
            # Local development
            return f"http://127.0.0.1:{self.server_port}"
    
    @property
    def accessible_live_server_url(self):
        """URL accessible from the Playwright container in Docker environment"""
        # In Docker, use the web service name for inter-container communication
        if os.environ.get('PW_TEST_CONNECT_WS_ENDPOINT'):
            # We're in a containerized environment with separate playwright server
            return f"http://web:{self.server_port}"
        else:
            # Local development or same-container setup
            return self.live_server_url


# Common test data creation methods
class PlaywrightTestDataMixin:
    """Mixin providing common test data creation methods for Playwright tests"""

    def create_test_user(self, username="testuser", email="test@example.com"):
        """Create a test user"""
        return User.objects.create_user(
            username=username, email=email, password="testpass123"
        )

    def create_test_medico(self, user=None):
        """Create a test medico"""
        if not user:
            user = self.create_test_user()
        return Medico.objects.create(
            user=user,
            crm="123456",
            nome_completo=f"Dr. {user.username}",
            especialidade="Clínica Geral",
        )

    def create_test_clinica(self, medico=None):
        """Create a test clinica"""
        if not medico:
            medico = self.create_test_medico()
        return Clinica.objects.create(
            medico=medico,
            nome="Clínica Teste",
            endereco="Rua Teste, 123",
            telefone="(11) 99999-9999",
        )

    def create_test_paciente(self, medico=None):
        """Create a test paciente"""
        if not medico:
            medico = self.create_test_medico()
        
        generator = UniqueDataGenerator()
        return Paciente.objects.create(
            medico=medico,
            nome_completo="Paciente Teste",
            cpf=generator.generate_valid_cpf(),
            data_nascimento="1990-01-01",
            telefone="(11) 88888-8888",
        )

    def create_test_processo(self, paciente=None, medico=None):
        """Create a test processo"""
        if not paciente:
            paciente = self.create_test_paciente(medico)
        return Processo.objects.create(
            paciente=paciente,
            data_inicio=datetime.date.today(),
            observacoes="Processo de teste",
        )