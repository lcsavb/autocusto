from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from django.contrib.messages import get_messages
import json

User = get_user_model()


class SecurityTestCase(TestCase):
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


class PatientSearchSecurityTest(TestCase):
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


class PatientListingSecurityTest(TestCase):
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


class ProcessAccessSecurityTest(TestCase):
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

    def test_process_edit_authorization(self):
        """Test that process edit page validates ownership."""
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Set up session data as if coming from search
        session = self.client.session
        session['processo_id'] = self.processo1.id
        session['cid'] = self.doenca.cid
        session.save()
        
        # Access edit page with valid process
        response = self.client.get(reverse('processos-edicao'))
        
        self.assertEqual(response.status_code, 200)

    def test_process_edit_unauthorized_session_hijack(self):
        """Test that users cannot hijack sessions to access unauthorized processes."""
        
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
        
        # Login as user1
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Try to hijack session by setting another user's process ID
        session = self.client.session
        session['processo_id'] = processo3.id  # Process belongs to user3
        session['cid'] = self.doenca.cid
        session.save()
        
        # Try to access edit page
        response = self.client.get(reverse('processos-edicao'))
        
        # Should redirect back to search with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('processos-busca'))
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('não tem permissão' in str(m) for m in messages))