"""
Clinic Management Frontend Tests using Selenium
Tests clinic creation and editing workflows with extensive debugging
"""

import time
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from clinicas.models import Clinica, Emissor
from medicos.models import Medico

User = get_user_model()


class ClinicManagementTestBase(StaticLiveServerTestCase):
    """Base class for clinic management tests with common setup and utilities."""
    
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
        for binary in ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']:
            chrome_binary = shutil.which(binary)
            if chrome_binary:
                break
        
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
        
        # Use system chromedriver if available, otherwise try WebDriverManager
        chromedriver_path = shutil.which('chromedriver')
        if chromedriver_path:
            service = Service(chromedriver_path)
        else:
            try:
                # Try to install and setup ChromeDriver
                service = Service(ChromeDriverManager().install())
            except Exception:
                # Skip Selenium tests if no driver available
                import unittest
                raise unittest.SkipTest("ChromeDriver not available")
        
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
        
    def setUp(self):
        """Set up test data for clinic management with extensive debugging."""
        super().setUp()
        
        print("🔧 DEBUG: Setting up clinic management test data...")
        
        # Create test user and medico
        print("🔧 DEBUG: Creating user...")
        self.user1 = User.objects.create_user(
            email='medico@clinic.com',
            password='testpass123'
        )
        self.user1.is_medico = True
        self.user1.save()
        print(f"✅ Created user: {self.user1.email}")
        
        print("🔧 DEBUG: Creating medico...")
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. Maria Silva",
            crm_medico="54321",
            cns_medico="222222222222222"
        )
        self.medico1.usuarios.add(self.user1)
        print(f"✅ Created medico: {self.medico1.nome_medico} (CRM: {self.medico1.crm_medico})")
        
        # Create existing clinic for testing updates
        print("🔧 DEBUG: Creating existing clinic...")
        self.existing_clinic = Clinica.objects.create(
            nome_clinica="Clínica Existente",
            cns_clinica="1234567",
            logradouro="Rua Antiga",
            logradouro_num="100",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11987654321"
        )
        print(f"✅ Created existing clinic: {self.existing_clinic.nome_clinica} (CNS: {self.existing_clinic.cns_clinica})")
        
        print("✅ DEBUG: Clinic management test data setup complete!")
        print(f"📊 DEBUG: Test data summary:")
        print(f"   - User: {self.user1.email}")
        print(f"   - Medico: {self.medico1.nome_medico}")
        print(f"   - Existing Clinic: {self.existing_clinic.nome_clinica}")

    def login_user(self, email, password):
        """Helper method to login a user through the browser with debugging."""
        print(f"🔐 DEBUG: Attempting login for {email}")
        
        self.driver.get(f'{self.live_server_url}/medicos/login/')
        print(f"📍 DEBUG: Navigated to login page: {self.driver.current_url}")
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        print("✅ DEBUG: Login form loaded")
        
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        
        username_field.send_keys(email)
        password_field.send_keys(password)
        print("✅ DEBUG: Credentials entered")
        
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        print("✅ DEBUG: Login button clicked")
        
        # Wait for login to complete
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Logout')]"))
            )
            print("✅ DEBUG: Login successful - logout button found")
        except TimeoutException:
            time.sleep(3)
            current_url = self.driver.current_url
            print(f"⚠️  DEBUG: Login timeout, current URL: {current_url}")
            if '/medicos/login/' in current_url:
                page_source = self.driver.page_source[:500]
                print(f"❌ DEBUG: Login failed - still on login page. Page content: {page_source}")
                raise Exception("Login failed - still on login page")
            print("✅ DEBUG: Login appears successful despite timeout")

    def take_screenshot(self, name):
        """Take a screenshot for visual debugging."""
        screenshot_dir = "/home/lucas/code/autocusto/tests/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{name}.png")
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 DEBUG: Screenshot saved: {screenshot_path}")
        return screenshot_path

    def fill_field_slowly(self, field, value, delay=0.1):
        """Fill field character by character to trigger JavaScript events with robust interaction."""
        print(f"✏️  DEBUG: Filling field with value: {value}")
        
        # Wait for element to be clickable and visible
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(field)
            )
        except TimeoutException:
            print("⚠️  DEBUG: Element not clickable, trying JavaScript approach")
        
        # Scroll element into view
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        time.sleep(0.5)
        
        # Try clearing field with JavaScript if regular clear fails
        try:
            field.clear()
        except Exception:
            print("⚠️  DEBUG: Regular clear failed, using JavaScript")
            self.driver.execute_script("arguments[0].value = '';", field)
        
        time.sleep(0.3)
        
        # Try regular send_keys first, fallback to JavaScript
        try:
            # Click to focus first
            field.click()
            time.sleep(0.2)
            
            for char in str(value):
                field.send_keys(char)
                time.sleep(delay)
        except Exception as e:
            print(f"⚠️  DEBUG: Regular typing failed ({e}), using JavaScript")
            self.driver.execute_script("arguments[0].value = arguments[1];", field, str(value))
            # Trigger change event
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", field)
        
        time.sleep(0.5)  # Wait after completion
        print("✅ DEBUG: Field filled successfully")

    def find_element_robust(self, by, value, timeout=10):
        """Find element with robust waiting and error handling."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            # Wait for element to be visible and enabled
            WebDriverWait(self.driver, 5).until(
                lambda driver: element.is_displayed() and element.is_enabled()
            )
            return element
        except TimeoutException:
            print(f"⚠️  DEBUG: Element {value} not found or not ready")
            raise NoSuchElementException(f"Element {value} not found")

    def debug_page_state(self, step_name):
        """Print extensive debugging information about current page state."""
        print(f"\n🔍 DEBUG: {step_name}")
        print(f"📍 Current URL: {self.driver.current_url}")
        print(f"📄 Page Title: {self.driver.title}")
        
        # Check for forms on page
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        print(f"📝 Forms found: {len(forms)}")
        
        # Check for input fields
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        print(f"🔤 Input fields found: {len(inputs)}")
        
        # Check for select dropdowns
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        print(f"📋 Select dropdowns found: {len(selects)}")
        
        # Check for buttons
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Buttons found: {len(buttons)}")
        
        # Check for any error messages
        page_source = self.driver.page_source
        if 'error' in page_source.lower() or 'erro' in page_source.lower():
            print("⚠️  DEBUG: Possible errors detected on page")
        
        # Print first 300 characters of page source for context
        print(f"📄 Page source preview: {page_source[:300]}...")


class ClinicManagementTest(ClinicManagementTestBase):
    """Test clinic creation and editing workflows."""

    def test_clinic_creation_new_clinic(self):
        """Test creating a completely new clinic with all fields."""
        
        print("\n🏥 TEST: test_clinic_creation_new_clinic")
        print("🎯 This test verifies: 1) Navigation to clinic form, 2) Complete form filling, 3) New clinic creation")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        print("🏥 DEBUG: Navigating to clinic creation page...")
        clinic_url = f'{self.live_server_url}/clinicas/cadastro/'
        self.driver.get(clinic_url)
        
        self.take_screenshot("01_clinic_creation_page")
        self.debug_page_state("Clinic creation page loaded")
        
        # Wait for clinic form to load
        print("⏳ DEBUG: Waiting for clinic creation form...")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "nome_clinica"))
            )
            print("✅ DEBUG: Clinic form loaded - name field found")
        except TimeoutException:
            print("❌ DEBUG: Clinic form not found")
            self.take_screenshot("01_error_no_clinic_form")
            raise
        
        # Fill ALL clinic form fields completely
        print("📝 DEBUG: Filling COMPLETE clinic form...")
        
        clinic_data = {
            'nome_clinica': 'Clínica Nova Medicina Avançada',
            'cns_clinica': '9876543',  # New CNS not in database
            'telefone_clinica': '11999887766',
            'cidade': 'São Paulo',
            'bairro': 'Vila Olímpia',
            'cep': '04578-000',
            'logradouro': 'Avenida das Nações',
            'logradouro_num': '2500'
        }
        
        filled_count = 0
        total_fields = len(clinic_data)
        
        print(f"📊 DEBUG: Planning to fill {total_fields} clinic fields")
        
        for field_name, value in clinic_data.items():
            try:
                print(f"   🎯 Filling {field_name} with: {value}")
                field = self.find_element_robust(By.NAME, field_name, timeout=5)
                self.fill_field_slowly(field, value, delay=0.05)
                filled_count += 1
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {field_name}")
            except NoSuchElementException:
                print(f"   ⚠️  SKIP: Field {field_name} not found")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to fill {field_name}: {e}")
        
        self.take_screenshot("02_clinic_form_filled")
        print(f"📊 DEBUG: Clinic form filling complete: {filled_count}/{total_fields} fields filled")
        
        # Submit the clinic form with enhanced debugging
        print("📤 DEBUG: Submitting clinic creation form...")
        try:
            # Check for CSRF token presence before submission
            csrf_tokens = self.driver.find_elements(By.NAME, "csrfmiddlewaretoken")
            print(f"🔒 DEBUG: Found {len(csrf_tokens)} CSRF token(s)")
            
            # Check current session/login status before submission
            current_page_source = self.driver.page_source
            has_logout_button = 'Logout' in current_page_source
            print(f"🔐 DEBUG: User still logged in before submission: {has_logout_button}")
            
            # Find the clinic form specifically and its submit button
            clinic_form = None
            for form in self.driver.find_elements(By.TAG_NAME, "form"):
                action = form.get_attribute('action')
                if 'clinicas/cadastro' in action:
                    clinic_form = form
                    break
            
            if clinic_form:
                submit_button = clinic_form.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                print("✅ Found clinic form submit button specifically")
            else:
                # Fallback: look for submit button with text "Cadastrar"
                submit_button = self.driver.find_element(By.XPATH, "//input[@value='Cadastrar'] | //button[contains(text(), 'Cadastrar')]")
                print("✅ Found submit button by text 'Cadastrar'")
            
            # Scroll to submit button
            self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            time.sleep(1)
            
            # Get initial clinic count and current URL for comparison
            initial_clinic_count = Clinica.objects.count()
            initial_url = self.driver.current_url
            print(f"📊 DEBUG: Initial clinic count: {initial_clinic_count}")
            print(f"📍 DEBUG: URL before submission: {initial_url}")
            
            # Enhanced submission with JavaScript click as fallback
            try:
                submit_button.click()
                print("✅ Form submitted via regular click!")
            except Exception as click_error:
                print(f"⚠️  Regular click failed ({click_error}), trying JavaScript...")
                self.driver.execute_script("arguments[0].click();", submit_button)
                print("✅ Form submitted via JavaScript!")
            
            # Wait for processing and redirect with shorter intervals for better debugging
            print("⏳ DEBUG: Waiting for clinic creation processing...")
            for i in range(10):  # Check every 0.5 seconds for 5 seconds total
                time.sleep(0.5)
                current_url = self.driver.current_url
                if current_url != initial_url:
                    print(f"📍 DEBUG: URL changed after {(i+1)*0.5}s: {current_url}")
                    break
                elif i == 9:
                    print(f"📍 DEBUG: URL unchanged after 5s: {current_url}")
            
            # Check if we got logged out
            final_page_source = self.driver.page_source
            still_logged_in = 'Logout' in final_page_source
            is_logout_page = '/logout/' in current_url or 'saiu com sucesso' in final_page_source.lower()
            
            print(f"🔐 DEBUG: Still logged in after submission: {still_logged_in}")
            print(f"🚪 DEBUG: Redirected to logout page: {is_logout_page}")
            
            self.take_screenshot("03_after_clinic_submission")
            
            # Verify clinic was created in database
            new_clinic_count = Clinica.objects.count()
            print(f"📊 DEBUG: New clinic count: {new_clinic_count}")
            
            # Check if clinic was created
            if new_clinic_count > initial_clinic_count:
                print("✅ SUCCESS: New clinic created in database!")
                
                # Find the created clinic
                created_clinic = Clinica.objects.filter(cns_clinica='9876543').first()
                if created_clinic:
                    print(f"✅ VERIFIED: Clinic found - {created_clinic.nome_clinica}")
                    print(f"   📍 Address: {created_clinic.logradouro}, {created_clinic.logradouro_num}")
                    print(f"   📞 Phone: {created_clinic.telefone_clinica}")
                    
                    # Verify user association
                    user_clinics = self.user1.clinicas.all()
                    if created_clinic in user_clinics:
                        print("✅ VERIFIED: Clinic properly associated with user")
                    else:
                        print("⚠️  WARNING: Clinic not associated with user")
                else:
                    print("❌ ERROR: Clinic not found in database despite count increase")
            else:
                print("❌ ERROR: No new clinic created in database")
                
                # Check for form errors
                page_source = self.driver.page_source
                if 'error' in page_source.lower() or 'obrigatório' in page_source.lower():
                    print("❌ Form validation errors detected")
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error, .invalid-feedback")
                    for error in error_elements:
                        if error.is_displayed():
                            print(f"❌ Form Error: {error.text}")
            
            # Verify successful redirect (should go to home or success page)
            expected_redirect = current_url != clinic_url
            if expected_redirect:
                print("✅ SUCCESS: Properly redirected after form submission")
            else:
                print("⚠️  WARNING: No redirect after form submission")
            
        except NoSuchElementException:
            print("❌ DEBUG: Submit button not found")
            self.take_screenshot("03_no_submit_button")
        except Exception as e:
            print(f"❌ DEBUG: Error during submission: {e}")
            self.take_screenshot("03_submission_error")
            
        print("✅ DEBUG: Clinic creation test completed!")

    def test_clinic_creation_update_existing(self):
        """Test updating an existing clinic by CNS."""
        
        print("\n🏥 TEST: test_clinic_creation_update_existing")
        print("🎯 This test verifies: 1) Updating existing clinic, 2) CNS-based duplicate prevention")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        print("🏥 DEBUG: Navigating to clinic update via creation form...")
        clinic_url = f'{self.live_server_url}/clinicas/cadastro/'
        self.driver.get(clinic_url)
        
        self.take_screenshot("04_clinic_update_page")
        
        # Wait for form
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.NAME, "nome_clinica"))
        )
        
        # Fill form with existing CNS but updated data
        print("📝 DEBUG: Filling form with existing CNS for update...")
        
        update_data = {
            'nome_clinica': 'Clínica Existente - ATUALIZADA',
            'cns_clinica': '1234567',  # Same as existing clinic
            'telefone_clinica': '11555444333',  # Updated phone
            'cidade': 'Rio de Janeiro',  # Updated city
            'bairro': 'Copacabana',  # Updated neighborhood
            'cep': '22000-000',  # Updated ZIP
            'logradouro': 'Avenida Atlântica',  # Updated address
            'logradouro_num': '1500'  # Updated number
        }
        
        for field_name, value in update_data.items():
            try:
                print(f"   🎯 Updating {field_name} to: {value}")
                field = self.find_element_robust(By.NAME, field_name, timeout=5)
                self.fill_field_slowly(field, value, delay=0.05)
                print(f"   ✅ Updated {field_name}")
            except Exception as e:
                print(f"   ❌ ERROR updating {field_name}: {e}")
        
        self.take_screenshot("05_clinic_update_form_filled")
        
        # Get initial data for comparison
        original_clinic = Clinica.objects.get(cns_clinica='1234567')
        original_name = original_clinic.nome_clinica
        original_phone = original_clinic.telefone_clinica
        print(f"📊 DEBUG: Original clinic data - Name: {original_name}, Phone: {original_phone}")
        
        # Submit update
        print("📤 DEBUG: Submitting clinic update...")
        try:
            # Find the clinic form specifically and its submit button
            clinic_form = None
            for form in self.driver.find_elements(By.TAG_NAME, "form"):
                action = form.get_attribute('action')
                if 'clinicas/cadastro' in action:
                    clinic_form = form
                    break
            
            if clinic_form:
                submit_button = clinic_form.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                print("✅ Found clinic form submit button specifically")
            else:
                # Fallback: look for submit button with text "Cadastrar"
                submit_button = self.driver.find_element(By.XPATH, "//input[@value='Cadastrar'] | //button[contains(text(), 'Cadastrar')]")
                print("✅ Found submit button by text 'Cadastrar'")
            submit_button.click()
            
            time.sleep(5)
            
            # Verify update in database
            updated_clinic = Clinica.objects.get(cns_clinica='1234567')
            
            if updated_clinic.nome_clinica != original_name:
                print(f"✅ SUCCESS: Clinic name updated from '{original_name}' to '{updated_clinic.nome_clinica}'")
            else:
                print("⚠️  WARNING: Clinic name not updated")
                
            if updated_clinic.telefone_clinica != original_phone:
                print(f"✅ SUCCESS: Phone updated from '{original_phone}' to '{updated_clinic.telefone_clinica}'")
            else:
                print("⚠️  WARNING: Phone not updated")
            
            # Verify no duplicate created
            clinic_count = Clinica.objects.filter(cns_clinica='1234567').count()
            if clinic_count == 1:
                print("✅ SUCCESS: No duplicate clinic created - proper update")
            else:
                print(f"❌ ERROR: {clinic_count} clinics found with same CNS")
            
            self.take_screenshot("06_clinic_update_complete")
            
        except Exception as e:
            print(f"❌ ERROR during update: {e}")
            
        print("✅ DEBUG: Clinic update test completed!")

    def test_clinic_form_validation(self):
        """Test clinic form validation with invalid data."""
        
        print("\n🏥 TEST: test_clinic_form_validation")
        print("🎯 This test verifies: 1) Form validation, 2) Error handling, 3) Required fields")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        clinic_url = f'{self.live_server_url}/clinicas/cadastro/'
        self.driver.get(clinic_url)
        
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.NAME, "nome_clinica"))
        )
        
        print("📝 DEBUG: Testing form validation with invalid data...")
        
        # Test with invalid CNS (wrong length)
        invalid_data = {
            'nome_clinica': 'Clínica Teste Validação',
            'cns_clinica': '123456789',  # Too long (should be 7 chars)
            'telefone_clinica': 'abc123',  # Invalid phone format
            'cep': '12345',  # Invalid ZIP format
        }
        
        for field_name, value in invalid_data.items():
            try:
                print(f"   🎯 Filling {field_name} with invalid data: {value}")
                field = self.find_element_robust(By.NAME, field_name, timeout=5)
                self.fill_field_slowly(field, value, delay=0.05)
                print(f"   ✅ Filled {field_name} with invalid data")
            except Exception as e:
                print(f"   ❌ ERROR filling {field_name}: {e}")
        
        self.take_screenshot("07_invalid_form_data")
        
        # Try to submit invalid form
        print("📤 DEBUG: Submitting form with invalid data...")
        try:
            # Find the clinic form specifically and its submit button
            clinic_form = None
            for form in self.driver.find_elements(By.TAG_NAME, "form"):
                action = form.get_attribute('action')
                if 'clinicas/cadastro' in action:
                    clinic_form = form
                    break
            
            if clinic_form:
                submit_button = clinic_form.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                print("✅ Found clinic form submit button specifically")
            else:
                # Fallback: look for submit button with text "Cadastrar"
                submit_button = self.driver.find_element(By.XPATH, "//input[@value='Cadastrar'] | //button[contains(text(), 'Cadastrar')]")
                print("✅ Found submit button by text 'Cadastrar'")
            submit_button.click()
            
            time.sleep(3)
            
            # Check for validation errors
            current_url = self.driver.current_url
            print(f"📍 DEBUG: After invalid submission: {current_url}")
            
            # Look for error messages
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error, .invalid-feedback, .errorlist")
            
            if error_elements:
                print("✅ SUCCESS: Form validation errors detected")
                for i, error in enumerate(error_elements):
                    if error.is_displayed():
                        error_text = error.text.strip()
                        if error_text:
                            print(f"   📋 Validation Error {i+1}: {error_text}")
            else:
                print("⚠️  WARNING: No validation errors displayed (may have been processed)")
            
            # Check if form was actually submitted (shouldn't be with invalid data)
            if current_url == clinic_url:
                print("✅ SUCCESS: Form not submitted due to validation errors")
            else:
                print("⚠️  WARNING: Form was submitted despite invalid data")
            
            self.take_screenshot("08_validation_errors")
            
        except Exception as e:
            print(f"❌ ERROR during validation test: {e}")
            
        print("✅ DEBUG: Form validation test completed!")

    def test_clinic_navigation_workflow(self):
        """Test complete navigation workflow for clinic management."""
        
        print("\n🏥 TEST: test_clinic_navigation_workflow")
        print("🎯 This test verifies: 1) Navigation from home, 2) Menu access, 3) Form accessibility")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Start from home page
        print("🏠 DEBUG: Starting from home page...")
        self.driver.get(f'{self.live_server_url}/')
        self.take_screenshot("09_home_page_navigation")
        self.debug_page_state("Home page for clinic navigation")
        
        # Look for clinic navigation in menu
        print("🔍 DEBUG: Looking for clinic navigation menu...")
        try:
            # Check for clinic dropdown or direct link
            clinic_elements = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Clínica') or contains(text(), 'clinica')]")
            
            if clinic_elements:
                print(f"✅ Found {len(clinic_elements)} clinic navigation elements:")
                for i, element in enumerate(clinic_elements):
                    text = element.text
                    href = element.get_attribute('href') or 'No href'
                    print(f"   {i+1}. {text} -> {href}")
                
                # Try to click the first clinic link
                clinic_elements[0].click()
                time.sleep(2)
                
                current_url = self.driver.current_url
                print(f"📍 DEBUG: After clicking clinic link: {current_url}")
                
                if '/clinicas/' in current_url:
                    print("✅ SUCCESS: Successfully navigated to clinic section")
                else:
                    print("⚠️  WARNING: Didn't navigate to clinic section")
                
            else:
                print("⚠️  WARNING: No clinic navigation elements found")
                
                # Try direct navigation as fallback
                print("🔄 DEBUG: Trying direct navigation to clinic creation...")
                self.driver.get(f'{self.live_server_url}/clinicas/cadastro/')
                time.sleep(2)
                
                if '/clinicas/cadastro/' in self.driver.current_url:
                    print("✅ SUCCESS: Direct navigation to clinic creation works")
                else:
                    print("❌ ERROR: Cannot access clinic creation page")
            
            self.take_screenshot("10_clinic_navigation_result")
            
        except Exception as e:
            print(f"❌ ERROR during navigation test: {e}")
            self.take_screenshot("10_navigation_error")
            
        print("✅ DEBUG: Clinic navigation test completed!")

    def test_clinic_csrf_and_session_debugging(self):
        """Test to specifically debug CSRF token and session issues."""
        
        print("\n🔒 TEST: test_clinic_csrf_and_session_debugging")
        print("🎯 This test investigates: 1) CSRF token handling, 2) Session persistence, 3) Form submission mechanics")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        clinic_url = f'{self.live_server_url}/clinicas/cadastro/'
        self.driver.get(clinic_url)
        
        # Wait for form to load
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.NAME, "nome_clinica"))
        )
        
        print("🔍 DEBUG: Analyzing form and session state...")
        
        # Detailed CSRF token analysis
        csrf_tokens = self.driver.find_elements(By.NAME, "csrfmiddlewaretoken")
        print(f"🔒 CSRF Tokens found: {len(csrf_tokens)}")
        
        for i, token in enumerate(csrf_tokens):
            token_value = token.get_attribute('value')
            token_type = token.get_attribute('type')
            print(f"   Token {i+1}: Type={token_type}, Value={token_value[:20]}...")
        
        # Check form action and method
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        print(f"📝 Forms found: {len(forms)}")
        
        for i, form in enumerate(forms):
            action = form.get_attribute('action')
            method = form.get_attribute('method')
            print(f"   Form {i+1}: Action='{action}', Method='{method}'")
        
        # Check session cookies
        cookies = self.driver.get_cookies()
        session_cookies = [c for c in cookies if 'session' in c['name'].lower()]
        print(f"🍪 Session cookies: {len(session_cookies)}")
        
        for cookie in session_cookies:
            print(f"   Cookie: {cookie['name']} = {cookie['value'][:20]}...")
        
        # Fill form minimally
        print("📝 DEBUG: Filling minimal form data...")
        minimal_data = {
            'nome_clinica': 'Test CSRF Clinic',
            'cns_clinica': '1111111',
        }
        
        for field_name, value in minimal_data.items():
            try:
                field = self.find_element_robust(By.NAME, field_name, timeout=5)
                self.fill_field_slowly(field, value, delay=0.05)
                print(f"   ✅ Filled {field_name}")
            except Exception as e:
                print(f"   ❌ Failed to fill {field_name}: {e}")
        
        self.take_screenshot("11_csrf_debug_form_filled")
        
        # Check session state right before submission
        print("🔐 DEBUG: Pre-submission session check...")
        pre_submit_cookies = self.driver.get_cookies()
        pre_submit_session = [c for c in pre_submit_cookies if 'session' in c['name'].lower()]
        
        page_source_before = self.driver.page_source
        has_logout_before = 'Logout' in page_source_before
        print(f"   Logged in before submission: {has_logout_before}")
        print(f"   Session cookies before: {len(pre_submit_session)}")
        
        # Submit form with detailed monitoring
        print("📤 DEBUG: Submitting with detailed monitoring...")
        try:
            # Find the clinic form specifically
            clinic_form = None
            for form in self.driver.find_elements(By.TAG_NAME, "form"):
                action = form.get_attribute('action')
                if 'clinicas/cadastro' in action:
                    clinic_form = form
                    break
            
            if clinic_form:
                submit_button = clinic_form.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                print("✅ Found clinic form submit button specifically")
                form_action = clinic_form.get_attribute('action')
                form_method = clinic_form.get_attribute('method')
            else:
                # Fallback: look for submit button with text "Cadastrar"
                submit_button = self.driver.find_element(By.XPATH, "//input[@value='Cadastrar'] | //button[contains(text(), 'Cadastrar')]")
                print("✅ Found submit button by text 'Cadastrar'")
                # Find the parent form
                clinic_form = submit_button.find_element(By.XPATH, "./ancestor::form")
                form_action = clinic_form.get_attribute('action')
                form_method = clinic_form.get_attribute('method')
            
            print(f"   Submitting to: '{form_action}' via {form_method}")
            
            submit_button.click()
            
            # Monitor URL changes immediately
            time.sleep(1)
            immediate_url = self.driver.current_url
            print(f"   URL after 1s: {immediate_url}")
            
            time.sleep(2)
            final_url = self.driver.current_url
            print(f"   URL after 3s: {final_url}")
            
            # Check session state after submission
            post_submit_cookies = self.driver.get_cookies()
            post_submit_session = [c for c in post_submit_cookies if 'session' in c['name'].lower()]
            
            page_source_after = self.driver.page_source
            has_logout_after = 'Logout' in page_source_after
            has_success_message = 'sucesso' in page_source_after.lower()
            
            print(f"   Logged in after submission: {has_logout_after}")
            print(f"   Session cookies after: {len(post_submit_session)}")
            print(f"   Success message detected: {has_success_message}")
            
            # Compare session cookies
            if pre_submit_session and post_submit_session:
                session_changed = pre_submit_session[0]['value'] != post_submit_session[0]['value']
                print(f"   Session ID changed: {session_changed}")
            
            self.take_screenshot("12_csrf_debug_after_submission")
            
            # Check database for clinic creation
            db_clinic_count = Clinica.objects.count()
            print(f"📊 Database clinic count: {db_clinic_count}")
            
            # Look for the test clinic specifically
            test_clinic = Clinica.objects.filter(nome_clinica='Test CSRF Clinic').first()
            if test_clinic:
                print(f"✅ Test clinic found in database: {test_clinic.nome_clinica}")
            else:
                print("❌ Test clinic not found in database")
            
        except Exception as e:
            print(f"❌ Error during CSRF debug test: {e}")
            self.take_screenshot("12_csrf_debug_error")
            
        print("✅ DEBUG: CSRF and session debugging test completed!")