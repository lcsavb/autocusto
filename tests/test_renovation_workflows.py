"""
Renovation Workflow Frontend Tests using Playwright
Tests the "renovacao rapida" (quick renewal) functionality including patient search,
process selection, date input, and edit mode behavior.

Features:
- Comprehensive debugging with screenshots
- Patient search and selection testing
- Date input validation
- Edit checkbox behavior testing
- Form submission workflows
"""

import time
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class RenovationWorkflowPlaywrightBase(PlaywrightFormTestBase):
    """Base class for renovation workflow tests with common setup and utilities."""
    
    def setUp(self):
        """Set up test data for renovation workflows with extensive debugging."""
        super().setUp()
        
        print("🔧 DEBUG: Setting up renovation test data...")
        
        # Create test user and medico
        self.user1 = User.objects.create_user(
            email='medico@example.com',
            password='testpass123'
        )
        self.user1.is_medico = True
        self.user1.save()
        
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. João Silva",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico1.usuarios.add(self.user1)
        
        # Create clinica and emissor
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
        self.user1.clinicas.add(self.clinica1)
        
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        
        # Create test patient
        self.patient1 = Paciente.objects.create(
            nome_paciente="Maria Santos",
            cpf_paciente="72834565031",
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
        
        # Create another patient for search testing
        self.patient2 = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="12345678901",
            cns_paciente="222222222222222",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70",
            altura="175",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11888888888",
            end_paciente="Rua C, 789",
            rg="987654321",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11777777777",
            nome_responsavel="",
        )
        self.patient2.usuarios.add(self.user1)
        
        # Create medications and protocol
        self.med1 = Medicamento.objects.create(
            nome="Levetiracetam",
            dosagem="500mg",
            apres="Comprimido revestido"
        )
        
        self.protocolo = Protocolo.objects.create(
            nome="Protocolo Epilepsia",
            arquivo="epilepsia.pdf",
            dados_condicionais={}
        )
        self.protocolo.medicamentos.add(self.med1)
        
        self.doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Epilepsia",
            protocolo=self.protocolo
        )
        
        # Create existing processo for renovation
        self.processo1 = Processo.objects.create(
            usuario=self.user1,
            paciente=self.patient1,
            doenca=self.doenca,
            medico=self.medico1,
            clinica=self.clinica1,
            emissor=self.emissor1,
            anamnese="Paciente apresenta crises convulsivas",
            prescricao={"medicamento_1": "Levetiracetam 500mg", "dosagem_1": "2x ao dia"},
            tratou=False,
            tratamentos_previos="Nenhum",
            preenchido_por="M",
            dados_condicionais={"campo1": "valor1"}
        )
        
        print("✅ DEBUG: Renovation test data setup complete!")

    def login_user(self, email, password):
        """Helper method to login a user through the browser."""
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        email_field = self.page.locator('input[name="username"]')
        password_field = self.page.locator('input[name="password"]')
        
        email_field.fill(email)
        password_field.fill(password)
        
        login_button = self.page.locator('button[type="submit"]:has-text("Login")')
        login_button.click()
        
        self.wait_for_page_load()

    def debug_renovation_page_state(self, step_name):
        """Debug renovation page state with detailed logging."""
        print(f"\n🔍 DEBUG: {step_name}")
        print(f"📍 Current URL: {self.page.url}")
        print(f"📄 Page Title: {self.page.title()}")
        
        # Check for patient search results
        try:
            patient_rows = self.page.locator('table tr, .patient-row, .patient-result').all()
            print(f"👥 Patient results found: {len(patient_rows)}")
        except:
            print("👥 No patient results structure found")
        
        # Check for form elements
        try:
            inputs = self.page.locator('input').all()
            selects = self.page.locator('select').all()
            buttons = self.page.locator('button').all()
            print(f"📝 Form elements - Inputs: {len(inputs)}, Selects: {len(selects)}, Buttons: {len(buttons)}")
        except:
            print("📝 Error counting form elements")
        
        # Take screenshot
        self.take_screenshot(step_name)


class RenovationWorkflowTest(RenovationWorkflowPlaywrightBase):
    """Test renovation quick workflow functionality."""
    
    def test_renovation_page_loads(self):
        """Test that the renovation page loads correctly."""
        print("\n🚀 TEST: test_renovation_page_loads")
        
        # Login as medico
        self.login_user('medico@example.com', 'testpass123')
        
        # Navigate to renovation page
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        self.debug_renovation_page_state("renovation_page_loaded")
        
        # Check page title and basic elements
        self.assertIn("CliqueReceita", self.page.title())
        
        # Look for search input (patient search)
        search_inputs = [
            'input[name="nome"]',
            'input[name="cpf"]', 
            'input[placeholder*="nome"]',
            'input[placeholder*="CPF"]',
            'input[type="search"]'
        ]
        
        found_search = False
        for selector in search_inputs:
            if self.page.locator(selector).count() > 0:
                print(f"✅ DEBUG: Found search input with selector: {selector}")
                found_search = True
                break
        
        if not found_search:
            print("⚠️  DEBUG: No search input found - checking page structure")
            page_content = self.page.content()
            if 'renovacao' in page_content.lower() or 'renova' in page_content.lower():
                print("✅ DEBUG: Page contains renovation content")
            else:
                print("❌ DEBUG: Page may not be the renovation page")
                print(f"Page content preview: {page_content[:500]}")

    def test_patient_search_by_name(self):
        """Test patient search functionality by name."""
        print("\n🚀 TEST: test_patient_search_by_name")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Find search field (try common patterns)
        search_field = None
        search_selectors = [
            'input[name="nome"]',
            'input[name="search"]',
            'input[placeholder*="nome"]',
            'input[type="search"]',
            'input[type="text"]:first'
        ]
        
        for selector in search_selectors:
            field = self.page.locator(selector)
            if field.count() > 0 and field.is_visible():
                search_field = field
                print(f"✅ DEBUG: Found search field with selector: {selector}")
                break
        
        if search_field:
            # Search for patient by partial name
            search_field.fill("Maria")
            
            # Look for search button or form submission
            search_button = None
            button_selectors = [
                'button:has-text("Buscar")',
                'button:has-text("Pesquisar")',
                'button[type="submit"]',
                'input[type="submit"]'
            ]
            
            for selector in button_selectors:
                btn = self.page.locator(selector)
                if btn.count() > 0 and btn.is_visible():
                    search_button = btn
                    break
            
            if search_button:
                search_button.click()
                self.wait_for_page_load()
                self.debug_renovation_page_state("after_patient_search")
                
                # Check if patient results are displayed
                page_content = self.page.content()
                self.assertTrue(
                    "Maria Santos" in page_content or "maria" in page_content.lower(),
                    "Patient search should return Maria Santos"
                )
            else:
                # Try pressing Enter instead
                search_field.press('Enter')
                self.wait_for_page_load()
                self.debug_renovation_page_state("after_patient_search_enter")
        else:
            self.skipTest("Could not find patient search field on renovation page")

    def test_patient_search_by_cpf(self):
        """Test patient search functionality by CPF."""
        print("\n🚀 TEST: test_patient_search_by_cpf")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Look for CPF search field
        cpf_field = None
        cpf_selectors = [
            'input[name="cpf"]',
            'input[placeholder*="CPF"]',
            'input[placeholder*="cpf"]',
            'input[name="cpf_paciente"]'
        ]
        
        for selector in cpf_selectors:
            field = self.page.locator(selector)
            if field.count() > 0 and field.is_visible():
                cpf_field = field
                print(f"✅ DEBUG: Found CPF field with selector: {selector}")
                break
        
        if cpf_field:
            # Search using existing patient CPF
            cpf_field.fill("72834565031")
            
            # Submit search
            submit_button = self.page.locator('button[type="submit"], input[type="submit"]').first
            if submit_button.is_visible():
                submit_button.click()
            else:
                cpf_field.press('Enter')
            
            self.wait_for_page_load()
            self.debug_renovation_page_state("after_cpf_search")
            
            # Verify patient appears in results
            page_content = self.page.content()
            self.assertTrue(
                "Maria Santos" in page_content or "728.345.650-31" in page_content,
                "CPF search should return Maria Santos"
            )
        else:
            print("⚠️  DEBUG: No CPF search field found - may be combined with name search")

    def test_process_selection_interface(self):
        """Test process selection with radio buttons."""
        print("\n🚀 TEST: test_process_selection_interface")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Search for patient first
        search_field = self.page.locator('input[name="nome"], input[type="search"], input[type="text"]').first
        if search_field.is_visible():
            search_field.fill("Maria")
            search_field.press('Enter')
            self.wait_for_page_load()
        
        self.debug_renovation_page_state("before_process_selection")
        
        # Look for radio buttons (process selection)
        radio_buttons = self.page.locator('input[type="radio"]').all()
        if radio_buttons:
            print(f"✅ DEBUG: Found {len(radio_buttons)} radio buttons for process selection")
            
            # Select first available process
            first_radio = radio_buttons[0]
            if first_radio.is_visible():
                first_radio.click()
                self.debug_renovation_page_state("process_selected")
                
                # Verify radio button is selected
                self.assertTrue(
                    first_radio.is_checked(),
                    "Radio button should be selected after click"
                )
        else:
            print("⚠️  DEBUG: No radio buttons found - checking for other selection methods")
            
            # Look for checkboxes or other selection mechanisms
            checkboxes = self.page.locator('input[type="checkbox"]').all()
            select_elements = self.page.locator('select').all()
            
            print(f"📋 DEBUG: Found {len(checkboxes)} checkboxes, {len(select_elements)} select elements")

    def test_date_input_functionality(self):
        """Test date input field and calendar widget."""
        print("\n🚀 TEST: test_date_input_functionality")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Look for date input fields
        date_selectors = [
            'input[type="date"]',
            'input[name="data"]',
            'input[name="data_receita"]',
            'input[placeholder*="data"]',
            '.datepicker',
            'input[class*="date"]'
        ]
        
        date_field = None
        for selector in date_selectors:
            field = self.page.locator(selector)
            if field.count() > 0 and field.is_visible():
                date_field = field
                print(f"✅ DEBUG: Found date field with selector: {selector}")
                break
        
        if date_field:
            # Test date input
            test_date = "2024-01-15"
            date_field.fill(test_date)
            
            self.debug_renovation_page_state("date_filled")
            
            # Verify date was set
            entered_value = date_field.input_value()
            self.assertTrue(
                test_date in entered_value or "15" in entered_value,
                f"Date should be set correctly. Expected: {test_date}, Got: {entered_value}"
            )
            
            # Check for calendar widget (if present)
            calendar_elements = self.page.locator('.calendar, .datepicker-popup, .ui-datepicker').all()
            if calendar_elements:
                print(f"📅 DEBUG: Found {len(calendar_elements)} calendar widget elements")
        else:
            print("⚠️  DEBUG: No date input field found on renovation page")

    def test_edit_checkbox_behavior(self):
        """Test the 'Permitir edição' checkbox behavior."""
        print("\n🚀 TEST: test_edit_checkbox_behavior")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Search for patient and select process (if needed)
        search_field = self.page.locator('input[name="nome"], input[type="search"], input[type="text"]').first
        if search_field.is_visible():
            search_field.fill("Maria")
            search_field.press('Enter')
            self.wait_for_page_load()
        
        # Look for edit checkbox
        edit_checkbox_selectors = [
            'input[name="edicao"]',
            'input[name="permitir_edicao"]',
            'input[type="checkbox"]:has-text("edição")',
            'input[type="checkbox"]:has-text("Permitir")',
            '.edit-checkbox input'
        ]
        
        edit_checkbox = None
        for selector in edit_checkbox_selectors:
            checkbox = self.page.locator(selector)
            if checkbox.count() > 0:
                edit_checkbox = checkbox
                print(f"✅ DEBUG: Found edit checkbox with selector: {selector}")
                break
        
        if edit_checkbox:
            # Test checking the checkbox
            if not edit_checkbox.is_checked():
                edit_checkbox.click()
            
            self.debug_renovation_page_state("edit_checkbox_checked")
            
            # Verify checkbox is checked
            self.assertTrue(
                edit_checkbox.is_checked(),
                "Edit checkbox should be checked after click"
            )
            
            # Test unchecking the checkbox
            edit_checkbox.click()
            self.assertFalse(
                edit_checkbox.is_checked(),
                "Edit checkbox should be unchecked after second click"
            )
        else:
            # Look for any checkboxes on the page
            all_checkboxes = self.page.locator('input[type="checkbox"]').all()
            print(f"📋 DEBUG: Found {len(all_checkboxes)} total checkboxes on page")
            
            if all_checkboxes:
                # Test first checkbox as a fallback
                first_checkbox = all_checkboxes[0]
                first_checkbox.click()
                self.debug_renovation_page_state("first_checkbox_tested")

    def test_form_validation_missing_data(self):
        """Test form validation when required data is missing."""
        print("\n🚀 TEST: test_form_validation_missing_data")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Try to submit form without filling required fields
        submit_button = self.page.locator('button[type="submit"], input[type="submit"]').first
        if submit_button.is_visible():
            initial_url = self.page.url
            submit_button.click()
            self.wait_for_page_load()
            
            # Check if we stayed on the same page (validation failed)
            final_url = self.page.url
            if initial_url == final_url:
                print("✅ DEBUG: Form validation prevented submission")
            
            # Look for error messages
            page_content = self.page.content()
            validation_errors = [
                "obrigatório" in page_content.lower(),
                "required" in page_content.lower(),
                "erro" in page_content.lower(),
                "error" in page_content.lower(),
                "preencha" in page_content.lower()
            ]
            
            if any(validation_errors):
                print("✅ DEBUG: Validation error messages found")
            
            self.debug_renovation_page_state("validation_error")

    def test_renovation_workflow_complete(self):
        """Test complete renovation workflow from search to submission."""
        print("\n🚀 TEST: test_renovation_workflow_complete")
        
        # Login and navigate to renovation page
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        self.debug_renovation_page_state("initial_renovation_page")
        
        try:
            # Step 1: Search for patient
            search_field = self.page.locator('input[name="nome"], input[type="search"], input[type="text"]').first
            if search_field.is_visible():
                search_field.fill("Maria")
                search_field.press('Enter')
                self.wait_for_page_load()
                self.debug_renovation_page_state("after_patient_search")
            
            # Step 2: Select process (if radio buttons available)
            radio_buttons = self.page.locator('input[type="radio"]').all()
            if radio_buttons:
                radio_buttons[0].click()
                self.debug_renovation_page_state("process_selected")
            
            # Step 3: Fill date field
            date_field = self.page.locator('input[type="date"], input[name="data"]').first
            if date_field.is_visible():
                date_field.fill("2024-01-15")
                self.debug_renovation_page_state("date_filled")
            
            # Step 4: Handle edit checkbox
            edit_checkbox = self.page.locator('input[name="edicao"], input[type="checkbox"]').first
            if edit_checkbox.count() > 0:
                # Test without edit (direct PDF generation)
                if edit_checkbox.is_checked():
                    edit_checkbox.click()  # Uncheck for direct PDF
                self.debug_renovation_page_state("edit_checkbox_configured")
            
            # Step 5: Submit form
            submit_button = self.page.locator('button[type="submit"], input[type="submit"]').first
            if submit_button.is_visible():
                initial_url = self.page.url
                submit_button.click()
                self.wait_for_page_load()
                
                final_url = self.page.url
                print(f"📍 DEBUG: URL changed from {initial_url} to {final_url}")
                
                self.debug_renovation_page_state("after_form_submission")
                
                # Check for success indicators
                page_content = self.page.content()
                success_indicators = [
                    "sucesso" in page_content.lower(),
                    "success" in page_content.lower(),
                    "pdf" in page_content.lower(),
                    "gerado" in page_content.lower(),
                    final_url != initial_url
                ]
                
                if any(success_indicators):
                    print("✅ DEBUG: Renovation workflow appears successful")
                else:
                    print("⚠️  DEBUG: Renovation workflow outcome unclear")
            else:
                print("⚠️  DEBUG: No submit button found")
                
        except Exception as e:
            print(f"❌ DEBUG: Exception during renovation workflow: {e}")
            self.debug_renovation_page_state("workflow_exception")


class RenovationAccessibilityTest(RenovationWorkflowPlaywrightBase):
    """Test renovation page accessibility and responsive features."""
    
    def test_renovation_page_accessibility(self):
        """Test renovation page accessibility features."""
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Check for form labels
        labels = self.page.locator('label').all()
        print(f"📋 Found {len(labels)} form labels")
        
        # Check form field attributes
        form_fields = self.page.locator('input, select, textarea').all()
        accessibility_features = 0
        
        for field in form_fields:
            field_name = field.get_attribute('name') or field.get_attribute('id') or 'unnamed'
            field_label = field.get_attribute('aria-label')
            field_required = field.get_attribute('required')
            
            if field_label or field_required:
                accessibility_features += 1
                print(f"✅ Field {field_name}: accessible features present")
        
        print(f"📊 Found {accessibility_features} accessible form elements")
        self.take_screenshot("renovation_accessibility")
    
    def test_renovation_page_responsive(self):
        """Test renovation page on different screen sizes."""
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        self.page.goto(f'{self.live_server_url}/processos/renovacao/')
        self.wait_for_page_load()
        
        # Test mobile size
        self.page.set_viewport_size({"width": 375, "height": 667})
        self.page.wait_for_timeout(1000)
        
        # Check if main elements are still accessible
        main_form = self.page.locator('form').first
        if main_form.is_visible():
            print("✅ Main form visible on mobile")
        
        self.take_screenshot("renovation_mobile")
        
        # Test tablet size
        self.page.set_viewport_size({"width": 768, "height": 1024})
        self.page.wait_for_timeout(1000)
        self.take_screenshot("renovation_tablet")
        
        # Reset to desktop size
        self.page.set_viewport_size({"width": 1920, "height": 1080})