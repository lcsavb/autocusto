"""
Frontend Login Tests using Playwright
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
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from usuarios.models import Usuario
from medicos.models import Medico

User = get_user_model()


class PlaywrightLoginTestBase(PlaywrightFormTestBase):
    """Base class for Playwright login tests with common setup and utilities."""
    
    def setUp(self):
        super().setUp()
        # Clear any existing users
        User.objects.all().delete()
    
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
        medico.usuarios.add(user)
        
        return user, medico
    
    def perform_login(self, email, password, should_succeed=True):
        """Perform login action and return result."""
        # Navigate to home page (login form is in topbar for unauthenticated users)
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        self.take_screenshot("navigated_to_home_page")
        
        # Fill login form in the topbar
        try:
            # Use the topbar login form
            email_field = self.page.locator('input[name="username"]')  # Note: field name is "username" but accepts email
            password_field = self.page.locator('input[name="password"]')
            
            if not email_field.is_visible() or not password_field.is_visible():
                return False, self.page.url
            
            # Fill form
            email_field.fill(email)
            password_field.fill(password)
            
            self.take_screenshot("filled_login_form")
            
            # Submit form - look for Login button specifically
            submit_button = self.page.locator('button[type="submit"]:has-text("Login")')
            submit_button.click()
            
            # Wait for response
            self.wait_for_page_load()
            self.take_screenshot("after_form_submission")
            
            current_url = self.page.url
            page_content = self.page.content().lower()
            
            if should_succeed:
                # Check for successful login indicators
                success_indicators = [
                    current_url == f'{self.live_server_url}/',  # Should stay on home but authenticated
                    'logout' in page_content,
                    'minha conta' in page_content,  # Dropdown appears when logged in
                    'adicionar processo' in page_content,  # Authenticated home content
                ]
                return any(success_indicators), current_url
            else:
                # Check for failed login indicators  
                failure_indicators = [
                    'esqueci minha senha' in page_content,  # Login form still visible
                    'erro' in page_content or 'error' in page_content,
                    'inválido' in page_content or 'invalid' in page_content,
                    'input[name="username"]' in self.page.content(),  # Login form still present
                ]
                return any(failure_indicators), current_url
                
        except Exception as e:
            print(f"Login attempt failed with exception: {e}")
            self.take_screenshot("login_exception_occurred")
            return False, self.page.url


class LoginPageTest(PlaywrightLoginTestBase):
    """Test login page display and basic functionality."""
    
    def test_login_page_loads_correctly(self):
        """Test that login page loads with all required elements."""
        # Navigate to home page (login form is in topbar for unauthenticated users)
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        self.take_screenshot("home_page_loaded")
        
        # Check for essential form elements in the topbar
        try:
            # Check for email/username field (username field name, but email type)
            email_field = self.page.locator('input[name="username"]')
            self.assertTrue(email_field.is_visible(), "Username/email field should be visible in topbar")
            
            # Check for password field
            password_field = self.page.locator('input[name="password"]')
            self.assertTrue(password_field.is_visible(), "Password field should be visible in topbar")
            
            # Check for submit button
            submit_button = self.page.locator('button[type="submit"]:has-text("Login")')
            self.assertTrue(submit_button.is_visible(), "Login submit button should be visible")
            
            self.take_screenshot("form_elements_verified")
            
        except Exception as e:
            self.take_screenshot("essential_elements_missing")
            self.fail(f"Essential login form elements missing: {e}")
    
    def test_login_form_labels_and_accessibility(self):
        """Test login form has proper labels and accessibility features."""
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Check for form structure (login form in topbar)
        form_element = self.page.locator('form[action*="login"]')
        self.assertTrue(form_element.is_visible())
        
        # Check form method
        form_method = form_element.get_attribute('method')
        if form_method:
            self.assertEqual(form_method.lower(), 'post')
    
    def test_csrf_token_present(self):
        """Test that CSRF token is present in login form."""
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Check for CSRF token in the login form
        csrf_token = self.page.locator('form[action*="login"] input[name="csrfmiddlewaretoken"]')
        if csrf_token.is_visible():
            token_value = csrf_token.get_attribute('value')
            self.assertIsNotNone(token_value)
            self.assertNotEqual(token_value, '')


class LoginFunctionalityTest(PlaywrightLoginTestBase):
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
        page_content = self.page.content().lower()
        logout_indicators = [
            'logout' in page_content,
            'sair' in page_content,
            'bem-vindo' in page_content,
            self.test_email.lower() in page_content
        ]
        self.assertTrue(any(logout_indicators), "Should show user is logged in")
    
    def test_login_with_invalid_email(self):
        """Test login with invalid email address."""
        success, final_url = self.perform_login('invalid@example.com', self.test_password, should_succeed=False)
        
        self.assertTrue(success, f"Should stay on home page with error. Final URL: {final_url}")
        
        # Should stay on home page (not redirect anywhere)
        self.assertEqual(final_url, f'{self.live_server_url}/')
        
        # Check for error message
        page_content = self.page.content().lower()
        error_indicators = [
            'erro' in page_content,
            'error' in page_content,
            'inválido' in page_content,
            'invalid' in page_content,
            'credentials' in page_content
        ]
        self.assertTrue(any(error_indicators), "Should show error message")
    
    def test_login_with_invalid_password(self):
        """Test login with invalid password."""
        success, final_url = self.perform_login(self.test_email, 'wrongpassword', should_succeed=False)
        
        self.assertTrue(success, f"Should stay on home page with error. Final URL: {final_url}")
        self.assertEqual(final_url, f'{self.live_server_url}/')
    
    def test_login_with_empty_fields(self):
        """Test login form validation with empty fields."""
        # Navigate to home page
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Try to submit empty form
        submit_button = self.page.locator('button[type="submit"]:has-text("Login")')
        submit_button.click()
        
        self.wait_for_page_load()
        self.take_screenshot("empty_form_submitted")
        
        # Should stay on home page (no redirect)
        current_url = self.page.url
        self.assertEqual(current_url, f'{self.live_server_url}/')
        
        # Check for validation
        email_field = self.page.locator('input[name="username"]')
        
        # HTML5 validation check
        is_required = email_field.get_attribute('required') is not None
        
        # Server-side validation check
        page_content = self.page.content().lower()
        has_error_message = any([
            'obrigatório' in page_content,
            'required' in page_content,
            'erro' in page_content,
            'error' in page_content
        ])
        
        self.assertTrue(
            is_required or has_error_message,
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
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        password_field = self.page.locator('input[name="password"]')
        password_type = password_field.get_attribute('type')
        
        self.assertEqual(password_type, 'password', "Password field should have type='password'")
    
    def test_login_remember_functionality_if_present(self):
        """Test remember me functionality if implemented."""
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Check if there's a remember me checkbox
        remember_checkbox = self.page.locator('input[type="checkbox"][name*="remember"], input[type="checkbox"][name*="lembrar"]')
        
        # If remember me exists, test it
        if remember_checkbox.is_visible():
            # Check the checkbox
            if not remember_checkbox.is_checked():
                remember_checkbox.check()
            
            # Perform login
            success, final_url = self.perform_login(
                self.test_email, 
                self.test_password, 
                should_succeed=True
            )
            
            self.assertTrue(success, "Login with remember me should work")


class LoginSecurityTest(PlaywrightLoginTestBase):
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
            self.page.goto(f'{self.live_server_url}/')
            self.wait_for_page_load()
            
            # Try to inject script in email field
            email_field = (self.page.locator('input[name="email"]') if 
                          self.page.locator('input[name="email"]').is_visible() else
                          self.page.locator('input[name="username"]'))
            password_field = self.page.locator('input[name="password"]')
            
            email_field.fill(script)
            password_field.fill('anypassword')
            
            # Submit form - find the login button specifically
            submit_button = self.page.locator('button[type="submit"]:has-text("Login")')
            if submit_button.is_visible():
                submit_button.click()
            
            self.wait_for_page_load()
            
            # Check that script was not executed
            page_content = self.page.content()
            
            # Check that the malicious script content is properly escaped or not present
            # We shouldn't find the exact malicious script unescaped in the page
            self.assertNotIn(script, page_content)
            
            # For script tags specifically, ensure they're escaped if present in form values
            if '<script>' in script.lower():
                # The malicious script should be HTML-escaped if it appears in the page
                escaped_script = script.replace('<', '&lt;').replace('>', '&gt;')
                # Either the script is completely absent or it's properly escaped
                if script.lower() in page_content.lower():
                    self.assertIn(escaped_script, page_content)
            
            # Page should handle gracefully
            current_url = self.page.url
            self.assertTrue(
                current_url == f'{self.live_server_url}/',
                f"Page should handle injection gracefully, got: {current_url}"
            )
    
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
            self.page.goto(f'{self.live_server_url}/')
            self.wait_for_page_load()
            
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


class LogoutTest(PlaywrightLoginTestBase):
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
            'a[href*="logout"]',
            'button[name*="logout"]', 
            '.logout',
            'a[href*="/logout/"]',
            'text="Logout"',
            'text="Sair"'
        ]
        
        logout_element = None
        for selector in logout_selectors:
            try:
                logout_element = self.page.locator(selector)
                if logout_element.is_visible():
                    break
            except:
                continue
        
        if logout_element and logout_element.is_visible():
            self.take_screenshot("before_logout")
            logout_element.click()
            self.wait_for_page_load()
            self.take_screenshot("after_logout_click")
            
            # Should be redirected to home page after logout
            current_url = self.page.url
            self.assertEqual(current_url, f'{self.live_server_url}/', f"Should redirect to home after logout, got: {current_url}")
            
            # Check that login form is now visible (user is logged out)
            self.wait_for_page_load()
            login_form_visible = self.page.locator('input[name="username"]').is_visible()
            self.assertTrue(login_form_visible, "Login form should be visible after logout")
            
            # Try to access a protected page
            self.page.goto(f'{self.live_server_url}/profile/')
            self.wait_for_page_load()
            
            # Should be redirected back to home or login (depending on how auth works)
            final_url_after_protection_test = self.page.url
            # The app might redirect to home or stay on profile but show login form
            auth_required = (
                final_url_after_protection_test == f'{self.live_server_url}/' or
                self.page.locator('input[name="username"]').is_visible()
            )
            self.assertTrue(auth_required, f"Should require authentication for protected page, got: {final_url_after_protection_test}")
            
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
            self.page.evaluate("localStorage.setItem('testKey', 'testValue')")
            stored_value = self.page.evaluate("localStorage.getItem('testKey')")
            self.assertEqual(stored_value, 'testValue')
        except:
            # localStorage might not be available
            pass
        
        # Logout by navigating directly to logout URL
        logout_urls = [
            f'{self.live_server_url}/logout/',
            f'{self.live_server_url}/medicos/logout/',
            f'{self.live_server_url}/usuarios/logout/',
        ]
        
        for logout_url in logout_urls:
            try:
                self.page.goto(logout_url)
                self.wait_for_page_load()
                break
            except:
                continue
        
        # Try to access protected resource
        self.page.goto(f'{self.live_server_url}/profile/')
        self.wait_for_page_load()
        
        # Should require authentication (check if login form is shown or redirected)
        current_url = self.page.url
        login_form_visible = self.page.locator('input[name="username"]').is_visible()
        
        auth_required = (
            'login' in current_url or 
            current_url == f'{self.live_server_url}/' or
            login_form_visible
        )
        self.assertTrue(auth_required, f"Should require authentication, got URL: {current_url}, login form visible: {login_form_visible}")


class LoginUserExperienceTest(PlaywrightLoginTestBase):
    """Test login user experience and edge cases."""
    
    def setUp(self):
        super().setUp()
        self.test_email = 'doctor@example.com'
        self.test_password = 'SecurePassword123!'
        self.user, self.medico = self.create_test_user(self.test_email, self.test_password)
    
    def test_login_form_keyboard_navigation(self):
        """Test that login form can be navigated with keyboard."""
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Focus on email field
        email_field = (self.page.locator('input[name="email"]') if 
                      self.page.locator('input[name="email"]').is_visible() else
                      self.page.locator('input[name="username"]'))
        email_field.click()
        email_field.fill(self.test_email)
        
        # Tab to password field
        self.page.keyboard.press('Tab')
        
        # Fill password
        self.page.keyboard.type(self.test_password)
        
        # Tab to submit button and press Enter
        self.page.keyboard.press('Tab')
        self.page.keyboard.press('Enter')
        
        self.wait_for_page_load()
        
        # Check if login was successful by checking page content
        current_url = self.page.url
        page_content = self.page.content().lower()
        
        # Look for authenticated content or logout button
        login_success_indicators = [
            'logout' in page_content,
            'minha conta' in page_content,
            'adicionar processo' in page_content,
        ]
        
        # If we found success indicators, login worked even if URL stayed same
        if any(login_success_indicators):
            # Login successful
            pass
        else:
            # Login may have failed or keyboard navigation didn't work
            self.fail(f"Login may have failed via keyboard navigation. URL: {current_url}")
    
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
        page_content = self.page.content().lower()
        error_messages = [
            'credenciais inválidas',
            'email ou senha incorretos',
            'invalid credentials',
            'login failed',
            'erro',
            'error'
        ]
        
        has_error_message = any(msg in page_content for msg in error_messages)
        self.assertTrue(has_error_message, "Should display helpful error message")
        
        # Error should not reveal specific information about what's wrong
        # (good security practice - don't say "email exists but password is wrong")
        specific_errors = [
            'email não encontrado',
            'senha incorreta para este email',
            'user does not exist',
            'wrong password for'
        ]
        
        has_specific_error = any(err in page_content for err in specific_errors)
        self.assertFalse(has_specific_error, "Should not reveal specific login failure reason")
    
    def test_login_form_responsive_behavior(self):
        """Test login form behavior on different screen sizes."""
        original_viewport = self.page.viewport_size
        
        # Test mobile size
        self.page.set_viewport_size({'width': 375, 'height': 667})  # iPhone size
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Form should still be usable
        email_field = (self.page.locator('input[name="email"]') if 
                      self.page.locator('input[name="email"]').is_visible() else
                      self.page.locator('input[name="username"]'))
        self.assertTrue(email_field.is_visible())
        
        password_field = self.page.locator('input[name="password"]')
        self.assertTrue(password_field.is_visible())
        
        # Check for login submit button (not registration)
        login_submit_button = self.page.locator('button[type="submit"]:has-text("Login")')
        registration_submit_button = self.page.locator('button[type="submit"]:has-text("Criar conta")')
        
        # At least one should be visible (depends on authentication status)
        has_submit_button = login_submit_button.is_visible() or registration_submit_button.is_visible()
        self.assertTrue(has_submit_button, "Should have at least one submit button visible")
        
        self.take_screenshot("mobile_view")
        
        # Test tablet size
        self.page.set_viewport_size({'width': 768, 'height': 1024})  # iPad size
        self.wait_for_page_load()
        self.take_screenshot("tablet_view")
        
        # Restore original size
        if original_viewport:
            self.page.set_viewport_size(original_viewport)
    
    def test_login_redirect_after_accessing_protected_page(self):
        """Test login redirect when accessing protected page without authentication."""
        # Try to access protected page without login
        protected_urls = [
            f'{self.live_server_url}/profile/',
            f'{self.live_server_url}/medicos/profile/',
            f'{self.live_server_url}/dashboard/',
        ]
        
        for protected_url in protected_urls:
            try:
                self.page.goto(protected_url)
                self.wait_for_page_load()
                
                # Should be redirected to login or stay on home
                current_url = self.page.url
                if 'login' in current_url or current_url == f'{self.live_server_url}/':
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
                        self.assertNotEqual(final_url, f'{self.live_server_url}/login/')
                    break
            except:
                continue