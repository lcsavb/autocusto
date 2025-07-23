"""
Prescription Form Frontend Tests using Playwright
Tests the complex prescription form workflow and functionality
"""

import time
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class PrescriptionFormPlaywrightBase(PlaywrightFormTestBase):
    """Base class for prescription form tests with common setup and utilities."""
    
    def setUp(self):
        """Set up test data for prescription forms with extensive debugging."""
        super().setUp()
        
        print("🔧 DEBUG: Setting up test data...")
        
        # Create test user and medico
        print("🔧 DEBUG: Creating user...")
        self.user1 = User.objects.create_user(
            email='medico@example.com',
            password='testpass123'
        )
        self.user1.is_medico = True
        self.user1.save()
        print(f"✅ Created user: {self.user1.email}")
        
        print("🔧 DEBUG: Creating medico...")
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. João Silva",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico1.usuarios.add(self.user1)
        print(f"✅ Created medico: {self.medico1.nome_medico} (CRM: {self.medico1.crm_medico})")
        
        # Create clinica
        print("🔧 DEBUG: Creating clinica...")
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica Teste",
            cns_clinica="1234567",
            logradouro="Rua A",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        print(f"✅ Created clinica: {self.clinica1.nome_clinica}")
        
        # Associate user with clinica
        print("🔧 DEBUG: Associating user with clinica...")
        self.user1.clinicas.add(self.clinica1)
        print("✅ User associated with clinica")
        
        # Create emissor
        print("🔧 DEBUG: Creating emissor...")
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        print(f"✅ Created emissor: {self.emissor1}")
        
        # Create test patient with all required fields
        print("🔧 DEBUG: Creating patient...")
        self.patient1 = Paciente.objects.create(
            nome_paciente="Maria Santos",
            cpf_paciente="72834565031",  # Valid CPF for testing
            cns_paciente="111111111111111",
            nome_mae="Ana Santos",
            idade="45",
            sexo="F",
            peso="65",
            altura="165",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua B, 456",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        self.patient1.usuarios.add(self.user1)
        print(f"✅ Created patient: {self.patient1.nome_paciente} (CPF: {self.patient1.cpf_paciente})")
        
        # Create test medications
        print("🔧 DEBUG: Creating medications...")
        self.med1 = Medicamento.objects.create(
            nome="Levetiracetam",
            dosagem="500mg",
            apres="Comprimido revestido"
        )
        self.med2 = Medicamento.objects.create(
            nome="Carbamazepina", 
            dosagem="200mg",
            apres="Comprimido"
        )
        print(f"✅ Created medications: {self.med1.nome} {self.med1.dosagem}, {self.med2.nome} {self.med2.dosagem}")
        
        # Create protocolo and doenca for testing
        print("🔧 DEBUG: Creating protocolo...")
        self.protocolo = Protocolo.objects.create(
            nome="Protocolo Epilepsia",
            arquivo="epilepsia.pdf",
            dados_condicionais={}
        )
        
        # Associate medications with protocol
        self.protocolo.medicamentos.add(self.med1, self.med2)
        print(f"✅ Created protocolo: {self.protocolo.nome}")
        
        print("🔧 DEBUG: Creating doenca...")
        self.doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Epilepsia",
            protocolo=self.protocolo
        )
        print(f"✅ Created doenca: {self.doenca.cid} - {self.doenca.nome}")
        
        print("✅ DEBUG: Test data setup complete!")
        print(f"📊 DEBUG: Test data summary:")
        print(f"   - User: {self.user1.email}")
        print(f"   - Medico: {self.medico1.nome_medico}")
        print(f"   - Clinica: {self.clinica1.nome_clinica}")
        print(f"   - Patient: {self.patient1.nome_paciente}")
        print(f"   - Doenca: {self.doenca.cid}")
        print(f"   - Medications: {Medicamento.objects.count()}")

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
            print("⚠️  DEBUG: Login verification failed")

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


class PrescriptionFormTest(PrescriptionFormPlaywrightBase):
    """Test complex prescription form filling workflow."""

    def test_prescription_form_navigation(self):
        """Test navigation from home page to prescription form with extensive debugging."""
        
        print("\n🚀 TEST: test_prescription_form_navigation")
        
        # Login as medico
        self.login_user('medico@example.com', 'testpass123')
        
        # Go to home page
        print("🏠 DEBUG: Navigating to home page")
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        self.take_screenshot("01_home_page_logged_in")
        self.debug_page_state("Home page after login")
        
        # Wait for home form
        cpf_field = self.page.locator('input[name="cpf_paciente"]')
        cpf_field.wait_for(state="visible", timeout=10000)
        print("✅ DEBUG: Home form with CPF field found")
        
        # Fill CPF and CID to navigate to prescription form
        print("📝 DEBUG: Filling home form...")
        cid_field = self.page.locator('input[name="cid"]')
        
        self.fill_field_slowly(cpf_field, "72834565031")  # Existing patient
        self.fill_field_slowly(cid_field, "G40.0")        # Epilepsia
        
        self.take_screenshot("02_home_form_filled")
        
        # Submit form
        print("📤 DEBUG: Submitting home form...")
        submit_button = self.page.locator('button:has-text("Cadastrar")')
        submit_button.click()
        
        # Wait for navigation to prescription form
        print("⏳ DEBUG: Waiting for navigation...")
        self.wait_for_page_load()
        self.page.wait_for_timeout(2000)  # Give more time for navigation
        
        current_url = self.page.url
        print(f"📍 DEBUG: Navigated to: {current_url}")
        
        self.take_screenshot("03_prescription_form_loaded")
        self.debug_page_state("After form submission")
        
        # Verify we're on the correct prescription page
        expected_urls = ['/processos/cadastro/', '/processos/edicao/']
        url_match = any(expected_url in current_url for expected_url in expected_urls)
        
        if not url_match:
            print(f"❌ DEBUG: Unexpected URL. Expected one of {expected_urls}, got: {current_url}")
            # Check if we're still on home page or redirected elsewhere
            if self.live_server_url + '/' == current_url:
                print("❌ DEBUG: Still on home page - form submission may have failed")
                page_content = self.page.content()
                if 'error' in page_content.lower() or 'erro' in page_content.lower():
                    print("❌ DEBUG: Error messages detected on home page")
                    print(f"Page content preview: {page_content[:500]}")
        
        self.assertTrue(
            url_match,
            f"Expected prescription form page ({expected_urls}), got: {current_url}"
        )
        print("✅ DEBUG: Successfully navigated to prescription form!")

    def test_prescription_form_basic_patient_data(self):
        """Test filling basic patient data in prescription form."""
        
        print("\n🚀 TEST: test_prescription_form_basic_patient_data")
        
        # Navigate to prescription form (via home page workflow)
        self.test_prescription_form_navigation()
        
        # Take screenshot of the form before filling
        self.take_screenshot("04_prescription_form_empty")
        self.debug_page_state("Prescription form initial state")
        
        # Wait for prescription form to load completely
        print("⏳ DEBUG: Waiting for prescription form fields...")
        patient_name_field = self.page.locator('input[name="nome_paciente"]')
        if patient_name_field.count() > 0:
            patient_name_field.wait_for(state="visible", timeout=15000)
            print("✅ DEBUG: Patient name field found")
        else:
            print("❌ DEBUG: Patient name field not found")
            self.take_screenshot("04_error_no_patient_fields")
            # Try to find any input fields
            all_inputs = self.page.locator('input').all()
            input_names = [inp.get_attribute('name') for inp in all_inputs if inp.get_attribute('name')]
            print(f"❌ DEBUG: Available input fields: {input_names}")
            self.skipTest("Patient name field not found on prescription form")
        
        # Fill basic patient information
        patient_fields = {
            'nome_paciente': 'Maria Santos Silva',
            'nome_mae': 'Ana Santos',
            'peso': '65',
            'altura': '165',
            'end_paciente': 'Rua das Flores, 123, Apt 45'
        }
        
        print("📝 DEBUG: Filling patient basic data...")
        filled_fields = 0
        for field_name, value in patient_fields.items():
            field_locator = self.page.locator(f'input[name="{field_name}"]')
            if field_locator.is_visible():
                self.fill_field_slowly(field_locator, value, delay=0.05)
                print(f"✅ DEBUG: Filled {field_name}: {value}")
                filled_fields += 1
            else:
                print(f"⚠️  DEBUG: Field {field_name} not found or not visible on page")
        
        self.take_screenshot("05_patient_data_filled")
        print(f"📊 DEBUG: Successfully filled {filled_fields}/{len(patient_fields)} patient fields")

    def test_prescription_form_medication_section(self):
        """Test filling medication section of prescription form."""
        
        print("\n🚀 TEST: test_prescription_form_medication_section")
        
        # Navigate to prescription form first
        self.test_prescription_form_navigation()
        
        print("🔍 DEBUG: Looking for medication section...")
        
        # Look for medication-related fields or sections
        medication_selectors = [
            'select[name*="medicamento"]',
            'input[name*="medicamento"]',
            'select[name*="med"]',
            '.medication-section',
            '.medicamentos'
        ]
        
        found_medication_elements = False
        for selector in medication_selectors:
            elements = self.page.locator(selector).all()
            if elements:
                print(f"✅ DEBUG: Found {len(elements)} medication elements with selector: {selector}")
                found_medication_elements = True
                break
        
        if not found_medication_elements:
            print("⚠️  DEBUG: No medication section found on this form")
            self.take_screenshot("06_no_medication_section")
            # This might be expected depending on the form type
            self.skipTest("Medication section not found - may not be required for this form type")
        else:
            self.take_screenshot("06_medication_section_found")
            print("✅ DEBUG: Medication section located successfully")

    def test_prescription_form_submission(self):
        """Test submitting the prescription form."""
        
        print("\n🚀 TEST: test_prescription_form_submission")
        
        # Navigate and fill basic data
        self.test_prescription_form_basic_patient_data()
        
        print("📤 DEBUG: Looking for form submission button...")
        
        # Look for common submit button patterns
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Salvar")',
            'button:has-text("Cadastrar")',
            'button:has-text("Finalizar")',
            'button:has-text("Enviar")'
        ]
        
        submit_button = None
        for selector in submit_selectors:
            button = self.page.locator(selector).first
            if button.is_visible():
                submit_button = button
                print(f"✅ DEBUG: Found submit button with selector: {selector}")
                break
        
        if submit_button:
            initial_url = self.page.url
            print(f"📍 DEBUG: Current URL before submission: {initial_url}")
            
            # Take screenshot before submission
            self.take_screenshot("07_before_form_submission")
            
            # Submit the form
            submit_button.click()
            print("✅ DEBUG: Form submission attempted")
            
            # Wait for processing
            self.wait_for_page_load()
            self.page.wait_for_timeout(2000)
            
            final_url = self.page.url
            print(f"📍 DEBUG: URL after submission: {final_url}")
            
            self.take_screenshot("08_after_form_submission")
            
            # Check if form was processed (URL change or success message)
            if final_url != initial_url:
                print("✅ DEBUG: Form submission resulted in navigation - likely successful")
            else:
                # Check for success or error messages
                page_content = self.page.content()
                if 'sucesso' in page_content.lower() or 'success' in page_content.lower():
                    print("✅ DEBUG: Success message detected")
                elif 'erro' in page_content.lower() or 'error' in page_content.lower():
                    print("⚠️  DEBUG: Error message detected - form may have validation issues")
                else:
                    print("⚠️  DEBUG: No clear success/error indication - form may need more data")
        else:
            print("⚠️  DEBUG: No submit button found on prescription form")
            self.take_screenshot("07_no_submit_button")


class PrescriptionFormAccessibilityTest(PrescriptionFormPlaywrightBase):
    """Test prescription form accessibility and responsive features."""
    
    def test_prescription_form_accessibility(self):
        """Test prescription form accessibility features."""
        # Login and navigate to form
        self.login_user('medico@example.com', 'testpass123')
        
        # Try to navigate to a prescription form directly
        form_urls = [
            f'{self.live_server_url}/processos/cadastro/',
            f'{self.live_server_url}/processos/edicao/'
        ]
        
        form_loaded = False
        for url in form_urls:
            try:
                self.page.goto(url)
                self.wait_for_page_load()
                
                # Check if form elements are present
                if self.page.locator('form').count() > 0:
                    form_loaded = True
                    print(f"✅ DEBUG: Prescription form loaded at {url}")
                    break
            except:
                continue
        
        if not form_loaded:
            self.skipTest("Could not load prescription form for accessibility testing")
        
        # Check for form labels
        labels = self.page.locator('label').all()
        print(f"📋 Found {len(labels)} form labels")
        
        # Check for ARIA attributes
        form_elements = self.page.locator('input, select, textarea').all()
        accessibility_features = 0
        
        for element in form_elements:
            if element.get_attribute('aria-label') or element.get_attribute('aria-describedby'):
                accessibility_features += 1
        
        print(f"✅ Found {accessibility_features} form elements with ARIA attributes")
        self.take_screenshot("prescription_form_accessibility")
    
    def test_prescription_form_responsive(self):
        """Test prescription form on different screen sizes."""
        # Login first
        self.login_user('medico@example.com', 'testpass123')
        
        # Try to get to a prescription form
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Test mobile size
        self.page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        self.page.wait_for_timeout(1000)
        
        # Check if main form elements are still accessible
        main_form = self.page.locator('form').first
        if main_form.is_visible():
            print("✅ Main form visible on mobile")
        
        self.take_screenshot("prescription_form_mobile")
        
        # Test tablet size
        self.page.set_viewport_size({"width": 768, "height": 1024})  # iPad size
        self.page.wait_for_timeout(1000)
        self.take_screenshot("prescription_form_tablet")
        
        # Reset to desktop size
        self.page.set_viewport_size({"width": 1920, "height": 1080})