"""
Frontend Security Tests using Playwright - Migrated from Selenium
Tests the actual browser interactions to verify security fixes work in real user scenarios
"""

import time
from django.contrib.auth import get_user_model
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from tests.playwright_base import PlaywrightSecurityTestBase

User = get_user_model()


class FrontendSecurityTest(PlaywrightSecurityTestBase):
    """
    Frontend security tests using Playwright to ensure real browser security works.
    Tests actual user interaction flows to verify security fixes.
    """
    
    def setUp(self):
        super().setUp()
        
        # Create test doctors
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. João Silva",
            crm_medico=self.data_generator.generate_unique_crm(), 
            cns_medico=self.data_generator.generate_unique_cns_medico()
        )
        self.medico1.usuarios.add(self.user1)
        
        self.medico2 = Medico.objects.create(
            nome_medico="Dr. Maria Santos",
            crm_medico=self.data_generator.generate_unique_crm(),
            cns_medico=self.data_generator.generate_unique_cns_medico()
        )
        self.medico2.usuarios.add(self.user2)
        
        # Create test clinics
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica Test 1",
            cns_clinica="1111111",
            logradouro="Rua Test 1",
            logradouro_num="123",
            cidade="Test City",
            bairro="Test Neighborhood", 
            cep="12345-678",
            telefone_clinica="11999999999"
        )
        self.clinica2 = Clinica.objects.create(
            nome_clinica="Clínica Test 2", 
            cns_clinica="2222222",
            logradouro="Rua Test 2",
            logradouro_num="456",
            cidade="Test City 2",
            bairro="Test Neighborhood 2",
            cep="87654-321", 
            telefone_clinica="11888888888"
        )
        
        # Create emissors (doctor-clinic relationships)
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        self.emissor2 = Emissor.objects.create(
            medico=self.medico2,
            clinica=self.clinica2
        )
        
        # Create test patients for each user
        self.paciente1 = Paciente.objects.create(
            nome_paciente="Paciente 1",
            cpf_paciente=self.data_generator.generate_unique_cpf(),
            rg="123456789",
            idade="30",
            sexo="M",
            nome_mae="Mae Paciente 1",
            incapaz=False,
            nome_responsavel="",
            peso="70kg",
            altura="1,70m",
            escolha_etnia="Branco",
            cns_paciente=self.data_generator.generate_unique_cns_paciente(),
            email_paciente="paciente1@test.com",
            cidade_paciente="Test City",
            end_paciente="Endereço 1",
            cep_paciente="12345-678",
            telefone1_paciente="11999999999",
            telefone2_paciente="",
            etnia="Branco"
        )
        self.paciente1.usuarios.add(self.user1)
        
        self.paciente2 = Paciente.objects.create(
            nome_paciente="Paciente 2", 
            cpf_paciente=self.data_generator.generate_unique_cpf(),
            rg="987654321",
            idade="25",
            sexo="F",
            nome_mae="Mae Paciente 2",
            incapaz=False,
            nome_responsavel="",
            peso="60kg",
            altura="1,65m",
            escolha_etnia="Branco",
            cns_paciente=self.data_generator.generate_unique_cns_paciente(),
            email_paciente="paciente2@test.com",
            cidade_paciente="Test City 2",
            end_paciente="Endereço 2",
            cep_paciente="87654-321",
            telefone1_paciente="11888888888",
            telefone2_paciente="",
            etnia="Branco"
        )
        self.paciente2.usuarios.add(self.user2)
        
        # Create test diseases and medications
        self.doenca = Doenca.objects.create(
            cid="A00.0",
            nome="Test Disease"
        )
        self.medicamento = Medicamento.objects.create(
            nome="Test Medicine",
            dosagem="10mg",
            apres="Comprimido"
        )
        
    def test_unauthenticated_user_cannot_access_home(self):
        """Test that unauthenticated users are redirected to login"""
        # Navigate to home page
        self.page.goto(f"{self.live_server_url}/")
        self.wait_for_page_load()
        
        # Check if redirected to login (allow some flexibility in URL matching)
        current_url = self.page.url
        self.assertTrue(
            '/login/' in current_url,
            f"Expected redirect to login page, but got: {current_url}"
        )
        
        # Should see login form
        self.assertTrue(self.page.locator('input[name="email"]').is_visible())
        self.assertTrue(self.page.locator('input[name="password"]').is_visible())
        self.assertTrue(self.page.locator('button[type="submit"]').is_visible())
        
        self.take_screenshot("unauthenticated_home_access")
    
    def test_patient_cpf_access_authorization(self):
        """Test that users can only access patients they own"""
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Try to access user2's patient via CPF search/URL manipulation  
        user2_patient_url = f"{self.live_server_url}/pacientes/cpf/{self.paciente2.cpf_paciente}/"
        
        self.page.goto(user2_patient_url)
        
        # Should be denied access (redirect or error message)
        current_url = self.page.url
        self.assertTrue(
            '/login/' in current_url or 
            self.page.locator('text=Access Denied').is_visible() or
            self.page.locator('text=Não encontrado').is_visible(),
            f"Expected access denied but got URL: {current_url}"
        )
        
        self.take_screenshot("patient_cpf_access_denied")
    
    def test_patient_search_authorization(self):
        """Test that patient search only returns user's own patients"""
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Navigate to patient search/list page
        self.page.goto(f"{self.live_server_url}/pacientes/")
        self.wait_for_page_load()
        
        # Should only see user1's patients
        page_content = self.page.content()
        
        # Should contain user1's patient
        self.assertIn(self.paciente1.nome_paciente, page_content)
        # Should NOT contain user2's patient
        self.assertNotIn(self.paciente2.nome_paciente, page_content)
        
        self.take_screenshot("patient_search_authorization")
    
    def test_cross_user_session_isolation(self):
        """Test that different users cannot access each other's data"""
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Verify we can access our own patient
        self.page.goto(f"{self.live_server_url}/pacientes/")
        self.wait_for_page_load()
        
        page_content = self.page.content()
        self.assertIn(self.paciente1.nome_paciente, page_content)
        
        # Logout and login as user2
        self.page.goto(f"{self.live_server_url}/logout/")
        self.wait_for_page_load()
        
        self.login_user('user2@test.com', 'testpass123')
        
        # Verify we can only see user2's data
        self.page.goto(f"{self.live_server_url}/pacientes/")
        self.wait_for_page_load()
        
        page_content = self.page.content()
        self.assertIn(self.paciente2.nome_paciente, page_content)
        self.assertNotIn(self.paciente1.nome_paciente, page_content)
        
        self.take_screenshot("cross_user_session_isolation")
    
    def test_new_process_creation_flow(self):
        """Test the complete flow for creating new processes"""
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Navigate to process creation
        self.page.goto(f"{self.live_server_url}/processos/novo/")
        self.wait_for_page_load()
        
        # Fill in the process form
        if self.page.locator('select[name="paciente"]').is_visible():
            self.page.select_option('select[name="paciente"]', str(self.paciente1.id))
        
        if self.page.locator('select[name="doenca"]').is_visible():
            self.page.select_option('select[name="doenca"]', str(self.doenca.id))
        
        if self.page.locator('select[name="emissor"]').is_visible():
            self.page.select_option('select[name="emissor"]', str(self.emissor1.id))
        
        self.take_screenshot("new_process_form_filled")
        
        # Submit the form
        self.page.click('button[type="submit"]')
        self.wait_for_page_load()
        
        # Verify successful creation
        current_url = self.page.url
        self.assertTrue(
            '/processos/' in current_url or
            self.page.locator('text=sucesso').is_visible(),
            f"Process creation failed, URL: {current_url}"
        )
        
        self.take_screenshot("new_process_created")
    
    def test_process_workflow_security(self):
        """Test that process workflow respects user authorization"""
        # Create a process for user1
        processo1 = Processo.objects.create(
            usuario=self.user1,
            paciente=self.paciente1,
            doenca=self.doenca,
            emissor=self.emissor1
        ,
            dados_condicionais={}
        )
        
        # Create a process for user2
        processo2 = Processo.objects.create(
            usuario=self.user2,
            paciente=self.paciente2,
            doenca=self.doenca,
            emissor=self.emissor2
        ,
            dados_condicionais={}
        )
        
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Try to access user2's process
        user2_process_url = f"{self.live_server_url}/processos/{processo2.id}/"
        self.page.goto(user2_process_url)
        
        # Should be denied access
        self.assert_access_denied()
        
        self.take_screenshot("process_workflow_security")
    
    def test_process_page_authorization(self):
        """Test that process edit page validates user ownership"""
        # Create a process for user2
        processo2 = Processo.objects.create(
            usuario=self.user2,
            paciente=self.paciente2,
            doenca=self.doenca,
            emissor=self.emissor2
        ,
            dados_condicionais={}
        )
        
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Try to access user2's process edit page
        edit_url = f"{self.live_server_url}/processos/{processo2.id}/edit/"
        self.page.goto(edit_url)
        
        # Should be denied access
        self.assert_access_denied()
        
        self.take_screenshot("process_page_authorization")
    
    def test_login_logout_flow(self):
        """Test complete login/logout security flow"""
        # Start at home page (should redirect to login)
        self.page.goto(f"{self.live_server_url}/")
        self.page.wait_for_url(f"{self.live_server_url}/login/")
        
        # Login with valid credentials
        self.login_user('user1@test.com', 'testpass123')
        
        # Should be redirected to dashboard/home
        current_url = self.page.url
        self.assertNotIn('/login/', current_url)
        
        # Verify logged in state
        page_content = self.page.content()
        self.assertTrue(
            'logout' in page_content.lower() or 
            'sair' in page_content.lower()
        )
        
        # Logout
        self.page.goto(f"{self.live_server_url}/logout/")
        self.wait_for_page_load()
        
        # Should be redirected to login
        self.page.wait_for_url(f"{self.live_server_url}/login/")
        
        # Try to access protected page - should be redirected to login
        self.page.goto(f"{self.live_server_url}/pacientes/")
        self.page.wait_for_url(f"{self.live_server_url}/login/")
        
        self.take_screenshot("login_logout_flow")
    
    def test_invalid_login_attempt(self):
        """Test that invalid login attempts are properly rejected"""
        self.page.goto(f"{self.live_server_url}/login/")
        
        # Try invalid credentials
        self.page.fill('input[name="email"]', 'invalid@test.com')
        self.page.fill('input[name="password"]', 'wrongpassword')
        self.page.click('button[type="submit"]')
        
        self.wait_for_page_load()
        
        # Should still be on login page with error
        current_url = self.page.url
        self.assertIn('/login/', current_url)
        
        # Should show error message
        page_content = self.page.content()
        self.assertTrue(
            'inválid' in page_content.lower() or
            'erro' in page_content.lower() or
            'incorrect' in page_content.lower()
        )
        
        self.take_screenshot("invalid_login_attempt")


class PatientAuthorizationTest(PlaywrightSecurityTestBase):
    """
    Specific tests for patient data authorization using Playwright
    """
    
    def setUp(self):
        super().setUp()
        
        # Create patients for different users
        self.paciente_user1 = Paciente.objects.create(
            nome_paciente="Test Patient User1",
            cpf_paciente=self.data_generator.generate_unique_cpf(),
            rg="111111111",
            idade="30",
            sexo="M",
            nome_mae="Mae Test 1",
            incapaz=False,
            nome_responsavel="",
            peso="70kg",
            altura="1,70m",
            escolha_etnia="Branco",
            cns_paciente=self.data_generator.generate_unique_cns_paciente(),
            email_paciente="patient1@test.com",
            cidade_paciente="Test City",
            end_paciente="Test Address 1",
            cep_paciente="12345-678",
            telefone1_paciente="11999999999",
            telefone2_paciente="",
            etnia="Branco"
        )
        self.paciente_user1.usuarios.add(self.user1)
        
        self.paciente_user2 = Paciente.objects.create(
            nome_paciente="Test Patient User2", 
            cpf_paciente=self.data_generator.generate_unique_cpf(),
            rg="222222222",
            idade="25",
            sexo="F",
            nome_mae="Mae Test 2",
            incapaz=False,
            nome_responsavel="",
            peso="60kg",
            altura="1,65m",
            escolha_etnia="Branco",
            cns_paciente=self.data_generator.generate_unique_cns_paciente(),
            email_paciente="patient2@test.com",
            cidade_paciente="Test City 2",
            end_paciente="Test Address 2",
            cep_paciente="87654-321",
            telefone1_paciente="11888888888",
            telefone2_paciente="",
            etnia="Branco"
        )
        self.paciente_user2.usuarios.add(self.user2)
    
    def test_patient_list_authorization(self):
        """Test that patient list only shows user's patients"""
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Go to patients page
        self.page.goto(f"{self.live_server_url}/pacientes/")
        self.wait_for_page_load()
        
        page_content = self.page.content()
        
        # Should see own patient
        self.assertIn(self.paciente_user1.nome_paciente, page_content)
        # Should NOT see other user's patient
        self.assertNotIn(self.paciente_user2.nome_paciente, page_content)
        
        self.take_screenshot("patient_list_authorization")
    
    def test_patient_detail_authorization(self):
        """Test that patient detail pages are properly protected"""
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Try to access user2's patient detail
        detail_url = f"{self.live_server_url}/pacientes/{self.paciente_user2.id}/"
        self.page.goto(detail_url)
        
        # Should be denied access
        self.assert_access_denied()
        
        self.take_screenshot("patient_detail_authorization")


class ProcessAuthorizationTest(PlaywrightSecurityTestBase):
    """
    Process-specific authorization tests using Playwright
    """
    
    def setUp(self):
        super().setUp()
        
        # Create necessary medical data
        self.doenca = Doenca.objects.create(
            cid="TEST001",
            nome="Test Disease"
        )
        
        # Create patients
        self.paciente1 = Paciente.objects.create(
            nome_paciente="Patient 1",
            cpf_paciente=self.data_generator.generate_unique_cpf(),
            rg="111111111",
            idade="30",
            sexo="M",
            nome_mae="Mae 1",
            incapaz=False,
            nome_responsavel="",
            peso="70kg",
            altura="1,70m",
            escolha_etnia="Branco",
            cns_paciente=self.data_generator.generate_unique_cns_paciente(),
            email_paciente="patient1@process.com",
            cidade_paciente="Test City",
            end_paciente="Test Address 1",
            cep_paciente="12345-678",
            telefone1_paciente="11999999999",
            telefone2_paciente="",
            etnia="Branco"
        )
        self.paciente1.usuarios.add(self.user1)
        
        self.paciente2 = Paciente.objects.create(
            nome_paciente="Patient 2",
            cpf_paciente=self.data_generator.generate_unique_cpf(),
            rg="222222222",
            idade="25",
            sexo="F",
            nome_mae="Mae 2",
            incapaz=False,
            nome_responsavel="",
            peso="60kg",
            altura="1,65m",
            escolha_etnia="Branco",
            cns_paciente=self.data_generator.generate_unique_cns_paciente(),
            email_paciente="patient2@process.com",
            cidade_paciente="Test City 2",
            end_paciente="Test Address 2",
            cep_paciente="87654-321",
            telefone1_paciente="11888888888",
            telefone2_paciente="",
            etnia="Branco"
        )
        self.paciente2.usuarios.add(self.user2)
        
        # Create doctors and emissors
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. Test 1",
            crm_medico="123456"
        )
        self.medico1.usuarios.add(self.user1)
        
        self.clinica = Clinica.objects.create(
            nome_clinica="Test Clinic",
            cns_clinica="1111111",
            logradouro="Test Street",
            logradouro_num="123",
            cidade="Test City",
            bairro="Test Neighborhood",
            cep="12345-678",
            telefone_clinica="11999999999"
        )
        
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica
        )
    
    def test_process_list_authorization(self):
        """Test that process list only shows user's processes"""
        # Create processes for both users
        processo1 = Processo.objects.create(
            usuario=self.user1,
            paciente=self.paciente1,
            doenca=self.doenca,
            emissor=self.emissor1
        ,
            dados_condicionais={}
        )
        
        processo2 = Processo.objects.create(
            usuario=self.user2,
            paciente=self.paciente2,
            doenca=self.doenca,
            emissor=self.emissor1  # Same emissor for simplicity
        ,
            dados_condicionais={}
        )
        
        # Login as user1
        self.login_user('user1@test.com', 'testpass123')
        
        # Go to processes page
        self.page.goto(f"{self.live_server_url}/processos/")
        self.wait_for_page_load()
        
        page_content = self.page.content()
        
        # Should see own patient's process
        self.assertIn(self.paciente1.nome_paciente, page_content)
        # Should NOT see other user's patient's process
        self.assertNotIn(self.paciente2.nome_paciente, page_content)
        
        self.take_screenshot("process_list_authorization")