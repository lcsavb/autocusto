"""
Prescription Form Frontend Tests using Selenium
Tests the complex prescription form workflow and functionality
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
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class PrescriptionFormTestBase(StaticLiveServerTestCase):
    """Base class for prescription form tests with common setup and utilities."""
    
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
            import time
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


class PrescriptionFormTest(PrescriptionFormTestBase):
    """Test complex prescription form filling workflow."""

    def test_prescription_form_navigation(self):
        """Test navigation from home page to prescription form with extensive debugging."""
        
        print("\n🚀 TEST: test_prescription_form_navigation")
        
        # Login as medico
        self.login_user('medico@example.com', 'testpass123')
        
        # Go to home page
        print("🏠 DEBUG: Navigating to home page")
        self.driver.get(f'{self.live_server_url}/')
        self.take_screenshot("01_home_page_logged_in")
        self.debug_page_state("Home page after login")
        
        # Wait for home form
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "cpf_paciente"))
            )
            print("✅ DEBUG: Home form with CPF field found")
        except TimeoutException:
            print("❌ DEBUG: CPF field not found on home page")
            self.take_screenshot("01_error_no_cpf_field")
            raise
        
        # Fill CPF and CID to navigate to prescription form
        print("📝 DEBUG: Filling home form...")
        cpf_field = self.driver.find_element(By.NAME, "cpf_paciente")
        cid_field = self.driver.find_element(By.NAME, "cid")
        
        self.fill_field_slowly(cpf_field, "72834565031")  # Existing patient
        self.fill_field_slowly(cid_field, "G40.0")        # Epilepsia
        
        self.take_screenshot("02_home_form_filled")
        
        # Submit form
        print("📤 DEBUG: Submitting home form...")
        submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cadastrar')]")
        submit_button.click()
        
        # Wait for navigation to prescription form
        print("⏳ DEBUG: Waiting for navigation...")
        time.sleep(5)  # Give more time for navigation
        current_url = self.driver.current_url
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
                page_source = self.driver.page_source
                if 'error' in page_source.lower() or 'erro' in page_source.lower():
                    print("❌ DEBUG: Error messages detected on home page")
                    print(f"Page content preview: {page_source[:500]}")
        
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
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "nome_paciente"))
            )
            print("✅ DEBUG: Patient name field found")
        except TimeoutException:
            print("❌ DEBUG: Patient name field not found")
            self.take_screenshot("04_error_no_patient_fields")
            # Try to find any input fields
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"❌ DEBUG: Available input fields: {[inp.get_attribute('name') for inp in all_inputs]}")
            raise
        
        # Fill basic patient information
        patient_fields = {
            'nome_paciente': 'Maria Santos Silva',
            'nome_mae': 'Ana Santos',
            'peso': '65',
            'altura': '165',
            'end_paciente': 'Rua das Flores, 123, Apt 45'
        }
        
        print("📝 DEBUG: Filling patient basic data...")
        for field_name, value in patient_fields.items():
            try:
                field = self.driver.find_element(By.NAME, field_name)
                self.fill_field_slowly(field, value, delay=0.05)
                print(f"✅ DEBUG: Filled {field_name}: {value}")
            except NoSuchElementException:
                print(f"⚠️  DEBUG: Field {field_name} not found on page")
        
        self.take_screenshot("05_patient_basic_data_filled")
        
        # Test dropdown selection (incapaz field)
        print("📋 DEBUG: Testing dropdown fields...")
        try:
            incapaz_select = Select(self.driver.find_element(By.NAME, "incapaz"))
            options = [opt.get_attribute('value') for opt in incapaz_select.options]
            print(f"✅ DEBUG: Incapaz dropdown options: {options}")
            incapaz_select.select_by_value("False")  # "Não"
            print("✅ DEBUG: Selected incapaz: Não")
        except NoSuchElementException:
            print("⚠️  DEBUG: Incapaz dropdown not found")
        
        # Test clinic selection
        try:
            clinica_select = Select(self.driver.find_element(By.NAME, "clinicas"))
            options = [(opt.get_attribute('value'), opt.text) for opt in clinica_select.options]
            print(f"✅ DEBUG: Clinica dropdown options: {options}")
            # Select first available clinic (should be our test clinic)
            if len(options) > 1:  # Skip empty option
                clinica_select.select_by_index(1)
                print("✅ DEBUG: Selected clinic")
            else:
                print("⚠️  DEBUG: No clinic options available")
        except NoSuchElementException:
            print("⚠️  DEBUG: Clinic dropdown not found")
        
        self.take_screenshot("06_patient_data_with_dropdowns")
        print("✅ DEBUG: Basic patient data test completed successfully!")

    def test_prescription_form_debug_fields(self):
        """Debug test to explore all available fields on the prescription form."""
        
        print("\n🔍 TEST: test_prescription_form_debug_fields")
        
        # Navigate to prescription form
        self.test_prescription_form_navigation()
        
        print("🔍 DEBUG: Analyzing all form fields...")
        
        # Get all input fields
        all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 DEBUG: Found {len(all_inputs)} input fields:")
        for i, inp in enumerate(all_inputs):
            name = inp.get_attribute('name') or f"unnamed_{i}"
            field_type = inp.get_attribute('type') or 'text'
            placeholder = inp.get_attribute('placeholder') or ''
            print(f"   {i+1}. {name} (type: {field_type}) - {placeholder}")
        
        # Get all select fields
        all_selects = self.driver.find_elements(By.TAG_NAME, "select")
        print(f"📋 DEBUG: Found {len(all_selects)} select fields:")
        for i, sel in enumerate(all_selects):
            name = sel.get_attribute('name') or f"unnamed_select_{i}"
            options = sel.find_elements(By.TAG_NAME, "option")
            option_texts = [opt.text for opt in options[:3]]  # First 3 options
            print(f"   {i+1}. {name} - Options: {option_texts}...")
        
        # Get all textarea fields
        all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        print(f"📄 DEBUG: Found {len(all_textareas)} textarea fields:")
        for i, ta in enumerate(all_textareas):
            name = ta.get_attribute('name') or f"unnamed_textarea_{i}"
            placeholder = ta.get_attribute('placeholder') or ''
            print(f"   {i+1}. {name} - {placeholder}")
        
        # Take comprehensive screenshot
        self.take_screenshot("07_form_fields_debug")
        
        print("✅ DEBUG: Field analysis complete!")

    def test_prescription_form_with_pdf_generation(self):
        """Test complete prescription form filling AND PDF generation verification."""
        
        print("\n📄 TEST: test_prescription_form_with_pdf_generation")
        print("🎯 This test verifies: 1) Complete form filling, 2) Form submission, 3) PDF generation")
        
        # Navigate to prescription form
        self.test_prescription_form_navigation()
        
        print("📝 DEBUG: Filling COMPLETE prescription form for PDF generation...")
        
        # Wait for form to be fully loaded
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.NAME, "nome_paciente"))
        )
        
        # Fill ALL FORM FIELDS COMPLETELY for PDF generation
        print("👤 DEBUG: Filling COMPLETE patient data (ALL FIELDS)...")
        
        # Count total fields to fill for progress tracking
        total_text_fields = 67  # From our debug analysis
        total_dropdowns = 16
        total_textareas = 2
        total_fields = total_text_fields + total_dropdowns + total_textareas
        filled_count = 0
        
        print(f"📊 DEBUG: Planning to fill {total_fields} total fields ({total_text_fields} inputs + {total_dropdowns} dropdowns + {total_textareas} textareas)")
        
        # COMPLETE patient information fields
        comprehensive_fields = {
            'nome_paciente': 'Maria Santos Silva de Oliveira',
            'nome_mae': 'Ana Santos Silva',
            'altura': '165',
            'peso': '65',
            'end_paciente': 'Rua das Flores, 123, Apt 45, Vila Madalena, São Paulo, SP',
            'anamnese': 'Paciente com epilepsia focal temporal. Crises iniciaram há 2 anos com frequência de 2-3 episódios por semana. Sem comorbidades conhecidas. Nega uso de álcool ou drogas.',
            'telefone1_paciente': '11999999999',
            'telefone2_paciente': '11888888888', 
            'email_paciente': 'maria.santos@email.com',
            'rg': '123456789',
            'tratamentos_previos': 'Uso prévio de fenitoína 300mg/dia por 6 meses sem controle adequado das crises. Suspendido por efeitos colaterais.',
        }
        
        print(f"🔍 DEBUG: Filling {len(comprehensive_fields)} comprehensive patient fields...")
        for field_name, value in comprehensive_fields.items():
            try:
                print(f"   🎯 Attempting to fill {field_name} with: {value[:50]}...")
                field = self.find_element_robust(By.NAME, field_name, timeout=5)
                self.fill_field_slowly(field, value, delay=0.01)
                filled_count += 1
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {field_name}")
            except NoSuchElementException:
                print(f"   ⚠️  SKIP: Field {field_name} not found on form")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to fill {field_name}: {e}")
        
        print(f"📊 DEBUG: Patient fields progress: {filled_count}/{total_fields} fields filled so far")
        
        # Fill date field
        print("📅 DEBUG: Filling date field...")
        try:
            import datetime
            today = datetime.date.today()
            date_str = today.strftime("%d/%m/%Y")
            print(f"   🎯 Attempting to fill data_1 with: {date_str}")
            date_field = self.find_element_robust(By.NAME, "data_1", timeout=5)
            self.fill_field_slowly(date_field, date_str)
            filled_count += 1
            print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled date: {date_str}")
        except NoSuchElementException:
            print("   ⚠️  SKIP: Date field not found")
        except Exception as e:
            print(f"   ❌ ERROR: Failed to fill date: {e}")
        
        # Fill ALL dropdown fields with extensive debugging
        print("📋 DEBUG: Filling ALL dropdown fields...")
        dropdown_selections = {
            'incapaz': ('False', 'Não'),
            'tratou': ('False', 'Não'), 
            'preenchido_por': ('medico', 'médico'),
            'consentimento': ('True', 'Sim'),
            'emitir_exames': ('True', 'Sim'),
            'emitir_relatorio': ('True', 'Sim'),
            'etnia': ('branca', 'Branca'),  # Try first available option
        }
        
        print(f"🔍 DEBUG: Filling {len(dropdown_selections)} dropdown selections...")
        for field_name, (value, display_name) in dropdown_selections.items():
            try:
                print(f"   🎯 Attempting dropdown {field_name} = {value} ({display_name})...")
                select_element = Select(self.driver.find_element(By.NAME, field_name))
                
                # Show available options for debugging
                options = [(opt.get_attribute('value'), opt.text) for opt in select_element.options]
                print(f"      📋 Available options: {options}")
                
                select_element.select_by_value(value)
                filled_count += 1
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Selected {field_name}: {display_name}")
            except NoSuchElementException:
                print(f"   ⚠️  SKIP: Dropdown {field_name} not found")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to select {field_name}: {e}")
        
        # Special handling for clinica dropdown
        print("🏥 DEBUG: Handling clinica dropdown...")
        try:
            print("   🎯 Attempting to select clinica...")
            clinica_select = Select(self.driver.find_element(By.NAME, "clinicas"))
            options = [(opt.get_attribute('value'), opt.text) for opt in clinica_select.options]
            print(f"      📋 Clinica options: {options}")
            
            if len(clinica_select.options) > 1:
                clinica_select.select_by_index(1)  # Select first real option
                filled_count += 1
                selected_text = clinica_select.first_selected_option.text
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Selected clinica: {selected_text}")
            else:
                print("   ⚠️  SKIP: No clinica options available")
        except Exception as e:
            print(f"   ❌ ERROR: Failed to select clinica: {e}")
        
        print(f"📊 DEBUG: Dropdown progress: {filled_count}/{total_fields} fields filled so far")
        
        # Fill ALL 4 MEDICATIONS COMPLETELY with extensive debugging
        print("💊 DEBUG: Filling ALL 4 MEDICATIONS with ALL FIELDS...")
        
        for med_num in range(1, 5):  # med1, med2, med3, med4
            print(f"💊 DEBUG: === MEDICATION {med_num} ===")
            
            # Select medication from dropdown
            med_select_name = f"id_med{med_num}"
            try:
                print(f"   🎯 Selecting medication {med_num} from dropdown...")
                med_select = Select(self.driver.find_element(By.NAME, med_select_name))
                options = [(opt.get_attribute('value'), opt.text) for opt in med_select.options]
                print(f"      📋 Med{med_num} options: {options}")
                
                if len(med_select.options) > med_num:  # Ensure we have enough options
                    med_select.select_by_index(med_num)  # Select different med for each slot
                    filled_count += 1
                    selected_text = med_select.first_selected_option.text
                    print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Selected med{med_num}: {selected_text}")
                elif len(med_select.options) > 1:
                    med_select.select_by_index(1)  # Select first available
                    filled_count += 1
                    selected_text = med_select.first_selected_option.text
                    print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Selected med{med_num}: {selected_text}")
                else:
                    print(f"   ⚠️  SKIP: No medication options for med{med_num}")
                    continue
            except Exception as e:
                print(f"   ❌ ERROR: Failed to select med{med_num}: {e}")
                continue
            
            # Fill medication via/route
            via_field_name = f"med{med_num}_via"
            try:
                print(f"   🎯 Filling {via_field_name}...")
                via_field = self.find_element_robust(By.NAME, via_field_name, timeout=5)
                self.fill_field_slowly(via_field, "Oral", delay=0.01)
                filled_count += 1
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {via_field_name}: Oral")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to fill {via_field_name}: {e}")
            
            # Fill ALL 6 months of posologia and quantity for this medication
            for mes in range(1, 7):  # mes1 through mes6
                posologia_field = f"med{med_num}_posologia_mes{mes}"
                qtd_field = f"med{med_num}_qtd_mes{mes}"
                
                # Fill posologia
                try:
                    print(f"   🎯 Filling {posologia_field}...")
                    pos_field = self.find_element_robust(By.NAME, posologia_field, timeout=5)
                    posologia_value = f"1 comprimido {8 + med_num}/{8 + med_num}h"  # Vary by medication
                    self.fill_field_slowly(pos_field, posologia_value, delay=0.01)
                    filled_count += 1
                    print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {posologia_field}: {posologia_value}")
                except Exception as e:
                    print(f"   ❌ ERROR: Failed to fill {posologia_field}: {e}")
                
                # Fill quantity  
                try:
                    print(f"   🎯 Filling {qtd_field}...")
                    qtd_field_element = self.find_element_robust(By.NAME, qtd_field, timeout=5)
                    qtd_value = str(90 + (med_num * 10) + mes)  # Vary quantity by med and month
                    self.fill_field_slowly(qtd_field_element, qtd_value, delay=0.01)
                    filled_count += 1
                    print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {qtd_field}: {qtd_value}")
                except Exception as e:
                    print(f"   ❌ ERROR: Failed to fill {qtd_field}: {e}")
            
            # Set repetir posologia dropdown
            repetir_field_name = f"med{med_num}_repetir_posologia"
            try:
                print(f"   🎯 Setting {repetir_field_name}...")
                repetir_select = Select(self.driver.find_element(By.NAME, repetir_field_name))
                options = [(opt.get_attribute('value'), opt.text) for opt in repetir_select.options]
                print(f"      📋 Repetir options: {options}")
                
                repetir_select.select_by_value("True")
                filled_count += 1
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Set {repetir_field_name}: Sim")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to set {repetir_field_name}: {e}")
            
            print(f"📊 DEBUG: Med{med_num} progress: {filled_count}/{total_fields} fields filled so far")
        
        # Fill textarea fields
        print("📄 DEBUG: Filling textarea fields...")
        textarea_data = {
            'relatorio': f'RELATÓRIO MÉDICO\n\nPaciente: Maria Santos Silva de Oliveira\nDiagnóstico: Epilepsia focal temporal (G40.0)\n\nHistória: Crises epilépticas há 2 anos, frequência 2-3x/semana.\nExame físico: Normal\nExames complementares: EEG alterado, RM cerebral normal\n\nConclusão: Epilepsia focal temporal sem lesão estrutural.\nTratamento indicado conforme protocolo.',
            'exames': f'EXAMES SOLICITADOS\n\n1. EEG de controle em 3 meses\n2. Hemograma completo\n3. Função hepática (TGO, TGP)\n4. Função renal (creatinina, ureia)\n5. Níveis séricos do anticonvulsivante\n\nReavaliação em 30 dias.'
        }
        
        for field_name, value in textarea_data.items():
            try:
                print(f"   🎯 Filling textarea {field_name} ({len(value)} chars)...")
                textarea_field = self.find_element_robust(By.NAME, field_name, timeout=5)
                self.fill_field_slowly(textarea_field, value, delay=0.001)  # Faster for long text
                filled_count += 1
                print(f"   ✅ SUCCESS [{filled_count}/{total_fields}] Filled {field_name}")
            except Exception as e:
                print(f"   ❌ ERROR: Failed to fill {field_name}: {e}")
        
        print(f"🎉 DEBUG: FORM FILLING COMPLETE! Total fields filled: {filled_count}/{total_fields}")
        
        # Take comprehensive screenshot of filled form
        self.take_screenshot("13_complete_form_filled_all_fields")
        
        self.take_screenshot("13_form_ready_for_submission")
        
        # Check for PDF-related files before submission
        print("📄 DEBUG: Checking PDF directory before submission...")
        pdf_directories = [
            "/home/lucas/code/autocusto/static/tmp/",
            "/home/lucas/code/autocusto/processos/tmp/",
            "/home/lucas/code/autocusto/tmp/"
        ]
        
        initial_pdf_files = {}
        for pdf_dir in pdf_directories:
            try:
                import os
                if os.path.exists(pdf_dir):
                    files = os.listdir(pdf_dir)
                    pdf_files = [f for f in files if f.endswith('.pdf')]
                    initial_pdf_files[pdf_dir] = pdf_files
                    print(f"📄 Initial PDFs in {pdf_dir}: {len(pdf_files)} files")
                else:
                    print(f"📄 Directory {pdf_dir} does not exist")
            except Exception as e:
                print(f"⚠️  Error checking {pdf_dir}: {e}")
        
        # Submit the form
        print("📤 DEBUG: Submitting form for PDF generation...")
        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            
            # Scroll to submit button
            self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            time.sleep(1)
            
            submit_button.click()
            print("✅ Form submitted!")
            
            # Wait for processing and potential PDF generation
            print("⏳ DEBUG: Waiting for PDF generation...")
            time.sleep(10)  # Give time for PDF processing
            
            current_url = self.driver.current_url
            print(f"📍 DEBUG: After submission: {current_url}")
            
            self.take_screenshot("14_after_pdf_submission")
            
            # Check if redirected to PDF page
            pdf_url_indicators = [
                '/processos/pdf/' in current_url,
                'pdf' in current_url.lower()
            ]
            
            if any(pdf_url_indicators):
                print("✅ DEBUG: Redirected to PDF page!")
                
                # Look for iframe containing PDF
                print("🖼️  DEBUG: Checking for PDF iframe...")
                try:
                    iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                    print(f"📦 Found {len(iframes)} iframe(s)")
                    
                    pdf_iframe_found = False
                    for i, iframe in enumerate(iframes):
                        src = iframe.get_attribute('src') or ''
                        print(f"   iframe {i+1}: {src}")
                        
                        if '.pdf' in src or 'pdf' in src.lower():
                            print(f"✅ PDF iframe found: {src}")
                            pdf_iframe_found = True
                            
                            # Try to access the iframe to verify PDF content
                            try:
                                self.driver.switch_to.frame(iframe)
                                iframe_title = self.driver.title
                                iframe_url = self.driver.current_url
                                print(f"🔍 Inside iframe - Title: {iframe_title}, URL: {iframe_url}")
                                
                                # Check if it's a PDF by looking for PDF viewer elements
                                pdf_indicators = [
                                    iframe_url.endswith('.pdf'),
                                    'pdf' in iframe_url.lower(),
                                    'application/pdf' in self.driver.page_source.lower()
                                ]
                                
                                if any(pdf_indicators):
                                    print("✅ CONFIRMED: PDF content detected in iframe!")
                                else:
                                    print("⚠️  DEBUG: Iframe doesn't appear to contain PDF")
                                
                                self.driver.switch_to.default_content()
                                
                            except Exception as iframe_e:
                                print(f"⚠️  DEBUG: Cannot access iframe content: {iframe_e}")
                                self.driver.switch_to.default_content()
                    
                    if not pdf_iframe_found:
                        print("⚠️  DEBUG: No PDF iframe found")
                        
                except Exception as e:
                    print(f"⚠️  DEBUG: Error checking iframes: {e}")
                
                # Also look for direct PDF links
                page_source = self.driver.page_source
                pdf_elements = [
                    'pdf' in page_source.lower(),
                    'download' in page_source.lower(),
                    '.pdf' in page_source
                ]
                
                if any(pdf_elements):
                    print("✅ DEBUG: PDF-related content found on page")
                else:
                    print("⚠️  DEBUG: No PDF content detected on page")
                    
            else:
                print(f"⚠️  DEBUG: Not redirected to PDF page. Current URL: {current_url}")
                
                # Check if there are form errors
                page_source = self.driver.page_source
                if 'error' in page_source.lower() or 'obrigatório' in page_source.lower():
                    print("❌ DEBUG: Form has validation errors")
                    # Look for specific error messages
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error, .invalid-feedback")
                    for error in error_elements:
                        if error.is_displayed():
                            print(f"❌ Error: {error.text}")
                else:
                    print("⚠️  DEBUG: No obvious form errors detected")
            
            # Check for new PDF files created
            print("📄 DEBUG: Checking for new PDF files...")
            new_pdf_files = {}
            for pdf_dir in pdf_directories:
                try:
                    if os.path.exists(pdf_dir):
                        files = os.listdir(pdf_dir)
                        pdf_files = [f for f in files if f.endswith('.pdf')]
                        new_pdf_files[pdf_dir] = pdf_files
                        
                        initial_count = len(initial_pdf_files.get(pdf_dir, []))
                        new_count = len(pdf_files)
                        
                        if new_count > initial_count:
                            new_files = [f for f in pdf_files if f not in initial_pdf_files.get(pdf_dir, [])]
                            print(f"✅ NEW PDF created in {pdf_dir}: {new_files}")
                        else:
                            print(f"📄 No new PDFs in {pdf_dir} ({new_count} files)")
                except Exception as e:
                    print(f"⚠️  Error checking {pdf_dir}: {e}")
            
            # Try to find PDF links on the current page
            print("🔗 DEBUG: Looking for PDF download links...")
            try:
                pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf') or contains(text(), 'PDF') or contains(text(), 'Download')]")
                if pdf_links:
                    print(f"✅ Found {len(pdf_links)} PDF-related links:")
                    for i, link in enumerate(pdf_links[:3]):  # Show first 3
                        href = link.get_attribute('href') or 'No href'
                        text = link.text or 'No text'
                        print(f"   {i+1}. {text} - {href}")
                else:
                    print("⚠️  No PDF download links found")
            except Exception as e:
                print(f"⚠️  Error finding PDF links: {e}")
                
        except NoSuchElementException:
            print("❌ DEBUG: Submit button not found")
            self.take_screenshot("14_no_submit_button")
        except Exception as e:
            print(f"❌ DEBUG: Error during submission: {e}")
            self.take_screenshot("14_submission_error")
            
        # COMPREHENSIVE PDF VERIFICATION with assertions
        print("🎯 DEBUG: FINAL PDF VERIFICATION - Testing both form submission AND PDF generation...")
        
        # Verify form submission was successful
        current_url = self.driver.current_url
        form_submitted_successfully = '/processos/pdf/' in current_url or 'pdf' in current_url.lower()
        
        if not form_submitted_successfully:
            print(f"❌ CRITICAL: Form submission failed - not redirected to PDF page. URL: {current_url}")
            page_source = self.driver.page_source
            if 'error' in page_source.lower() or 'obrigatório' in page_source.lower():
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error, .invalid-feedback")
                for error in error_elements:
                    if error.is_displayed():
                        print(f"❌ FORM ERROR: {error.text}")
            self.take_screenshot("15_form_submission_failed")
            self.fail(f"Form submission failed - expected PDF redirect but got: {current_url}")
        
        print("✅ VERIFIED: Form submitted successfully - redirected to PDF page")
        
        # Verify PDF generation via iframe detection
        print("🖼️  DEBUG: Verifying PDF generation via iframe...")
        pdf_iframe_found = False
        pdf_iframe_src = ""
        
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"   📦 Found {len(iframes)} iframe(s) on page")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute('src') or ''
                print(f"   iframe {i+1}: {src}")
                
                if '.pdf' in src or 'pdf' in src.lower():
                    pdf_iframe_found = True
                    pdf_iframe_src = src
                    print(f"✅ VERIFIED: PDF iframe found at {src}")
                    
                    # Try to access iframe content for additional verification
                    try:
                        self.driver.switch_to.frame(iframe)
                        iframe_url = self.driver.current_url
                        print(f"   🔍 Inside iframe URL: {iframe_url}")
                        
                        # Verify it's actually a PDF
                        if iframe_url.endswith('.pdf') or 'application/pdf' in self.driver.page_source.lower():
                            print("✅ CONFIRMED: Iframe contains actual PDF content")
                        
                        self.driver.switch_to.default_content()
                        
                    except Exception as iframe_e:
                        print(f"   ⚠️  Could not access iframe content: {iframe_e}")
                        self.driver.switch_to.default_content()
                    
                    break
            
            if not pdf_iframe_found:
                print("❌ CRITICAL: No PDF iframe found on page")
                self.take_screenshot("15_no_pdf_iframe")
                # Look for any PDF-related content as fallback
                page_source = self.driver.page_source
                if 'pdf' in page_source.lower():
                    print("   ⚠️  Found PDF text in page source, but no iframe")
                else:
                    print("   ❌ No PDF content detected at all")
                    
        except Exception as e:
            print(f"❌ ERROR during iframe verification: {e}")
            self.take_screenshot("15_iframe_verification_error")
        
        # Verify new PDF files were created (secondary verification)
        print("📄 DEBUG: Verifying PDF file creation...")
        new_pdf_files_created = False
        
        for pdf_dir in pdf_directories:
            try:
                if os.path.exists(pdf_dir):
                    files = os.listdir(pdf_dir)
                    pdf_files = [f for f in files if f.endswith('.pdf')]
                    initial_count = len(initial_pdf_files.get(pdf_dir, []))
                    new_count = len(pdf_files)
                    
                    if new_count > initial_count:
                        new_files = [f for f in pdf_files if f not in initial_pdf_files.get(pdf_dir, [])]
                        new_pdf_files_created = True
                        print(f"✅ VERIFIED: New PDF files created in {pdf_dir}: {new_files}")
                        break
                    else:
                        print(f"   📄 No new files in {pdf_dir} ({new_count} total files)")
            except Exception as e:
                print(f"   ❌ Error checking {pdf_dir}: {e}")
        
        # FINAL ASSERTIONS
        print("🎯 DEBUG: FINAL TEST ASSERTIONS...")
        
        # Assert form was filled completely
        min_expected_fields = 50  # Should have filled at least 50 fields
        self.assertGreaterEqual(
            filled_count, 
            min_expected_fields,
            f"Form not filled completely - only {filled_count} fields filled, expected at least {min_expected_fields}"
        )
        print(f"✅ ASSERTION PASSED: Form filled completely ({filled_count} fields)")
        
        # Assert form submission successful  
        self.assertTrue(
            form_submitted_successfully,
            f"Form submission failed - not redirected to PDF page. Current URL: {current_url}"
        )
        print("✅ ASSERTION PASSED: Form submitted successfully")
        
        # Assert PDF generation successful
        self.assertTrue(
            pdf_iframe_found,
            f"PDF generation failed - no PDF iframe found on page after form submission"
        )
        print("✅ ASSERTION PASSED: PDF generation verified via iframe")
        
        # Take final success screenshot
        self.take_screenshot("16_pdf_generation_success")
        
        print("🎉 SUCCESS: COMPLETE TEST PASSED!")
        print(f"   ✅ Form filled: {filled_count} fields")
        print(f"   ✅ Form submitted: {current_url}")
        print(f"   ✅ PDF generated: {pdf_iframe_src}")
        
        return True

    def test_pdf_generation_verification_only(self):
        """Simplified test focused specifically on PDF generation verification."""
        
        print("\\n📄 TEST: test_pdf_generation_verification_only")
        
        # Navigate to prescription form
        self.test_prescription_form_navigation()
        
        print("🎯 DEBUG: Running focused PDF generation test...")
        
        # Fill minimal required fields
        try:
            # Patient name (required)
            name_field = self.find_element_robust(By.NAME, "nome_paciente", timeout=5)
            self.fill_field_slowly(name_field, "Test Patient PDF", delay=0.01)
            
            # Date (required)
            import datetime
            today = datetime.date.today()
            date_str = today.strftime("%d/%m/%Y")
            date_field = self.find_element_robust(By.NAME, "data_1", timeout=5)
            self.fill_field_slowly(date_field, date_str)
            
            # Essential dropdowns
            incapaz_select = Select(self.driver.find_element(By.NAME, "incapaz"))
            incapaz_select.select_by_value("False")
            
            clinica_select = Select(self.driver.find_element(By.NAME, "clinicas"))
            if len(clinica_select.options) > 1:
                clinica_select.select_by_index(1)
            
            print("✅ DEBUG: Minimal form data filled")
            
        except Exception as e:
            print(f"❌ DEBUG: Error filling minimal form: {e}")
            self.take_screenshot("16_minimal_form_error")
            self.fail("Could not fill minimal form data")
        
        # Submit and verify PDF
        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            time.sleep(1)
            submit_button.click()
            
            print("⏳ DEBUG: Waiting for PDF response...")
            time.sleep(15)  # Longer wait for PDF generation
            
            current_url = self.driver.current_url
            print(f"📍 DEBUG: Final URL: {current_url}")
            
            self.take_screenshot("17_pdf_final_result")
            
            # Check for PDF iframe specifically
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            pdf_iframe_found = False
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if '.pdf' in src or 'pdf' in src.lower():
                    pdf_iframe_found = True
                    print(f"✅ SUCCESS: PDF iframe confirmed at {src}")
                    break
            
            # Assert PDF generation was successful
            self.assertTrue(
                pdf_iframe_found,
                "PDF generation failed: No PDF iframe found after form submission"
            )
            
            print("✅ SUCCESS: PDF generation test passed!")
            
        except NoSuchElementException:
            self.take_screenshot("17_no_submit_button")
            self.fail("Submit button not found")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.take_screenshot("17_pdf_generation_error")
            self.fail(f"PDF generation test failed: {e}")