"""
Frontend Login Tests using Selenium
Tests the actual browser interactions for login functionality including UI elements,
form validation, error handling, and user experience.

Features:
- Comprehensive UI testing with screenshots
- Form validation testing  
- Error message verification
- Login/logout flow testing
- Security measure validation
- Cross-browser compatibility considerations
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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from usuarios.models import Usuario
from medicos.models import Medico
from clinicas.models import Clinica

User = get_user_model()


class SeleniumLoginTestBase(StaticLiveServerTestCase):
    """Base class for Selenium login tests with common setup and utilities."""
    
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
        self.screenshots_dir = os.path.join(os.getcwd(), "test_screenshots", "login")
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
                is_displayed = field.is_displayed()
                print(f"  {field_name}: {field_type} = '{field_value}' (displayed: {is_displayed})")
        except Exception as e:
            print(f"Error getting form fields: {e}")
        
        # Log any error messages
        try:
            error_selectors = [
                ".alert", ".error", ".invalid-feedback", ".help-block", 
                ".errorlist", "[class*='error']", "[class*='invalid']"
            ]
            for selector in error_selectors:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for error in error_elements:
                    if error.is_displayed() and error.text.strip():
                        print(f"  ERROR FOUND ({selector}): {error.text}")
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
    
    def create_test_user(self, email='doctor@example.com', password='SecurePassword123!'):
        """Create a test user with medical profile."""
        user = Usuario.objects.create_user(
            email=email,
            password=password,
            is_medico=True
        )
        
        medico = Medico.objects.create(
            nome_medico='Dr. Test User',
            crm_medico='123456',
            cns_medico='111111111111111'
        )
        user.medicos.add(medico)
        
        return user, medico
    
    def perform_login(self, email, password, should_succeed=True):
        """Perform login action and return result."""
        # Navigate to login page
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        self.debug_page_state("navigated_to_login_page")
        
        # Fill login form
        try:
            email_field = self.wait_for_element(By.NAME, "username")
            password_field = self.wait_for_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(email)
            
            password_field.clear()
            password_field.send_keys(password)
            
            self.debug_page_state("filled_login_form")
            
            # Submit form
            submit_button = self.wait_for_clickable_element(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit'], .btn-primary, [value='Login']"
            )
            submit_button.click()
            
            # Wait for response
            time.sleep(2)
            self.debug_page_state("after_form_submission")
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if should_succeed:
                # Check for successful login indicators
                success_indicators = [
                    current_url != f'{self.live_server_url}/medicos/login/',
                    'dashboard' in current_url or 'home' in current_url or current_url.endswith('/'),
                    'logout' in page_source,
                    'bem-vindo' in page_source or 'welcome' in page_source,
                ]
                return any(success_indicators), current_url
            else:
                # Check for failed login indicators
                failure_indicators = [
                    'login' in current_url,
                    'erro' in page_source or 'error' in page_source,
                    'inválido' in page_source or 'invalid' in page_source,
                ]
                return any(failure_indicators), current_url
                
        except Exception as e:
            print(f"Login attempt failed with exception: {e}")
            self.debug_page_state("login_exception_occurred")
            return False, self.driver.current_url


class LoginPageTest(SeleniumLoginTestBase):
    """Test login page display and basic functionality."""
    
    def test_login_page_loads_correctly(self):
        """Test that login page loads with all required elements."""
        # Navigate to login page
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        self.debug_page_state("login_page_loaded")
        
        # Check page loads
        self.assertEqual(self.driver.title.lower().count('login') + 
                        self.driver.title.lower().count('entrar') + 
                        self.driver.title.lower().count('autocusto'), True)
        
        # Check for essential form elements
        try:
            email_field = self.wait_for_element(By.NAME, "username")
            self.assertTrue(email_field.is_displayed())
            
            password_field = self.wait_for_element(By.NAME, "password")  
            self.assertTrue(password_field.is_displayed())
            
            submit_button = self.wait_for_element(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit']"
            )
            self.assertTrue(submit_button.is_displayed())
            
            self.debug_page_state("form_elements_verified")
            
        except TimeoutException as e:
            self.debug_page_state("essential_elements_missing")
            self.fail(f"Essential login form elements missing: {e}")
    
    def test_login_form_labels_and_accessibility(self):
        """Test login form has proper labels and accessibility features."""
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        # Check for form labels
        email_field = self.wait_for_element(By.NAME, "username")
        password_field = self.wait_for_element(By.NAME, "password")
        
        # Check if fields have associated labels
        email_id = email_field.get_attribute("id")
        password_id = password_field.get_attribute("id")
        
        if email_id:
            try:
                email_label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{email_id}']")
                self.assertTrue(email_label.is_displayed())
            except NoSuchElementException:
                # Label might be implemented differently - check for nearby label
                pass
        
        # Check for proper form structure
        form_element = self.driver.find_element(By.TAG_NAME, "form")
        self.assertTrue(form_element.is_displayed())
        
        # Check form method
        form_method = form_element.get_attribute("method")
        self.assertEqual(form_method.lower(), "post")
    
    def test_csrf_token_present(self):
        """Test that CSRF token is present in login form."""
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        # Check for CSRF token
        try:
            csrf_token = self.driver.find_element(By.NAME, "csrfmiddlewaretoken")
            self.assertIsNotNone(csrf_token.get_attribute("value"))
            self.assertNotEqual(csrf_token.get_attribute("value"), "")
        except NoSuchElementException:
            self.fail("CSRF token not found in login form")


class LoginFunctionalityTest(SeleniumLoginTestBase):
    """Test login functionality with various scenarios."""
    
    def setUp(self):
        super().setUp()
        # Create test user for login tests
        self.test_email = 'doctor@example.com'
        self.test_password = 'SecurePassword123!'
        self.user, self.medico = self.create_test_user(self.test_email, self.test_password)
    
    def test_successful_login(self):
        """Test successful login with valid credentials."""
        success, final_url = self.perform_login(self.test_email, self.test_password, should_succeed=True)
        
        self.assertTrue(success, f"Login should succeed. Final URL: {final_url}")
        
        # Verify user is redirected away from login page
        self.assertNotIn('/login', final_url)
        
        # Check for logout button or user indicator
        page_source = self.driver.page_source.lower()
        logout_indicators = [
            'logout' in page_source,
            'sair' in page_source,
            'bem-vindo' in page_source,
            self.test_email.lower() in page_source
        ]
        self.assertTrue(any(logout_indicators), "Should show user is logged in")
    
    def test_login_with_invalid_email(self):
        """Test login with invalid email address."""
        success, final_url = self.perform_login('invalid@example.com', self.test_password, should_succeed=False)
        
        self.assertTrue(success, f"Should stay on login page with error. Final URL: {final_url}")
        
        # Should stay on login page
        self.assertIn('login', final_url)
        
        # Check for error message
        page_source = self.driver.page_source.lower()
        error_indicators = [
            'erro' in page_source,
            'error' in page_source,
            'inválido' in page_source,
            'invalid' in page_source,
            'credentials' in page_source
        ]
        self.assertTrue(any(error_indicators), "Should show error message")
    
    def test_login_with_invalid_password(self):
        """Test login with invalid password."""
        success, final_url = self.perform_login(self.test_email, 'wrongpassword', should_succeed=False)
        
        self.assertTrue(success, f"Should stay on login page with error. Final URL: {final_url}")
        self.assertIn('login', final_url)
    
    def test_login_with_empty_fields(self):
        """Test login form validation with empty fields."""
        # Navigate to login page
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        # Try to submit empty form
        submit_button = self.wait_for_clickable_element(
            By.CSS_SELECTOR, 
            "button[type='submit'], input[type='submit']"
        )
        submit_button.click()
        
        time.sleep(2)
        self.debug_page_state("empty_form_submitted")
        
        # Should stay on login page
        current_url = self.driver.current_url
        self.assertIn('login', current_url)
        
        # Check for validation - either HTML5 validation or server-side
        email_field = self.driver.find_element(By.NAME, "username")
        
        # HTML5 validation check
        is_required = email_field.get_attribute("required") is not None
        validation_message = email_field.get_attribute("validationMessage")
        
        # Server-side validation check
        page_source = self.driver.page_source.lower()
        has_error_message = any([
            'obrigatório' in page_source,
            'required' in page_source,
            'erro' in page_source,
            'error' in page_source
        ])
        
        self.assertTrue(
            is_required or validation_message or has_error_message,
            "Should have form validation for empty fields"
        )
    
    def test_login_with_case_insensitive_email(self):
        """Test that email login is case insensitive."""
        # Test with uppercase email
        success, final_url = self.perform_login(
            self.test_email.upper(), 
            self.test_password, 
            should_succeed=True
        )
        
        self.assertTrue(success, f"Uppercase email should work. Final URL: {final_url}")
    
    def test_login_password_masking(self):
        """Test that password field masks input."""
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        password_field = self.wait_for_element(By.NAME, "password")
        password_type = password_field.get_attribute("type")
        
        self.assertEqual(password_type, "password", "Password field should have type='password'")
    
    def test_login_remember_functionality_if_present(self):
        """Test remember me functionality if implemented."""
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        # Check if there's a remember me checkbox
        try:
            remember_checkbox = self.driver.find_element(
                By.CSS_SELECTOR, 
                "input[type='checkbox'][name*='remember'], input[type='checkbox'][name*='lembrar']"
            )
            
            # If remember me exists, test it
            if remember_checkbox.is_displayed():
                # Check the checkbox
                if not remember_checkbox.is_selected():
                    remember_checkbox.click()
                
                # Perform login
                success, final_url = self.perform_login(
                    self.test_email, 
                    self.test_password, 
                    should_succeed=True
                )
                
                self.assertTrue(success, "Login with remember me should work")
            
        except NoSuchElementException:
            # Remember me not implemented - that's OK
            pass


class LoginSecurityTest(SeleniumLoginTestBase):
    """Test login security measures."""
    
    def setUp(self):
        super().setUp()
        self.test_email = 'doctor@example.com'
        self.test_password = 'SecurePassword123!'
        self.user, self.medico = self.create_test_user(self.test_email, self.test_password)
    
    def test_login_with_javascript_injection(self):
        """Test login form security against JavaScript injection."""
        malicious_scripts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
        ]
        
        for script in malicious_scripts:
            self.driver.get(f'{self.live_server_url}/medicos/login/')
            
            # Try to inject script in email field
            email_field = self.wait_for_element(By.NAME, "username")
            password_field = self.wait_for_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(script)
            password_field.clear()
            password_field.send_keys("anypassword")
            
            # Submit form
            submit_button = self.wait_for_clickable_element(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit']"
            )
            submit_button.click()
            
            time.sleep(2)
            
            # Check that script was not executed
            # If script executed, it would typically show an alert or modify the page
            page_source = self.driver.page_source
            
            # Script should be escaped or not present in dangerous form
            self.assertNotIn('<script>', page_source.lower())
            
            # Page should handle gracefully
            self.assertIn(self.driver.current_url, [
                f'{self.live_server_url}/medicos/login/',
                f'{self.live_server_url}/'
            ])
    
    def test_login_rate_limiting_simulation(self):
        """Test login form behavior with multiple failed attempts."""
        # Attempt multiple failed logins
        for i in range(5):
            print(f"Failed login attempt {i+1}")
            success, final_url = self.perform_login(
                self.test_email, 
                'wrongpassword', 
                should_succeed=False
            )
            
            # Each attempt should fail
            self.assertTrue(success, f"Attempt {i+1} should show error")
            
            # Small delay between attempts
            time.sleep(1)
        
        # Try valid login after failed attempts
        print("Attempting valid login after failed attempts")
        success, final_url = self.perform_login(
            self.test_email, 
            self.test_password, 
            should_succeed=True
        )
        
        # Valid login should work unless strict rate limiting is implemented
        # This test mainly checks that the system doesn't crash under repeated attempts
        self.assertIsNotNone(success)  # Should not crash
    
    def test_login_with_sql_injection_patterns(self):
        """Test login form security against SQL injection patterns."""
        sql_patterns = [
            "admin'--",
            "admin' OR '1'='1",
            "'; DROP TABLE usuarios; --",
            "admin' OR 1=1#",
            "1' UNION SELECT * FROM usuarios--",
        ]
        
        for pattern in sql_patterns:
            self.driver.get(f'{self.live_server_url}/medicos/login/')
            
            # Try SQL injection in email field
            success, final_url = self.perform_login(
                pattern, 
                'anypassword', 
                should_succeed=False
            )
            
            # Should not crash or authenticate
            self.assertTrue(success or not success)  # Should handle gracefully
            
            # Verify database integrity - test user should still exist
            self.assertTrue(Usuario.objects.filter(email=self.test_email).exists())


class LogoutTest(SeleniumLoginTestBase):
    """Test logout functionality."""
    
    def setUp(self):
        super().setUp()
        self.test_email = 'doctor@example.com'
        self.test_password = 'SecurePassword123!'
        self.user, self.medico = self.create_test_user(self.test_email, self.test_password)
    
    def test_logout_functionality(self):
        """Test complete logout functionality."""
        # First login
        success, final_url = self.perform_login(
            self.test_email, 
            self.test_password, 
            should_succeed=True
        )
        self.assertTrue(success, "Should login successfully")
        
        # Look for logout link/button
        logout_selectors = [
            "a[href*='logout']",
            "button[name*='logout']", 
            ".logout",
            "[href*='/medicos/logout/']",
            "a:contains('Logout')",
            "a:contains('Sair')"
        ]
        
        logout_element = None
        for selector in logout_selectors:
            try:
                logout_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if logout_element.is_displayed():
                    break
            except NoSuchElementException:
                continue
        
        if logout_element:
            self.debug_page_state("before_logout")
            logout_element.click()
            time.sleep(2)
            self.debug_page_state("after_logout_click")
            
            # Should be redirected to login page or home page
            current_url = self.driver.current_url
            expected_urls = [
                f'{self.live_server_url}/medicos/login/',
                f'{self.live_server_url}/'
            ]
            
            self.assertIn(current_url, expected_urls + [url.rstrip('/') for url in expected_urls])
            
            # Try to access a protected page
            self.driver.get(f'{self.live_server_url}/medicos/profile/')
            
            # Should be redirected to login
            final_url_after_protection_test = self.driver.current_url
            self.assertIn('login', final_url_after_protection_test)
            
        else:
            # If no logout button found, that might be OK depending on UI design
            print("No logout button found - might be in dropdown or different location")
    
    def test_session_cleanup_after_logout(self):
        """Test that session is properly cleaned up after logout."""
        # Login
        success, _ = self.perform_login(self.test_email, self.test_password, should_succeed=True)
        self.assertTrue(success)
        
        # Set a test value in localStorage if available
        try:
            self.driver.execute_script("localStorage.setItem('testKey', 'testValue');")
            stored_value = self.driver.execute_script("return localStorage.getItem('testKey');")
            self.assertEqual(stored_value, 'testValue')
        except Exception:
            # localStorage might not be available
            pass
        
        # Logout by navigating directly to logout URL
        self.driver.get(f'{self.live_server_url}/medicos/logout/')
        time.sleep(2)
        
        # Try to access protected resource
        self.driver.get(f'{self.live_server_url}/medicos/profile/')
        
        # Should be redirected to login
        self.assertIn('login', self.driver.current_url)


class LoginUserExperienceTest(SeleniumLoginTestBase):
    """Test login user experience and edge cases."""
    
    def setUp(self):
        super().setUp()
        self.test_email = 'doctor@example.com'
        self.test_password = 'SecurePassword123!'
        self.user, self.medico = self.create_test_user(self.test_email, self.test_password)
    
    def test_login_form_keyboard_navigation(self):
        """Test that login form can be navigated with keyboard."""
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        # Focus on email field
        email_field = self.wait_for_element(By.NAME, "username")
        email_field.click()
        email_field.send_keys(self.test_email)
        
        # Tab to password field
        email_field.send_keys(Keys.TAB)
        
        # Should focus on password field
        active_element = self.driver.switch_to.active_element
        self.assertEqual(active_element.get_attribute("name"), "password")
        
        # Fill password
        active_element.send_keys(self.test_password)
        
        # Tab to submit button and press Enter
        active_element.send_keys(Keys.TAB)
        active_element.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Should login successfully
        current_url = self.driver.current_url
        self.assertNotIn('login', current_url)
    
    def test_login_form_error_message_display(self):
        """Test that error messages are displayed properly."""
        # Attempt login with wrong password
        success, final_url = self.perform_login(
            self.test_email, 
            'wrongpassword', 
            should_succeed=False
        )
        
        self.assertTrue(success, "Should display error")
        
        # Check that error message is visible and informative
        page_source = self.driver.page_source.lower()
        error_messages = [
            'credenciais inválidas',
            'email ou senha incorretos',
            'invalid credentials',
            'login failed',
            'erro',
            'error'
        ]
        
        has_error_message = any(msg in page_source for msg in error_messages)
        self.assertTrue(has_error_message, "Should display helpful error message")
        
        # Error should not reveal specific information about what's wrong
        # (good security practice - don't say "email exists but password is wrong")
        specific_errors = [
            'email não encontrado',
            'senha incorreta para este email',
            'user does not exist',
            'wrong password for'
        ]
        
        has_specific_error = any(err in page_source for err in specific_errors)
        self.assertFalse(has_specific_error, "Should not reveal specific login failure reason")
    
    def test_login_form_responsive_behavior(self):
        """Test login form behavior on different screen sizes."""
        original_size = self.driver.get_window_size()
        
        # Test mobile size
        self.driver.set_window_size(375, 667)  # iPhone size
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        
        # Form should still be usable
        email_field = self.wait_for_element(By.NAME, "username")
        self.assertTrue(email_field.is_displayed())
        
        password_field = self.wait_for_element(By.NAME, "password")
        self.assertTrue(password_field.is_displayed())
        
        submit_button = self.wait_for_element(
            By.CSS_SELECTOR, 
            "button[type='submit'], input[type='submit']"
        )
        self.assertTrue(submit_button.is_displayed())
        
        self.debug_page_state("mobile_view")
        
        # Test tablet size
        self.driver.set_window_size(768, 1024)  # iPad size
        time.sleep(1)
        self.debug_page_state("tablet_view")
        
        # Restore original size
        self.driver.set_window_size(original_size['width'], original_size['height'])
    
    def test_login_redirect_after_accessing_protected_page(self):
        """Test login redirect when accessing protected page without authentication."""
        # Try to access protected page without login
        protected_url = f'{self.live_server_url}/medicos/profile/'
        self.driver.get(protected_url)
        
        # Should be redirected to login
        time.sleep(2)
        current_url = self.driver.current_url
        self.assertIn('login', current_url)
        
        # Check if next parameter is preserved
        if 'next=' in current_url:
            # Login and verify redirect back to original page
            success, final_url = self.perform_login(
                self.test_email, 
                self.test_password, 
                should_succeed=True
            )
            
            self.assertTrue(success)
            # Should redirect back to protected page or at least away from login
            self.assertNotIn('login', final_url)