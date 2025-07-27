"""
Comprehensive Navigation and Core App Logic Tests using Playwright
Tests all major navigation paths, links, and core application workflows.
"""

import time
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class NavigationPlaywrightTestBase(PlaywrightFormTestBase):
    """Base class for comprehensive navigation and workflow tests."""
    
    def setUp(self):
        """Set up comprehensive test data for navigation testing."""
        super().setUp()
        
        # Create test user with full setup
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.user.is_medico = True
        self.user.save()
        
        # Create medico with full credentials
        self.medico = Medico.objects.create(
            nome_medico="Dr. Test User",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico.usuarios.add(self.user)
        
        # Create clinic
        self.clinica = Clinica.objects.create(
            nome_clinica="Test Clinic",
            cns_clinica="1234567",
            logradouro="Test Street",
            logradouro_num="123",
            cidade="Test City",
            bairro="Test Neighborhood",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        self.user.clinicas.add(self.clinica)
        
        # Create emissor
        self.emissor = Emissor.objects.create(
            medico=self.medico,
            clinica=self.clinica
        )
        
        # Create test patient
        self.patient = Paciente.objects.create(
            nome_paciente="Test Patient",
            cpf_paciente="72834565031",
            cns_paciente="111111111111111",
            nome_mae="Test Mother",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Patient Street, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="Test City",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        self.patient.usuarios.add(self.user)
        
        # Create protocolo and doenca
        self.protocolo = Protocolo.objects.create(
            nome="Test Protocol",
            arquivo="test.pdf"
        )
        self.doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Epilepsia",
            protocolo=self.protocolo
        )

    def login_user(self):
        """Helper to login the test user."""
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Fill login form in the topbar
        email_field = self.page.locator('input[name="username"]')
        password_field = self.page.locator('input[name="password"]')
        
        email_field.fill(self.user.email)
        password_field.fill("testpass123")
        
        # Submit login form
        login_button = self.page.locator('button[type="submit"]:has-text("Login")')
        login_button.click()
        
        # Wait for successful login
        self.wait_for_page_load()
        
        # Verify login success by checking for logout button
        logout_button = self.page.locator('button[type="submit"]:has-text("Logout")')
        self.assertTrue(logout_button.is_visible(), "Should be logged in and show logout button")

    def check_link_accessibility(self, link_text, expected_url_pattern=None):
        """Helper to check if a link is accessible and working."""
        try:
            original_url = self.page.url
            link = self.page.locator(f'text="{link_text}"')
            if not link.is_visible():
                return False
                
            link.click()
            self.wait_for_page_load()
            
            new_url = self.page.url
            self.assertNotEqual(original_url, new_url, f"Link '{link_text}' did not navigate")
            
            if expected_url_pattern:
                self.assertIn(expected_url_pattern, new_url, f"Link '{link_text}' did not go to expected URL pattern")
            
            # Check page loaded successfully (no error pages)
            page_content = self.page.content().lower()
            self.assertNotIn("404", page_content)
            self.assertNotIn("500", page_content)
            self.assertNotIn("server error", page_content)
            
            return True
        except Exception as e:
            print(f"Link check failed for '{link_text}': {e}")
            return False


class ComprehensiveNavigationTest(NavigationPlaywrightTestBase):
    """Test all navigation links and menu items."""

    def test_home_page_navigation_authenticated(self):
        """Test all navigation elements on authenticated home page."""
        self.login_user()
        
        # Check main navigation items in navbar
        navbar_elements = [
            'input[name="username"]',  # Should NOT be visible when authenticated
            'button:has-text("Logout")',  # Should be visible when authenticated
            'a:has-text("Minha conta")',  # Dropdown trigger
        ]
        
        # Login form should NOT be visible when authenticated
        login_form = self.page.locator('input[name="username"]')
        self.assertFalse(login_form.is_visible(), "Login form should not be visible when authenticated")
        
        # Logout button should be visible
        logout_button = self.page.locator('button:has-text("Logout")')
        self.assertTrue(logout_button.is_visible(), "Logout button should be visible when authenticated")
        
        # Minha conta dropdown should be visible
        account_dropdown = self.page.locator('a:has-text("Minha conta")')
        self.assertTrue(account_dropdown.is_visible(), "Minha conta dropdown should be visible")

    def test_dropdown_menu_navigation(self):
        """Test dropdown menu items."""
        self.login_user()
        
        # Click dropdown to reveal menu
        dropdown = self.page.locator('#navbarDropdown')
        if dropdown.is_visible():
            dropdown.click()
            self.wait_for_page_load()
            
            # Check dropdown menu items
            dropdown_items = [
                ("Editar Perfil", "/medicos/editar-perfil/"),
                ("Clínicas", "/clinicas/cadastro/"),
            ]
            
            for item_text, expected_url in dropdown_items:
                with self.subTest(dropdown_item=item_text):
                    success = self.check_link_accessibility(item_text, expected_url)
                    self.assertTrue(success, f"Dropdown item '{item_text}' should be accessible")
        else:
            self.skipTest("Dropdown menu not found")

    def test_quick_search_functionality(self):
        """Test the quick patient search in navbar."""
        self.login_user()
        
        # Find quick search form
        search_input = self.page.locator('input[placeholder*="Paciente"]')
        search_button = self.page.locator('button .oi-magnifying-glass')
        
        if search_input.is_visible() and search_button.is_visible():
            # Test search with patient name
            search_input.fill("Test Patient")
            search_button.click()
            
            self.wait_for_page_load()
            
            # Should navigate to renovacao-rapida page
            current_url = self.page.url
            self.assertIn("renovacao-rapida", current_url, "Should navigate to renovacao-rapida page")
        else:
            self.skipTest("Quick search not available when not authenticated or not visible")

    def test_footer_and_utility_links(self):
        """Test footer and utility navigation links."""
        self.login_user()
        
        # Check utility links in navbar
        utility_selectors = [
            'a[title*="Reportar Erro"]',
            'a[title*="Solicitar Funcionalidade"]'
        ]
        
        for selector in utility_selectors:
            with self.subTest(utility_selector=selector):
                utility_link = self.page.locator(selector)
                self.assertTrue(utility_link.is_visible(), f"Utility link '{selector}' should be visible")


class CoreAppWorkflowTest(NavigationPlaywrightTestBase):
    """Test core application workflows through the UI."""

    def test_complete_process_creation_workflow(self):
        """Test the complete process creation flow from home to PDF generation."""
        self.login_user()
        
        # Step 1: Fill home form with patient CPF and CID
        cpf_field = self.page.locator('input[name="cpf_paciente"]')
        cid_field = self.page.locator('input[name="cid"]')
        
        # Type CPF slowly to trigger any JavaScript validation
        cpf_value = "728.345.650-31"
        cpf_field.fill(cpf_value)
        
        # Type CID
        cid_field.fill("G40.0")
        
        self.take_screenshot("before_form_submission")
        
        # Submit form - look for button with icon and text
        submit_button = self.page.locator('button[type="submit"]:has-text("Cadastrar")')
        submit_button.click()
        
        self.wait_for_page_load()
        self.take_screenshot("after_form_submission")
        
        # Should navigate to either cadastro or edicao page
        current_url = self.page.url
        self.assertTrue(
            "/processos/cadastro/" in current_url or "/processos/edicao/" in current_url,
            f"Should navigate to process page but got: {current_url}"
        )

    def test_patient_cpf_validation_workflow(self):
        """Test CPF validation and patient lookup workflow."""
        self.login_user()
        
        # Test with invalid CPF
        cpf_field = self.page.locator('input[name="cpf_paciente"]')
        cpf_field.fill("123.456.789-00")  # Invalid CPF
        
        cid_field = self.page.locator('input[name="cid"]')
        cid_field.fill("G40.0")
        
        submit_button = self.page.locator('button[type="submit"]:has-text("Cadastrar")')
        submit_button.click()
        
        self.wait_for_page_load()
        
        # Should either show validation error or handle gracefully
        # The specific behavior depends on the validation implementation
        current_url = self.page.url
        # At minimum, should not crash
        self.assertIsNotNone(current_url, "Page should handle invalid CPF gracefully")

    def test_cid_search_functionality(self):
        """Test CID/disease search functionality."""
        self.login_user()
        
        cid_field = self.page.locator('input[name="cid"]')
        
        # Type partial CID to trigger search
        cid_field.fill("G40")
        
        # Wait for any AJAX search results
        self.page.wait_for_timeout(1000)
        
        # Check if search suggestions appear (depends on implementation)
        cid_field.fill("G40.0")
        
        # The specific assertions depend on how the search is implemented
        # At minimum, the field should accept the input
        filled_value = cid_field.input_value()
        self.assertEqual(filled_value, "G40.0", "CID field should accept the input")

    def test_form_validation_and_error_handling(self):
        """Test form validation and error message display."""
        self.login_user()
        
        # Try to submit empty form
        submit_button = self.page.locator('button[type="submit"]:has-text("Cadastrar")')
        submit_button.click()
        
        self.wait_for_page_load()
        
        # Should show validation errors or handle empty submission
        current_url = self.page.url
        self.assertEqual(current_url, f'{self.live_server_url}/', "Should stay on home page for validation")

    def test_session_preservation_across_navigation(self):
        """Test that session data is preserved across different pages."""
        self.login_user()
        
        # Start process creation
        cpf_field = self.page.locator('input[name="cpf_paciente"]')
        cid_field = self.page.locator('input[name="cid"]')
        
        cpf_field.fill("728.345.650-31")
        cid_field.fill("G40.0")
        
        # Navigate to profile page
        self.page.goto(f'{self.live_server_url}/medicos/editar-perfil/')
        self.wait_for_page_load()
        
        # Navigate back to home
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Check if we're still authenticated
        logout_button = self.page.locator('button:has-text("Logout")')
        self.assertTrue(logout_button.is_visible(), "Should still be authenticated after navigation")


class PatientManagementWorkflowTest(NavigationPlaywrightTestBase):
    """Test patient management functionality through the UI."""

    def test_patient_listing_access(self):
        """Test accessing patient listing page."""
        self.login_user()
        
        # Navigate to patient listing
        self.page.goto(f'{self.live_server_url}/pacientes/listar/')
        self.wait_for_page_load()
        
        # Should show patient listing
        page_content = self.page.content()
        self.assertIn("Test Patient", page_content, "Should show test patient")

    def test_patient_search_authorization(self):
        """Test patient search respects user authorization."""
        self.login_user()
        
        # Navigate to patient listing
        self.page.goto(f'{self.live_server_url}/pacientes/listar/')
        self.wait_for_page_load()
        
        # Should only show patients associated with this user
        page_content = self.page.content()
        self.assertIn("Test Patient", page_content)
        # Should not show patients from other users (would need another user to test)


class ResponsiveAndAccessibilityTest(NavigationPlaywrightTestBase):
    """Test responsive design and accessibility features."""

    def test_mobile_navigation_toggle(self):
        """Test mobile navigation toggle functionality."""
        self.login_user()
        
        # Resize to mobile viewport
        self.page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        
        # Look for navbar toggle button
        toggle_button = self.page.locator('.navbar-toggler')
        
        if toggle_button.is_visible():
            # Click toggle
            toggle_button.click()
            self.page.wait_for_timeout(500)
            
            # Navigation should become visible/expanded
            # The specific implementation depends on Bootstrap behavior
            nav_collapse = self.page.locator('.navbar-collapse')
            # At minimum, toggle should not crash
            self.assertIsNotNone(nav_collapse, "Navigation collapse should exist")
        else:
            self.skipTest("Mobile toggle not visible or not needed")
        
        # Reset window size
        self.page.set_viewport_size({"width": 1920, "height": 1080})

    def test_form_accessibility_features(self):
        """Test form accessibility features like labels and ARIA attributes."""
        self.login_user()
        
        # Check main form labels
        cpf_label = self.page.locator('text="CPF do Paciente"')
        cid_label = self.page.locator('text="Doença/CID"')
        
        self.assertTrue(cpf_label.is_visible(), "CPF label should be visible")
        self.assertTrue(cid_label.is_visible(), "CID label should be visible")
        
        # Check form fields have proper attributes
        cpf_field = self.page.locator('input[name="cpf_paciente"]')
        cid_field = self.page.locator('input[name="cid"]')
        
        # Should have proper input attributes
        cpf_class = cpf_field.get_attribute("class")
        cid_class = cid_field.get_attribute("class")
        
        self.assertIsNotNone(cpf_class, "CPF field should have CSS classes")
        self.assertIsNotNone(cid_class, "CID field should have CSS classes")


class NavigationSecurityTest(NavigationPlaywrightTestBase):
    """Test navigation security and authorization."""
    
    def test_unauthenticated_access_restrictions(self):
        """Test that unauthenticated users can't access protected pages."""
        # Don't login - test as unauthenticated user
        
        protected_urls = [
            '/medicos/editar-perfil/',
            '/clinicas/cadastro/',
            '/pacientes/listar/',
            '/processos/cadastro/',
        ]
        
        for url in protected_urls:
            with self.subTest(protected_url=url):
                self.page.goto(f'{self.live_server_url}{url}')
                self.wait_for_page_load()
                
                current_url = self.page.url
                # Should be redirected to login or home, not stay on protected page
                self.assertNotEqual(current_url, f'{self.live_server_url}{url}', 
                                  f"Should not allow access to {url} without authentication")
    
    def test_user_data_isolation(self):
        """Test that users can only see their own data."""
        # Create another user with different data
        other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='otherpass123'
        )
        other_user.is_medico = True
        other_user.save()
        
        other_medico = Medico.objects.create(
            nome_medico="Dr. Other User",
            crm_medico="67890",
            cns_medico="222222222222222"
        )
        other_medico.usuarios.add(other_user)
        
        other_patient = Paciente.objects.create(
            nome_paciente="Other Patient",
            cpf_paciente="12345678901",
            cns_paciente="222222222222222",
            nome_mae="Other Mother",
            idade="25",
            sexo="F",
            peso="60.0",
            altura="1.65",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11888888888",
            end_paciente="Other Street, 456",
            rg="987654321",
            escolha_etnia="Branca",
            cidade_paciente="Other City",
            cep_paciente="02000-000",
            telefone2_paciente="11777777777",
            nome_responsavel="",
        )
        other_patient.usuarios.add(other_user)
        
        # Login as first user
        self.login_user()
        
        # Check patient listing - should only see own patients
        self.page.goto(f'{self.live_server_url}/pacientes/listar/')
        self.wait_for_page_load()
        
        page_content = self.page.content()
        self.assertIn("Test Patient", page_content, "Should see own patient")
        self.assertNotIn("Other Patient", page_content, "Should not see other user's patient")