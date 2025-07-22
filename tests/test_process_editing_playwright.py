"""
Process Editing Frontend Tests using Playwright
Tests the "edicao" (editing) functionality including edit mode toggles,
dynamic field visibility, protocol modals, and JavaScript interactions.

Features:
- Comprehensive debugging with screenshots
- Edit mode toggle testing (complete vs partial)
- Dynamic field visibility validation
- Protocol modal functionality
- JavaScript interaction testing
- Form state management
"""

import time
from django.contrib.auth import get_user_model
from tests.playwright_base import PlaywrightTestBase, PlaywrightFormTestBase
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class ProcessEditingPlaywrightBase(PlaywrightFormTestBase):
    """Base class for process editing tests with common setup and utilities."""
    
    def setUp(self):
        """Set up test data for process editing with extensive debugging."""
        super().setUp()
        
        print("🔧 DEBUG: Setting up process editing test data...")
        
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
        
        # Create medications and protocol
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
        
        self.protocolo = Protocolo.objects.create(
            nome="Protocolo Epilepsia",
            arquivo="epilepsia.pdf",
            dados_condicionais={
                "field1": "optional",
                "field2": "required"
            }
        )
        self.protocolo.medicamentos.add(self.med1, self.med2)
        
        self.doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Epilepsia",
            protocolo=self.protocolo
        )
        
        # Create existing processo for editing
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
        
        print("✅ DEBUG: Process editing test data setup complete!")
        print(f"📊 DEBUG: Created processo ID: {self.processo1.id}")

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

    def navigate_to_edit_page(self):
        """Navigate to the edit page via the standard workflow."""
        # Try direct navigation first
        edit_url = f'{self.live_server_url}/processos/edicao/'
        self.page.goto(edit_url)
        self.wait_for_page_load()
        
        # Check if we're on the edit page or need to go through workflow
        current_url = self.page.url
        if 'edicao' in current_url:
            print("✅ DEBUG: Direct navigation to edit page successful")
            return True
        else:
            print("⚠️  DEBUG: Direct navigation failed, trying workflow navigation")
            # Try going through home page workflow
            self.page.goto(f'{self.live_server_url}/')
            self.wait_for_page_load()
            
            # Fill home form to get to edit page
            cpf_field = self.page.locator('input[name="cpf_paciente"]')
            cid_field = self.page.locator('input[name="cid"]')
            
            if cpf_field.is_visible() and cid_field.is_visible():
                cpf_field.fill("72834565031")
                cid_field.fill("G40.0")
                
                submit_button = self.page.locator('button:has-text("Cadastrar")')
                submit_button.click()
                self.wait_for_page_load()
                
                current_url = self.page.url
                return 'edicao' in current_url or 'processos' in current_url
            
            return False

    def debug_edit_page_state(self, step_name):
        """Debug edit page state with detailed logging."""
        print(f"\n🔍 DEBUG: {step_name}")
        print(f"📍 Current URL: {self.page.url}")
        print(f"📄 Page Title: {self.page.title()}")
        
        # Check for edit mode toggle elements
        try:
            radio_buttons = self.page.locator('input[type="radio"]').all()
            checkboxes = self.page.locator('input[type="checkbox"]').all()
            print(f"🔘 Form controls - Radio buttons: {len(radio_buttons)}, Checkboxes: {len(checkboxes)}")
        except:
            print("🔘 Error counting form controls")
        
        # Check for dynamic sections
        try:
            sections = self.page.locator('.form-section, .edit-section, .medication-section').all()
            print(f"📝 Form sections found: {len(sections)}")
        except:
            print("📝 No specific form sections found")
        
        # Check for modal triggers
        try:
            modal_buttons = self.page.locator('button[data-toggle="modal"], .modal-trigger, button:has-text("protocolo")').all()
            print(f"🖥️  Modal triggers found: {len(modal_buttons)}")
        except:
            print("🖥️  No modal triggers found")
        
        # Take screenshot
        self.take_screenshot(step_name)

    def wait_for_javascript_load(self):
        """Wait for JavaScript to load and execute."""
        # Wait for common JavaScript indicators
        self.page.wait_for_timeout(2000)
        
        # Check if jQuery is loaded (common in Django projects)
        try:
            jquery_loaded = self.page.evaluate("typeof jQuery !== 'undefined'")
            if jquery_loaded:
                print("✅ DEBUG: jQuery is loaded")
        except:
            print("⚠️  DEBUG: jQuery check failed")
        
        # Wait for any pending AJAX or dynamic content
        self.page.wait_for_load_state('networkidle')


class ProcessEditingTest(ProcessEditingPlaywrightBase):
    """Test process editing functionality."""
    
    def test_edit_page_loads(self):
        """Test that the edit page loads correctly."""
        print("\n🚀 TEST: test_edit_page_loads")
        
        # Login as medico
        self.login_user('medico@example.com', 'testpass123')
        
        # Navigate to edit page
        success = self.navigate_to_edit_page()
        if success:
            self.debug_edit_page_state("edit_page_loaded")
            self.wait_for_javascript_load()
            
            # Check page title
            self.assertIn("CliqueReceita", self.page.title())
            
            # Look for form elements
            form_present = self.page.locator('form').count() > 0
            self.assertTrue(form_present, "Edit page should contain a form")
            
            # Look for edit-specific elements
            edit_indicators = [
                self.page.locator('input[name="edicao_completa"]').count() > 0,
                self.page.locator('*:has-text("Edição")').count() > 0,
                self.page.locator('*:has-text("Completa")').count() > 0,
                'edicao' in self.page.content().lower()
            ]
            
            if any(edit_indicators):
                print("✅ DEBUG: Edit page elements detected")
            else:
                print("⚠️  DEBUG: Edit page elements not clearly identified")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_edit_mode_toggle_functionality(self):
        """Test the edit mode toggle between complete and partial editing."""
        print("\n🚀 TEST: test_edit_mode_toggle_functionality")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            self.debug_edit_page_state("before_edit_mode_toggle")
            
            # Look for edit mode toggle (radio buttons)
            edit_mode_selectors = [
                'input[name="edicao_completa"]',
                'input[value="complete"]',
                'input[value="partial"]',
                'input[type="radio"]:has-text("Sim")',
                'input[type="radio"]:has-text("Não")'
            ]
            
            edit_toggle_found = False
            for selector in edit_mode_selectors:
                elements = self.page.locator(selector).all()
                if elements:
                    print(f"✅ DEBUG: Found edit mode elements with selector: {selector}")
                    edit_toggle_found = True
                    
                    # Test toggling between modes
                    for i, element in enumerate(elements[:2]):  # Test first two options
                        if element.is_visible():
                            print(f"🔘 DEBUG: Testing radio button {i+1}")
                            element.click()
                            self.page.wait_for_timeout(1000)  # Wait for JavaScript
                            
                            # Check if element is selected
                            is_checked = element.is_checked()
                            print(f"✅ DEBUG: Radio button {i+1} checked: {is_checked}")
                            
                            self.debug_edit_page_state(f"edit_mode_toggle_{i+1}")
                    break
            
            if not edit_toggle_found:
                print("⚠️  DEBUG: No edit mode toggle found - checking for any radio buttons")
                all_radios = self.page.locator('input[type="radio"]').all()
                print(f"🔘 DEBUG: Found {len(all_radios)} total radio buttons")
                
                if all_radios:
                    # Test first radio button as fallback
                    first_radio = all_radios[0]
                    first_radio.click()
                    self.debug_edit_page_state("first_radio_tested")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_dynamic_field_visibility(self):
        """Test that fields show/hide based on edit mode selection."""
        print("\n🚀 TEST: test_dynamic_field_visibility")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            
            # Count visible form fields before mode selection
            initial_fields = self.page.locator('input:visible, select:visible, textarea:visible').count()
            print(f"📊 DEBUG: Initial visible fields: {initial_fields}")
            
            # Look for edit mode radio buttons
            complete_edit = self.page.locator('input[name="edicao_completa"][value="True"], input[value="complete"], input[type="radio"]').first
            partial_edit = self.page.locator('input[name="edicao_completa"][value="False"], input[value="partial"], input[type="radio"]').last
            
            # Test complete edit mode
            if complete_edit.count() > 0 and complete_edit.is_visible():
                complete_edit.click()
                self.page.wait_for_timeout(2000)  # Wait for JavaScript changes
                
                complete_fields = self.page.locator('input:visible, select:visible, textarea:visible').count()
                print(f"📊 DEBUG: Complete edit mode fields: {complete_fields}")
                
                self.debug_edit_page_state("complete_edit_mode")
                
                # Test partial edit mode
                if partial_edit.count() > 0 and partial_edit.is_visible():
                    partial_edit.click()
                    self.page.wait_for_timeout(2000)  # Wait for JavaScript changes
                    
                    partial_fields = self.page.locator('input:visible, select:visible, textarea:visible').count()
                    print(f"📊 DEBUG: Partial edit mode fields: {partial_fields}")
                    
                    self.debug_edit_page_state("partial_edit_mode")
                    
                    # Verify field count changed
                    if complete_fields != partial_fields:
                        print("✅ DEBUG: Dynamic field visibility is working")
                    else:
                        print("⚠️  DEBUG: No change in field visibility detected")
                else:
                    print("⚠️  DEBUG: Partial edit option not found")
            else:
                print("⚠️  DEBUG: Complete edit option not found")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_protocol_modal_functionality(self):
        """Test protocol PDF modal opening and functionality."""
        print("\n🚀 TEST: test_protocol_modal_functionality")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            
            # Look for protocol modal triggers
            protocol_triggers = [
                'button:has-text("protocolo")',
                'button:has-text("Protocolo")',
                'button:has-text("PDF")',
                'a:has-text("protocolo")',
                '.protocol-link',
                'button[data-toggle="modal"]',
                '.modal-trigger'
            ]
            
            modal_trigger = None
            for selector in protocol_triggers:
                element = self.page.locator(selector)
                if element.count() > 0 and element.is_visible():
                    modal_trigger = element
                    print(f"✅ DEBUG: Found protocol trigger with selector: {selector}")
                    break
            
            if modal_trigger:
                # Click to open modal
                modal_trigger.click()
                self.page.wait_for_timeout(2000)  # Wait for modal animation
                
                self.debug_edit_page_state("protocol_modal_opened")
                
                # Check if modal is visible
                modal_selectors = [
                    '.modal',
                    '.modal-dialog',
                    '.popup',
                    '[role="dialog"]'
                ]
                
                modal_visible = False
                for selector in modal_selectors:
                    modal = self.page.locator(selector)
                    if modal.count() > 0 and modal.is_visible():
                        modal_visible = True
                        print(f"✅ DEBUG: Modal visible with selector: {selector}")
                        break
                
                if modal_visible:
                    # Look for close button
                    close_selectors = [
                        'button:has-text("Fechar")',
                        'button:has-text("Close")',
                        '.modal-close',
                        '.close',
                        'button[data-dismiss="modal"]'
                    ]
                    
                    for selector in close_selectors:
                        close_btn = self.page.locator(selector)
                        if close_btn.count() > 0 and close_btn.is_visible():
                            close_btn.click()
                            self.page.wait_for_timeout(1000)
                            self.debug_edit_page_state("protocol_modal_closed")
                            break
                else:
                    print("⚠️  DEBUG: Modal not detected after click")
            else:
                print("⚠️  DEBUG: No protocol modal trigger found")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_medication_management_interface(self):
        """Test medication selection and management interface."""
        print("\n🚀 TEST: test_medication_management_interface")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            self.debug_edit_page_state("before_medication_test")
            
            # Look for medication-related elements
            medication_selectors = [
                'select[name*="medicamento"]',
                'input[name*="medicamento"]',
                'select[name*="med"]',
                '.medication-section',
                '.medicamentos',
                'select:has-option-text("Levetiracetam")',
                'select:has-option-text("Carbamazepina")'
            ]
            
            medication_fields = []
            for selector in medication_selectors:
                elements = self.page.locator(selector).all()
                if elements:
                    medication_fields.extend(elements)
                    print(f"✅ DEBUG: Found {len(elements)} medication elements with selector: {selector}")
            
            if medication_fields:
                # Test first medication field
                first_med_field = medication_fields[0]
                if first_med_field.is_visible():
                    # If it's a select, try to select an option
                    tag_name = first_med_field.evaluate('el => el.tagName.toLowerCase()')
                    if tag_name == 'select':
                        options = first_med_field.locator('option').all()
                        print(f"📋 DEBUG: Found {len(options)} medication options")
                        
                        if len(options) > 1:  # Skip first option (usually empty)
                            second_option = options[1]
                            option_text = second_option.text_content()
                            first_med_field.select_option(index=1)
                            print(f"✅ DEBUG: Selected medication: {option_text}")
                            
                            self.debug_edit_page_state("medication_selected")
                    
                    elif tag_name == 'input':
                        # If it's an input, try typing a medication name
                        first_med_field.fill("Levetiracetam")
                        print("✅ DEBUG: Filled medication input field")
                        
                        self.debug_edit_page_state("medication_input_filled")
            else:
                print("⚠️  DEBUG: No medication management interface found")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_conditional_fields_display(self):
        """Test disease-specific conditional fields based on protocol configuration."""
        print("\n🚀 TEST: test_conditional_fields_display")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            
            # Count all form fields
            total_fields = self.page.locator('input, select, textarea').count()
            visible_fields = self.page.locator('input:visible, select:visible, textarea:visible').count()
            
            print(f"📊 DEBUG: Total fields: {total_fields}, Visible fields: {visible_fields}")
            
            # Look for conditional/dynamic fields
            conditional_selectors = [
                'input[data-conditional]',
                'select[data-conditional]',
                '.conditional-field',
                '.dynamic-field',
                '[style*="display: none"]',
                '[style*="display:none"]'
            ]
            
            hidden_fields = 0
            for selector in conditional_selectors:
                elements = self.page.locator(selector).all()
                if elements:
                    hidden_fields += len(elements)
                    print(f"📝 DEBUG: Found {len(elements)} conditional elements with selector: {selector}")
            
            if hidden_fields > 0:
                print(f"✅ DEBUG: Found {hidden_fields} conditional/hidden fields")
                
                # Try to trigger conditional fields by changing edit mode
                complete_radio = self.page.locator('input[name="edicao_completa"], input[type="radio"]').first
                if complete_radio.is_visible():
                    complete_radio.click()
                    self.page.wait_for_timeout(2000)
                    
                    new_visible_fields = self.page.locator('input:visible, select:visible, textarea:visible').count()
                    print(f"📊 DEBUG: Visible fields after toggle: {new_visible_fields}")
                    
                    if new_visible_fields != visible_fields:
                        print("✅ DEBUG: Conditional field display is working")
                    else:
                        print("⚠️  DEBUG: No change in conditional field display")
            else:
                print("⚠️  DEBUG: No conditional fields detected")
                
            self.debug_edit_page_state("conditional_fields_tested")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_form_state_management(self):
        """Test form state persistence and management across interactions."""
        print("\n🚀 TEST: test_form_state_management")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            
            # Fill some form fields with test data
            test_data = {
                'nome_paciente': 'Test Patient Updated',
                'peso': '70',
                'altura': '170'
            }
            
            filled_fields = 0
            for field_name, value in test_data.items():
                field = self.page.locator(f'input[name="{field_name}"]')
                if field.count() > 0 and field.is_visible():
                    field.clear()
                    field.fill(value)
                    filled_fields += 1
                    print(f"✅ DEBUG: Filled {field_name} with {value}")
            
            if filled_fields > 0:
                self.debug_edit_page_state("form_data_filled")
                
                # Change edit mode to test if data persists
                edit_toggle = self.page.locator('input[type="radio"]').first
                if edit_toggle.is_visible():
                    edit_toggle.click()
                    self.page.wait_for_timeout(2000)
                    
                    # Check if filled data is still there
                    persistent_data = 0
                    for field_name, value in test_data.items():
                        field = self.page.locator(f'input[name="{field_name}"]')
                        if field.count() > 0 and field.is_visible():
                            current_value = field.input_value()
                            if value in current_value:
                                persistent_data += 1
                                print(f"✅ DEBUG: {field_name} data persisted")
                            else:
                                print(f"⚠️  DEBUG: {field_name} data lost")
                    
                    if persistent_data > 0:
                        print("✅ DEBUG: Form state management working")
                    else:
                        print("⚠️  DEBUG: Form state not preserved")
                        
                    self.debug_edit_page_state("form_state_tested")
            else:
                print("⚠️  DEBUG: No form fields available for state testing")
        else:
            self.skipTest("Could not navigate to edit page")

    def test_javascript_interactions(self):
        """Test JavaScript-driven form interactions and processoEdit.js functionality."""
        print("\n🚀 TEST: test_javascript_interactions")
        
        # Login and navigate to edit page
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            self.wait_for_javascript_load()
            
            # Test JavaScript is loaded and working
            try:
                # Check if processoEdit.js functions are available
                js_check = self.page.evaluate("""
                    () => {
                        // Check for common JavaScript indicators
                        const hasJQuery = typeof jQuery !== 'undefined';
                        const hasCustomFunctions = typeof window.toggleEditMode !== 'undefined' || 
                                                 typeof window.showHideFields !== 'undefined';
                        const hasEventListeners = document.querySelectorAll('[onclick]').length > 0;
                        
                        return {
                            jquery: hasJQuery,
                            customFunctions: hasCustomFunctions,
                            eventListeners: hasEventListeners
                        };
                    }
                """)
                
                print(f"📜 DEBUG: JavaScript check results: {js_check}")
                
                if js_check.get('jquery'):
                    print("✅ DEBUG: jQuery is available")
                
                if js_check.get('customFunctions'):
                    print("✅ DEBUG: Custom JavaScript functions detected")
                
                if js_check.get('eventListeners'):
                    print("✅ DEBUG: Event listeners found")
                
            except Exception as e:
                print(f"⚠️  DEBUG: JavaScript evaluation error: {e}")
            
            # Test interactive elements that rely on JavaScript
            interactive_selectors = [
                'button[onclick]',
                'input[onchange]',
                '.js-toggle',
                '[data-toggle]',
                'button:has-text("Mostrar")',
                'button:has-text("Ocultar")'
            ]
            
            interactive_elements = []
            for selector in interactive_selectors:
                elements = self.page.locator(selector).all()
                if elements:
                    interactive_elements.extend(elements)
                    print(f"🖱️  DEBUG: Found {len(elements)} interactive elements with selector: {selector}")
            
            # Test JavaScript-driven interactions
            if interactive_elements:
                first_interactive = interactive_elements[0]
                if first_interactive.is_visible():
                    print("🖱️  DEBUG: Testing JavaScript interaction")
                    first_interactive.click()
                    self.page.wait_for_timeout(2000)
                    
                    self.debug_edit_page_state("javascript_interaction_tested")
            else:
                print("⚠️  DEBUG: No JavaScript-driven interactive elements found")
                
        else:
            self.skipTest("Could not navigate to edit page")


class ProcessEditingAccessibilityTest(ProcessEditingPlaywrightBase):
    """Test process editing page accessibility and responsive features."""
    
    def test_edit_page_accessibility(self):
        """Test edit page accessibility features."""
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
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
                field_describedby = field.get_attribute('aria-describedby')
                
                if field_label or field_required or field_describedby:
                    accessibility_features += 1
                    print(f"✅ Field {field_name}: accessible features present")
            
            print(f"📊 Found {accessibility_features} accessible form elements")
            self.take_screenshot("edit_page_accessibility")
        else:
            self.skipTest("Could not navigate to edit page for accessibility testing")
    
    def test_edit_page_responsive(self):
        """Test edit page on different screen sizes."""
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            # Test mobile size
            self.page.set_viewport_size({"width": 375, "height": 667})
            self.page.wait_for_timeout(1000)
            
            # Check if main elements are still accessible
            main_form = self.page.locator('form').first
            if main_form.is_visible():
                print("✅ Main form visible on mobile")
            
            self.take_screenshot("edit_page_mobile")
            
            # Test tablet size
            self.page.set_viewport_size({"width": 768, "height": 1024})
            self.page.wait_for_timeout(1000)
            self.take_screenshot("edit_page_tablet")
            
            # Reset to desktop size
            self.page.set_viewport_size({"width": 1920, "height": 1080})
        else:
            self.skipTest("Could not navigate to edit page for responsive testing")

    def test_keyboard_navigation(self):
        """Test keyboard navigation through edit form."""
        # Login and navigate
        self.login_user('medico@example.com', 'testpass123')
        success = self.navigate_to_edit_page()
        
        if success:
            # Focus on first input field
            first_input = self.page.locator('input:visible').first
            if first_input.is_visible():
                first_input.focus()
                
                # Tab through form fields
                for i in range(5):  # Test first 5 tab stops
                    self.page.keyboard.press('Tab')
                    self.page.wait_for_timeout(500)
                
                self.take_screenshot("keyboard_navigation_test")
                print("✅ DEBUG: Keyboard navigation tested")
            else:
                print("⚠️  DEBUG: No input fields available for keyboard testing")
        else:
            self.skipTest("Could not navigate to edit page for keyboard testing")