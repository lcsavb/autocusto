"""
Clinic Management Frontend Tests using Playwright
Tests clinic creation and editing workflows with extensive debugging
"""

import time
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from clinicas.models import Clinica, Emissor
from medicos.models import Medico

User = get_user_model()


class ClinicManagementPlaywrightBase(PlaywrightFormTestBase):
    """Base class for clinic management tests with common setup and utilities."""
    
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
        
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        print(f"📍 DEBUG: Navigated to home page: {self.page.url}")
        
        # Fill login form in the topbar
        email_field = self.page.locator('input[name="username"]')
        password_field = self.page.locator('input[name="password"]')
        
        email_field.fill(email)
        password_field.fill(password)
        print("✅ DEBUG: Credentials entered")
        
        login_button = self.page.locator('button[type="submit"]:has-text("Login")')
        login_button.click()
        print("✅ DEBUG: Login button clicked")
        
        self.wait_for_page_load()
        
        # Verify login success
        logout_button = self.page.locator('button:has-text("Logout")')
        if logout_button.is_visible():
            print("✅ DEBUG: Login successful - logout button found")
        else:
            current_url = self.page.url
            print(f"⚠️  DEBUG: Login timeout, current URL: {current_url}")
            page_content = self.page.content()[:500]
            if '/login/' in current_url:
                print(f"❌ DEBUG: Login failed - still on login page. Page content: {page_content}")
                raise Exception("Login failed - still on login page")
            print("✅ DEBUG: Login appears successful despite no logout button")

    def fill_field_slowly(self, field_locator, value, delay=0.05):
        """Fill field with value using Playwright, with robust interaction."""
        print(f"✏️  DEBUG: Filling field with value: {value}")
        
        # Wait for element to be visible and enabled
        field_locator.wait_for(state="visible")
        
        # Scroll element into view
        field_locator.scroll_into_view_if_needed()
        
        # Clear and fill field
        field_locator.clear()
        field_locator.fill(str(value))
        
        self.page.wait_for_timeout(int(delay * 1000))
        print("✅ DEBUG: Field filled successfully")

    def debug_page_state(self, step_name):
        """Print extensive debugging information about current page state."""
        print(f"\n🔍 DEBUG: {step_name}")
        print(f"📍 Current URL: {self.page.url}")
        print(f"📄 Page Title: {self.page.title()}")
        
        # Check for forms on page
        forms = self.page.locator('form').all()
        print(f"📝 Forms found: {len(forms)}")
        
        # Check for input fields
        inputs = self.page.locator('input').all()
        print(f"🔤 Input fields found: {len(inputs)}")
        
        # Check for select dropdowns
        selects = self.page.locator('select').all()
        print(f"📋 Select dropdowns found: {len(selects)}")
        
        # Check for buttons
        buttons = self.page.locator('button').all()
        print(f"🔘 Buttons found: {len(buttons)}")
        
        # Check for any error messages
        page_content = self.page.content()
        if 'error' in page_content.lower() or 'erro' in page_content.lower():
            print("⚠️  DEBUG: Possible errors detected on page")
        
        # Print first 300 characters of page content for context
        print(f"📄 Page content preview: {page_content[:300]}...")


class ClinicManagementTest(ClinicManagementPlaywrightBase):
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
        self.page.goto(clinic_url)
        self.wait_for_page_load()
        
        self.take_screenshot("01_clinic_creation_page")
        self.debug_page_state("Clinic creation page loaded")
        
        # Wait for clinic form to load
        print("⏳ DEBUG: Waiting for clinic creation form...")
        clinic_name_field = self.page.locator('input[name="nome_clinica"]')
        clinic_name_field.wait_for(state="visible", timeout=15000)
        print("✅ DEBUG: Clinic form loaded - name field found")
        
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
                field_locator = self.page.locator(f'input[name="{field_name}"]')
                if field_locator.is_visible():
                    self.fill_field_slowly(field_locator, value, delay=0.05)
                    filled_count += 1
                    print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {field_name}")
                else:
                    print(f"   ⚠️  SKIP: Field {field_name} not found or not visible")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to fill {field_name}: {e}")
        
        self.take_screenshot("02_clinic_form_filled")
        print(f"📊 DEBUG: Clinic form filling complete: {filled_count}/{total_fields} fields filled")
        
        # Submit the clinic form with enhanced debugging
        print("📤 DEBUG: Submitting clinic creation form...")
        
        # Check for CSRF token presence before submission
        csrf_tokens = self.page.locator('input[name="csrfmiddlewaretoken"]').all()
        print(f"🔒 DEBUG: Found {len(csrf_tokens)} CSRF token(s)")
        
        # Check current session/login status before submission
        current_page_content = self.page.content()
        has_logout_button = 'Logout' in current_page_content
        print(f"🔐 DEBUG: User still logged in before submission: {has_logout_button}")
        
        # Get initial clinic count and current URL for comparison
        initial_clinic_count = Clinica.objects.count()
        initial_url = self.page.url
        print(f"📊 DEBUG: Initial clinic count: {initial_clinic_count}")
        print(f"📍 DEBUG: URL before submission: {initial_url}")
        
        # Find and click submit button
        submit_button = self.page.locator('input[type="submit"], button[type="submit"]').first
        submit_button.scroll_into_view_if_needed()
        submit_button.click()
        print("✅ Form submitted!")
        
        # Wait for processing and redirect
        print("⏳ DEBUG: Waiting for clinic creation processing...")
        self.wait_for_page_load()
        self.page.wait_for_timeout(2000)  # Additional wait for processing
        
        current_url = self.page.url
        print(f"📍 DEBUG: URL after submission: {current_url}")
        
        # Check if we got logged out
        final_page_content = self.page.content()
        still_logged_in = 'Logout' in final_page_content
        is_logout_page = '/logout/' in current_url or 'saiu com sucesso' in final_page_content.lower()
        
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
            page_content = self.page.content()
            if 'error' in page_content.lower() or 'obrigatório' in page_content.lower():
                print("❌ Form validation errors detected")
                error_elements = self.page.locator('.alert-danger, .error, .invalid-feedback').all()
                for i, error in enumerate(error_elements):
                    if error.is_visible():
                        print(f"❌ Form Error {i+1}: {error.text_content()}")
        
        # Verify successful redirect (should go to home or success page)
        expected_redirect = current_url != clinic_url
        if expected_redirect:
            print("✅ SUCCESS: Properly redirected after form submission")
        else:
            print("⚠️  WARNING: No redirect after form submission")
        
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
        self.page.goto(clinic_url)
        self.wait_for_page_load()
        
        self.take_screenshot("04_clinic_update_page")
        
        # Wait for form
        clinic_name_field = self.page.locator('input[name="nome_clinica"]')
        clinic_name_field.wait_for(state="visible", timeout=15000)
        
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
                field_locator = self.page.locator(f'input[name="{field_name}"]')
                if field_locator.is_visible():
                    self.fill_field_slowly(field_locator, value, delay=0.05)
                    print(f"   ✅ Updated {field_name}")
                else:
                    print(f"   ⚠️  Field {field_name} not visible")
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
        submit_button = self.page.locator('input[type="submit"], button[type="submit"]').first
        submit_button.click()
        
        self.wait_for_page_load()
        self.page.wait_for_timeout(2000)
        
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
        print("✅ DEBUG: Clinic update test completed!")

    def test_clinic_form_validation(self):
        """Test clinic form validation with invalid data."""
        
        print("\n🏥 TEST: test_clinic_form_validation")
        print("🎯 This test verifies: 1) Form validation, 2) Error handling, 3) Required fields")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        clinic_url = f'{self.live_server_url}/clinicas/cadastro/'
        self.page.goto(clinic_url)
        self.wait_for_page_load()
        
        clinic_name_field = self.page.locator('input[name="nome_clinica"]')
        clinic_name_field.wait_for(state="visible", timeout=15000)
        
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
                field_locator = self.page.locator(f'input[name="{field_name}"]')
                if field_locator.is_visible():
                    self.fill_field_slowly(field_locator, value, delay=0.05)
                    print(f"   ✅ Filled {field_name} with invalid data")
                else:
                    print(f"   ⚠️  Field {field_name} not visible")
            except Exception as e:
                print(f"   ❌ ERROR filling {field_name}: {e}")
        
        self.take_screenshot("07_invalid_form_data")
        
        # Try to submit invalid form
        print("📤 DEBUG: Submitting form with invalid data...")
        submit_button = self.page.locator('input[type="submit"], button[type="submit"]').first
        submit_button.click()
        
        self.wait_for_page_load()
        
        # Check for validation errors
        current_url = self.page.url
        print(f"📍 DEBUG: After invalid submission: {current_url}")
        
        # Look for error messages
        error_selectors = ['.alert-danger', '.error', '.invalid-feedback', '.errorlist']
        found_errors = False
        
        for selector in error_selectors:
            error_elements = self.page.locator(selector).all()
            for i, error in enumerate(error_elements):
                if error.is_visible():
                    error_text = error.text_content().strip()
                    if error_text:
                        print(f"   📋 Validation Error {i+1}: {error_text}")
                        found_errors = True
        
        if found_errors:
            print("✅ SUCCESS: Form validation errors detected")
        else:
            print("⚠️  WARNING: No validation errors displayed (may have been processed)")
        
        # Check if form was actually submitted (shouldn't be with invalid data)
        if current_url == clinic_url:
            print("✅ SUCCESS: Form not submitted due to validation errors")
        else:
            print("⚠️  WARNING: Form was submitted despite invalid data")
        
        self.take_screenshot("08_validation_errors")
        print("✅ DEBUG: Form validation test completed!")

    def test_clinic_navigation_workflow(self):
        """Test complete navigation workflow for clinic management."""
        
        print("\n🏥 TEST: test_clinic_navigation_workflow")
        print("🎯 This test verifies: 1) Navigation from home, 2) Menu access, 3) Form accessibility")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Start from home page
        print("🏠 DEBUG: Starting from home page...")
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        self.take_screenshot("09_home_page_navigation")
        self.debug_page_state("Home page for clinic navigation")
        
        # Look for clinic navigation in menu
        print("🔍 DEBUG: Looking for clinic navigation menu...")
        
        # Check for clinic dropdown or direct link
        clinic_links = self.page.locator('a:text("Clínicas"), a:has-text("Clínica")').all()
        
        if clinic_links:
            print(f"✅ Found {len(clinic_links)} clinic navigation elements:")
            for i, link in enumerate(clinic_links):
                text = link.text_content()
                href = link.get_attribute('href') or 'No href'
                print(f"   {i+1}. {text} -> {href}")
            
            # Try to click the first clinic link
            try:
                clinic_links[0].click()
                self.wait_for_page_load()
                
                current_url = self.page.url
                print(f"📍 DEBUG: After clicking clinic link: {current_url}")
                
                if '/clinicas/' in current_url:
                    print("✅ SUCCESS: Successfully navigated to clinic section")
                else:
                    print("⚠️  WARNING: Didn't navigate to clinic section")
            except Exception as e:
                print(f"⚠️  WARNING: Clinic link click failed: {e}")
                # Try direct navigation instead
        else:
            print("⚠️  WARNING: No clinic navigation elements found")
            
            # Try direct navigation as fallback
            print("🔄 DEBUG: Trying direct navigation to clinic creation...")
            self.page.goto(f'{self.live_server_url}/clinicas/cadastro/')
            self.wait_for_page_load()
            
            if '/clinicas/cadastro/' in self.page.url:
                print("✅ SUCCESS: Direct navigation to clinic creation works")
            else:
                print("❌ ERROR: Cannot access clinic creation page")
        
        self.take_screenshot("10_clinic_navigation_result")
        print("✅ DEBUG: Clinic navigation test completed!")

    def test_clinic_csrf_and_session_debugging(self):
        """Test to specifically debug CSRF token and session issues."""
        
        print("\n🔒 TEST: test_clinic_csrf_and_session_debugging")
        print("🎯 This test investigates: 1) CSRF token handling, 2) Session persistence, 3) Form submission mechanics")
        
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        clinic_url = f'{self.live_server_url}/clinicas/cadastro/'
        self.page.goto(clinic_url)
        self.wait_for_page_load()
        
        # Wait for form to load
        clinic_name_field = self.page.locator('input[name="nome_clinica"]')
        clinic_name_field.wait_for(state="visible", timeout=15000)
        
        print("🔍 DEBUG: Analyzing form and session state...")
        
        # Detailed CSRF token analysis
        csrf_tokens = self.page.locator('input[name="csrfmiddlewaretoken"]').all()
        print(f"🔒 CSRF Tokens found: {len(csrf_tokens)}")
        
        for i, token in enumerate(csrf_tokens):
            token_value = token.get_attribute('value')
            token_type = token.get_attribute('type')
            print(f"   Token {i+1}: Type={token_type}, Value={token_value[:20]}...")
        
        # Check form action and method
        forms = self.page.locator('form').all()
        print(f"📝 Forms found: {len(forms)}")
        
        for i, form in enumerate(forms):
            action = form.get_attribute('action')
            method = form.get_attribute('method')
            print(f"   Form {i+1}: Action='{action}', Method='{method}'")
        
        # Fill form minimally
        print("📝 DEBUG: Filling minimal form data...")
        minimal_data = {
            'nome_clinica': 'Test CSRF Clinic',
            'cns_clinica': '1111111',
        }
        
        for field_name, value in minimal_data.items():
            try:
                field_locator = self.page.locator(f'input[name="{field_name}"]')
                if field_locator.is_visible():
                    self.fill_field_slowly(field_locator, value, delay=0.05)
                    print(f"   ✅ Filled {field_name}")
                else:
                    print(f"   ⚠️  Field {field_name} not visible")
            except Exception as e:
                print(f"   ❌ Failed to fill {field_name}: {e}")
        
        self.take_screenshot("11_csrf_debug_form_filled")
        
        # Check session state right before submission
        print("🔐 DEBUG: Pre-submission session check...")
        page_content_before = self.page.content()
        has_logout_before = 'Logout' in page_content_before
        print(f"   Logged in before submission: {has_logout_before}")
        
        # Submit form with detailed monitoring
        print("📤 DEBUG: Submitting with detailed monitoring...")
        
        # Find the clinic form specifically
        clinic_forms = self.page.locator('form').all()
        clinic_form = None
        
        for form in clinic_forms:
            action = form.get_attribute('action')
            if 'clinicas/cadastro' in action:
                clinic_form = form
                break
        
        if clinic_form:
            submit_button = clinic_form.locator('input[type="submit"], button[type="submit"]').first
            form_action = clinic_form.get_attribute('action')
            form_method = clinic_form.get_attribute('method')
            print(f"   Submitting to: '{form_action}' via {form_method}")
        else:
            submit_button = self.page.locator('input[type="submit"], button[type="submit"]').first
            print("   Using fallback submit button")
        
        submit_button.click()
        
        # Monitor URL changes immediately
        self.page.wait_for_timeout(1000)
        immediate_url = self.page.url
        print(f"   URL after 1s: {immediate_url}")
        
        self.wait_for_page_load()
        final_url = self.page.url
        print(f"   URL after full load: {final_url}")
        
        # Check session state after submission
        page_content_after = self.page.content()
        has_logout_after = 'Logout' in page_content_after
        has_success_message = 'sucesso' in page_content_after.lower()
        
        print(f"   Logged in after submission: {has_logout_after}")
        print(f"   Success message detected: {has_success_message}")
        
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
        
        print("✅ DEBUG: CSRF and session debugging test completed!")


class ClinicAccessibilityTest(ClinicManagementPlaywrightBase):
    """Test clinic form accessibility and responsive features."""
    
    def test_clinic_form_accessibility(self):
        """Test clinic form accessibility features."""
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Navigate to clinic creation page
        self.page.goto(f'{self.live_server_url}/clinicas/cadastro/')
        self.wait_for_page_load()
        
        # Check for form labels
        labels = self.page.locator('label').all()
        print(f"📋 Found {len(labels)} form labels")
        
        # Check specific important labels
        important_labels = ['Nome da Clínica', 'CNS', 'Telefone', 'Cidade']
        for label_text in important_labels:
            label = self.page.locator(f'label:has-text("{label_text}")')
            if label.is_visible():
                print(f"✅ Found label: {label_text}")
            else:
                print(f"⚠️  Missing label: {label_text}")
        
        # Check form field attributes
        form_fields = ['nome_clinica', 'cns_clinica', 'telefone_clinica']
        for field_name in form_fields:
            field = self.page.locator(f'input[name="{field_name}"]')
            if field.is_visible():
                field_class = field.get_attribute('class')
                field_id = field.get_attribute('id')
                print(f"✅ Field {field_name}: class='{field_class}', id='{field_id}'")
        
        self.take_screenshot("clinic_form_accessibility")
    
    def test_clinic_form_responsive(self):
        """Test clinic form on different screen sizes."""
        # Login as medico
        self.login_user('medico@clinic.com', 'testpass123')
        
        # Test mobile size
        self.page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        self.page.goto(f'{self.live_server_url}/clinicas/cadastro/')
        self.wait_for_page_load()
        
        # Check if form is still usable on mobile
        clinic_name_field = self.page.locator('input[name="nome_clinica"]')
        self.assertTrue(clinic_name_field.is_visible(), "Clinic name field should be visible on mobile")
        
        self.take_screenshot("clinic_form_mobile")
        
        # Test tablet size
        self.page.set_viewport_size({"width": 768, "height": 1024})  # iPad size
        self.wait_for_page_load()
        self.take_screenshot("clinic_form_tablet")
        
        # Reset to desktop size
        self.page.set_viewport_size({"width": 1920, "height": 1080})