import os
import tempfile
from pathlib import Path
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

User = get_user_model()

# Fix for Django async context issues with Playwright
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


class PlaywrightTestBase(StaticLiveServerTestCase):
    """
    Base test class for Playwright tests in Django.
    Uses system Chrome instead of downloading Playwright browsers to save space.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Initialize Playwright in sync mode
        cls.playwright = sync_playwright().start()
        
        # Use system Chrome with headless mode
        try:
            cls.browser = cls.playwright.chromium.launch(
                headless=True,
                executable_path='/usr/bin/google-chrome-stable',  # Use system Chrome
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-default-apps',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--window-size=1920,1080',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
        except Exception as e:
            # Fallback to system chromium if Chrome fails
            cls.browser = cls.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-default-apps',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--window-size=1920,1080',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        
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
        self.page.goto(f"{self.live_server_url}/")
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