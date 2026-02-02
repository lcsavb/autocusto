"""
Prescription Form Frontend Tests for CI Environment
Uses the existing Django server instead of StaticLiveServerTestCase
"""

import os
import time
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class PrescriptionFormCITest(TransactionTestCase):
    """Prescription form tests optimized for CI environment."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Playwright for all tests."""
        super().setUpClass()
        
        # Connect to Playwright server
        playwright_endpoint = os.environ.get('PW_TEST_CONNECT_WS_ENDPOINT', 'ws://playwright-server:3000/')
        print(f"[CI-TEST] Connecting to Playwright server: {playwright_endpoint}", flush=True)
        
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.connect(playwright_endpoint)
            print("[CI-TEST] Connected to Playwright server", flush=True)
        except Exception as e:
            print(f"[CI-TEST] Failed to connect: {e}", flush=True)
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up Playwright."""
        if hasattr(cls, 'browser'):
            cls.browser.close()
        if hasattr(cls, 'playwright'):
            cls.playwright.stop()
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data and browser context."""
        super().setUp()
        
        # Create browser context and page
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = self.context.new_page()
        
        # Create test data
        from tests.test_base import UniqueDataGenerator
        data_generator = UniqueDataGenerator()
        
        self.user = User.objects.create_user(
            email=data_generator.generate_unique_email(),
            password='testpass123'
        )
        self.user.is_medico = True
        self.user.save()
        
        print(f"[CI-TEST] Created test user: {self.user.email}", flush=True)
    
    def tearDown(self):
        """Clean up browser context."""
        if hasattr(self, 'page'):
            self.page.close()
        if hasattr(self, 'context'):
            self.context.close()
        super().tearDown()
    
    def test_django_server_accessible(self):
        """Test that Django server is accessible."""
        print("\n[CI-TEST] Testing Django server accessibility", flush=True)
        
        # In CI, Django runs on port 8001 in the same container
        server_url = "http://127.0.0.1:8001"
        
        try:
            response = self.page.goto(server_url, timeout=30000)
            print(f"[CI-TEST] Server response: {response.status}", flush=True)
            
            # Take screenshot
            self.page.screenshot(path="ci_test_home.png")
            
            # Check if we got a response
            self.assertIsNotNone(response)
            self.assertIn(response.status, [200, 302])  # 302 for redirects
            
            print("[CI-TEST] ✅ Django server is accessible", flush=True)
        except Exception as e:
            print(f"[CI-TEST] ❌ Failed to access Django server: {e}", flush=True)
            self.fail(f"Cannot access Django server: {e}")
    
    def test_basic_page_load(self):
        """Test basic page loading without authentication."""
        print("\n[CI-TEST] Testing basic page load", flush=True)
        
        server_url = "http://127.0.0.1:8001"
        self.page.goto(server_url)
        
        # Wait a moment for page to stabilize
        self.page.wait_for_timeout(2000)
        
        # Get page title and content
        title = self.page.title()
        print(f"[CI-TEST] Page title: {title}", flush=True)
        
        # Look for any forms on the page
        forms = self.page.locator('form').count()
        print(f"[CI-TEST] Forms found: {forms}", flush=True)
        
        # Look for input fields
        inputs = self.page.locator('input').count()
        print(f"[CI-TEST] Input fields found: {inputs}", flush=True)
        
        self.assertGreater(forms, 0, "No forms found on page")
        print("[CI-TEST] ✅ Basic page load successful", flush=True)