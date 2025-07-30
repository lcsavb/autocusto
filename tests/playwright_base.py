import os
import tempfile
from pathlib import Path
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, TransactionTestCase
from django.db import transaction
from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from pacientes.models import Paciente
from processos.models import Doenca, Medicamento, Processo
import datetime
from tests.test_base import UniqueDataGenerator

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
    host = '0.0.0.0'
    
    @property
    def live_server_url(self):
        """Override to use container network-accessible URL."""
        # Return URL that playwright-browsers container can access
        # Use the web service name instead of localhost
        return f"http://web:{self.server_thread.port}"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Initialize Playwright in sync mode
        cls.playwright = sync_playwright().start()
        
        print("🔧 Initializing Playwright browser...")
        
        # Connect to remote Chromium browser in playwright-browsers container
        remote_browser_endpoint = os.environ.get('PLAYWRIGHT_CHROMIUM_WS_ENDPOINT', 'http://playwright-browsers:9222')
        
        try:
            print(f"🔗 Connecting to remote Chrome at {remote_browser_endpoint}")
            # Use CDP connection to remote Chrome instance
            cls.browser = cls.playwright.chromium.connect_over_cdp(remote_browser_endpoint)
            print("✅ Successfully connected to remote Chrome browser")
        except Exception as e:
            print(f"❌ Remote browser connection failed: {e}")
            # For debugging, let's see what's available at the endpoint
            try:
                import subprocess
                result = subprocess.run(['curl', '-s', f'{remote_browser_endpoint}/json'], 
                                      capture_output=True, text=True, timeout=5)
                print(f"🔍 DEBUG: Curl response: {result.stdout[:200]}...")
            except Exception as debug_e:
                print(f"🔍 DEBUG: Could not test endpoint: {debug_e}")
            raise Exception(f"Failed to connect to remote Chrome: {e}")
    
    @classmethod
    def tearDownClass(cls):
        # Ensure proper cleanup to prevent zombie processes
        try:
            if hasattr(cls, 'browser') and cls.browser:
                cls.browser.close()
        except Exception as e:
            print(f"Warning: Browser cleanup failed: {e}")
        try:
            if hasattr(cls, 'playwright') and cls.playwright:
                cls.playwright.stop()
        except Exception as e:
            print(f"Warning: Playwright cleanup failed: {e}")
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        
        # Initialize data generator
        self.data_generator = UniqueDataGenerator()
        
        # Initialize container debugger
        self.debugger = PlaywrightContainerDebugger(self)
        self.debugger.health_check_before_test()
        
        # Health check: ensure browser is still responsive
        try:
            if not self.browser.is_connected():
                raise Exception("Browser is not connected")
        except Exception as e:
            print(f"⚠️  DEBUG: Browser health check failed: {e}")
            # Clean up processes and try to recover
            ContainerProcessManager.cleanup_chrome_processes()
            try:
                if hasattr(self.__class__, 'browser'):
                    self.__class__.browser.close()
            except:
                pass
            # This will force browser recreation in next test
            
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            # Add additional container-friendly context options
            ignore_https_errors=True,
            bypass_csp=True
        )
        self.page = self.context.new_page()
        
        # Set reasonable timeouts for container environment
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        # Setup screenshot directory
        self.screenshot_dir = Path('test_screenshots')
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        if hasattr(self, 'context'):
            self.context.close()
        super().tearDown()
    
    def take_screenshot(self, name: str):
        """Take a screenshot with the given name."""
        screenshot_path = self.screenshot_dir / f"{self.__class__.__name__}_{name}.png"
        self.page.screenshot(path=str(screenshot_path))
        return screenshot_path
    
    def wait_for_page_load(self):
        """Wait for the page to fully load."""
        self.page.wait_for_load_state('networkidle')
    
    def login_user(self, email: str, password: str):
        """Helper method to log in a user."""
        # Connect to localhost since tests run in same container as Django
        server_url = "http://localhost:8001"
        print(f"🔍 Connecting to Django server: {server_url}")
        
        try:
            self.page.goto(f"{server_url}/", timeout=30000, wait_until='networkidle')
            print("✅ Successfully connected to Django server")
        except Exception as e:
            print(f"❌ Failed to connect to Django server: {e}")
            # Take screenshot for debugging
            try:
                self.take_screenshot("connection_failed")
            except:
                pass
            raise
            
        self.page.wait_for_load_state('domcontentloaded')
        
        # Fill login form (on home page)
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="password"]', password)
        
        # Click login submit button (look for specific login form button)
        login_button = self.page.locator('button[type="submit"]').first
        login_button.click()
        
        # Wait for navigation after login
        self.page.wait_for_load_state('domcontentloaded')
    
    # Common test data creation methods
    def create_test_user(self, email="test@example.com", password="testpass123"):
        """Create a test user with the given credentials."""
        return User.objects.create_user(
            email=email,
            password=password
        )
    
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
            status_aprovacao_medico=True
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
            telefone_clinica="1134567890"
        )
    
    def create_test_emissor(self, medico=None, clinica=None):
        """Create a test emissor (doctor-clinic relationship)."""
        if not medico:
            medico = self.create_test_medico()
        if not clinica:
            clinica = self.create_test_clinica()
            
        return Emissor.objects.create(
            medico=medico,
            clinica=clinica
        )
    
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
            telefone_paciente="1198765432"
        )
    
    def create_test_doenca(self, nome="Test Disease", codigo="T01"):
        """Create a test disease."""
        return Doenca.objects.create(
            nome_doenca=nome,
            codigo_doenca=codigo
        )
    
    def create_test_medicamento(self, nome="Test Medicine"):
        """Create a test medication."""
        return Medicamento.objects.create(
            nome_medicamento=nome,
            forma_farmaceutica="Comprimido",
            concentracao="100mg",
            laboratorio="Test Lab"
        )
    
    def create_complete_test_setup(self):
        """Create a complete test setup with user, medico, clinic, and emissor."""
        user = self.create_test_user()
        medico = self.create_test_medico(user=user)
        clinica = self.create_test_clinica()
        emissor = self.create_test_emissor(medico=medico, clinica=clinica)
        return {
            'user': user,
            'medico': medico,
            'clinica': clinica,
            'emissor': emissor
        }


class PlaywrightSecurityTestBase(PlaywrightTestBase):
    """Base class specifically for security-related frontend tests."""
    
    def setUp(self):
        super().setUp()
        # Create test users for security testing
        self.user1 = self.create_test_user(email='user1@test.com')
        self.user2 = self.create_test_user(email='user2@test.com')
    
    def assert_redirected_to_login(self):
        """Assert that the page redirected to login."""
        self.assertIn('/login/', self.page.url)
    
    def assert_access_denied(self):
        """Assert that access was denied (either redirect to login or 403)."""
        current_url = self.page.url
        # Check if redirected to login or got access denied
        self.assertTrue(
            '/login/' in current_url or self.page.locator('text=Access Denied').is_visible(),
            f"Expected access denied but got URL: {current_url}"
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
    
    def submit_form_and_wait(self, form_selector: str = 'form'):
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
        self.assertTrue(success_locator.is_visible(), f"Success message '{message}' not found")


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
        cls.host = '0.0.0.0'
        super().setUpClass()
        
        print("🔧 Initializing Playwright browser...")
        cls.playwright = sync_playwright().start()
        
        # Connect to remote Chromium browser in playwright-browsers container
        remote_browser_endpoint = os.environ.get('PLAYWRIGHT_CHROMIUM_WS_ENDPOINT', 'http://172.18.0.2:9222')
        try:
            print(f"🔗 Connecting to remote Chrome at {remote_browser_endpoint}")
            cls.browser = cls.playwright.chromium.connect_over_cdp(remote_browser_endpoint)
            print("✅ Successfully connected to remote Chrome browser")
        except Exception as e:
            print(f"❌ Failed to connect to remote browser: {e}")
            # Fallback to local browser
            cls.browser = cls.playwright.chromium.launch(headless=True)
            print("⚠️  Fallback: Using local browser")
        
        # Health checks
        try:
            manager = ContainerProcessManager()
            debugger = PlaywrightContainerDebugger(None)
            
            print("🏥 Performing container health checks...")
            manager.cleanup_chrome_processes()
            manager.monitor_resources()
            debugger.health_check_before_test()
            print("✅ Container health checks completed")
        except Exception as e:
            print(f"⚠️  Health check error: {e}")
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browser'):
            cls.browser.close()
        if hasattr(cls, 'playwright'):
            cls.playwright.stop()
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
    
    def tearDown(self):
        if hasattr(self, 'context'):
            self.context.close()
        super().tearDown()
    
    @property
    def accessible_live_server_url(self):
        """Get live server URL accessible from remote browser container."""
        # Replace localhost/127.0.0.1/0.0.0.0 with web container hostname
        if hasattr(self, 'live_server_url'):
            url = self.live_server_url
            # Replace various localhost forms with 'web'
            return url.replace('localhost', 'web').replace('127.0.0.1', 'web').replace('0.0.0.0', 'web')
        return "http://web:8001"  # Fallback
    
    def wait_for_page_load(self, timeout=30000):
        """Wait for page to finish loading."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            print(f"⚠️  Page load timeout: {e}")
    
    def take_screenshot(self, name):
        """Take a screenshot with the given name."""
        screenshot_dir = Path("test_screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        
        test_class = self.__class__.__name__
        screenshot_path = screenshot_dir / f"{test_class}_{name}.png"
        
        self.page.screenshot(path=str(screenshot_path))
        print(f"📸 Screenshot saved: {screenshot_path}")
    
    def authenticate_via_browser(self, email, password):
        """
        Perform browser-based authentication using Playwright.
        This ensures authentication works with the live server.
        """
        print(f"🔐 DEBUG: Authenticating {email} via browser")
        
        # Navigate to home page using accessible URL
        server_url = self.accessible_live_server_url
        print(f"🔍 DEBUG: Navigating to {server_url}")
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
        login_form = self.page.locator('form').filter(has=self.page.locator('input[name="username"]'))
        login_button = login_form.locator('button[type="submit"]')
        
        self.take_screenshot("before_login")
        login_button.click()
        self.wait_for_page_load()
        
        # Verify authentication success
        login_form_after = self.page.locator('input[name="username"]')
        if login_form_after.is_visible():
            self.take_screenshot("login_failed")
            # Check for error messages
            error_msgs = self.page.locator('.alert, .error, .message').all()
            error_text = ""
            for msg in error_msgs:
                if msg.is_visible():
                    error_text += msg.inner_text() + " "
            
            self.fail(f"Browser authentication failed for {email}. Error: {error_text}")
        
        print("✅ DEBUG: Browser authentication successful")
        self.take_screenshot("login_successful")