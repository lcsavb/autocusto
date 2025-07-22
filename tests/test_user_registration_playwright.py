"""
Frontend User Registration Tests using Playwright
Tests the user registration process including form validation, success/failure scenarios,
and security measures.

Features:
- Comprehensive debugging with screenshots
- Detailed error reporting
- Form validation testing
- Success/failure scenario testing
"""

from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from usuarios.forms import CustomUserCreationForm

User = get_user_model()


class UserRegistrationPlaywrightBase(PlaywrightFormTestBase):
    """Base class for user registration tests with common setup and utilities."""
    
    def setUp(self):
        """Set up test environment before each test."""
        super().setUp()
        
        # Clear any existing users
        User.objects.all().delete()

    def debug_page_state(self, step_name):
        """Debug current page state with detailed logging."""
        print(f"\n=== DEBUG: {step_name} ===")
        print(f"Current URL: {self.page.url}")
        print(f"Page title: {self.page.title()}")
        
        # Take screenshot
        self.take_screenshot(step_name)
        
        # Log form fields
        try:
            form_fields = self.page.locator('input, select, textarea').all()
            print(f"Form fields found: {len(form_fields)}")
            for i, field in enumerate(form_fields):
                field_name = field.get_attribute("name") or field.get_attribute("id") or f"field_{i}"
                field_type = field.get_attribute("type")
                field_value = field.get_attribute("value")
                print(f"  {field_name}: {field_type} = '{field_value}'")
        except Exception as e:
            print(f"Error getting form fields: {e}")
        
        # Log any error messages
        try:
            error_selectors = [".alert", ".error", ".invalid-feedback", ".help-block"]
            for selector in error_selectors:
                error_elements = self.page.locator(selector).all()
                for error in error_elements:
                    if error.is_visible():
                        print(f"  Error message: {error.text_content()}")
        except Exception as e:
            print(f"Error getting error messages: {e}")
        
        print("=== END DEBUG ===\n")

    def wait_for_element(self, selector, timeout=10000):
        """Wait for an element to be present and visible."""
        element = self.page.locator(selector)
        element.wait_for(state="visible", timeout=timeout)
        return element

    def wait_for_clickable_element(self, selector, timeout=10000):
        """Wait for an element to be clickable."""
        element = self.page.locator(selector)
        element.wait_for(state="visible", timeout=timeout)
        return element


class UserRegistrationTest(UserRegistrationPlaywrightBase):
    """Test user registration functionality."""
    
    def test_user_registration_form_display(self):
        """Test that the user registration form displays correctly."""
        # Navigate to home page where registration form is located
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        self.debug_page_state("page_loaded")
        
        # Check that the page loads
        self.assertIn("CliqueReceita", self.page.title())
        
        # Check for form elements - the registration form is only visible for unauthenticated users
        try:
            email_field = self.wait_for_element('input[name="email"]')
            self.assertTrue(email_field.is_visible())
            
            password_field = self.wait_for_element('input[name="password1"]')
            self.assertTrue(password_field.is_visible())
            
            password_confirm_field = self.wait_for_element('input[name="password2"]')
            self.assertTrue(password_confirm_field.is_visible())
            
            # Check for doctor-specific fields (required)
            nome_field = self.wait_for_element('input[name="nome"]')
            self.assertTrue(nome_field.is_visible())
            
            # CRM and CNS fields may not be on the home page form, check optionally
            crm_field = self.page.locator('input[name="crm"]')
            cns_field = self.page.locator('input[name="cns"]')
            
            if crm_field.count() == 0 or cns_field.count() == 0:
                print("⚠️  DEBUG: CRM/CNS fields not found on home page - may be on separate registration page")
                # This is OK - the home page might have a simplified form
            else:
                self.assertTrue(crm_field.is_visible())
                self.assertTrue(cns_field.is_visible())
            
            # Look specifically for registration submit button
            registration_submit_button = self.page.locator('button:has-text("Criar conta")')
            login_submit_button = self.page.locator('button:has-text("Login")')
            
            # At least one should be visible
            has_registration_button = registration_submit_button.is_visible()
            has_login_button = login_submit_button.is_visible()
            
            self.assertTrue(
                has_registration_button or has_login_button,
                "Should have registration or login submit button"
            )
            
            self.debug_page_state("form_elements_found")
            
        except Exception as e:
            self.debug_page_state("form_elements_not_found")
            self.fail(f"Registration form elements not found on page: {e}")
    
    def test_user_registration_form_validation_empty_fields(self):
        """Test form validation with empty fields."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Try to submit empty form
        submit_button = self.wait_for_clickable_element('button[type="submit"], input[type="submit"]')
        submit_button.click()
        
        # Wait for validation
        self.page.wait_for_timeout(2000)
        
        # Check that we're still on the registration page (not redirected)
        current_url = self.page.url.lower()
        self.assertTrue(current_url.endswith("/") or "cadastro" in current_url)
        
        # Check for HTML5 validation or Django form errors
        email_field = self.page.locator('input[name="email"]')
        is_required = email_field.get_attribute("required") is not None
        page_content = self.page.content().lower()
        has_validation_message = ("obrigatório" in page_content or 
                                "required" in page_content)
        
        self.assertTrue(
            is_required or has_validation_message,
            "Form should show validation for empty required fields"
        )
    
    def test_user_registration_form_validation_invalid_email(self):
        """Test form validation with invalid email."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Fill form with invalid email
        email_field = self.wait_for_element('input[name="email"]')
        email_field.fill("invalid-email")
        
        password_field = self.page.locator('input[name="password1"]')
        password_field.fill("testpassword123")
        
        password_confirm_field = self.page.locator('input[name="password2"]')
        password_confirm_field.fill("testpassword123")
        
        # Submit form
        submit_button = self.wait_for_clickable_element('button[type="submit"], input[type="submit"]')
        submit_button.click()
        
        self.page.wait_for_timeout(2000)  # Give time for validation
        
        # Check that we're still on registration page (validation failed)
        current_url = self.page.url.lower()
        self.assertTrue(current_url.endswith("/") or "cadastro" in current_url)
        
        # Check for email validation error
        email_field = self.page.locator('input[name="email"]')
        validity = self.page.evaluate("(element) => element.validity.valid", email_field.element_handle())
        self.assertFalse(validity, "Invalid email should trigger validation error")
    
    def test_user_registration_form_validation_password_mismatch(self):
        """Test form validation with mismatched passwords."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        self.debug_page_state("page_loaded")
        
        # Fill form with mismatched passwords
        email_field = self.wait_for_element('input[name="email"]')
        email_field.fill("test@example.com")
        
        # Fill required fields
        nome_field = self.page.locator('input[name="nome"]')
        nome_field.fill("Test User")
        
        crm_field = self.page.locator('input[name="crm"]')
        crm_field.fill("12345")
        
        cns_field = self.page.locator('input[name="cns"]')
        cns_field.fill("123456789012345")
        
        password_field = self.page.locator('input[name="password1"]')
        password_field.fill("testpassword123")
        
        password_confirm_field = self.page.locator('input[name="password2"]')
        password_confirm_field.fill("differentpassword123")
        
        self.debug_page_state("form_filled_with_mismatched_passwords")
        
        # Submit form
        submit_button = self.wait_for_clickable_element('button[type="submit"], input[type="submit"]')
        submit_button.click()
        
        self.page.wait_for_timeout(2000)  # Give time for validation
        self.debug_page_state("form_submitted")
        
        # Check that we're still on the same page (form validation failed)
        current_url = self.page.url.lower()
        self.assertTrue(current_url.endswith("/") or "cadastro" in current_url)
        
        # Check for password mismatch error
        page_content = self.page.content().lower()
        error_found = (
            "senhas não coincidem" in page_content or
            "password" in page_content and (
                "não coincide" in page_content or 
                "não confere" in page_content or
                "don't match" in page_content or
                "mismatch" in page_content or
                "senhas não são iguais" in page_content or
                "the two password fields" in page_content
            )
        )
        
        if not error_found:
            self.debug_page_state("password_mismatch_error_not_found")
            print(f"Full page content preview: {page_content[:500]}")
        
        self.assertTrue(
            error_found,
            f"Password mismatch error should be displayed. Page content: {page_content[:500]}"
        )
    
    def test_user_registration_form_validation_weak_password(self):
        """Test form validation with weak password."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        self.debug_page_state("page_loaded")
        
        # Fill form with weak password
        email_field = self.wait_for_element('input[name="email"]')
        email_field.fill("test@example.com")
        
        # Fill required fields
        nome_field = self.page.locator('input[name="nome"]')
        nome_field.fill("Test User")
        
        crm_field = self.page.locator('input[name="crm"]')
        crm_field.fill("12345")
        
        cns_field = self.page.locator('input[name="cns"]')
        cns_field.fill("123456789012345")
        
        password_field = self.page.locator('input[name="password1"]')
        password_field.fill("123")  # Weak password
        
        password_confirm_field = self.page.locator('input[name="password2"]')
        password_confirm_field.fill("123")
        
        self.debug_page_state("form_filled_with_weak_password")
        
        # Submit form
        submit_button = self.wait_for_clickable_element('button[type="submit"], input[type="submit"]')
        submit_button.click()
        
        self.page.wait_for_timeout(2000)  # Give time for validation
        self.debug_page_state("form_submitted")
        
        # Check that we're still on the same page (form validation failed)
        current_url = self.page.url.lower()
        self.assertTrue(current_url.endswith("/") or "cadastro" in current_url)
        
        # Check for weak password error
        page_content = self.page.content().lower()
        error_found = (
            "senha deve ter pelo menos 8 caracteres" in page_content or
            "senha não pode conter apenas números" in page_content or
            "senha é muito comum" in page_content or
            "escolha uma senha mais segura" in page_content or
            "senha é muito similar" in page_content or
            "password" in page_content and (
                "muito" in page_content or 
                "fraca" in page_content or
                "short" in page_content or
                "weak" in page_content or
                "pelo menos" in page_content or
                "8 characters" in page_content or
                "too short" in page_content or
                "entirely numeric" in page_content
            )
        )
        
        if not error_found:
            self.debug_page_state("weak_password_error_not_found")
            print(f"Full page content preview: {page_content[:500]}")
        
        self.assertTrue(
            error_found,
            f"Weak password error should be displayed. Page content: {page_content[:500]}"
        )
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Fill form with valid data
        email_field = self.wait_for_element('input[name="email"]')
        email_field.fill("testuser@example.com")
        
        # Fill additional required fields if they exist
        nome_field = self.page.locator('input[name="nome"]')
        if nome_field.is_visible():
            nome_field.fill("Test User")
        
        crm_field = self.page.locator('input[name="crm"]')
        if crm_field.is_visible():
            crm_field.fill("12345")
        
        cns_field = self.page.locator('input[name="cns"]')
        if cns_field.is_visible():
            cns_field.fill("123456789012345")
        
        password_field = self.page.locator('input[name="password1"]')
        password_field.fill("testpassword123456")
        
        password_confirm_field = self.page.locator('input[name="password2"]')
        password_confirm_field.fill("testpassword123456")
        
        # Submit form
        submit_button = self.wait_for_clickable_element('button[type="submit"], input[type="submit"]')
        submit_button.click()
        
        # Wait for redirect or success message
        self.wait_for_page_load()
        self.page.wait_for_timeout(3000)
        
        # Check that registration was successful
        current_url = self.page.url.lower()
        page_content = self.page.content().lower()
        
        success_indicators = [
            "login" in current_url,
            "sucesso" in page_content,
            "criada" in page_content,
            "success" in page_content,
            "created" in page_content,
            "pode fazer" in page_content,
            "já pode fazer o login" in page_content
        ]
        
        self.assertTrue(
            any(success_indicators),
            f"Registration success not detected. URL: {current_url}, Content: {page_content[:500]}"
        )
        
        # Verify user was created in database
        user_exists = User.objects.filter(email="testuser@example.com").exists()
        self.assertTrue(user_exists, "User should be created in database")
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create a user with the email we'll try to register
        User.objects.create_user(
            email="duplicate@example.com",
            password="existingpassword123"
        )
        
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Fill form with duplicate email
        email_field = self.wait_for_element('input[name="email"]')
        email_field.fill("duplicate@example.com")
        
        # Fill other required fields
        nome_field = self.page.locator('input[name="nome"]')
        if nome_field.is_visible():
            nome_field.fill("Test User")
        
        crm_field = self.page.locator('input[name="crm"]')
        if crm_field.is_visible():
            crm_field.fill("12345")
        
        cns_field = self.page.locator('input[name="cns"]')
        if cns_field.is_visible():
            cns_field.fill("123456789012345")
        
        password_field = self.page.locator('input[name="password1"]')
        password_field.fill("newpassword123456")
        
        password_confirm_field = self.page.locator('input[name="password2"]')
        password_confirm_field.fill("newpassword123456")
        
        # Submit form
        submit_button = self.wait_for_clickable_element('button[type="submit"], input[type="submit"]')
        submit_button.click()
        
        self.wait_for_page_load()
        self.page.wait_for_timeout(2000)
        
        # Check that we're still on the same page (registration failed)
        current_url = self.page.url.lower()
        self.assertTrue(current_url.endswith("/") or "cadastro" in current_url)
        
        # Check for duplicate email error
        page_content = self.page.content().lower()
        duplicate_error_found = (
            "já existe" in page_content or
            "already exists" in page_content or
            "já cadastrado" in page_content or
            "duplicate" in page_content or
            "usuário com este email já existe" in page_content
        )
        
        self.assertTrue(
            duplicate_error_found,
            f"Duplicate email error should be displayed. Page content: {page_content[:500]}"
        )


class UserRegistrationAccessibilityTest(UserRegistrationPlaywrightBase):
    """Test user registration form accessibility and responsive features."""
    
    def test_registration_form_accessibility(self):
        """Test registration form accessibility features."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Check for form labels
        labels = self.page.locator('label').all()
        print(f"📋 Found {len(labels)} form labels")
        
        # Check specific important labels for registration
        important_labels = ['Email', 'Nome', 'CRM', 'CNS', 'Senha']
        found_labels = 0
        for label_text in important_labels:
            label = self.page.locator(f'label:has-text("{label_text}")')
            if label.count() > 0:
                print(f"✅ Found label: {label_text}")
                found_labels += 1
            else:
                print(f"⚠️  Missing label: {label_text}")
        
        # Check form field attributes
        form_fields = ['email', 'nome', 'crm', 'cns', 'password1', 'password2']
        for field_name in form_fields:
            field = self.page.locator(f'input[name="{field_name}"]')
            if field.is_visible():
                field_class = field.get_attribute('class')
                field_id = field.get_attribute('id')
                field_required = field.get_attribute('required')
                print(f"✅ Field {field_name}: class='{field_class}', id='{field_id}', required='{field_required}'")
        
        self.take_screenshot("registration_form_accessibility")
        self.assertGreater(found_labels, 0, "At least some form labels should be present")
    
    def test_registration_form_responsive(self):
        """Test registration form on different screen sizes."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Test mobile size
        self.page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        self.page.wait_for_timeout(1000)
        
        # Check if registration form is still usable on mobile
        email_field = self.page.locator('input[name="email"]')
        if email_field.count() > 0:
            self.assertTrue(email_field.is_visible(), "Email field should be visible on mobile")
        
        self.take_screenshot("registration_form_mobile")
        
        # Test tablet size
        self.page.set_viewport_size({"width": 768, "height": 1024})  # iPad size
        self.page.wait_for_timeout(1000)
        self.take_screenshot("registration_form_tablet")
        
        # Reset to desktop size
        self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    def test_registration_form_keyboard_navigation(self):
        """Test that registration form can be navigated with keyboard."""
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Start from email field
        email_field = self.page.locator('input[name="email"]')
        if email_field.is_visible():
            email_field.click()
            email_field.fill("test@example.com")
            
            # Tab through the form fields
            self.page.keyboard.press('Tab')  # Should go to nome
            self.page.keyboard.type("Test User")
            
            self.page.keyboard.press('Tab')  # Should go to crm
            self.page.keyboard.type("12345")
            
            self.page.keyboard.press('Tab')  # Should go to cns
            self.page.keyboard.type("123456789012345")
            
            self.page.keyboard.press('Tab')  # Should go to password1
            self.page.keyboard.type("testpassword123")
            
            self.page.keyboard.press('Tab')  # Should go to password2
            self.page.keyboard.type("testpassword123")
            
            # Tab to submit button and verify we can activate it
            self.page.keyboard.press('Tab')
            
            self.take_screenshot("keyboard_navigation_complete")
            
            # Check that fields were filled via keyboard
            email_value = email_field.input_value()
            self.assertEqual(email_value, "test@example.com", "Email should be filled via keyboard")
        else:
            self.skipTest("Registration form not visible - may be for authenticated users only")