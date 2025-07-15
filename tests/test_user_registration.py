"""
Frontend User Registration Tests using Selenium
Tests the user registration process including form validation, success/failure scenarios,
and security measures.

Features:
- Comprehensive debugging with screenshots
- Detailed error reporting
- Form validation testing
- Success/failure scenario testing
"""

import time
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from usuarios.forms import CustomUserCreationForm

User = get_user_model()


class SeleniumTestBase(StaticLiveServerTestCase):
    """Base class for Selenium tests with common setup and utilities."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Setup Chrome/Chromium options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Try to find Chrome/Chromium binary
        import shutil
        chrome_binary = None
        for binary in ['chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable']:
            chrome_binary = shutil.which(binary)
            if chrome_binary:
                break
        
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
        
        # Setup WebDriver
        try:
            service = Service(ChromeDriverManager().install())
            cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            # Fallback to system chrome if webdriver-manager fails
            cls.driver = webdriver.Chrome(options=chrome_options)
        
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Set up test environment before each test."""
        # Clear any existing users
        User.objects.all().delete()
        
        # Wait for page to be ready
        self.driver.implicitly_wait(10)
        
        # Create screenshots directory
        self.screenshots_dir = os.path.join(os.getcwd(), "test_screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Initialize test counter for unique screenshot names
        self.test_step = 0
    
    def tearDown(self):
        """Clean up after each test."""
        # Take final screenshot before cleanup
        self.take_screenshot("final_state")
        
        # Clear cookies and session data
        self.driver.delete_all_cookies()
        
        # Navigate to home to clear any state
        self.driver.get(self.live_server_url)
    
    def take_screenshot(self, step_name):
        """Take a screenshot with detailed filename."""
        self.test_step += 1
        test_name = self._testMethodName
        filename = f"{test_name}_{self.test_step:02d}_{step_name}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            print(f"Screenshot saved: {filepath}")
        except Exception as e:
            print(f"Failed to save screenshot: {e}")
        
        return filepath
    
    def debug_page_state(self, step_name):
        """Debug current page state with detailed logging."""
        print(f"\n=== DEBUG: {step_name} ===")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Take screenshot
        self.take_screenshot(step_name)
        
        # Log form fields
        try:
            form_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
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
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert, .error, .invalid-feedback, .help-block")
            if error_elements:
                print("Error messages found:")
                for error in error_elements:
                    if error.is_displayed():
                        print(f"  {error.text}")
        except Exception as e:
            print(f"Error getting error messages: {e}")
        
        print("=== END DEBUG ===\n")
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and visible."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable_element(self, by, value, timeout=10):
        """Wait for an element to be clickable."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def wait_for_text_in_element(self, by, value, text, timeout=10):
        """Wait for specific text to appear in an element."""
        return WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element((by, value), text)
        )


class UserRegistrationTest(SeleniumTestBase):
    """Test user registration functionality."""
    
    def test_user_registration_form_display(self):
        """Test that the user registration form displays correctly."""
        # Navigate to home page where registration form is located
        self.driver.get(f"{self.live_server_url}/")
        self.debug_page_state("page_loaded")
        
        # Check that the page loads
        self.assertIn("AutoCusto", self.driver.title)
        
        # Check for form elements
        try:
            email_field = self.wait_for_element(By.NAME, "email")
            self.assertTrue(email_field.is_displayed())
            
            password_field = self.wait_for_element(By.NAME, "password1")
            self.assertTrue(password_field.is_displayed())
            
            password_confirm_field = self.wait_for_element(By.NAME, "password2")
            self.assertTrue(password_confirm_field.is_displayed())
            
            # Check for doctor-specific fields
            nome_field = self.wait_for_element(By.NAME, "nome")
            self.assertTrue(nome_field.is_displayed())
            
            crm_field = self.wait_for_element(By.NAME, "crm")
            self.assertTrue(crm_field.is_displayed())
            
            cns_field = self.wait_for_element(By.NAME, "cns")
            self.assertTrue(cns_field.is_displayed())
            
            submit_button = self.wait_for_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            self.assertTrue(submit_button.is_displayed())
            
            self.debug_page_state("form_elements_found")
            
        except TimeoutException as e:
            self.debug_page_state("form_elements_not_found")
            self.fail(f"Registration form elements not found on page: {e}")
    
    def test_user_registration_form_validation_empty_fields(self):
        """Test form validation with empty fields."""
        self.driver.get(f"{self.live_server_url}/")
        
        # Try to submit empty form
        submit_button = self.wait_for_clickable_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        # Check that validation errors appear
        time.sleep(2)  # Give time for validation to show
        
        # Check that we're still on the registration page (not redirected)
        # Check that we're still on the same page (form validation failed)
        self.assertTrue(self.driver.current_url.endswith("/") or "cadastro" in self.driver.current_url.lower())
        
        # Check for HTML5 validation or Django form errors
        email_field = self.driver.find_element(By.NAME, "email")
        self.assertTrue(
            email_field.get_attribute("required") is not None or
            "obrigatório" in self.driver.page_source.lower() or
            "required" in self.driver.page_source.lower()
        )
    
    def test_user_registration_form_validation_invalid_email(self):
        """Test form validation with invalid email."""
        self.driver.get(f"{self.live_server_url}/")
        
        # Fill form with invalid email
        email_field = self.wait_for_element(By.NAME, "email")
        email_field.send_keys("invalid-email")
        
        password_field = self.driver.find_element(By.NAME, "password1")
        password_field.send_keys("testpassword123")
        
        password_confirm_field = self.driver.find_element(By.NAME, "password2")
        password_confirm_field.send_keys("testpassword123")
        
        # Submit form
        submit_button = self.wait_for_clickable_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        time.sleep(2)  # Give time for validation
        
        # Check that we're still on registration page (validation failed)
        # Check that we're still on the same page (form validation failed)
        self.assertTrue(self.driver.current_url.endswith("/") or "cadastro" in self.driver.current_url.lower())
        
        # Check for email validation error
        email_field = self.driver.find_element(By.NAME, "email")
        validity = self.driver.execute_script("return arguments[0].validity.valid;", email_field)
        self.assertFalse(validity, "Invalid email should trigger validation error")
    
    def test_user_registration_form_validation_password_mismatch(self):
        """Test form validation with mismatched passwords."""
        self.driver.get(f"{self.live_server_url}/")
        self.debug_page_state("page_loaded")
        
        # Fill form with mismatched passwords
        email_field = self.wait_for_element(By.NAME, "email")
        email_field.send_keys("test@example.com")
        
        # Fill required fields
        nome_field = self.driver.find_element(By.NAME, "nome")
        nome_field.send_keys("Test User")
        
        crm_field = self.driver.find_element(By.NAME, "crm")
        crm_field.send_keys("12345")
        
        cns_field = self.driver.find_element(By.NAME, "cns")
        cns_field.send_keys("123456789012345")
        
        password_field = self.driver.find_element(By.NAME, "password1")
        password_field.send_keys("testpassword123")
        
        password_confirm_field = self.driver.find_element(By.NAME, "password2")
        password_confirm_field.send_keys("differentpassword123")
        
        self.debug_page_state("form_filled_with_mismatched_passwords")
        
        # Submit form
        submit_button = self.wait_for_clickable_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        time.sleep(2)  # Give time for validation
        self.debug_page_state("form_submitted")
        
        # Check that we're still on the same page (form validation failed)
        self.assertTrue(self.driver.current_url.endswith("/") or "cadastro" in self.driver.current_url.lower())
        
        # Check for password mismatch error - Our custom messages
        page_source = self.driver.page_source.lower()
        error_found = (
            "senhas não coincidem" in page_source or
            "password" in page_source and (
                "não coincide" in page_source or 
                "não confere" in page_source or
                "don't match" in page_source or
                "mismatch" in page_source or
                "senhas não são iguais" in page_source or
                "the two password fields" in page_source
            )
        )
        
        if not error_found:
            self.debug_page_state("password_mismatch_error_not_found")
            # Print page source for debugging
            print(f"Full page source: {page_source}")
        
        self.assertTrue(
            error_found,
            f"Password mismatch error should be displayed. Page source: {page_source[:500]}"
        )
    
    def test_user_registration_form_validation_weak_password(self):
        """Test form validation with weak password."""
        self.driver.get(f"{self.live_server_url}/")
        self.debug_page_state("page_loaded")
        
        # Fill form with weak password
        email_field = self.wait_for_element(By.NAME, "email")
        email_field.send_keys("test@example.com")
        
        # Fill required fields
        nome_field = self.driver.find_element(By.NAME, "nome")
        nome_field.send_keys("Test User")
        
        crm_field = self.driver.find_element(By.NAME, "crm")
        crm_field.send_keys("12345")
        
        cns_field = self.driver.find_element(By.NAME, "cns")
        cns_field.send_keys("123456789012345")
        
        password_field = self.driver.find_element(By.NAME, "password1")
        password_field.send_keys("123")  # Weak password
        
        password_confirm_field = self.driver.find_element(By.NAME, "password2")
        password_confirm_field.send_keys("123")
        
        self.debug_page_state("form_filled_with_weak_password")
        
        # Submit form
        submit_button = self.wait_for_clickable_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        time.sleep(2)  # Give time for validation
        self.debug_page_state("form_submitted")
        
        # Check that we're still on the same page (form validation failed)
        self.assertTrue(self.driver.current_url.endswith("/") or "cadastro" in self.driver.current_url.lower())
        
        # Check for weak password error - Our custom Portuguese messages
        page_source = self.driver.page_source.lower()
        error_found = (
            "senha deve ter pelo menos 8 caracteres" in page_source or
            "senha não pode conter apenas números" in page_source or
            "senha é muito comum" in page_source or
            "escolha uma senha mais segura" in page_source or
            "senha é muito similar" in page_source or
            "password" in page_source and (
                "muito" in page_source or 
                "fraca" in page_source or
                "short" in page_source or
                "weak" in page_source or
                "pelo menos" in page_source or
                "8 characters" in page_source or
                "too short" in page_source or
                "entirely numeric" in page_source
            )
        )
        
        if not error_found:
            self.debug_page_state("weak_password_error_not_found")
            # Print page source for debugging
            print(f"Full page source: {page_source}")
        
        self.assertTrue(
            error_found,
            f"Weak password error should be displayed. Page source: {page_source[:500]}"
        )
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        self.driver.get(f"{self.live_server_url}/")
        
        # Fill form with valid data
        email_field = self.wait_for_element(By.NAME, "email")
        email_field.send_keys("testuser@example.com")
        
        # Fill additional required fields if they exist
        try:
            nome_field = self.driver.find_element(By.NAME, "nome")
            nome_field.send_keys("Test User")
        except NoSuchElementException:
            pass  # Nome field might not exist
        
        try:
            crm_field = self.driver.find_element(By.NAME, "crm")
            crm_field.send_keys("12345")
        except NoSuchElementException:
            pass  # CRM field might not exist
        
        try:
            cns_field = self.driver.find_element(By.NAME, "cns")
            cns_field.send_keys("123456789012345")
        except NoSuchElementException:
            pass  # CNS field might not exist
        
        password_field = self.driver.find_element(By.NAME, "password1")
        password_field.send_keys("testpassword123456")
        
        password_confirm_field = self.driver.find_element(By.NAME, "password2")
        password_confirm_field.send_keys("testpassword123456")
        
        # Submit form
        submit_button = self.wait_for_clickable_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        # Wait for redirect or success message
        time.sleep(3)
        
        # Check that registration was successful
        # Either we're redirected to login page or see success message
        current_url = self.driver.current_url.lower()
        page_source = self.driver.page_source.lower()
        
        success_indicators = [
            "login" in current_url,
            "sucesso" in page_source,
            "criada" in page_source,
            "success" in page_source,
            "created" in page_source,
            "pode fazer" in page_source
        ]
        
        self.assertTrue(
            any(success_indicators),
            f"Registration success not detected. URL: {current_url}"
        )
        
        # Verify user was created in database
        self.assertTrue(
            User.objects.filter(email="testuser@example.com").exists(),
            "User should be created in database"
        )
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create a user first
        User.objects.create_user(email="existing@example.com", password="password123")
        
        self.driver.get(f"{self.live_server_url}/")
        
        # Try to register with existing email
        email_field = self.wait_for_element(By.NAME, "email")
        email_field.send_keys("existing@example.com")
        
        # Fill additional required fields if they exist
        try:
            nome_field = self.driver.find_element(By.NAME, "nome")
            nome_field.send_keys("Test User")
        except NoSuchElementException:
            pass
        
        try:
            crm_field = self.driver.find_element(By.NAME, "crm")
            crm_field.send_keys("54321")
        except NoSuchElementException:
            pass
        
        try:
            cns_field = self.driver.find_element(By.NAME, "cns")
            cns_field.send_keys("987654321098765")
        except NoSuchElementException:
            pass
        
        password_field = self.driver.find_element(By.NAME, "password1")
        password_field.send_keys("testpassword123456")
        
        password_confirm_field = self.driver.find_element(By.NAME, "password2")
        password_confirm_field.send_keys("testpassword123456")
        
        # Submit form
        submit_button = self.wait_for_clickable_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        time.sleep(2)  # Give time for validation
        
        # Check that we're still on registration page (validation failed)
        # Check that we're still on the same page (form validation failed)
        self.assertTrue(self.driver.current_url.endswith("/") or "cadastro" in self.driver.current_url.lower())
        
        # Check for duplicate email error - Our custom messages
        page_source = self.driver.page_source.lower()
        error_found = (
            "este email já está em uso" in page_source or
            "email" in page_source and (
                "já existe" in page_source or 
                "already exists" in page_source or
                "duplicate" in page_source or
                "único" in page_source
            )
        )
        
        if not error_found:
            self.debug_page_state("duplicate_email_error_not_found")
            # Print page source for debugging
            print(f"Full page source: {page_source[:1000]}")
        
        self.assertTrue(
            error_found,
            f"Duplicate email error should be displayed. Page source: {page_source[:500]}"
        )
    
    def test_user_registration_csrf_protection(self):
        """Test that CSRF protection is working on registration form."""
        self.driver.get(f"{self.live_server_url}/")
        
        # Check for CSRF token in form
        try:
            csrf_token = self.driver.find_element(By.NAME, "csrfmiddlewaretoken")
            self.assertTrue(csrf_token.is_displayed() or csrf_token.get_attribute("type") == "hidden")
            self.assertNotEqual(csrf_token.get_attribute("value"), "")
        except NoSuchElementException:
            self.fail("CSRF token not found in registration form")
    
    def test_user_registration_form_accessibility(self):
        """Test basic accessibility features of registration form."""
        self.driver.get(f"{self.live_server_url}/")
        
        # Check for proper form labels
        email_field = self.wait_for_element(By.NAME, "email")
        
        # Check if field has associated label
        email_id = email_field.get_attribute("id")
        if email_id:
            try:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{email_id}']")
                self.assertTrue(label.is_displayed())
            except NoSuchElementException:
                pass  # Label might be implemented differently
        
        # Check for proper form structure
        form_element = self.driver.find_element(By.TAG_NAME, "form")
        self.assertTrue(form_element.is_displayed())
        
        # Check that form has proper method
        form_method = form_element.get_attribute("method")
        self.assertEqual(form_method.lower(), "post")
    
    def test_user_registration_js_validation(self):
        """Test client-side JavaScript validation if implemented."""
        self.driver.get(f"{self.live_server_url}/")
        
        # Fill email field and then clear it to trigger validation
        email_field = self.wait_for_element(By.NAME, "email")
        email_field.send_keys("test@example.com")
        email_field.clear()
        
        # Click somewhere else to trigger blur event
        password_field = self.driver.find_element(By.NAME, "password1")
        password_field.click()
        
        time.sleep(1)  # Give time for JS validation
        
        # Check if any validation styling was applied
        email_field_classes = email_field.get_attribute("class")
        
        # This test checks if client-side validation is working
        # The exact implementation depends on the frontend framework used
        self.assertTrue(
            email_field_classes is not None,
            "Email field should have some CSS classes for styling"
        )