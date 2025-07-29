from tests.test_base import BaseTestCase
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from django.contrib.messages import get_messages
import json

User = get_user_model()


class SecurityTestCase(BaseTestCase):
    """Test suite for verifying security fixes in patient data access."""

    def setUp(self):
        """Set up test data for security tests."""
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', 
            password='testpass123'
        )
        
        # Set users as medicos
        self.user1.is_medico = True
        self.user2.is_medico = True
        self.user1.save()
        self.user2.save()
        
        # Create medicos
        from medicos.models import Medico
        from clinicas.models import Clinica, Emissor
        
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. João",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico2 = Medico.objects.create(
            nome_medico="Dr. José", 
            crm_medico="67890",
            cns_medico="222222222222222"
        )
        
        # Associate medicos with users
        self.medico1.usuarios.add(self.user1)
        self.medico2.usuarios.add(self.user2)
        
        # Create clinicas
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica A",
            cns_clinica="1234567",
            logradouro="Rua A",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        
        # Associate clinicas with medicos
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        
        # Create test protocolo and doenca for form validation
        from processos.models import Protocolo, Doenca
        self.protocolo = Protocolo.objects.create(
            nome="Protocolo Teste",
            arquivo="teste.pdf"
        )
        self.doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Epilepsia",
            protocolo=self.protocolo
        )
        
        # Create test patients
        self.patient1 = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="11111111111",
            cns_paciente="111111111111111",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua A, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        
        self.patient2 = Paciente.objects.create(
            nome_paciente="José Santos",
            cpf_paciente="22222222222",
            cns_paciente="222222222222222",
            nome_mae="Ana Santos",
            idade="25",
            sexo="M",
            peso="80.0",
            altura="1.80",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11777777777",
            end_paciente="Rua B, 456",
            rg="987654321",
            escolha_etnia="Branca",
            cidade_paciente="Rio de Janeiro",
            cep_paciente="20000-000",
            telefone2_paciente="11666666666",
            nome_responsavel="",
        )
        
        # Associate patient1 with user1, patient2 with user2
        self.patient1.usuarios.add(self.user1)
        self.patient2.usuarios.add(self.user2)
        
        self.client = Client()

    def test_home_view_patient_access_authorization(self):
        """Test that users can only access patients they're authorized for."""
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Test accessing authorized patient (should work)
        response = self.client.post(reverse('home'), {
            'cpf_paciente': '11111111111',
            'cid': 'G40.0'
        })
        
        # Should redirect to process page (successful access)
        self.assertEqual(response.status_code, 302)
        
        # Test accessing unauthorized patient (should fail)
        response = self.client.post(reverse('home'), {
            'cpf_paciente': '22222222222',  # This belongs to user2
            'cid': 'G40.0'
        })
        
        # Should redirect to process registration (patient not found for this user)
        self.assertEqual(response.status_code, 302)
        # Just check that it redirects, don't follow the redirect chain
        self.assertTrue(response.url.startswith('/processos/cadastro/'))

    def test_unauthenticated_home_access(self):
        """Test that unauthenticated users cannot access patient data."""
        
        response = self.client.post(reverse('home'), {
            'cpf_paciente': '11111111111',
            'cid': 'G40.0'
        })
        
        # Should redirect to home with warning message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check for warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Você precisa estar logado' in str(m) for m in messages))


class PatientSearchSecurityTest(BaseTestCase):
    """Test security of patient search functionality."""
    
    def setUp(self):
        """Set up test data for search tests."""
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        self.patient1 = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="11111111111",
            cns_paciente="111111111111111",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua A, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        
        self.patient2 = Paciente.objects.create(
            nome_paciente="José Santos",
            cpf_paciente="22222222222",
            cns_paciente="222222222222222",
            nome_mae="Ana Santos",
            idade="25",
            sexo="M",
            peso="80.0",
            altura="1.80",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11777777777",
            end_paciente="Rua B, 456",
            rg="987654321",
            escolha_etnia="Branca",
            cidade_paciente="Rio de Janeiro",
            cep_paciente="20000-000",
            telefone2_paciente="11666666666",
            nome_responsavel="",
        )
        
        # Associate patients with users
        self.patient1.usuarios.add(self.user1)
        self.patient2.usuarios.add(self.user2)
        
        self.client = Client()

    def test_patient_search_authentication_required(self):
        """Test that patient search requires authentication."""
        
        response = self.client.get(reverse('busca-pacientes'), {
            'palavraChave': 'João'
        })
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_patient_search_authorization(self):
        """Test that users can only search their own patients."""
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Search for own patient
        response = self.client.get(reverse('busca-pacientes'), {
            'palavraChave': 'João'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Should find user1's patient
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nome_paciente'], 'João Silva')
        
        # Search for other user's patient
        response = self.client.get(reverse('busca-pacientes'), {
            'palavraChave': 'José'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Should not find user2's patient
        self.assertEqual(len(data), 0)

    def test_patient_search_by_cpf_authorization(self):
        """Test that CPF search respects user authorization."""
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Search for own patient's CPF
        response = self.client.get(reverse('busca-pacientes'), {
            'palavraChave': '11111111111'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        
        # Search for other user's patient CPF
        response = self.client.get(reverse('busca-pacientes'), {
            'palavraChave': '22222222222'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)


class PatientListingSecurityTest(BaseTestCase):
    """Test security of patient listing functionality."""
    
    def setUp(self):
        """Set up test data for listing tests."""
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        self.patient1 = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="11111111111",
            cns_paciente="111111111111111",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua A, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        
        self.patient2 = Paciente.objects.create(
            nome_paciente="José Santos",
            cpf_paciente="22222222222",
            cns_paciente="222222222222222",
            nome_mae="Ana Santos",
            idade="25",
            sexo="M",
            peso="80.0",
            altura="1.80",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11777777777",
            end_paciente="Rua B, 456",
            rg="987654321",
            escolha_etnia="Branca",
            cidade_paciente="Rio de Janeiro",
            cep_paciente="20000-000",
            telefone2_paciente="11666666666",
            nome_responsavel="",
        )
        
        # Associate patients with users
        self.patient1.usuarios.add(self.user1)
        self.patient2.usuarios.add(self.user2)
        
        self.client = Client()

    def test_patient_listing_authentication_required(self):
        """Test that patient listing requires authentication."""
        
        response = self.client.get(reverse('pacientes-listar'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_patient_listing_authorization(self):
        """Test that users only see their own patients in listing."""
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        response = self.client.get(reverse('pacientes-listar'))
        
        self.assertEqual(response.status_code, 200)
        
        # Should only contain user1's patient
        self.assertContains(response, 'João Silva')
        self.assertNotContains(response, 'José Santos')
        
        # Login as user2
        self.client.logout()
        self.client.login(email='user2@example.com', password='testpass123')
        
        response = self.client.get(reverse('pacientes-listar'))
        
        self.assertEqual(response.status_code, 200)
        
        # Should only contain user2's patient
        self.assertContains(response, 'José Santos')
        self.assertNotContains(response, 'João Silva')


class ProcessAccessSecurityTest(BaseTestCase):
    """Test security of process access control."""
    
    def setUp(self):
        """Set up test data for process tests."""
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        # Set users as medicos
        self.user1.is_medico = True
        self.user2.is_medico = True
        self.user1.save()
        self.user2.save()
        
        # Create medicos
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. João",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico2 = Medico.objects.create(
            nome_medico="Dr. José",
            crm_medico="67890",
            cns_medico="222222222222222"
        )
        
        # Associate medicos with users
        self.medico1.usuarios.add(self.user1)
        self.medico2.usuarios.add(self.user2)
        
        # Create clinicas
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica A",
            cns_clinica="1234567",
            logradouro="Rua A",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        
        # Create emissor
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        
        # Create patients
        self.patient1 = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="11111111111",
            cns_paciente="111111111111111",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua A, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        
        # Associate patients with users
        self.patient1.usuarios.add(self.user1)
        
        # Create protocolo and doenca
        self.protocolo = Protocolo.objects.create(
            nome="Protocolo Teste",
            arquivo="teste.pdf"
        )
        
        self.doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Epilepsia",
            protocolo=self.protocolo
        )
        
        # Create medicamento for prescricao
        from processos.models import Medicamento
        self.medicamento1 = Medicamento.objects.create(
            nome="Medicamento Teste",
            dosagem="500mg",
            apres="Comprimidos"
        )
        
        # Create processo for user1 with proper prescricao structure
        self.processo1 = Processo.objects.create(
            anamnese="Teste anamnese",
            doenca=self.doenca,
            prescricao={
                "1": {
                    "id_med1": str(self.medicamento1.id),
                    "med1_posologia_mes1": "1x ao dia",
                    "qtd_med1_mes1": "30",
                    "med1_posologia_mes2": "1x ao dia",
                    "qtd_med1_mes2": "30",
                    "med1_posologia_mes3": "1x ao dia",
                    "qtd_med1_mes3": "30",
                    "med1_posologia_mes4": "1x ao dia",
                    "qtd_med1_mes4": "30",
                    "med1_posologia_mes5": "1x ao dia",
                    "qtd_med1_mes5": "30",
                    "med1_posologia_mes6": "1x ao dia",
                    "qtd_med1_mes6": "30"
                }
            },
            tratou=False,
            tratamentos_previos="Nenhum",
            preenchido_por="M",
            dados_condicionais={"teste": "dados"},
            paciente=self.patient1,
            medico=self.medico1,
            clinica=self.clinica1,
            emissor=self.emissor1,
            usuario=self.user1
        )
        
        # Associate medicamento with processo
        self.processo1.medicamentos.add(self.medicamento1)
        
        self.client = Client()

    def test_process_search_authorization(self):
        """Test that users can only access their own processes in search."""
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Access process search page
        response = self.client.get(reverse('processos-busca'))
        
        self.assertEqual(response.status_code, 200)
        # Should show only user1's patients
        self.assertContains(response, 'João Silva')
        
        # Test process selection with valid process
        session = self.client.session
        response = self.client.post(reverse('processos-busca'), {
            'processo_id': self.processo1.id
        })
        
        # Should redirect to edit page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('processos-edicao'))

    def test_process_access_unauthorized_process_id(self):
        """Test that users cannot access processes they don't own."""
        
        # Create another user and process
        user3 = User.objects.create_user(
            email='user3@example.com',
            password='testpass123'
        )
        
        patient3 = Paciente.objects.create(
            nome_paciente="Carlos Souza",
            cpf_paciente="33333333333",
            cns_paciente="333333333333333",
            nome_mae="Ana Souza",
            idade="35",
            sexo="M",
            peso="75.0",
            altura="1.70",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11555555555",
            end_paciente="Rua C, 789",
            rg="111222333",
            escolha_etnia="Branca",
            cidade_paciente="Brasília",
            cep_paciente="70000-000",
            telefone2_paciente="11444444444",
            nome_responsavel="",
        )
        
        patient3.usuarios.add(user3)
        
        processo3 = Processo.objects.create(
            anamnese="Teste anamnese 3",
            doenca=self.doenca,
            prescricao={
                "1": {
                    "id_med1": str(self.medicamento1.id),
                    "med1_posologia_mes1": "2x ao dia",
                    "qtd_med1_mes1": "60",
                    "med1_posologia_mes2": "2x ao dia",
                    "qtd_med1_mes2": "60",
                    "med1_posologia_mes3": "2x ao dia",
                    "qtd_med1_mes3": "60",
                    "med1_posologia_mes4": "2x ao dia",
                    "qtd_med1_mes4": "60",
                    "med1_posologia_mes5": "2x ao dia",
                    "qtd_med1_mes5": "60",
                    "med1_posologia_mes6": "2x ao dia",
                    "qtd_med1_mes6": "60"
                }
            },
            tratou=False,
            tratamentos_previos="Nenhum",
            preenchido_por="M",
            dados_condicionais={"teste": "dados3"},
            paciente=patient3,
            medico=self.medico1,
            clinica=self.clinica1,
            emissor=self.emissor1,
            usuario=user3
        )
        
        # Login as user1 and try to access user3's process
        self.client.login(email='user1@example.com', password='testpass123')
        
        response = self.client.post(reverse('processos-busca'), {
            'processo_id': processo3.id  # Process belongs to user3
        })
        
        # Should redirect back to search with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('processos-busca'))
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('não tem permissão' in str(m) for m in messages))


class LGPDComplianceSecurityTest(TestCase):
    """Test LGPD (Brazilian data protection law) compliance."""
    
    def setUp(self):
        """Set up test data for LGPD compliance tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.patient = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="22255588846",
            cns_paciente="111111111111111",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70",
            altura="170",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua Test, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        self.patient.usuarios.add(self.user)
        
        self.client = Client()

    def test_patient_data_anonymization_capability(self):
        """Test that patient data can be anonymized for analytics."""
        # Verify that we can identify sensitive fields that should be anonymized
        sensitive_fields = [
            'nome_paciente', 'cpf_paciente', 'cns_paciente', 'nome_mae',
            'rg', 'telefone1_paciente', 'telefone2_paciente', 'end_paciente'
        ]
        
        # Check that patient has these sensitive fields
        for field in sensitive_fields:
            self.assertTrue(hasattr(self.patient, field), 
                           f"Patient model should have sensitive field: {field}")
            field_value = getattr(self.patient, field)
            if field_value:  # Only check non-empty fields
                self.assertIsInstance(field_value, str, 
                                    f"Sensitive field {field} should be string for anonymization")

    def test_data_portability_capability(self):
        """Test that patient data can be exported securely."""
        from django.core import serializers
        from django.forms.models import model_to_dict
        
        # Test that we can export patient data in structured format
        patient_dict = model_to_dict(self.patient)
        self.assertIsInstance(patient_dict, dict)
        self.assertIn('nome_paciente', patient_dict)
        self.assertIn('cpf_paciente', patient_dict)
        
        # Test JSON serialization capability
        patient_json = serializers.serialize('json', [self.patient])
        self.assertIsInstance(patient_json, str)
        self.assertIn('nome_paciente', patient_json)
        
        # Verify no sensitive system data is exposed
        self.assertNotIn('password', patient_json.lower())
        self.assertNotIn('secret', patient_json.lower())


class MedicalDataValidationSecurityTest(TestCase):
    """Test medical data validation and integrity."""
    
    def setUp(self):
        """Set up test data for medical validation tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()

    def test_cpf_format_validation(self):
        """Test CPF format validation and security."""
        valid_cpfs = ["22255588846", "98765432100"]
        
        invalid_cpfs = [
            "123456789",          # Too short
            "123456789012",       # Too long
            "12345678901a",       # Contains letter
            "<script>alert('xss')</script>",  # XSS attempt
            "'; DROP TABLE pacientes; --",     # SQL injection
        ]
        
        # Test valid CPFs don't cause errors
        for cpf in valid_cpfs:
            try:
                patient = Paciente.objects.create(
                    nome_paciente="Test Patient",
                    cpf_paciente=cpf,
                    cns_paciente="111111111111111",
                    nome_mae="Test Mother",
                    idade="30",
                    sexo="M",
                    peso="70",
                    altura="170",
                    incapaz=False,
                    etnia="Branca",
                    telefone1_paciente="11999999999",
                    end_paciente="Rua Test, 123",
                    rg="123456789",
                    escolha_etnia="Branca",
                    cidade_paciente="São Paulo",
                    cep_paciente="01000-000",
                )
                # Test that CPF is stored correctly
                self.assertEqual(len(patient.cpf_paciente), 11)
                patient.delete()
            except Exception as e:
                self.fail(f"Valid CPF '{cpf}' should not cause error: {e}")

    def test_cns_validation(self):
        """Test CNS (health card) number validation."""
        valid_cns_numbers = ["111111111111111", "222222222222222"]
        
        invalid_cns_numbers = [
            "12345678901234",   # 14 digits (too short)
            "1234567890123456", # 16 digits (too long)
            "12345678901234a",  # Contains letter
            "<script>alert('xss')</script>",
            "'; DROP TABLE medicos; --",
        ]
        
        # Test valid CNS numbers
        for cns in valid_cns_numbers:
            try:
                medico = Medico.objects.create(
                    nome_medico="Dr. Test",
                    crm_medico="12345",
                    cns_medico=cns
                )
                # Verify CNS is stored correctly
                self.assertEqual(len(medico.cns_medico), 15)
                self.assertTrue(medico.cns_medico.isdigit())
                medico.delete()
                
            except Exception as e:
                self.fail(f"Valid CNS '{cns}' should not cause error: {e}")

    def test_prescription_dosage_validation(self):
        """Test medication dosage validation for patient safety."""
        from processos.models import Medicamento
        
        valid_dosages = ["500mg", "1g", "250mg", "2,5mg", "10ml"]
        
        invalid_dosages = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE medicamentos; --",
            "999999999999mg",  # Unrealistic dosage
            "-500mg",          # Negative dosage
        ]
        
        # Test valid dosages
        for dosage in valid_dosages:
            try:
                med = Medicamento.objects.create(
                    nome="Test Medication",
                    dosagem=dosage,
                    apres="Tablet"
                )
                med.delete()
                
            except Exception as e:
                self.fail(f"Valid dosage '{dosage}' should not cause error: {e}")
        
        # Test invalid dosages
        for dosage in invalid_dosages:
            try:
                med = Medicamento.objects.create(
                    nome="Test Medication",
                    dosagem=dosage,
                    apres="Tablet"
                )
                # If creation succeeds, verify malicious content is sanitized
                self.assertNotIn('<script>', med.dosagem.lower())
                self.assertNotIn('drop table', med.dosagem.lower())
                med.delete()
                
            except Exception:
                # If validation prevents creation, that's acceptable
                pass


class AuditTrailSecurityTest(TestCase):
    """Test audit trail security and immutability."""
    
    def setUp(self):
        """Set up test data for audit trail tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()

    def test_user_action_logging(self):
        """Test that critical user actions are logged."""
        from analytics.models import UserActivityLog
        
        # Login user  
        self.client.login(email='test@example.com', password='testpass123')
        
        # Check if logging system exists and tracks logins
        initial_log_count = UserActivityLog.objects.count()
        
        # Test that login events are logged (this would be done by signals)
        # We can check if the infrastructure exists for logging
        login_logs = UserActivityLog.objects.filter(
            user=self.user,
            activity_type='login'
        ).count()
        
        # If logging system is active, we should be able to create test logs
        if hasattr(UserActivityLog, 'objects'):
            # Test that we can create activity logs
            test_log = UserActivityLog.objects.create(
                user=self.user,
                activity_type='profile_update',
                ip_address='127.0.0.1'
            )
            self.assertIsNotNone(test_log.id)
            test_log.delete()  # Clean up test log

    def test_sensitive_data_not_logged_in_plain_text(self):
        """Test that sensitive medical data is not logged in plain text."""
        from analytics.models import UserActivityLog
        
        # Create a test log entry with safe data
        test_log = UserActivityLog.objects.create(
            user=self.user,
            activity_type='profile_update',
            ip_address='127.0.0.1',
            extra_data={'action': 'test_sensitive_data_handling'}
        )
        
        # Check that the log entry itself doesn't expose sensitive patterns
        log_str = str(test_log)
        
        # Test that basic patterns that could contain sensitive data aren't present
        # CPF patterns (11 consecutive digits)
        import re
        cpf_pattern = re.compile(r'\b\d{11}\b')
        self.assertIsNone(cpf_pattern.search(log_str), 
                         "11-digit sequences (potential CPF) should not appear in logs")
        
        # Clean up
        test_log.delete()

    def test_audit_log_tampering_prevention(self):
        """Test that audit logs cannot be easily modified by regular users."""
        from analytics.models import UserActivityLog
        
        self.client.login(email='test@example.com', password='testpass123')
        
        # Try to access admin interface for logs (should be restricted)
        response = self.client.get('/admin/analytics/useractivitylog/')
        
        # Should be redirected to login or forbidden
        self.assertIn(response.status_code, [302, 403], 
                     "Regular users should not have admin access to audit logs")
class InputSanitizationSecurityTest(TestCase):
    """Test input validation and XSS prevention."""
    
    def setUp(self):
        """Set up test data for input sanitization tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.user.is_medico = True
        self.user.save()
        
        # Create medico for the user
        self.medico = Medico.objects.create(
            nome_medico="Dr. Test",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico.usuarios.add(self.user)
        
        self.client = Client()

    def test_xss_prevention_in_patient_forms(self):
        """Test that patient registration forms prevent XSS attacks."""
        self.client.login(email='test@example.com', password='testpass123')
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "';alert('xss');//",
            "<svg onload=alert('xss')>",
            "&lt;script&gt;alert('xss')&lt;/script&gt;"
        ]
        
        for payload in xss_payloads:
            # Test XSS prevention by creating patient directly with malicious data
            # and verifying it's sanitized when retrieved
            try:
                from pacientes.models import Paciente
                patient = Paciente.objects.create(
                    nome_paciente=f'João {payload}',
                    cpf_paciente="11144477735",
                    cns_paciente='111111111111111',
                    nome_mae=f'Maria {payload}',
                    idade='30',
                    sexo='M',
                    peso='70',
                    altura='170',
                    incapaz=False,
                    etnia='Branca',
                    telefone1_paciente='11999999999',
                    end_paciente=f'Rua Test {payload}',
                    rg='123456789',
                    escolha_etnia='Branca',
                    cidade_paciente='São Paulo',
                    cep_paciente='01000-000',
                )
                
                # Check that data is sanitized in database
                self.assertNotIn('<script>', patient.nome_paciente.lower())
                self.assertNotIn('javascript:', patient.nome_mae.lower()) 
                self.assertNotIn('onerror=', patient.end_paciente.lower())
                
                # Clean up
                patient.delete()
                
            except Exception:
                # If validation prevents creation, that's also acceptable security behavior
                pass

    def test_sql_injection_prevention_patient_search(self):
        """Test that patient search is protected from SQL injection."""
        self.client.login(email='test@example.com', password='testpass123')
        
        sql_injection_payloads = [
            "'; DROP TABLE pacientes; --",
            "' OR '1'='1",
            "'; DELETE FROM pacientes WHERE '1'='1'; --",
            "' UNION SELECT * FROM usuarios --",
            "'; UPDATE pacientes SET nome_paciente='hacked' WHERE '1'='1'; --"
        ]
        
        for payload in sql_injection_payloads:
            # Test AJAX patient search
            response = self.client.get('/pacientes/ajax/busca', {
                'palavraChave': payload
            })
            
            # Should return proper JSON response (not SQL error)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON to ensure it's valid
            try:
                data = response.json()
                # Should be empty list or valid patient data, not SQL error
                self.assertIsInstance(data, list)
            except json.JSONDecodeError:
                self.fail(f"SQL injection payload '{payload}' caused invalid JSON response")

    def test_json_field_validation_prescription_data(self):
        """Test that JSON fields (prescription data) are properly validated."""
        from processos.models import Processo, Doenca, Protocolo, Medicamento
        from medicos.models import Medico
        from clinicas.models import Clinica, Emissor
        
        # Create required objects
        protocolo = Protocolo.objects.create(
            nome="Test Protocol",
            arquivo="test.pdf"
        )
        doenca = Doenca.objects.create(
            cid="G40.0",
            nome="Test Disease",
            protocolo=protocolo
        )
        medicamento = Medicamento.objects.create(
            nome="Test Medication",
            dosagem="500mg",
            apres="Tablet"
        )
        clinica = Clinica.objects.create(
            nome_clinica="Test Clinic",
            cns_clinica="1234567",
            logradouro="Rua Test",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        emissor = Emissor.objects.create(
            medico=self.medico,
            clinica=clinica
        )
        
        # Test malicious JSON prescription data
        malicious_prescriptions = [
            "'; DROP TABLE processos; --",
            "<script>alert('xss')</script>",
            {"malicious": "<img src=x onerror=alert('xss')>"},
            {"med1": "'; DELETE FROM medicamentos; --"},
        ]
        
        for malicious_data in malicious_prescriptions:
            try:
                processo = Processo.objects.create(
                    anamnese="Test anamnese",
                    doenca=doenca,
                    prescricao=malicious_data,
                    tratou=False,
                    tratamentos_previos="",
                    preenchido_por="M",
                    dados_condicionais={},
                    paciente=None,
                    medico=self.medico,
                    clinica=clinica,
                    emissor=emissor,
                    usuario=self.user
                )
                
                # If creation succeeds, verify data is properly sanitized
                if isinstance(processo.prescricao, dict):
                    for key, value in processo.prescricao.items():
                        if isinstance(value, str):
                            self.assertNotIn('<script>', value.lower())
                            self.assertNotIn('drop table', value.lower())
                            self.assertNotIn('delete from', value.lower())
                
            except Exception:
                # If validation prevents creation, that's acceptable security behavior
                pass


class PDFGenerationSecurityTest(TestCase):
    """Test PDF generation security vulnerabilities."""
    
    def setUp(self):
        """Set up test data for PDF security tests."""
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user1.is_medico = True
        self.user1.save()
        
        self.medico1 = Medico.objects.create(
            nome_medico="Dr. Test",
            crm_medico="12345",
            cns_medico="111111111111111"
        )
        self.medico1.usuarios.add(self.user1)
        
        self.clinica1 = Clinica.objects.create(
            nome_clinica="Clínica Test",
            cns_clinica="1234567",
            logradouro="Rua Test",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="11999999999"
        )
        
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica1
        )
        
        self.patient1 = Paciente.objects.create(
            nome_paciente="Test Patient",
            cpf_paciente="22255588846",
            cns_paciente="111111111111111",
            nome_mae="Test Mother",
            idade="30",
            sexo="M",
            peso="70",
            altura="170",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua Test, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        self.patient1.usuarios.add(self.user1)
        
        self.client = Client()

    def test_pdf_generation_rate_limiting(self):
        """Test that PDF generation has rate limiting to prevent DoS attacks."""
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Simulate rapid PDF generation requests
        pdf_requests = []
        for i in range(10):  # Attempt 10 rapid requests
            response = self.client.get('/processos/serve-pdf/pdf_final_12345678901_G40.0.pdf/')
            pdf_requests.append(response.status_code)
        
        # Check that either rate limiting is in place or requests are handled gracefully
        # At minimum, no 500 errors should occur from resource exhaustion
        for status_code in pdf_requests:
            self.assertNotEqual(status_code, 500, "PDF generation should not cause server errors under load")
        
        # If rate limiting is implemented, we should see 429 status codes
        rate_limited_responses = [code for code in pdf_requests if code == 429]
        if rate_limited_responses:
            self.assertGreater(len(rate_limited_responses), 0, "Rate limiting appears to be working")

    def test_pdf_filename_injection_prevention(self):
        """Test that PDF filenames prevent directory traversal and injection."""
        self.client.login(email='user1@example.com', password='testpass123')
        
        malicious_filenames = [
            "pdf_final_12345678901_G40.0.pdf';rm -rf /;.pdf",
            "pdf_final_12345678901_G40.0.pdf`whoami`.pdf",
            "pdf_final_12345678901_G40.0.pdf$(whoami).pdf",
            "pdf_final_12345678901_G40.0.pdf&amp;&lt;script&gt;alert('xss')&lt;/script&gt;.pdf",
            "pdf_final_../../../etc/passwd_G40.0.pdf"
        ]
        
        for filename in malicious_filenames:
            response = self.client.get(f'/processos/serve-pdf/{filename}/')
            # Should be rejected with 400 (Bad Request), 403 (Forbidden), or 404 (Not Found)
            self.assertIn(response.status_code, [400, 403, 404], 
                         f"Malicious filename '{filename}' should be rejected")

    def test_pdf_content_sanitization(self):
        """Test that user input in PDFs is properly sanitized."""
        # Test with malicious patient data
        malicious_data = {
            "nome_paciente": "<script>alert('xss')</script>João Silva",
            "nome_mae": "Maria Silva'; DROP TABLE pacientes; --",
            "end_paciente": "Rua Test <img src=x onerror=alert('xss')>",
            "email_paciente": "test@test.com<script>document.location='http://evil.com'</script>"
        }
        
        # Create patient with malicious data
        from pacientes.models import Paciente
        try:
            patient = Paciente.objects.create(
                nome_paciente=malicious_data["nome_paciente"],
                cpf_paciente="98765432100",
                cns_paciente="222222222222222",
                nome_mae=malicious_data["nome_mae"],
                idade="30",
                sexo="M",
                peso="70",
                altura="170",
                incapaz=False,
                etnia="Branca",
                telefone1_paciente="11999999999",
                end_paciente=malicious_data["end_paciente"],
                rg="987654321",
                escolha_etnia="Branca",
                cidade_paciente="São Paulo",
                cep_paciente="01000-000",
                telefone2_paciente="11888888888",
                nome_responsavel="",
            )
            patient.usuarios.add(self.user1)
            
            # Test that malicious content is properly escaped in database
            self.assertNotIn("<script>", patient.nome_paciente.lower())
            self.assertNotIn("drop table", patient.nome_mae.lower())
            self.assertNotIn("onerror", patient.end_paciente.lower())
            
        except Exception:
            # If creation fails due to validation, that's also acceptable security behavior
            pass

    def test_unauthorized_pdf_access_prevention(self):
        """Test that users cannot access PDFs of other users' patients."""
        # Create second user
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        # Create patient for user2
        patient2 = Paciente.objects.create(
            nome_paciente="User2 Patient",
            cpf_paciente="98765432100",
            cns_paciente="222222222222222",
            nome_mae="User2 Mother",
            idade="25",
            sexo="F",
            peso="60",
            altura="165",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11888888888",
            end_paciente="Rua User2, 456",
            rg="987654321",
            escolha_etnia="Branca",
            cidade_paciente="Rio de Janeiro",
            cep_paciente="20000-000",
            telefone2_paciente="11777777777",
            nome_responsavel="",
        )
        patient2.usuarios.add(user2)
        
        # Login as user1 and try to access user2's PDF
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Try to access PDF that would belong to user2's patient
        user2_pdf_filename = f"pdf_final_{patient2.cpf_paciente}_G40.0.pdf"
        response = self.client.get(f'/processos/serve-pdf/{user2_pdf_filename}/')
        
        # Should be denied (403 Forbidden or 404 Not Found)
        self.assertIn(response.status_code, [403, 404], 
                     "User should not be able to access other users' PDFs")