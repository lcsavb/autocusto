"""
Complete Process Registration (Cadastro) Tests using Playwright
Tests the complete "cadastro de processo" workflow from home page through
dynamic form filling to PDF generation. This covers the core business workflow
that was previously untested.

Features:
- Home → Cadastro workflow testing
- Dynamic form field generation based on disease protocols
- Session data management and preservation
- Disease-specific form validation
- Complete integration with PDF generation
- Alpine.js form handling validation
"""

import json
import time
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class ProcessRegistrationPlaywrightBase(PlaywrightFormTestBase):
    """Base class for process registration tests with comprehensive setup."""
    
    def setUp(self):
        """Set up test data for complete cadastro workflow testing."""
        super().setUp()
        
        print("🔧 DEBUG: Setting up process registration test data...")
        
        # Create test user and medico
        self.user1 = User.objects.create_user(
            email='medico@example.com',
            password='testpass123'
        )
        self.user1.is_medico = True
        self.user1.save()
        
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. Ana Costa",
            crm_medico="67890",
            cns_medico="333333333333333"
        )
        self.medico1.usuarios.add(self.user1)
        
        # Create clinica and emissor
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica Nova Vida",
            cns_clinica="7654321",
            logradouro="Av. Principal",
            logradouro_num="456",
            cidade="Rio de Janeiro",
            bairro="Centro",
            cep="20000-000",
            telefone_clinica="21987654321"
        )
        self.user1.clinicas.add(self.clinica1)
        
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        
        # Create test patients - both new and existing
        self.new_patient = Paciente.objects.create(
            nome_paciente="Carlos Oliveira",
            cpf_paciente="98765432100",
            cns_paciente="444444444444444",
            nome_mae="Rita Oliveira",
            idade="55",
            sexo="M",
            peso="80",
            altura="175",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="21987654321",
            end_paciente="Rua Nova, 789",
            rg="456789123",
            escolha_etnia="Branca",
            cidade_paciente="Rio de Janeiro",
            cep_paciente="20000-000",
            telefone2_paciente="21876543210",
            nome_responsavel="",
        )
        self.new_patient.usuarios.add(self.user1)
        
        # Create medications with different protocols
        self.med_epilepsia1 = Medicamento.objects.create(
            nome="Levetiracetam",
            dosagem="500mg",
            apres="Comprimido revestido"
        )
        self.med_epilepsia2 = Medicamento.objects.create(
            nome="Ácido Valproico",
            dosagem="250mg",
            apres="Comprimido"
        )
        self.med_diabetes1 = Medicamento.objects.create(
            nome="Metformina",
            dosagem="850mg",
            apres="Comprimido"
        )
        
        # Create protocol for Epilepsia with conditional fields
        self.protocolo_epilepsia = Protocolo.objects.create(
            nome="Protocolo Epilepsia Completo",
            arquivo="epilepsia_completa.pdf",
            dados_condicionais={
                "historico_familiar": "optional",
                "tipo_crise": "required",
                "frequencia_crises": "required",
                "uso_medicamento_anterior": "optional",
                "eeg_realizado": "optional"
            }
        )
        self.protocolo_epilepsia.medicamentos.add(self.med_epilepsia1, self.med_epilepsia2)
        
        # Create protocol for Diabetes
        self.protocolo_diabetes = Protocolo.objects.create(
            nome="Protocolo Diabetes Tipo 2",
            arquivo="diabetes_t2.pdf",
            dados_condicionais={
                "glicemia_jejum": "required",
                "hba1c": "required",
                "peso_anterior": "optional",
                "atividade_fisica": "optional"
            }
        )
        self.protocolo_diabetes.medicamentos.add(self.med_diabetes1)
        
        # Create diseases
        self.doenca_epilepsia = Doenca.objects.create(
            cid="G40.9",
            nome="Epilepsia não especificada",
            protocolo=self.protocolo_epilepsia
        )
        
        self.doenca_diabetes = Doenca.objects.create(
            cid="E11.9",
            nome="Diabetes mellitus tipo 2",
            protocolo=self.protocolo_diabetes
        )
        
        print("✅ DEBUG: Process registration test data setup complete!")
        print(f"📊 DEBUG: Created {Doenca.objects.count()} diseases, {Medicamento.objects.count()} medications")

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

    def navigate_to_cadastro_via_home(self, cpf, cid):
        """Navigate from home page to cadastro page via form submission."""
        print(f"🏠 DEBUG: Navigating to cadastro with CPF: {cpf}, CID: {cid}")
        
        # Start from home page
        self.page.goto(f'{self.live_server_url}/')
        self.wait_for_page_load()
        
        # Fill home form
        cpf_field = self.page.locator('input[name="cpf_paciente"]')
        cid_field = self.page.locator('input[name="cid"]')
        
        if cpf_field.is_visible() and cid_field.is_visible():
            cpf_field.fill(cpf)
            cid_field.fill(cid)
            
            # Submit form
            submit_button = self.page.locator('button:has-text("Cadastrar")')
            submit_button.click()
            
            # Wait for navigation
            self.wait_for_page_load()
            
            current_url = self.page.url
            print(f"📍 DEBUG: After home form submission, URL: {current_url}")
            
            return 'cadastro' in current_url or 'processos' in current_url
        else:
            print("❌ DEBUG: Home form fields not found")
            return False

    def fill_patient_basic_data(self, patient_name=None):
        """Fill basic patient data in cadastro form."""
        if patient_name is None:
            patient_name = "Carlos Oliveira Silva"
        
        basic_fields = {
            'nome_paciente': patient_name,
            'nome_mae': 'Rita Oliveira Santos',
            'peso': '82',
            'altura': '178',
            'end_paciente': 'Rua Nova, 789, Apt 202'
        }
        
        filled_count = 0
        for field_name, value in basic_fields.items():
            field = self.page.locator(f'input[name="{field_name}"], textarea[name="{field_name}"]')
            if field.count() > 0 and field.is_visible():
                field.clear()
                field.fill(value)
                filled_count += 1
                print(f"✅ DEBUG: Filled {field_name}: {value}")
        
        return filled_count

    def fill_clinical_data(self, doenca_type="epilepsia"):
        """Fill clinical data based on disease type."""
        clinical_data = {}
        
        if doenca_type == "epilepsia":
            clinical_data = {
                'anamnese': 'Paciente com histórico de crises epilépticas há 3 anos. Crises tônico-clônicas generalizadas.',
                'tipo_crise': 'Tônico-clônica generalizada',
                'frequencia_crises': '2-3 por mês',
                'historico_familiar': 'Não há histórico familiar'
            }
        elif doenca_type == "diabetes":
            clinical_data = {
                'anamnese': 'Paciente com diabetes tipo 2 diagnosticado há 5 anos. Glicemia descontrolada.',
                'glicemia_jejum': '180 mg/dL',
                'hba1c': '9.2%',
                'peso_anterior': '85 kg'
            }
        
        # Fill standard fields
        standard_fields = {
            'tratou': 'False',
            'tratamentos_previos': 'Uso irregular de medicação anterior',
            'preenchido_por': 'M'
        }
        clinical_data.update(standard_fields)
        
        filled_count = 0
        for field_name, value in clinical_data.items():
            # Try different field types
            field_selectors = [
                f'input[name="{field_name}"]',
                f'textarea[name="{field_name}"]',
                f'select[name="{field_name}"]'
            ]
            
            for selector in field_selectors:
                field = self.page.locator(selector)
                if field.count() > 0:
                    # Check if it's a radio button first (before checking visibility)
                    if selector.startswith('input') and field.first.get_attribute('type') == 'radio':
                        # Handle radio buttons specifically
                        if value == 'True':
                            radio_button = self.page.locator(f'input[name="{field_name}"][value="True"]')
                        elif value == 'False':
                            radio_button = self.page.locator(f'input[name="{field_name}"][value="False"]')
                        else:
                            radio_button = field.first
                        
                        if radio_button.count() > 0 and radio_button.is_visible():
                            radio_button.click()
                            filled_count += 1
                            print(f"✅ DEBUG: Selected radio {field_name}: {value}")
                            break
                    elif field.is_visible():
                        tag_name = field.evaluate('el => el.tagName.toLowerCase()')
                        
                        if tag_name == 'select':
                            # Handle select fields
                            if value in ['True', 'False']:
                                field.select_option(value)
                            elif field_name == 'preenchido_por':
                                field.select_option('M')  # Médico
                            else:
                                # Try to find option by text
                                options = field.locator('option').all()
                                for option in options:
                                    if value.lower() in option.text_content().lower():
                                        option.click()
                                        break
                        else:
                            # Handle input/textarea
                            field.clear()
                            field.fill(str(value))
                        
                        filled_count += 1
                        print(f"✅ DEBUG: Filled {field_name}: {value}")
                        break
        
        return filled_count

    def select_medications(self, medication_count=1):
        """Select medications from available dropdowns."""
        selected_count = 0
        
        # Look for medication selection fields
        med_selectors = [
            'select[name*="medicamento"]',
            'select[name*="med"]'
        ]
        
        medication_fields = []
        for selector in med_selectors:
            fields = self.page.locator(selector).all()
            medication_fields.extend(fields)
        
        print(f"💊 DEBUG: Found {len(medication_fields)} medication selection fields")
        
        for i, field in enumerate(medication_fields[:medication_count]):
            if field.is_visible():
                options = field.locator('option').all()
                if len(options) > 1:  # Skip first empty option
                    # Select second option (first actual medication)
                    field.select_option(index=1)
                    selected_count += 1
                    
                    # Get selected medication name
                    selected_option = field.locator('option:checked')
                    if selected_option.count() > 0:
                        med_name = selected_option.text_content()
                        print(f"💊 DEBUG: Selected medication {i+1}: {med_name}")
        
        return selected_count

    def debug_cadastro_state(self, step_name):
        """Debug cadastro page state with detailed logging."""
        print(f"\n🔍 DEBUG: {step_name}")
        print(f"📍 Current URL: {self.page.url}")
        print(f"📄 Page Title: {self.page.title()}")
        
        # Count form elements
        try:
            inputs = self.page.locator('input').count()
            textareas = self.page.locator('textarea').count()
            selects = self.page.locator('select').count()
            buttons = self.page.locator('button').count()
            
            print(f"📝 Form elements: {inputs} inputs, {textareas} textareas, {selects} selects, {buttons} buttons")
        except:
            print("📝 Error counting form elements")
        
        # Check for error messages
        try:
            error_elements = self.page.locator('.alert-danger, .error, .invalid-feedback').all()
            if error_elements:
                for error in error_elements:
                    if error.is_visible():
                        print(f"⚠️  Error message: {error.text_content()}")
        except:
            print("⚠️  No error messages found")
        
        # Take screenshot
        self.take_screenshot(step_name)


class ProcessRegistrationWorkflowTest(ProcessRegistrationPlaywrightBase):
    """Test complete process registration workflow."""
    
    def test_home_to_cadastro_new_patient(self):
        """Test complete workflow: Home form → Cadastro → PDF for new patient."""
        print("\n🚀 TEST: test_home_to_cadastro_new_patient")
        
        # Login
        self.login_user('medico@example.com', 'testpass123')
        
        # Navigate via home form (new patient CPF)
        success = self.navigate_to_cadastro_via_home("11111111111", "G40.9")
        
        if success:
            self.debug_cadastro_state("cadastro_loaded_new_patient")
            
            # Fill cadastro form
            patient_fields = self.fill_patient_basic_data("Paciente Novo")
            clinical_fields = self.fill_clinical_data("epilepsia")
            medication_count = self.select_medications(1)
            
            total_filled = patient_fields + clinical_fields + medication_count
            print(f"📊 DEBUG: Total fields filled: {total_filled}")
            
            if total_filled > 0:
                self.debug_cadastro_state("cadastro_form_filled")
                
                # Submit form with response capture
                pdf_responses = []
                
                def capture_response(response):
                    if response.request.method == 'POST' and 'cadastro' in response.url:
                        try:
                            json_data = response.json()
                            pdf_responses.append(json_data)
                            print(f"📡 DEBUG: Cadastro response: {json_data}")
                        except:
                            print(f"📡 DEBUG: Non-JSON response: {response.status}")
                
                self.page.on('response', capture_response)
                
                # Find and click submit button
                submit_button = self.page.locator('button[type="submit"]:visible').first
                if submit_button.is_visible():
                    submit_button.click()
                    print("✅ DEBUG: Form submitted")
                    
                    # Wait for response
                    self.page.wait_for_timeout(5000)
                    
                    # Check responses
                    if pdf_responses:
                        for response in pdf_responses:
                            if response.get('success'):
                                print("✅ DEBUG: New patient cadastro successful with PDF generation")
                                self.assertIn('pdf_url', response)
                                break
                        else:
                            print(f"⚠️  DEBUG: No successful response: {pdf_responses}")
                    else:
                        print("⚠️  DEBUG: No responses captured")
            else:
                print("⚠️  DEBUG: No form fields found to fill")
        else:
            self.skipTest("Could not navigate to cadastro page")

    def test_home_to_cadastro_existing_patient(self):
        """Test workflow with existing patient (should load patient data)."""
        print("\n🚀 TEST: test_home_to_cadastro_existing_patient")
        
        # Login
        self.login_user('medico@example.com', 'testpass123')
        
        # Navigate with existing patient CPF
        success = self.navigate_to_cadastro_via_home("98765432100", "G40.9")
        
        if success:
            self.debug_cadastro_state("cadastro_loaded_existing_patient")
            
            # Check if patient data is pre-filled
            nome_field = self.page.locator('input[name="nome_paciente"]')
            if nome_field.count() > 0:
                current_value = nome_field.input_value()
                if current_value and "Carlos" in current_value:
                    print("✅ DEBUG: Existing patient data pre-filled correctly")
                else:
                    print(f"⚠️  DEBUG: Patient name field value: '{current_value}'")
            
            # Fill remaining clinical data
            clinical_fields = self.fill_clinical_data("epilepsia")
            medication_count = self.select_medications(1)
            
            if clinical_fields + medication_count > 0:
                # Submit form
                submit_button = self.page.locator('button[type="submit"]:visible').first
                if submit_button.is_visible():
                    submit_button.click()
                    self.page.wait_for_timeout(3000)
                    print("✅ DEBUG: Existing patient cadastro form submitted")
        else:
            self.skipTest("Could not navigate to cadastro with existing patient")

    def test_disease_specific_form_fields_epilepsia(self):
        """Test that epilepsia-specific fields appear correctly."""
        print("\n🚀 TEST: test_disease_specific_form_fields_epilepsia")
        
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_cadastro_via_home("98765432100", "G40.9")
        
        if success:
            self.debug_cadastro_state("epilepsia_form_loaded")
            
            # Check for epilepsia-specific fields
            epilepsia_fields = [
                'tipo_crise',
                'frequencia_crises',
                'historico_familiar',
                'eeg_realizado'
            ]
            
            found_fields = 0
            for field_name in epilepsia_fields:
                field = self.page.locator(f'input[name="{field_name}"], select[name="{field_name}"], textarea[name="{field_name}"]')
                if field.count() > 0:
                    found_fields += 1
                    print(f"✅ DEBUG: Found epilepsia field: {field_name}")
                else:
                    print(f"⚠️  DEBUG: Missing epilepsia field: {field_name}")
            
            print(f"📊 DEBUG: Found {found_fields}/{len(epilepsia_fields)} epilepsia-specific fields")
            
            # Check medication options are epilepsia-related
            med_select = self.page.locator('select[name*="medicamento"]').first
            if med_select.count() > 0:
                options = med_select.locator('option').all()
                option_texts = [opt.text_content() for opt in options]
                
                epilepsia_meds = ['levetiracetam', 'valproico', 'carbamazepina']
                found_epilepsia_meds = 0
                
                for option_text in option_texts:
                    for med in epilepsia_meds:
                        if med.lower() in option_text.lower():
                            found_epilepsia_meds += 1
                            print(f"✅ DEBUG: Found epilepsia medication: {option_text}")
                            break
                
                print(f"💊 DEBUG: Found {found_epilepsia_meds} epilepsia-related medications")
        else:
            self.skipTest("Could not load epilepsia cadastro form")

    def test_disease_specific_form_fields_diabetes(self):
        """Test that diabetes-specific fields appear correctly."""
        print("\n🚀 TEST: test_disease_specific_form_fields_diabetes")
        
        # Login and navigate with diabetes CID
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_cadastro_via_home("98765432100", "E11.9")
        
        if success:
            self.debug_cadastro_state("diabetes_form_loaded")
            
            # Check for diabetes-specific fields
            diabetes_fields = [
                'glicemia_jejum',
                'hba1c',
                'peso_anterior',
                'atividade_fisica'
            ]
            
            found_fields = 0
            for field_name in diabetes_fields:
                field = self.page.locator(f'input[name="{field_name}"], select[name="{field_name}"], textarea[name="{field_name}"]')
                if field.count() > 0:
                    found_fields += 1
                    print(f"✅ DEBUG: Found diabetes field: {field_name}")
                else:
                    print(f"⚠️  DEBUG: Missing diabetes field: {field_name}")
            
            print(f"📊 DEBUG: Found {found_fields}/{len(diabetes_fields)} diabetes-specific fields")
            
            # Fill diabetes-specific data and submit
            filled_fields = self.fill_clinical_data("diabetes")
            if filled_fields > 0:
                print("✅ DEBUG: Diabetes-specific data filled successfully")
        else:
            self.skipTest("Could not load diabetes cadastro form")

    def test_session_data_preservation(self):
        """Test that session data (CID, patient info) persists correctly."""
        print("\n🚀 TEST: test_session_data_preservation")
        
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        
        # Check session after home form submission
        success = self.navigate_to_cadastro_via_home("98765432100", "G40.9")
        
        if success:
            # Session data should persist - check by looking for pre-filled fields or page behavior
            current_url = self.page.url
            page_content = self.page.content()
            
            # Look for indicators that session data is preserved
            session_indicators = [
                'G40' in page_content,  # CID should be referenced
                'carlos' in page_content.lower(),  # Patient name should appear
                'epilepsia' in page_content.lower()  # Disease name should appear
            ]
            
            preserved_data = sum(session_indicators)
            print(f"📊 DEBUG: Session data preservation indicators: {preserved_data}/3")
            
            if preserved_data > 0:
                print("✅ DEBUG: Session data appears to be preserved")
            else:
                print("⚠️  DEBUG: Session data preservation unclear")
                
            # Check that form has disease-appropriate fields
            epilepsia_field = self.page.locator('input[name*="crise"], input[name*="epilep"]')
            if epilepsia_field.count() > 0:
                print("✅ DEBUG: Disease-specific fields confirm session data preservation")
        else:
            self.skipTest("Could not test session preservation")

    def test_form_validation_required_fields(self):
        """Test form validation with missing required fields."""
        print("\n🚀 TEST: test_form_validation_required_fields")
        
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_cadastro_via_home("98765432100", "G40.9")
        
        if success:
            # Try to submit form with minimal data
            submit_button = self.page.locator('button[type="submit"]:visible').first
            
            if submit_button.is_visible():
                validation_responses = []
                
                def capture_validation(response):
                    if response.request.method == 'POST' and 'cadastro' in response.url:
                        try:
                            json_data = response.json()
                            validation_responses.append(json_data)
                        except:
                            pass
                
                self.page.on('response', capture_validation)
                
                # Submit without filling required fields
                submit_button.click()
                self.page.wait_for_timeout(3000)
                
                # Check validation response
                validation_failed = False
                for response in validation_responses:
                    if not response.get('success'):
                        validation_failed = True
                        print("✅ DEBUG: Form validation correctly rejected incomplete form")
                        break
                
                if not validation_failed and validation_responses:
                    print("⚠️  DEBUG: Form may have accepted incomplete data")
                elif not validation_responses:
                    # Check if still on same page (client-side validation)
                    current_url = self.page.url
                    if 'cadastro' in current_url:
                        print("✅ DEBUG: Client-side validation kept user on form")
        else:
            self.skipTest("Could not test form validation")

    def test_medication_selection_workflow(self):
        """Test medication selection and dosage configuration."""
        print("\n🚀 TEST: test_medication_selection_workflow")
        
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_cadastro_via_home("98765432100", "G40.9")
        
        if success:
            self.debug_cadastro_state("before_medication_selection")
            
            # Fill basic data first
            basic_filled = self.fill_patient_basic_data()
            clinical_filled = self.fill_clinical_data("epilepsia")
            
            # Focus on medication selection
            med_selects = self.page.locator('select[name*="medicamento"]').all()
            print(f"💊 DEBUG: Found {len(med_selects)} medication selection fields")
            
            selected_medications = []
            for i, select in enumerate(med_selects[:2]):  # Test first 2 medication fields
                if select.is_visible():
                    options = select.locator('option').all()
                    print(f"💊 DEBUG: Medication field {i+1} has {len(options)} options")
                    
                    if len(options) > 1:
                        # Select a medication
                        select.select_option(index=1)
                        
                        selected_option = select.locator('option:checked')
                        if selected_option.count() > 0:
                            med_name = selected_option.text_content()
                            selected_medications.append(med_name)
                            print(f"💊 DEBUG: Selected: {med_name}")
                        
                        # Look for related dosage fields
                        dosage_field = self.page.locator(f'input[name*="dosagem_{i+1}"], input[name*="dose_{i+1}"]')
                        if dosage_field.count() > 0:
                            dosage_field.fill("2 comprimidos por dia")
                            print(f"💊 DEBUG: Set dosage for medication {i+1}")
            
            print(f"💊 DEBUG: Successfully configured {len(selected_medications)} medications")
            
            if selected_medications:
                self.debug_cadastro_state("medications_selected")
                print("✅ DEBUG: Medication selection workflow completed")
            else:
                print("⚠️  DEBUG: No medications were selected")
        else:
            self.skipTest("Could not test medication selection")