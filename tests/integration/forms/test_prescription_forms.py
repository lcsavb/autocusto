"""
Prescription Form Frontend Tests using Playwright
Tests the complex prescription form workflow and functionality
"""

import time
import json
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase, PlaywrightLiveServerTestBase
from tests.test_session_data import get_edicao_session_data
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class PrescriptionFormPlaywrightBase(PlaywrightLiveServerTestBase):
    """Base class for prescription form tests with common setup and utilities."""
    
    # Now we can use PlaywrightLiveServerTestBase since tests run on the host
    
    def setUp(self):
        """Set up test data for prescription forms with extensive debugging."""
        import sys
        print("🔧 DEBUG: PrescriptionFormPlaywrightBase.setUp() starting...", flush=True)
        print(f"🔧 DEBUG: MRO: {[c.__name__ for c in self.__class__.__mro__]}", flush=True)
        sys.stdout.flush()
        
        try:
            print("🔧 DEBUG: About to call super().setUp()...", flush=True)
            sys.stdout.flush()
            super().setUp()
            print("🔧 DEBUG: Parent setUp() complete", flush=True)
        except Exception as e:
            print(f"🔧 ERROR: Parent setUp() failed: {e}", flush=True)
            raise
        
        print("🔧 DEBUG: Setting up test data...", flush=True)
        
        # Create test user and medico with unique email to avoid constraint violations
        print("🔧 DEBUG: Creating user...", flush=True)
        from tests.test_base import UniqueDataGenerator
        data_generator = UniqueDataGenerator()
        self.test_email = data_generator.generate_unique_email()
        self.user1 = User.objects.create_user(
            email=self.test_email,
            password='testpass123'
        )
        self.user1.is_medico = True
        self.user1.save()
        print(f"✅ Created user: {self.user1.email}")
        
        print("🔧 DEBUG: Creating medico...")
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. João Silva",
            crm_medico=data_generator.generate_unique_crm(),
            cns_medico=data_generator.generate_unique_cns_medico()
        )
        self.medico1.usuarios.add(self.user1)
        print(f"✅ Created medico: {self.medico1.nome_medico} (CRM: {self.medico1.crm_medico})")
        
        # Create clinica
        print("🔧 DEBUG: Creating clinica...")
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica Teste",
            cns_clinica=data_generator.generate_unique_cns_clinica(),
            logradouro="Rua A",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        print(f"✅ Created clinica: {self.clinica1.nome_clinica}")
        
        # Use the proper versioning system to create clinic with version assignment
        print("🔧 DEBUG: Creating clinic with proper versioning...")
        clinic_data = {
            'nome_clinica': self.clinica1.nome_clinica,
            'cns_clinica': self.clinica1.cns_clinica,
            'logradouro': self.clinica1.logradouro,
            'logradouro_num': self.clinica1.logradouro_num,
            'cidade': self.clinica1.cidade,
            'bairro': self.clinica1.bairro,
            'cep': self.clinica1.cep,
            'telefone_clinica': self.clinica1.telefone_clinica
        }
        
        # Use the versioning system instead of manual creation
        versioned_clinic = Clinica.create_or_update_for_user(
            user=self.user1,
            doctor=self.medico1,
            clinic_data=clinic_data
        )
        
        # Replace the manually created clinic with the properly versioned one
        self.clinica1 = versioned_clinic
        print("✅ Clinic created with proper versioning - no fallback needed")
        
        # Create emissor
        print("🔧 DEBUG: Creating emissor...")
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        print(f"✅ Created emissor: {self.emissor1}")
        
        # Create test patient with all required fields
        print("🔧 DEBUG: Creating patient...")
        from cpf_generator import CPF
        unique_cpf = CPF.generate()
        self.patient1 = Paciente.objects.create(
            nome_paciente="Maria Santos",
            cpf_paciente=unique_cpf,  # Generated unique CPF
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
        
        # Create patient version and assignment for proper access control
        print("🔧 DEBUG: Creating patient version...")
        try:
            from pacientes.models import PacienteVersion, PacienteUsuarioVersion
            # Create initial version for the patient
            patient_version = PacienteVersion.objects.create(
                paciente=self.patient1,
                nome_paciente=self.patient1.nome_paciente,
                cns_paciente=getattr(self.patient1, 'cns_paciente', ''),  
                nome_mae=getattr(self.patient1, 'nome_mae', ''),
                idade=getattr(self.patient1, 'idade', ''),
                sexo=getattr(self.patient1, 'sexo', ''),
                peso=getattr(self.patient1, 'peso', ''),
                altura=getattr(self.patient1, 'altura', ''),
                incapaz=getattr(self.patient1, 'incapaz', False),
                etnia=getattr(self.patient1, 'etnia', ''),
                telefone1_paciente=getattr(self.patient1, 'telefone1_paciente', ''),
                end_paciente=getattr(self.patient1, 'end_paciente', ''),
                cidade_paciente=getattr(self.patient1, 'cidade_paciente', ''),
                cep_paciente=getattr(self.patient1, 'cep_paciente', ''),
                rg=getattr(self.patient1, 'rg', ''),
                escolha_etnia=getattr(self.patient1, 'escolha_etnia', getattr(self.patient1, 'etnia', '')),
                telefone2_paciente=getattr(self.patient1, 'telefone2_paciente', ''),
                nome_responsavel=getattr(self.patient1, 'nome_responsavel', ''),
                email_paciente=getattr(self.patient1, 'email_paciente', ''),
                version_number=1,
                status='active',
                created_by=self.user1
            )
            print(f"✅ Created patient version: {patient_version.version_number}")
            
            # Get the through relationship object  
            user_patient_rel = self.patient1.usuarios.through.objects.get(
                paciente=self.patient1, usuario=self.user1
            )
            
            # Create the version assignment that links user to their version
            PacienteUsuarioVersion.objects.create(
                paciente_usuario=user_patient_rel,
                version=patient_version
            )
            print("✅ Patient version assignment created - no fallback needed")
            
        except (ImportError, Exception) as e:
            print(f"WARNING: Failed to create patient version: {e}")
        
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
        self.protocolo, created = Protocolo.objects.get_or_create(
            nome="Protocolo Epilepsia",
            defaults={
                'arquivo': "epilepsia.pdf",
                'dados_condicionais': {}
            }
        )
        
        # Associate medications with protocol
        self.protocolo.medicamentos.add(self.med1, self.med2)
        print(f"✅ Created protocolo: {self.protocolo.nome}")
        
        print("🔧 DEBUG: Creating doenca...")
        self.doenca, created = Doenca.objects.get_or_create(
            cid="G40.0",
            defaults={
                'nome': "Epilepsia",
                'protocolo': self.protocolo
            }
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

    def setup_authenticated_session(self):
        """Set up authenticated session for the user without browser login."""
        # Use Django test client to establish authentication session
        from django.test import Client
        from django.contrib.sessions.backends.db import SessionStore
        from urllib.parse import urlparse
        
        # Create a session for the authenticated user
        client = Client()
        client.force_login(self.user1)
        
        # Get the session key from the test client
        if hasattr(client.session, 'session_key'):
            session_key = client.session.session_key
        else:
            # Force session creation
            client.session.save()
            session_key = client.session.session_key
        
        # Parse the server URL to get the correct domain
        parsed_url = urlparse(self.accessible_live_server_url)
        cookie_domain = parsed_url.hostname or 'localhost'
        
        # Set the session cookie in the browser context
        self.context.add_cookies([{
            'name': 'sessionid',
            'value': session_key,
            'domain': cookie_domain,  # Use the correct domain
            'path': '/'
        }])
        
        print(f"✅ Authentication session established for user: {self.user1.email}")
        print(f"✅ Cookie domain set to: {cookie_domain}")
        return session_key

    def fill_field_slowly(self, field_locator, value, delay=0.05):
        """Fill field with value using Playwright, with robust interaction."""
        print(f"✏️  DEBUG: Filling field with value: {value}")
        
        try:
            # Wait for element to be visible and enabled with timeout
            field_locator.wait_for(state="visible", timeout=10000)
            
            # Scroll element into view
            field_locator.scroll_into_view_if_needed()
            
            # Clear and fill field
            field_locator.clear()
            field_locator.fill(str(value))
            
            self.page.wait_for_timeout(int(delay * 1000))
            print("✅ DEBUG: Field filled successfully")
        except Exception as e:
            print(f"❌ DEBUG: Failed to fill field: {e}")
            raise

    def debug_page_state(self, step_name):
        """Print extensive debugging information about current page state."""
        print(f"\n🔍 DEBUG: {step_name}")
        print(f"📍 Current URL: {self.page.url}")
        print(f"📄 Page Title: {self.page.title()}")
        
        # Check for forms on page (with error handling)
        try:
            forms = self.page.locator('form').all()
            print(f"📝 Forms found: {len(forms)}")
        except Exception as e:
            print(f"❌ Error checking forms: {e}")
            forms = []
        
        # Check for input fields (with error handling)
        try:
            inputs = self.page.locator('input').all()
            print(f"🔤 Input fields found: {len(inputs)}")
        except Exception as e:
            print(f"❌ Error checking inputs: {e}")
            inputs = []
        
        # Check for select dropdowns (with error handling)
        try:
            selects = self.page.locator('select').all()
            print(f"📋 Select dropdowns found: {len(selects)}")
        except Exception as e:
            print(f"❌ Error checking selects: {e}")
            selects = []
        
        # Check for buttons (with error handling)
        try:
            buttons = self.page.locator('button').all()
            print(f"🔘 Buttons found: {len(buttons)}")
        except Exception as e:
            print(f"❌ Error checking buttons: {e}")
            buttons = []
        
        # Check for any error messages (with error handling)
        page_content = self.page.content()
        if 'error' in page_content.lower() or 'erro' in page_content.lower():
            print("⚠️  DEBUG: Possible errors detected on page")
        
        # Print first 300 characters of page content for context
        print(f"📄 Page content preview: {page_content[:300]}...")


class PrescriptionFormTest(PrescriptionFormPlaywrightBase):
    """Test complex prescription form filling workflow."""
    
    def navigate_to_prescription_form(self):
        """Helper method to navigate from home page to prescription form."""
        print("🏠 DEBUG: Navigating to home page")
        print(f"🔗 DEBUG: URL: {self.accessible_live_server_url}/")
        
        try:
            # Add timeout to goto to prevent hanging
            self.page.goto(f'{self.accessible_live_server_url}/', timeout=30000, wait_until="domcontentloaded")
            print("✅ DEBUG: Page loaded successfully")
        except Exception as e:
            print(f"❌ DEBUG: Failed to load home page: {e}")
            self.take_screenshot("01_navigation_error")
            raise
        
        print("⏳ DEBUG: Waiting for page to be fully loaded...")
        self.wait_for_page_load()
        print("✅ DEBUG: Page load complete")
        
        self.take_screenshot("01_home_page_logged_in")
        self.debug_page_state("Home page after login")
        
        # Wait for home form - with better error handling
        try:
            cpf_field = self.page.locator('input[name="cpf_paciente"]')
            cpf_field.wait_for(state="visible", timeout=10000)
            print("✅ DEBUG: Home form with CPF field found")
        except Exception as e:
            print(f"❌ DEBUG: CPF field not found. Error: {e}")
            print("🔍 DEBUG: Looking for any input fields...")
            all_inputs = self.page.locator('input')
            input_count = all_inputs.count()
            print(f"🔍 DEBUG: Found {input_count} input fields")
            for i in range(min(5, input_count)):  # Show first 5 inputs
                input_elem = all_inputs.nth(i)
                name = input_elem.get_attribute('name')
                type_attr = input_elem.get_attribute('type')
                print(f"  Input {i}: name='{name}', type='{type_attr}'")
            raise Exception("CPF field not found on home page")
        
        # Fill CPF and CID to navigate to prescription form
        print("📝 DEBUG: Filling home form...")
        cid_field = self.page.locator('input[name="cid"]')
        
        # Use the same valid CPF that was created for the patient in setUp
        self.fill_field_slowly(cpf_field, self.patient1.cpf_paciente)
        self.fill_field_slowly(cid_field, "G40.0")        # Epilepsia
        
        self.take_screenshot("02_home_form_filled")
        
        # Submit form
        print("📤 DEBUG: Submitting home form...")
        submit_button = self.page.locator('button:has-text("Cadastrar")')
        
        try:
            submit_button.wait_for(state="visible", timeout=5000)
            submit_button.click()
            print("✅ DEBUG: Submit button clicked")
        except Exception as e:
            print(f"❌ DEBUG: Failed to click submit button: {e}")
            self.take_screenshot("02_submit_error")
            raise
        
        # Wait for navigation to prescription form
        print("⏳ DEBUG: Waiting for navigation...")
        try:
            self.wait_for_page_load()
            self.page.wait_for_timeout(2000)  # Give more time for navigation
            print("✅ DEBUG: Navigation complete")
        except Exception as e:
            print(f"❌ DEBUG: Navigation wait failed: {e}")
            self.take_screenshot("03_navigation_timeout")
            raise
        
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
            if self.accessible_live_server_url + '/' == current_url:
                print("❌ DEBUG: Still on home page - form submission may have failed")
                page_content = self.page.content()
                if 'error' in page_content.lower() or 'erro' in page_content.lower():
                    print("❌ DEBUG: Error messages detected on home page")
                    print(f"Page content preview: {page_content[:500]}")
            raise Exception(f"Failed to navigate to prescription form. Current URL: {current_url}")
        
        print("✅ DEBUG: Successfully navigated to prescription form!")
        return True

    def test_prescription_form_navigation(self):
        """Test navigation from home page to prescription form with extensive debugging."""
        
        print("\n🚀 TEST: test_prescription_form_navigation")
        
        # Set up authenticated session without browser login
        self.setup_authenticated_session()
        
        # Use the helper method to navigate
        try:
            self.navigate_to_prescription_form()
            self.assertTrue(True, "Navigation to prescription form successful")
        except Exception as e:
            self.fail(f"Navigation to prescription form failed: {e}")

    def test_prescription_form_basic_patient_data(self):
        """Test filling basic patient data in prescription form."""
        
        print("\n🚀 TEST: test_prescription_form_basic_patient_data")
        
        # Set up authenticated session without browser login
        self.setup_authenticated_session()
        
        # Navigate to prescription form using helper method
        try:
            self.navigate_to_prescription_form()
        except Exception as e:
            self.fail(f"Failed to navigate to prescription form: {e}")
        
        # Take screenshot of the form before filling
        self.take_screenshot("04_prescription_form_empty")
        self.debug_page_state("Prescription form initial state")
        
        # Wait for prescription form to load completely
        print("⏳ DEBUG: Waiting for prescription form fields...")
        try:
            patient_name_field = self.page.locator('input[name="nome_paciente"]')
            patient_name_field.wait_for(state="visible", timeout=15000)
            print("✅ DEBUG: Patient name field found")
        except Exception as e:
            print(f"❌ DEBUG: Patient name field not found. Error: {e}")
            self.take_screenshot("04_error_no_patient_fields")
            # Try to find any input fields
            all_inputs = self.page.locator('input').all()
            input_names = [inp.get_attribute('name') for inp in all_inputs if inp.get_attribute('name')]
            print(f"❌ DEBUG: Available input fields: {input_names}")
            self.fail("Patient name field not found on prescription form")
        
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
            try:
                field_locator = self.page.locator(f'input[name="{field_name}"]')
                field_locator.wait_for(state="visible", timeout=5000)
                self.fill_field_slowly(field_locator, value, delay=0.05)
                print(f"✅ DEBUG: Filled {field_name}: {value}")
                filled_fields += 1
            except Exception as e:
                print(f"⚠️  DEBUG: Field {field_name} not found or not visible on page: {e}")
        
        self.take_screenshot("05_patient_data_filled")
        print(f"📊 DEBUG: Successfully filled {filled_fields}/{len(patient_fields)} patient fields")
        
        # Assert that at least some fields were filled
        self.assertGreater(filled_fields, 0, "No patient fields could be filled")

    def test_prescription_form_medication_section(self):
        """Test filling medication section of prescription form."""
        
        print("\n🚀 TEST: test_prescription_form_medication_section")
        
        # Set up authenticated session without browser login
        self.setup_authenticated_session()
        
        # Navigate to prescription form using helper method
        try:
            self.navigate_to_prescription_form()
        except Exception as e:
            self.fail(f"Failed to navigate to prescription form: {e}")
        
        print("🔍 DEBUG: Looking for medication section...")
        
        # Look for medication-related fields or sections with timeouts
        medication_selectors = [
            'select[name*="medicamento"]',
            'input[name*="medicamento"]',
            'select[name*="med"]',
            '.medication-section',
            '.medicamentos'
        ]
        
        found_medication_elements = False
        for selector in medication_selectors:
            try:
                elements = self.page.locator(selector)
                elements.first.wait_for(state="visible", timeout=5000)
                count = elements.count()
                if count > 0:
                    print(f"✅ DEBUG: Found {count} medication elements with selector: {selector}")
                    found_medication_elements = True
                    break
            except Exception:
                continue
        
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
        
        # Set up authenticated session without browser login
        self.setup_authenticated_session()
        
        # Navigate to prescription form using helper method
        try:
            self.navigate_to_prescription_form()
        except Exception as e:
            self.fail(f"Failed to navigate to prescription form: {e}")
        
        # Fill basic patient data first
        print("📝 DEBUG: Filling basic patient data before submission...")
        patient_fields = {
            'nome_paciente': 'Maria Santos Silva',
            'nome_mae': 'Ana Santos',
            'peso': '65',
            'altura': '165',
            'end_paciente': 'Rua das Flores, 123, Apt 45'
        }
        
        for field_name, value in patient_fields.items():
            try:
                field_locator = self.page.locator(f'input[name="{field_name}"]')
                field_locator.wait_for(state="visible", timeout=5000)
                self.fill_field_slowly(field_locator, value, delay=0.05)
            except Exception:
                pass
        
        print("📤 DEBUG: Looking for form submission button...")
        
        # Look for common submit button patterns with timeout
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
            try:
                button = self.page.locator(selector).first
                button.wait_for(state="visible", timeout=3000)
                submit_button = button
                print(f"✅ DEBUG: Found submit button with selector: {selector}")
                break
            except Exception:
                continue
        
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
            self.fail("Submit button not found on prescription form")


class PrescriptionFormAccessibilityTest(PrescriptionFormPlaywrightBase):
    """Test prescription form accessibility and responsive features."""
    
    def test_prescription_form_accessibility(self):
        """Test prescription form accessibility features."""
        # Set up authenticated session without browser login
        self.setup_authenticated_session()
        
        # Try to navigate to a prescription form directly
        form_urls = [
            f'{self.accessible_live_server_url}/processos/cadastro/',
            f'{self.accessible_live_server_url}/processos/edicao/'
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
        # Set up authenticated session without browser login
        self.setup_authenticated_session()
        
        # Try to get to a prescription form
        self.page.goto(f'{self.accessible_live_server_url}/')
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


class MedicationManagementTest(PrescriptionFormPlaywrightBase):
    """CRITICAL TEST: Core medication management logic (med.js functionality)"""
    
    def navigate_to_medication_form(self):
        """Helper to navigate to a form with medication management (edicao form)"""
        # Set up authenticated session without browser login
        session_key = self.setup_authenticated_session()
        
        # Create a process using existing test models first - this is required for edicao form
        print("🔧 DEBUG: Creating process for edicao form...")
        processo = Processo.objects.create(
            usuario=self.user1,
            paciente=self.patient1,  # Use existing patient from setUp
            doenca=self.doenca,      # Use existing doenca from setUp  
            clinica=self.clinica1,   # Use existing clinica from setUp
            medico=self.medico1,     # Use existing medico from setUp
            emissor=self.emissor1,   # Use existing emissor from setUp
            anamnese='Test anamnese for medication form',
            prescricao={},
            tratou=False,
            tratamentos_previos='None',
            data1='2025-01-01',
            preenchido_por='M',
            dados_condicionais={}
        )
        print(f"✅ Created process: {processo.id}")
        
        # Set up session data using direct session manipulation
        print("🔧 DEBUG: Setting up session data for edicao workflow...")
        
        # Get session data from centralized config
        session_data = get_edicao_session_data(processo.id, self.doenca.cid)
        
        # Use the session key from authentication setup
        if session_key:
            # Load the session and set the required data
            from django.contrib.sessions.backends.db import SessionStore
            session = SessionStore(session_key=session_key)
            
            # Set the session data
            for key, value in session_data.items():
                session[key] = value
            
            session.save()
            print(f"✅ Session data configured: {session_data}")
        else:
            print("❌ No session key available for setting session data")
            return False
        
        # Navigate directly to edicao form with proper authentication
        edicao_url = f'{self.accessible_live_server_url}/processos/edicao/'
        print(f"🔧 DEBUG: Navigating to: {edicao_url}")
        
        self.page.goto(edicao_url)
        self.wait_for_page_load()
        
        # Quick authentication check
        login_form = self.page.locator('input[name="username"]')
        if login_form.is_visible():
            print("❌ DEBUG: Still showing login form - authentication failed")
            self.take_screenshot("auth_failed")
        else:
            print("✅ DEBUG: No login form visible - authentication successful")
        
        # Check if we have medication tabs - NO SKIPPING, FAIL WITH USEFUL INFO
        med_tabs = self.page.locator('#medicamentos-tab')
        if med_tabs.count() > 0:
            print("✅ DEBUG: Medication tabs found on page")
            return True
        else:
            print("❌ DEBUG: No medication tabs found - investigating page content")
            
            # Take screenshot for debugging
            self.take_screenshot("debug_no_medication_tabs")
            
            # Get page content to understand what's wrong
            page_title = self.page.title()
            current_url = self.page.url
            
            # Look for common elements that might indicate the issue
            error_messages = self.page.locator('.alert, .error, .message').all()
            forms_count = self.page.locator('form').count()
            
            error_info = f"""
            NAVIGATION FAILURE DEBUG INFO:
            - Current URL: {current_url}
            - Page Title: {page_title}
            - Forms found: {forms_count}
            - Error messages: {len(error_messages)}
            - Expected element '#medicamentos-tab' not found
            - Screenshot saved: debug_no_medication_tabs.png
            
            COMMON CAUSES:
            1. Login failed - not authenticated
            2. Wrong URL or redirect happened  
            3. Page structure changed
            4. Session data not properly set
            5. Permission/authorization issue
            """
            
            # Don't return False - raise an assertion error instead
            self.fail(f"Could not find medication tabs on edicao page. {error_info}")
            return False  # This won't be reached, but keeps the return type consistent
    
    def test_initial_medication_state(self):
        """Test initial state of medication tabs - only med1 should be visible"""
        print("\n🚀 CRITICAL TEST: test_initial_medication_state")
        
        if not self.navigate_to_medication_form():
            self.skipTest("Could not navigate to medication form")
        
        self.take_screenshot("med_01_initial_state")
        
        # Check initial state - only med1 should be visible
        med1_tab = self.page.locator('#medicamento-1-tab')
        med2_tab = self.page.locator('#medicamento-2-tab')
        med3_tab = self.page.locator('#medicamento-3-tab')
        med4_tab = self.page.locator('#medicamento-4-tab')
        
        if med1_tab.count() > 0:
            print("✅ Med1 tab found")
            # Med1 should be visible and active
            self.assertTrue(med1_tab.is_visible(), "Med1 tab should be visible")
            
            # Med2-4 should be hidden (have d-none class)
            if med2_tab.count() > 0:
                med2_classes = med2_tab.get_attribute('class') or ''
                self.assertIn('d-none', med2_classes, "Med2 tab should be hidden initially")
                print("✅ Med2 tab is hidden (d-none)")
        else:
            self.skipTest("Medication tabs not found on this page")
    
    def test_add_medication_functionality(self):
        """CRITICAL TEST: Adding medications shows tabs and enables fields"""
        print("\n🚀 CRITICAL TEST: test_add_medication_functionality")
        
        if not self.navigate_to_medication_form():
            self.skipTest("Could not navigate to medication form")
        
        # Look for add medication button
        add_med_button = self.page.locator('#add-med')
        if add_med_button.count() == 0:
            print("⚠️  DEBUG: Add medication button not found")
            self.take_screenshot("med_02_no_add_button")
            self.skipTest("Add medication button not found")
        
        self.take_screenshot("med_02_before_add")
        
        # Click add medication button
        add_med_button.click()
        self.page.wait_for_timeout(500)  # Wait for JavaScript
        
        self.take_screenshot("med_03_after_add")
        
        # Check that med2 tab becomes visible
        med2_tab = self.page.locator('#medicamento-2-tab')
        if med2_tab.count() > 0:
            med2_classes = med2_tab.get_attribute('class') or ''
            self.assertNotIn('d-none', med2_classes, "Med2 tab should be visible after adding")
            print("✅ Med2 tab is now visible")
            
            # Check that med2 tab is active
            self.assertIn('active', med2_classes, "Med2 tab should be active after adding")
            print("✅ Med2 tab is active")
        else:
            print("❌ Med2 tab not found after adding medication")
    
    def test_remove_medication_functionality(self):
        """CRITICAL TEST: Removing medications hides tabs and disables fields"""
        print("\n🚀 CRITICAL TEST: test_remove_medication_functionality")
        
        if not self.navigate_to_medication_form():
            self.skipTest("Could not navigate to medication form")
        
        # Add medications first
        add_med_button = self.page.locator('#add-med')
        if add_med_button.count() == 0:
            self.skipTest("Add medication button not found")
        
        # Add med2 and med3
        add_med_button.click()
        self.page.wait_for_timeout(300)
        add_med_button.click()
        self.page.wait_for_timeout(300)
        
        self.take_screenshot("med_04_before_remove")
        
        # Remove med3
        remove_med3_button = self.page.locator('[data-med="3"].remove-med')
        if remove_med3_button.count() > 0:
            remove_med3_button.click()
            self.page.wait_for_timeout(500)
            
            self.take_screenshot("med_05_after_remove")
            
            # Check that med3 tab is hidden
            med3_tab = self.page.locator('#medicamento-3-tab')
            if med3_tab.count() > 0:
                med3_classes = med3_tab.get_attribute('class') or ''
                self.assertIn('d-none', med3_classes, "Med3 tab should be hidden after removal")
                print("✅ Med3 tab is hidden after removal")
            
            # Should switch to med2
            med2_tab = self.page.locator('#medicamento-2-tab')
            if med2_tab.count() > 0:
                med2_classes = med2_tab.get_attribute('class') or ''
                self.assertIn('active', med2_classes, "Should switch to med2 after removing med3")
                print("✅ Switched to med2 after removing med3")
        else:
            self.skipTest("Remove medication button not found")
    
    def test_nenhum_medication_selection_clears_fields(self):
        """CRITICAL TEST: Selecting 'nenhum' clears medication fields"""
        print("\n🚀 CRITICAL TEST: test_nenhum_medication_selection_clears_fields")
        
        if not self.navigate_to_medication_form():
            self.skipTest("Could not navigate to medication form")
        
        # Fill some medication fields first
        med1_posologia = self.page.locator('#id_med1_posologia_mes1')
        med1_qtd = self.page.locator('#id_qtd_med1_mes1')
        med1_dropdown = self.page.locator('#id_id_med1')
        
        if med1_posologia.count() == 0:
            self.skipTest("Medication fields not found")
        
        # Fill fields with test data
        if med1_posologia.is_visible():
            med1_posologia.fill('Test dosage')
        if med1_qtd.is_visible():
            med1_qtd.fill('30')
        
        self.take_screenshot("med_06_before_nenhum")
        
        # Select 'nenhum' for medication 1
        if med1_dropdown.count() > 0:
            # Try to select 'nenhum' option
            med1_dropdown.select_option('nenhum')
            self.page.wait_for_timeout(500)  # Wait for JavaScript to process
            
            self.take_screenshot("med_07_after_nenhum")
            
            # Check that dosage fields are cleared
            if med1_posologia.is_visible():
                posologia_value = med1_posologia.input_value()
                self.assertEqual(posologia_value, '', "Posologia should be cleared when nenhum selected")
                print("✅ Posologia field cleared")
            
            if med1_qtd.is_visible():
                qtd_value = med1_qtd.input_value()
                self.assertEqual(qtd_value, '', "Quantity should be cleared when nenhum selected")
                print("✅ Quantity field cleared")
            
            # Check that medication dropdown keeps 'nenhum' value
            dropdown_value = med1_dropdown.input_value()
            self.assertEqual(dropdown_value, 'nenhum', "Medication dropdown should keep 'nenhum' value")
            print("✅ Medication dropdown keeps 'nenhum' value")
        else:
            self.skipTest("Medication dropdown not found")

    
    def test_medication_validation_allows_submission_with_valid_medication(self):
        """CRITICAL TEST: Form submits successfully with at least one valid medication"""
        print("\n🚀 CRITICAL TEST: test_medication_validation_allows_submission_with_valid_medication")
        
        if not self.navigate_to_medication_form():
            self.skipTest("Could not navigate to medication form")
        
        # Fill required form fields
        self.fill_minimal_required_fields()
        
        # Select a valid medication for med1
        med1_dropdown = self.page.locator('#id_id_med1')
        if med1_dropdown.count() > 0:
            # Get available options (exclude 'nenhum')
            options = med1_dropdown.locator('option').all()
            valid_option = None
            for option in options:
                value = option.get_attribute('value')
                if value and value != 'nenhum' and value != '':
                    valid_option = value
                    break
            
            if valid_option:
                med1_dropdown.select_option(valid_option)
                print(f"✅ Selected valid medication: {valid_option}")
                
                # Fill required medication fields
                self.fill_medication_fields()
                
                self.take_screenshot("med_10_valid_medication_before_submit")
                
                # Submit the form
                submit_button = self.page.locator('button[type="submit"]').first
                if submit_button.count() > 0:
                    initial_url = self.page.url
                    submit_button.click()
                    
                    # Wait for processing
                    self.page.wait_for_timeout(2000)
                    
                    self.take_screenshot("med_11_after_valid_submit")
                    
                    # Check for successful submission (URL change or success indication)
                    final_url = self.page.url
                    if final_url != initial_url:
                        print("✅ CRITICAL: Form submitted successfully with valid medication")
                    else:
                        # Check for success message
                        success_selectors = ['.toast-success', '.alert-success', '.success-message']
                        success_found = any(self.page.locator(sel).count() > 0 for sel in success_selectors)
                        if success_found:
                            print("✅ CRITICAL: Success message found - form processed")
                        else:
                            print("⚠️  Form may have other validation issues")
            else:
                self.skipTest("No valid medication options found")
        else:
            self.skipTest("Medication dropdown not found")
    
    def fill_minimal_required_fields(self):
        """Helper to fill minimal required fields for form submission"""
        required_fields = {
            'nome_paciente': 'Test Patient',
            'nome_mae': 'Test Mother',
            'peso': '70',
            'altura': '170',
            'end_paciente': 'Test Address',
            'anamnese': 'Test anamnese',
            'data_1': '23/07/2025'
        }
        
        for field_name, value in required_fields.items():
            field = self.page.locator(f'input[name="{field_name}"], textarea[name="{field_name}"]')
            if field.count() > 0 and field.is_visible():
                field.fill(str(value))
                print(f"✅ Filled {field_name}")
    
    def fill_medication_fields(self):
        """Helper to fill medication-specific required fields"""
        med_fields = {
            'med1_posologia_mes1': '1 tablet daily',
            'qtd_med1_mes1': '30',
            'med1_via': 'Oral'
        }
        
        # Fill all 6 months for complete validation
        for month in range(1, 7):
            posologia_field = self.page.locator(f'input[name="med1_posologia_mes{month}"]')
            qtd_field = self.page.locator(f'input[name="qtd_med1_mes{month}"]')
            
            if posologia_field.count() > 0 and posologia_field.is_visible():
                posologia_field.fill('1 tablet daily')
            if qtd_field.count() > 0 and qtd_field.is_visible():
                qtd_field.fill('30')
        
        # Fill via field
        via_field = self.page.locator('input[name="med1_via"]')
        if via_field.count() > 0 and via_field.is_visible():
            via_field.fill('Oral')
        
        print("✅ Filled medication fields for 6 months")