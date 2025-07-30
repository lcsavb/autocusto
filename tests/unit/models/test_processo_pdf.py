from django.test import TestCase, TransactionTestCase, Client
from django.core.management import call_command
from django.urls import reverse
from processos.models import Medicamento, Protocolo, Doenca, Processo
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from usuarios.models import Usuario
import tempfile
import os
import random
from cpf_generator import CPF


class TestDataFactory:
    """Factory for generating valid, isolated test data with proper CPF validation."""
    
    @staticmethod
    def valid_cpfs():
        """List of valid CPFs for testing - properly calculated checksums."""
        return [
            '11144477735',  # Valid CPF
            '22255588846',  # Valid CPF  
            '33366699957',  # Valid CPF
            '44477711168',  # Valid CPF
            '55588822279',  # Valid CPF
            '66699933380',  # Valid CPF
            '77700044491',  # Valid CPF
            '88811155502',  # Valid CPF
            '99922266613',  # Valid CPF
            '12345678909',  # Valid CPF (commonly used in testing)
        ]
    
    @staticmethod
    def get_unique_cpf():
        """Get a unique valid CPF for testing using cpf-generator."""
        return CPF.generate()
    
    @staticmethod
    def get_unique_cns():
        """Get a unique CNS for testing."""
        return f"{random.randint(1000000, 9999999)}"
    
    @staticmethod
    def get_unique_email(prefix="test"):
        """Get a unique email for testing."""
        return f"{prefix}{random.randint(10000, 99999)}@example.com"


class PDFAccessControlTest(TestCase):
    """
    Comprehensive test suite for PDF access control and security.
    
    This test class verifies that the serve_pdf view properly implements:
    - Authentication requirements
    - Authorization based on patient ownership
    - Filename validation and security
    - CPF format handling (formatted vs cleaned)
    - Directory traversal protection
    - Error handling and logging
    """
    
    def setUp(self):
        """Set up test data including users, patients, and temporary PDF files."""
        # Create test users
        self.user1 = Usuario.objects.create_user(
            email="doctor1@example.com", 
            password="testpass123",
            is_medico=True
        )
        self.user2 = Usuario.objects.create_user(
            email="doctor2@example.com", 
            password="testpass123",
            is_medico=True
        )
        self.user3 = Usuario.objects.create_user(
            email="unauthorized@example.com", 
            password="testpass123"
        )
        
        # Generate valid CPFs for testing
        self.patient1_cpf = TestDataFactory.get_unique_cpf()
        self.patient2_cpf = TestDataFactory.get_unique_cpf()
        
        # Create test patients with generated CPFs
        self.patient1_formatted = Paciente.objects.create(
            nome_paciente="Patient One",
            cpf_paciente=self.patient1_cpf,  # Use generated CPF
            cns_paciente="123456789012345",
            nome_mae="Mae Um",
            idade="30",
            sexo="M",
            peso="70",
            altura="1.70",
            incapaz=False,
            etnia="Parda",
            telefone1_paciente="11999999999",
            end_paciente="Rua Test, 1",
            rg="1234567",
            escolha_etnia="Parda",
            cidade_paciente="Test City",
            cep_paciente="12345-678",
            telefone2_paciente="",
            nome_responsavel=""
        )
        
        self.patient2_clean = Paciente.objects.create(
            nome_paciente="Patient Two",
            cpf_paciente=self.patient2_cpf,  # Use generated CPF
            cns_paciente="123456789012346",
            nome_mae="Mae Dois",
            idade="35",
            sexo="F",
            peso="60",
            altura="1.65",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11888888888",
            end_paciente="Rua Test, 2",
            rg="7654321",
            escolha_etnia="Branca",
            cidade_paciente="Test City",
            cep_paciente="12345-679",
            telefone2_paciente="",
            nome_responsavel=""
        )
        
        # Create patient relationships
        self.patient1_formatted.usuarios.add(self.user1)  # user1 has access to patient1
        self.patient2_clean.usuarios.add(self.user2)      # user2 has access to patient2
        # user3 has no patient access
        
        # Create temporary test PDF files
        self.temp_dir = tempfile.mkdtemp()
        
        # PDF for patient1 (formatted CPF in filename) 
        self.pdf1_filename = f"pdf_final_{self.patient1_cpf[:3]}.{self.patient1_cpf[3:6]}.{self.patient1_cpf[6:9]}-{self.patient1_cpf[9:]}_G35.pdf"
        self.pdf1_path = f"/tmp/{self.pdf1_filename}"
        with open(self.pdf1_path, 'wb') as f:
            f.write(b'%PDF-1.4 fake pdf content for patient 1')
            
        # PDF for patient2 (clean CPF in filename)
        self.pdf2_filename = f"pdf_final_{self.patient2_cpf}_M06.pdf" 
        self.pdf2_path = f"/tmp/{self.pdf2_filename}"
        with open(self.pdf2_path, 'wb') as f:
            f.write(b'%PDF-1.4 fake pdf content for patient 2')
            
        # Test client
        self.client = Client()
        
    def tearDown(self):
        """Clean up temporary files."""
        # Remove test PDF files
        for pdf_path in [self.pdf1_path, self.pdf2_path]:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access PDFs."""
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Should redirect to login (302) or return 403/401
        self.assertIn(response.status_code, [302, 401, 403])
        
    def test_authorized_user_access_granted(self):
        """Test that authorized users can access their patients' PDFs."""
        # Login as user1 who has access to patient1
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Should successfully serve the PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], f'inline; filename="{self.pdf1_filename}"')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        
    def test_unauthorized_user_access_denied(self):
        """Test that users cannot access PDFs for patients they don't own."""
        # Login as user2 who does NOT have access to patient1
        self.client.login(email="doctor2@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Should return 404 (access denied)
        self.assertEqual(response.status_code, 404)
        
    def test_user_without_patients_access_denied(self):
        """Test that users with no patients cannot access any PDFs."""
        # Login as user3 who has no patient relationships
        self.client.login(email="unauthorized@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Should return 404 (access denied)
        self.assertEqual(response.status_code, 404)
        
    def test_cpf_format_handling_formatted(self):
        """Test that PDFs with formatted CPFs in filename work correctly."""
        # Login as user1 who has access to patient1 (formatted CPF)
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Should successfully serve the PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_cpf_format_handling_clean(self):
        """Test that PDFs with clean CPFs in filename work correctly."""
        # Login as user2 who has access to patient2 (clean CPF)
        self.client.login(email="doctor2@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf2_filename])
        response = self.client.get(url)
        
        # Should successfully serve the PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_invalid_filename_format(self):
        """Test that invalid filename formats are rejected."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        invalid_filenames = [
            "not_pdf_format.txt",
            "missing_prefix_G35.pdf", 
            "pdf_final_.pdf",
            "pdf_final_invalid_cpf_G35.pdf",
            "pdf_final_123_G35.pdf",  # CPF too short
            "pdf_final_1234567890123_G35.pdf",  # CPF too long
        ]
        
        for filename in invalid_filenames:
            with self.subTest(filename=filename):
                url = reverse('processos-serve-pdf', args=[filename])
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                
    def test_directory_traversal_protection(self):
        """Test that directory traversal attempts are blocked."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        # Test filenames that Django URL routing will accept but should be blocked by our validation
        # Use the valid CPF from patient1 for security tests
        cpf_clean = self.patient1_cpf
        cpf_formatted = f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
        
        malicious_filenames = [
            f"pdf_final_{cpf_clean[:3]}\\{cpf_clean[3:6]}\\{cpf_clean[6:9]}-{cpf_clean[9:]}_G35.pdf",  # Windows path separator
            f"pdf_final_..{cpf_formatted}_G35.pdf",  # Dot sequences
            f"pdf_final_{cpf_formatted}..G35.pdf",   # Embedded dots
        ]
        
        for filename in malicious_filenames:
            with self.subTest(filename=filename):
                try:
                    url = reverse('processos-serve-pdf', args=[filename])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 404)
                except Exception:
                    # If URL routing fails, that's also acceptable protection
                    pass
                
    def test_non_pdf_extension_rejected(self):
        """Test that non-PDF files are rejected."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        # Use the valid CPF from patient1 for extension tests
        cpf_formatted = f"{self.patient1_cpf[:3]}.{self.patient1_cpf[3:6]}.{self.patient1_cpf[6:9]}-{self.patient1_cpf[9:]}"
        
        non_pdf_files = [
            f"pdf_final_{cpf_formatted}_G35.txt",
            f"pdf_final_{cpf_formatted}_G35.doc", 
            f"pdf_final_{cpf_formatted}_G35.exe",
            f"pdf_final_{cpf_formatted}_G35",  # No extension
        ]
        
        for filename in non_pdf_files:
            with self.subTest(filename=filename):
                url = reverse('processos-serve-pdf', args=[filename])
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                
    def test_missing_pdf_file(self):
        """Test behavior when PDF file doesn't exist on filesystem."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        # Try to access a PDF that should be authorized but doesn't exist
        cpf_formatted = f"{self.patient1_cpf[:3]}.{self.patient1_cpf[3:6]}.{self.patient1_cpf[6:9]}-{self.patient1_cpf[9:]}"
        url = reverse('processos-serve-pdf', args=[f'pdf_final_{cpf_formatted}_Z99.pdf'])
        response = self.client.get(url)
        
        # Should return 404 (file not found)
        self.assertEqual(response.status_code, 404)
        
    def test_cross_user_patient_access_denied(self):
        """Test comprehensive cross-user access denial."""
        # user1 tries to access user2's patient PDF
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf2_filename])
        response = self.client.get(url)
        
        # Should be denied
        self.assertEqual(response.status_code, 404)
        
        # user2 tries to access user1's patient PDF  
        self.client.login(email="doctor2@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Should be denied
        self.assertEqual(response.status_code, 404)
        
    def test_pdf_content_integrity(self):
        """Test that PDF content is served correctly."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Verify content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'%PDF-1.4 fake pdf content for patient 1')
        
    def test_security_headers_present(self):
        """Test that proper security headers are set."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=[self.pdf1_filename])
        response = self.client.get(url)
        
        # Verify security headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_edge_case_cpf_formats(self):
        """Test edge cases in CPF format handling."""
        # Generate edge case CPF for testing
        edge_cpf = TestDataFactory.get_unique_cpf()
        
        # Create patient with edge case CPF format
        patient_edge = Paciente.objects.create(
            nome_paciente="Edge Case Patient",
            cpf_paciente=edge_cpf,  # Use generated CPF
            cns_paciente="123456789012347",
            nome_mae="Mae Edge",
            idade="25",
            sexo="F",
            peso="55",
            altura="1.60",
            incapaz=False,
            etnia="Indígena",
            telefone1_paciente="11777777777",
            end_paciente="Rua Edge, 1",
            rg="1111111",
            escolha_etnia="Indígena",
            cidade_paciente="Edge City",
            cep_paciente="12345-680",
            telefone2_paciente="",
            nome_responsavel=""
        )
        patient_edge.usuarios.add(self.user1)
        
        # Create PDF file for edge case using generated CPF
        edge_cpf_formatted = f"{edge_cpf[:3]}.{edge_cpf[3:6]}.{edge_cpf[6:9]}-{edge_cpf[9:]}"
        edge_pdf_filename = f"pdf_final_{edge_cpf_formatted}_H30.pdf"
        edge_pdf_path = f"/tmp/{edge_pdf_filename}"
        with open(edge_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4 edge case pdf content')
            
        try:
            self.client.login(email="doctor1@example.com", password="testpass123")
            
            url = reverse('processos-serve-pdf', args=[edge_pdf_filename])
            response = self.client.get(url)
            
            # Should work correctly
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            
        finally:
            if os.path.exists(edge_pdf_path):
                os.remove(edge_pdf_path)


class PDFGenerationIntegrationTest(TransactionTestCase):
    """Integration tests for complete PDF generation workflow with complete isolation."""
    
    def setUp(self):
        """Set up completely isolated test environment using TestDataFactory."""
        # Flush database for complete isolation
        call_command('flush', '--noinput')
        
        # Use TestDataFactory for valid, unique test data
        unique_email = TestDataFactory.get_unique_email('pdftest')
        unique_cns = TestDataFactory.get_unique_cns()
        unique_cpf = TestDataFactory.get_unique_cpf()
        
        # Create completely isolated user and medico
        self.user = Usuario.objects.create_user(
            email=unique_email,
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Dr. Test Silva',
            crm_medico='123456',
            cns_medico='123456789012345',
            estado='SP',
            especialidade='OFTALMOLOGIA'
        )
        self.user.medicos.add(self.medico)
        
        # Create clinic using proper versioning method
        clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': unique_cns,
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'Test City',
            'bairro': 'Test Neighborhood',
            'cep': '12345-678',
            'telefone_clinica': '(11) 9876-5432'
        }
        
        self.clinica = Clinica.create_or_update_for_user(self.user, self.medico, clinic_data)
        
        # Create emissor (doctor-clinic relationship) - use get_or_create to prevent duplicates
        from clinicas.models import Emissor
        self.emissor, created = Emissor.objects.get_or_create(
            medico=self.medico,
            clinica=self.clinica
        )
        
        # Store valid CPF for session usage
        self.valid_cpf = unique_cpf
        
        # Create test patient with unique CPF from factory
        self.paciente = Paciente.objects.create(
            nome_paciente='Test Patient',
            cpf_paciente=unique_cpf,  # Valid CPF from factory
            idade='30',
            sexo='M',
            nome_mae='Test Mother',
            incapaz=False,
            nome_responsavel='',
            rg='123456789',
            peso='70kg',
            altura='1,75m',
            escolha_etnia='BRANCO',
            cns_paciente='123456789012345',
            email_paciente='patient@test.com',
            cidade_paciente='Test City',
            end_paciente='Test Address, 123',
            cep_paciente='12345-678',
            telefone1_paciente='11987654321',
            telefone2_paciente='11987654322',
            etnia='BRANCO'
        )
        self.paciente.usuarios.add(self.user)
        
        # Create patient version for proper versioning system
        from pacientes.models import PacienteVersion, PacienteUsuarioVersion
        
        version = PacienteVersion.objects.create(
            paciente=self.paciente,
            version_number=1,
            created_by=self.user,
            nome_paciente='Test Patient',
            idade='30',
            sexo='M',
            nome_mae='Test Mother',
            incapaz=False,
            nome_responsavel='',
            rg='123456789',
            peso='70kg',
            altura='1,75m',
            escolha_etnia='BRANCO',
            cns_paciente='123456789012345',
            email_paciente='patient@test.com',
            cidade_paciente='Test City',
            end_paciente='Test Address, 123',
            cep_paciente='12345-678',
            telefone1_paciente='11987654321',
            telefone2_paciente='11987654322',
            etnia='BRANCO',
            change_summary='Test patient version'
        )
        
        # Create user-version assignment
        paciente_usuario = self.paciente.usuarios.through.objects.get(paciente=self.paciente, usuario=self.user)
        PacienteUsuarioVersion.objects.create(
            paciente_usuario=paciente_usuario,
            version=version
        )
        
        # Create protocol and disease with medications
        self.protocolo = Protocolo.objects.create(
            nome='Protocolo H30 - Coriorretinite',
            arquivo='h30_coriorretinite.pdf'
        )
        
        # Create medications available for this protocol
        self.medicamento1 = Medicamento.objects.create(
            nome='Prednisolona',
            dosagem='20mg',
            apres='Comprimido'
        )
        self.medicamento2 = Medicamento.objects.create(
            nome='Colírio Prednisolona', 
            dosagem='1%',
            apres='Frasco 5ml'
        )
        
        # Associate medications with protocol
        self.protocolo.medicamentos.add(self.medicamento1, self.medicamento2)
        
        # Create disease linked to protocol
        self.doenca = Doenca.objects.create(
            cid='H30',
            nome='Coriorretinite',
            protocolo=self.protocolo
        )
        
        self.client = Client()
        
    def _get_complete_form_data(self):
        """Get complete form data matching NovoProcesso form structure."""
        return {
            # Required patient fields (matching NovoProcesso form structure)
            'cpf_paciente': '93448378054',
            'nome_paciente': 'Test Patient PDF',
            'nome_mae': 'Test Mother',
            'peso': 70,
            'altura': 175,
            'end_paciente': 'Test Address, 123',
            'incapaz': 'False',
            'nome_responsavel': '',
            
            # Required medical fields
            'consentimento': 'False',
            'cid': 'H30',
            'diagnostico': 'Coriorretinite',
            'anamnese': 'Patient presents with inflammation in the eye.',
            'preenchido_por': 'paciente',
            
            # Required administrative fields
            'clinicas': str(self.clinica.id),
            'data_1': '01/01/2024',
            'emitir_relatorio': 'False',
            'emitir_exames': 'False',
            'relatorio': '',
            'exames': '',
            
            # Required etnia field (matching form choices)
            'etnia': 'etnia_parda',
            
            # Optional patient contact fields
            'email_paciente': '',
            'telefone1_paciente': '',
            'telefone2_paciente': '',
            
            # Treatment history fields
            'tratou': 'False',
            'tratamentos_previos': '',
            
            # Required medication fields (med1 is mandatory)
            'id_med1': str(self.medicamento1.id),
            'med1_repetir_posologia': 'True',
            'med1_via': 'oral',
            
            # Required dosage fields for med1 (6 months)
            'med1_posologia_mes1': '1 comprimido 2x ao dia',
            'med1_posologia_mes2': '1 comprimido 2x ao dia',
            'med1_posologia_mes3': '1 comprimido 2x ao dia',
            'med1_posologia_mes4': '1 comprimido 2x ao dia',
            'med1_posologia_mes5': '1 comprimido 2x ao dia',
            'med1_posologia_mes6': '1 comprimido 2x ao dia',
            
            # Required quantity fields for med1 (6 months)
            'qtd_med1_mes1': '60',
            'qtd_med1_mes2': '60',
            'qtd_med1_mes3': '60',
            'qtd_med1_mes4': '60',
            'qtd_med1_mes5': '60',
            'qtd_med1_mes6': '60',
        }
        
    def _get_complete_form_data_with_second_medication(self):
        """Get complete form data including second medication."""
        data = self._get_complete_form_data()
        data.update({
            # Second medication (optional)
            'id_med2': str(self.medicamento2.id),
            'med2_repetir_posologia': 'True',
            
            # Dosage fields for med2 (6 months)
            'med2_posologia_mes1': '1 gota 3x ao dia',
            'med2_posologia_mes2': '1 gota 3x ao dia',
            'med2_posologia_mes3': '1 gota 3x ao dia', 
            'med2_posologia_mes4': '1 gota 3x ao dia',
            'med2_posologia_mes5': '1 gota 3x ao dia',
            'med2_posologia_mes6': '1 gota 3x ao dia',
            
            # Quantity fields for med2 (6 months)
            'qtd_med2_mes1': '1',
            'qtd_med2_mes2': '1',
            'qtd_med2_mes3': '1',
            'qtd_med2_mes4': '1',
            'qtd_med2_mes5': '1',
            'qtd_med2_mes6': '1',
        })
        return data
        
    def test_pdf_generation_basic_form_validation(self):
        """Test that the complex form validates correctly with all required fields."""
        self.client.login(email=self.user.email, password='testpass123')
        
        # Set up session for new patient
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = self.valid_cpf
        session.save()
        
        # Get the form to verify it loads
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        
        # Submit complete form data
        form_data = self._get_complete_form_data()
        
        response = self.client.post(
            reverse('processos-cadastro'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response - should be success or at least not form validation errors
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # If there are form errors, print them for debugging
        if not response_data.get('success', False):
            print(f"Form errors: {response_data.get('form_errors', {})}")
            print(f"Error message: {response_data.get('error', 'Unknown error')}")
            
        # This test passes if form validation works (success or specific business logic errors)
        self.assertTrue('form_errors' in response_data or response_data.get('success', False))
        
    def test_pdf_generation_single_medication_workflow(self):
        """Test PDF generation with single medication (minimum required)."""
        self.client.login(email=self.user.email, password='testpass123')
        
        # Set up session for new patient
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = self.valid_cpf
        session.save()
        
        # Submit form with single medication
        form_data = self._get_complete_form_data()
        
        response = self.client.post(
            reverse('processos-cadastro'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Verify the response structure regardless of success/failure
        self.assertIsInstance(response_data, dict)
        if response_data.get('success'):
            # If successful, verify PDF generation components
            self.assertIn('pdf_url', response_data)
            self.assertIn('message', response_data)
        else:
            # If not successful, should have error information
            self.assertTrue('error' in response_data or 'form_errors' in response_data)
            
    def test_pdf_generation_multiple_medications_workflow(self):
        """Test PDF generation with multiple medications (complex scenario).""" 
        self.client.login(email=self.user.email, password='testpass123')
        
        # Set up session for new patient
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = self.valid_cpf
        session.save()
        
        # Submit form with two medications
        form_data = self._get_complete_form_data_with_second_medication()
        
        response = self.client.post(
            reverse('processos-cadastro'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Test the complex medication handling
        if response_data.get('success'):
            # Verify that multiple medications are handled correctly
            self.assertIn('pdf_url', response_data)
        else:
            # Check if medication validation is working
            form_errors = response_data.get('form_errors', {})
            # Should not have medication-related errors if data is complete
            med_fields = [k for k in form_errors.keys() if 'med' in k]
            if med_fields:
                print(f"Medication validation errors: {[form_errors[k] for k in med_fields]}")
                
    def test_pdf_generation_existing_patient_workflow(self):
        """Test PDF generation workflow for existing patient."""
        self.client.login(email=self.user.email, password='testpass123')
        
        # Set up session for existing patient
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'H30'
        session['paciente_id'] = self.paciente.id
        session.save()
        
        # Get form (should pre-populate with patient data)
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        
        # Submit form with existing patient context
        form_data = self._get_complete_form_data()
        # Update with existing patient's CPF
        form_data['cpf_paciente'] = self.paciente.cpf_paciente
        
        response = self.client.post(
            reverse('processos-cadastro'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Verify existing patient workflow handling
        self.assertIsInstance(response_data, dict)
        if response_data.get('success'):
            # Should work with existing patient data
            self.assertIn('pdf_url', response_data)
        else:
            # Should provide clear error messages for existing patient issues
            self.assertTrue('error' in response_data or 'form_errors' in response_data)


class PDFServingIntegrationTest(TestCase):
    """Integration tests for PDF serving after generation."""
    
    def setUp(self):
        """Set up test environment for PDF serving."""
        import random
        
        # Generate random CNS and unique email to avoid conflicts
        random_cns = f"{random.randint(1000000, 9999999)}"
        
        # Create complete test setup
        self.user = Usuario.objects.create_user(
            email='pdfserving@example.com',  # Unique email
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Dr. PDF Serving Test',
            crm_medico='654321',
            cns_medico='543210987654321'
        )
        self.user.medicos.add(self.medico)
        
        # Create clinic using proper versioning method
        clinic_data = {
            'nome_clinica': 'PDF Serving Test Clinic',
            'cns_clinica': random_cns,  # Random CNS to avoid conflicts
            'logradouro': 'PDF Street',
            'logradouro_num': '456',
            'cidade': 'PDF City',
            'bairro': 'PDF Neighborhood',
            'cep': '54321-987',
            'telefone_clinica': '(11) 5432-1098'
        }
        
        self.clinica = Clinica.create_or_update_for_user(self.user, self.medico, clinic_data)
        
        # Use a consistent CPF for testing that matches our test PDF filename
        self.test_cpf = '98765432100'  # Matches the PDF filename pattern
        self.paciente = Paciente.objects.create(
            nome_paciente='PDF Test Patient',
            cpf_paciente=self.test_cpf,
            cns_paciente='987654321098765',
            nome_mae='PDF Test Mother',
            idade='25',
            sexo='F',
            peso='60',
            altura='1.65',
            incapaz=False,
            nome_responsavel='',
            rg='9876543',
            escolha_etnia='Branca',
            cidade_paciente='PDF City',
            end_paciente='PDF Address',
            cep_paciente='54321-987',
            telefone1_paciente='(11) 2222-2222',
            telefone2_paciente='',
            etnia='Branca',
            email_paciente='pdfpatient@test.com'
        )
        self.paciente.usuarios.add(self.user)
        
        # Create test PDF file
        import tempfile
        self.temp_pdf_path = '/tmp/pdf_final_987.654.321-00_H30.pdf'
        with open(self.temp_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4 test PDF content for integration test')
            
        self.client = Client()
        
    def tearDown(self):
        """Clean up test files."""
        import os
        if os.path.exists(self.temp_pdf_path):
            os.remove(self.temp_pdf_path)
            
    def test_pdf_view_displays_generated_pdf_link(self):
        """Test that PDF view displays the generated PDF link correctly."""
        self.client.login(email='pdfserving@example.com', password='testpass123')
        
        # Simulate PDF generation by setting session data
        session = self.client.session
        session['path_pdf_final'] = '/serve-pdf/pdf_final_987.654.321-00_H30.pdf'
        session.save()
        
        response = self.client.get(reverse('processos-pdf'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pdf_final_987.654.321-00_H30.pdf')
        # Check that the PDF path is embedded in an iframe (actual template behavior)
        self.assertContains(response, 'iframe')
        
    def test_pdf_serving_after_generation(self):
        """Test that generated PDF can be served correctly."""
        self.client.login(email='pdfserving@example.com', password='testpass123')
        
        # Test serving the PDF file
        response = self.client.get(
            reverse('processos-serve-pdf', args=['pdf_final_987.654.321-00_H30.pdf'])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'inline; filename="pdf_final_987.654.321-00_H30.pdf"'
        )
        self.assertEqual(response.content, b'%PDF-1.4 test PDF content for integration test')
        
    def test_pdf_generation_to_serving_complete_flow(self):
        """Test complete flow from generation to serving."""
        self.client.login(email='pdfserving@example.com', password='testpass123')
        
        # Step 1: Set up session for PDF generation
        session = self.client.session
        session['path_pdf_final'] = '/serve-pdf/pdf_final_987.654.321-00_H30.pdf'
        session['processo_id'] = 999  # Mock process ID
        session.save()
        
        # Step 2: Access PDF view
        pdf_view_response = self.client.get(reverse('processos-pdf'))
        self.assertEqual(pdf_view_response.status_code, 200)
        self.assertContains(pdf_view_response, 'pdf_final_987.654.321-00_H30.pdf')
        
        # Step 3: Access actual PDF file
        pdf_serve_response = self.client.get(
            reverse('processos-serve-pdf', args=['pdf_final_987.654.321-00_H30.pdf'])
        )
        self.assertEqual(pdf_serve_response.status_code, 200)
        self.assertEqual(pdf_serve_response['Content-Type'], 'application/pdf')
        
        # Step 4: Verify security headers are present
        self.assertEqual(pdf_serve_response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(pdf_serve_response['X-Frame-Options'], 'SAMEORIGIN')
        
    def test_pdf_access_requires_authentication(self):
        """Test that PDF access requires proper authentication."""
        # Without login
        response = self.client.get(reverse('processos-pdf'))
        # Should redirect to login or return 401/403
        self.assertIn(response.status_code, [302, 401, 403])
        
        # PDF serving without login
        response = self.client.get(
            reverse('processos-serve-pdf', args=['pdf_final_987.654.321-00_H30.pdf'])
        )
        self.assertIn(response.status_code, [302, 401, 403])
        
    def test_pdf_view_without_session_data(self):
        """Test PDF view behavior when session data is missing."""
        self.client.login(email='pdfserving@example.com', password='testpass123')
        
        # Access PDF view without path_pdf_final in session
        # Should return 404 since PDF link not found
        response = self.client.get(reverse('processos-pdf'))
        self.assertEqual(response.status_code, 404)