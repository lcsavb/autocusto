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
                browser_version = cls.browser.version()
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
        try:
            if hasattr(cls, "browser") and cls.browser:
                await cls.browser.close()
        except Exception as e:
            print(f"Warning: Browser cleanup failed: {e}")
        try:
            if hasattr(cls, "playwright") and cls.playwright:
                await cls.playwright.stop()
        except Exception as e:
            print(f"Warning: Playwright cleanup failed: {e}")

    @classmethod
    def tearDownClass(cls):
        # Run async cleanup
        import asyncio

        asyncio.run(cls.async_class_teardown())
        super().tearDownClass()

    def setUp(self):
        super().setUp()

        # Initialize data generator
        self.data_generator = UniqueDataGenerator()

        # Initialize container debugger
        self.debugger = PlaywrightContainerDebugger(self)
        self.debugger.health_check_before_test()

        # Create context and page using async operations
        import asyncio

        asyncio.run(self.async_setup())

        # Setup screenshot directory
        self.screenshot_dir = Path("tests/screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    async def async_setup(self):
        """Async setup for browser context and page"""
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            bypass_csp=True,
        )
        self.page = await self.context.new_page()

        # Set reasonable timeouts for container environment
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)

    def tearDown(self):
        if hasattr(self, "context"):
            import asyncio

            asyncio.run(self.context.close())
        super().tearDown()

    def take_screenshot(self, name: str):
        """Take a screenshot with the given name."""
        screenshot_path = self.screenshot_dir / f"{self.__class__.__name__}_{name}.png"
        self.page.screenshot(path=str(screenshot_path))
        return screenshot_path

    def wait_for_page_load(self):
        """Wait for the page to fully load."""
        self.page.wait_for_load_state("networkidle")

    def login_user(self, email: str, password: str):
        """Helper method to log in a user."""
        # Use the proper live server URL for container communication
        server_url = self.live_server_url
        print(f"[DEBUG] Connecting to Django server: {server_url}")

        try:
            self.page.goto(f"{server_url}/", timeout=30000, wait_until="networkidle")
            print("[OK] Successfully connected to Django server")
        except Exception as e:
            print(f"[ERROR] Failed to connect to Django server: {e}")
            # Take screenshot for debugging
            try:
                self.take_screenshot("connection_failed")
            except BaseException:
                pass
            raise

        self.page.wait_for_load_state("domcontentloaded")

        # Fill login form (on home page)
        # The form uses 'username' field for email
        self.page.fill('input[name="username"]', email)
        self.page.fill('input[name="password"]', password)

        # Click login submit button (look for specific login form button)
        login_button = self.page.locator('button[type="submit"]').first
        login_button.click()

        # Wait for navigation and full page reload after login
        self.page.wait_for_load_state("networkidle")

        # Give the page a moment to update the UI after successful login
        import time

        time.sleep(1)

    # Common test data creation methods
    def create_test_user(
        self, email="test@example.com", password="testpass123", is_medico=False
    ):
        """Create a test user with the given credentials."""
        user = User.objects.create_user(email=email, password=password)
        if is_medico:
            user.is_medico = True
            user.save()
        return user

    def create_test_medico(self, user=None, crm="123456", cns="111111111111111"):
        """Create a test medical professional."""
        if not user:
            user = self.create_test_user()

        return Medico.objects.create(
            usuario=user,
            nome_medico="Dr. Test Silva",
            crm_medico=crm,
            cns_medico=cns,
            uf_medico="SP",
            cidade_medico="São Paulo",
            status_aprovacao_medico=True,
        )

    def create_test_clinica(self, cnes="1234567"):
        """Create a test clinic."""
        return Clinica.objects.create(
            nome_clinica="Test Clinic",
            cnpj_clinica="12345678901234",
            cnes_clinica=cnes,
            endereco_clinica="Test Street, 123",
            cidade_clinica="São Paulo",
            uf_clinica="SP",
            cep_clinica="12345678",
            telefone_clinica="1134567890",
        )

    def create_test_emissor(self, medico=None, clinica=None):
        """Create a test emissor (doctor-clinic relationship)."""
        if not medico:
            medico = self.create_test_medico()
        if not clinica:
            clinica = self.create_test_clinica()

        return Emissor.objects.create(medico=medico, clinica=clinica)

    def create_test_paciente(self, cpf="12345678901"):
        """Create a test patient."""
        return Paciente.objects.create(
            nome_paciente="Test Patient",
            cpf_paciente=cpf,
            data_nascimento_paciente=datetime.date(1990, 1, 1),
            sexo_paciente="M",
            endereco_paciente="Test Address",
            cidade_paciente="São Paulo",
            uf_paciente="SP",
            cep_paciente="12345678",
            telefone_paciente="1198765432",
        )

    def create_test_doenca(self, nome="Test Disease", codigo="T01"):
        """Create a test disease."""
        return Doenca.objects.create(nome_doenca=nome, codigo_doenca=codigo)

    def create_test_medicamento(self, nome="Test Medicine"):
        """Create a test medication."""
        return Medicamento.objects.create(
            nome_medicamento=nome,
            forma_farmaceutica="Comprimido",
            concentracao="100mg",
            laboratorio="Test Lab",
        )

    def create_complete_test_setup(self):
        """Create a complete test setup with user, medico, clinic, and emissor."""
        user = self.create_test_user()
        medico = self.create_test_medico(user=user)
        clinica = self.create_test_clinica()
        emissor = self.create_test_emissor(medico=medico, clinica=clinica)
        return {"user": user, "medico": medico, "clinica": clinica, "emissor": emissor}


class PlaywrightSecurityTestBase(PlaywrightTestBase):
    """Base class specifically for security-related frontend tests."""

    def setUp(self):
        super().setUp()
        # Create test users for security testing (must be medicos to login)
        self.user1 = self.create_test_user(
            email=self.data_generator.generate_unique_email(), is_medico=True
        )
        self.user2 = self.create_test_user(
            email=self.data_generator.generate_unique_email(), is_medico=True
        )

    def assert_redirected_to_login(self):
        """Assert that the page redirected to login."""
        self.assertIn("/login/", self.page.url)

    def assert_access_denied(self):
        """Assert that access was denied (either redirect to login or 403)."""
        current_url = self.page.url
        # Check if redirected to login or got access denied
        self.assertTrue(
            "/login/" in current_url
            or self.page.locator("text=Access Denied").is_visible(),
            f"Expected access denied but got URL: {current_url}",
        )


class PlaywrightFormTestBase(PlaywrightTestBase):
    """Base class for testing forms and complex interactions."""

    def fill_form_field(self, selector: str, value: str):
        """Fill a form field and wait for it to be updated."""
        self.page.fill(selector, value)
        self.page.wait_for_timeout(100)  # Small delay for form updates

    def select_dropdown_option(self, selector: str, value: str):
        """Select an option from a dropdown."""
        self.page.select_option(selector, value)
        self.page.wait_for_timeout(100)

    def submit_form_and_wait(self, form_selector: str = "form"):
        """Submit a form and wait for the response."""
        self.page.click(f'{form_selector} button[type="submit"]')
        self.wait_for_page_load()

    def assert_form_error(self, message: str):
        """Assert that a form error message is displayed."""
        error_locator = self.page.locator(f'text="{message}"')
        self.assertTrue(error_locator.is_visible(), f"Form error '{message}' not found")

    def assert_success_message(self, message: str):
        """Assert that a success message is displayed."""
        success_locator = self.page.locator(f'text="{message}"')
        self.assertTrue(
            success_locator.is_visible(), f"Success message '{message}' not found"
        )


class PlaywrightNavigationTestBase(PlaywrightTestBase):
    """Base class for testing navigation and workflow."""

    def click_link_and_wait(self, selector: str):
        """Click a link and wait for navigation."""
        self.page.click(selector)
        self.wait_for_page_load()

    def assert_page_title(self, expected_title: str):
        """Assert the page title matches expected."""
        actual_title = self.page.title()
        self.assertEqual(actual_title, expected_title)

    def assert_url_contains(self, url_fragment: str):
        """Assert the current URL contains the given fragment."""
        current_url = self.page.url
        self.assertIn(url_fragment, current_url)

    def navigate_to_section(self, section_name: str):
        """Navigate to a specific section via menu/navigation."""
        # This will be implemented based on your specific navigation structure
        nav_link = self.page.locator(f'a:has-text("{section_name}")')
        if nav_link.is_visible():
            nav_link.click()
            self.wait_for_page_load()
        else:
            raise AssertionError(f"Navigation link '{section_name}' not found")


class PlaywrightLiveServerTestBase(StaticLiveServerTestCase):
    """
    Playwright test base using StaticLiveServerTestCase for shared database state.
    This ensures the live server and test database share the same state,
    fixing authentication issues between Django test client and Playwright browser.
    """

    # Configure live server to be accessible from remote browser container
    @classmethod
    def setUpClass(cls):
        # Set the live server to bind to all interfaces for container access
        cls.host = "0.0.0.0"
        super().setUpClass()

        # Run the async setup
        import asyncio

        asyncio.run(cls.async_class_setup())

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
                browser_version = cls.browser.version()
                print(f"[DEBUG] Connected browser version: {browser_version}")

                if remote_browser_endpoint.startswith("ws://"):
                    # Direct WebSocket URL provided
                    cdp_endpoint = remote_browser_endpoint
                    print(
                        f"[CONNECT] Using provided WebSocket endpoint: {cdp_endpoint}"
                    )
                else:
                    # Discover the proper WebSocket URL from Chrome DevTools
                    # API
                    import aiohttp

                    base_url = remote_browser_endpoint.rstrip("/")

                    print(f"[DEBUG] Discovering WebSocket endpoint from {base_url}")
                    print(f"[DEBUG] Container networking - trying to reach: {base_url}")

                    async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as session:
                        # First, get browser version info to verify Chrome is
                        # running
                        print(
                            f"[DEBUG] Step 1: Testing version endpoint {base_url}/json/version"
                        )
                        try:
                            async with session.get(
                                f"{base_url}/json/version",
                                headers={"Host": "localhost"},
                            ) as response:
                                if response.status == 200:
                                    version_info = await response.json()
                                    print(
                                        f"[OK] Chrome DevTools responding: {version_info.get('Browser', 'Unknown')}"
                                    )
                                    print(f"[INFO] Full version info: {version_info}")
                                else:
                                    print(
                                        f"[WARN]  Version endpoint returned status {response.status}"
                                    )
                                    response_text = await response.text()
                                    print(
                                        f"[RESPONSE] Response body: {response_text[:200]}..."
                                    )
                        except Exception as e:
                            print(f"[ERROR] Version check failed: {e}")
                            print(f"[DEBUG] Error type: {type(e).__name__}")

                        # Get browser-level WebSocket URL from /json/version endpoint
                        print(
                            f"[DEBUG] Step 2: Getting browser WebSocket URL from {base_url}/json/version"
                        )
                        try:
                            async with session.get(
                                f"{base_url}/json/version", headers={"Host": "localhost"}
                            ) as response:
                                if response.status == 200:
                                    version_info = await response.json()
                                    ws_url = version_info.get("webSocketDebuggerUrl")
                                    if ws_url:
                                        print(f"[OK] Found browser WebSocket URL: {ws_url}")
                                        
                                        # connect_over_cdp needs HTTP endpoint, not WebSocket URL
                                        # Use the base_url with container hostname adjustment
                                        if ":9223" in base_url:
                                            cdp_endpoint = base_url  # Already adjusted for proxy
                                        else:
                                            cdp_endpoint = base_url.replace(
                                                "localhost", "playwright-browsers"
                                            ).replace("127.0.0.1", "playwright-browsers")
                                        print(
                                            f"[CONNECT] Container-adjusted HTTP endpoint: {cdp_endpoint}"
                                        )
                                    else:
                                        print("[WARN] No webSocketDebuggerUrl in version info, trying fallback")
                                        raise Exception("No webSocketDebuggerUrl in version response")
                                else:
                                    print(f"[WARN] Version endpoint returned status {response.status}, trying fallback")
                                    raise Exception(f"Version endpoint failed: HTTP {response.status}")
                        except Exception as version_error:
                            print(f"[WARN] Version endpoint method failed: {version_error}")
                            print(f"[DEBUG] Step 2 Fallback: Testing targets endpoint {base_url}/json")
                            
                            # Fallback to targets discovery method
                            async with session.get(
                                f"{base_url}/json", headers={"Host": "localhost"}
                            ) as response:
                                print(
                                    f"[INFO] Targets endpoint status: {response.status}"
                                )
                                if response.status != 200:
                                    response_text = await response.text()
                                    print(f"[RESPONSE] Error response: {response_text}")
                                    raise Exception(
                                        f"Failed to get browser targets: HTTP {response.status}"
                                    )

                                targets = await response.json()
                                print(f"[DEBUG] Found {len(targets)} Chrome targets")
                                print(f"[INFO] All targets: {targets}")

                                # Look for the browser target (not page targets)
                                browser_target = None
                                for i, target in enumerate(targets):
                                    target_type = target.get("type", "unknown")
                                    target_url = target.get("url", "no-url")
                                    ws_url = target.get(
                                        "webSocketDebuggerUrl", "no-ws-url"
                                    )
                                    print(
                                        f"[DEBUG] Target {i}: type='{target_type}', url='{target_url}', ws='{ws_url}'"
                                    )

                                    if target_type == "browser":
                                        browser_target = target
                                        print(
                                            f"[OK] Found browser target: {browser_target}"
                                        )
                                        break

                                if not browser_target:
                                    # If no browser target, try to use the first available target
                                    if targets:
                                        browser_target = targets[0]
                                        print(
                                            f"[WARN] No browser target found, using first target: {browser_target}"
                                        )
                                    else:
                                        raise Exception("No Chrome targets available")

                                ws_url = browser_target.get("webSocketDebuggerUrl")
                                if not ws_url:
                                    print(
                                        f"[ERROR] No WebSocket URL in target: {browser_target}"
                                    )
                                    raise Exception(
                                        f"No WebSocket URL in target: {browser_target}"
                                    )

                                print(f"[DEBUG] Original WebSocket URL: {ws_url}")
                                # Replace localhost with container hostname for inter-container communication
                                if ":9223" in base_url:
                                    # If we're using the proxy fallback, adjust the WebSocket URL port too
                                    cdp_endpoint = ws_url.replace(
                                        "localhost:9222", "playwright-browsers:9223"
                                    ).replace("127.0.0.1:9222", "playwright-browsers:9223")
                                else:
                                    cdp_endpoint = ws_url.replace(
                                        "localhost", "playwright-browsers"
                                    ).replace("127.0.0.1", "playwright-browsers")
                                print(
                                    f"[CONNECT] Container-adjusted WebSocket endpoint: {cdp_endpoint}"
                                )
                        except Exception as e:
                            print(f"[ERROR] Failed to get targets: {e}")
                            print(f"[DEBUG] Error type: {type(e).__name__}")
                        raise  # Re-raise to try next endpoint

                print(f"[CONNECT] Step 3: Attempting CDP connection to: {cdp_endpoint}")
                print(
                    f"[DEBUG] Connection details - protocol: {cdp_endpoint.split('://')[0]}, host: {cdp_endpoint.split('://')[1].split('/')[0] if '://' in cdp_endpoint else 'unknown'}"
                )

                # EXTENSIVE CONNECTION DEBUGGING
                print("[DEBUG] === EXTENSIVE CDP CONNECTION DEBUG ===")
                
                # Test HTTP connectivity first
                try:
                    import aiohttp
                    base_host = cdp_endpoint.split('://')[1].split('/')[0] if '://' in cdp_endpoint else cdp_endpoint
                    if cdp_endpoint.startswith('ws://'):
                        # Extract base URL from WebSocket URL
                        if ':9223' in base_host:
                            test_url = f"http://{base_host.replace(':9223', ':9223')}/json/version"
                        else:
                            test_url = f"http://{base_host.replace(':9222', ':9222')}/json/version"
                    else:
                        test_url = f"{cdp_endpoint}/json/version"
                    
                    print(f"[DEBUG] Testing HTTP connectivity to: {test_url}")
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                        try:
                            async with session.get(test_url) as response:
                                if response.status == 200:
                                    version_info = await response.json()
                                    print(f"[DEBUG] ✅ HTTP connectivity works: {version_info.get('Browser', 'Unknown')}")
                                    actual_ws_url = version_info.get('webSocketDebuggerUrl', 'none')
                                    print(f"[DEBUG] Server reports WebSocket URL: {actual_ws_url}")
                                else:
                                    print(f"[DEBUG] ❌ HTTP connectivity failed: HTTP {response.status}")
                        except Exception as http_error:
                            print(f"[DEBUG] ❌ HTTP connectivity failed: {http_error}")
                            print(f"[DEBUG] Error type: {type(http_error).__name__}")
                except Exception as debug_error:
                    print(f"[DEBUG] Debug connectivity test failed: {debug_error}")
                
                # Test WebSocket connectivity
                print(f"[DEBUG] Testing WebSocket connectivity to: {cdp_endpoint}")
                
                try:
                    cls.browser = await cls.playwright.chromium.connect_over_cdp(
                        cdp_endpoint, timeout=30000  # 30 second timeout
                    )
                    print("[OK] Successfully connected to remote Chrome browser")
                    connection_successful = True

                    # Test the connection by getting browser version
                    try:
                        browser_version = cls.browser.version()
                        print(f"[DEBUG] Connected browser version: {browser_version}")
                    except Exception as version_error:
                        print(f"[WARN]  Could not get browser version: {version_error}")

                    break  # Connection successful, exit the retry loop

                except Exception as connection_error:
                    print(
                        f"[ERROR] CDP connection failed with error: {connection_error}"
                    )
                    print(
                        f"[DEBUG] Connection error type: {type(connection_error).__name__}"
                    )
                    print(f"[DEBUG] Attempted endpoint: {cdp_endpoint}")
                    last_error = connection_error
            except Exception as e:
                print(
                    f"[ERROR] Remote browser connection attempt {i + 1} failed: {e}"
                )
                last_error = e
                if i < len(fallback_endpoints) - 1:
                    print(f"[RETRY] Trying next endpoint...")
                    continue

        if not connection_successful:
            print(f"[ERROR] All connection attempts failed. Last error: {last_error}")
            raise Exception(
                f"Failed to connect to remote Chrome after {len(fallback_endpoints)} attempts: {last_error}"
            )

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
        try:
            if hasattr(cls, "browser") and cls.browser:
                await cls.browser.close()
        except Exception as e:
            print(f"Warning: Browser cleanup failed: {e}")
        try:
            if hasattr(cls, "playwright") and cls.playwright:
                await cls.playwright.stop()
        except Exception as e:
            print(f"Warning: Playwright cleanup failed: {e}")

    @classmethod
    def tearDownClass(cls):
        # Run async cleanup
        import asyncio

        asyncio.run(cls.async_class_teardown())
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        # Create context and page using async operations
        import asyncio

        asyncio.run(self.async_setup())

    async def async_setup(self):
        """Async setup for browser context and page"""
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    def tearDown(self):
        if hasattr(self, "context"):
            import asyncio

            asyncio.run(self.context.close())
        super().tearDown()

    @property
    def accessible_live_server_url(self):
        """Get live server URL accessible from remote browser container."""
        # Replace localhost/127.0.0.1/0.0.0.0 with web container hostname
        if hasattr(self, "live_server_url"):
            url = self.live_server_url
            # Replace various localhost forms with 'web'
            return (
                url.replace("localhost", "web")
                .replace("127.0.0.1", "web")
                .replace("0.0.0.0", "web")
            )
        return "http://web:8001"  # Fallback

    def wait_for_page_load(self, timeout=30000):
        """Wait for page to finish loading."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            print(f"[WARN]  Page load timeout: {e}")

    def take_screenshot(self, name):
        """Take a screenshot with the given name."""
        screenshot_dir = Path("tests/screenshots")
        screenshot_dir.mkdir(exist_ok=True)

        test_class = self.__class__.__name__
        screenshot_path = screenshot_dir / f"{test_class}_{name}.png"

        self.page.screenshot(path=str(screenshot_path))
        print(f"[SCREENSHOT] Screenshot saved: {screenshot_path}")

    def authenticate_via_browser(self, email, password):
        """
        Perform browser-based authentication using Playwright.
        This ensures authentication works with the live server.
        """
        print(f"[AUTH] DEBUG: Authenticating {email} via browser")

        # Navigate to home page using accessible URL
        server_url = self.accessible_live_server_url
        print(f"[DEBUG] DEBUG: Navigating to {server_url}")
        self.page.goto(server_url)
        self.wait_for_page_load()

        # Fill login form
        email_field = self.page.locator('input[name="username"]')
        password_field = self.page.locator('input[name="password"]')

        if not (email_field.is_visible() and password_field.is_visible()):
            self.take_screenshot("login_form_not_found")
            self.fail("Login form not visible on home page")

        email_field.fill(email)
        password_field.fill(password)

        # Click login button - be specific to avoid button ambiguity
        login_form = self.page.locator("form").filter(
            has=self.page.locator('input[name="username"]')
        )
        login_button = login_form.locator('button[type="submit"]')

        self.take_screenshot("before_login")
        login_button.click()
        self.wait_for_page_load()

        # Verify authentication success
        login_form_after = self.page.locator('input[name="username"]')
        if login_form_after.is_visible():
            self.take_screenshot("login_failed")
            # Check for error messages
            error_msgs = self.page.locator(".alert, .error, .message").all()
            error_text = ""
            for msg in error_msgs:
                if msg.is_visible():
                    error_text += msg.inner_text() + " "

            self.fail(f"Browser authentication failed for {email}. Error: {error_text}")

        print("[OK] DEBUG: Browser authentication successful")
        self.take_screenshot("login_successful")
