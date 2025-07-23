"""
Base test classes for Django tests to reduce repetition across test files.
Provides common setup for users, medical professionals, clinics, and patients.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from pacientes.models import Paciente
from processos.models import Doenca, Medicamento, Processo
import datetime

Usuario = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup for AutoCusto tests."""
    
    def setUp(self):
        """Common setup for all tests."""
        super().setUp()
        self.client = Client()
        
    def create_test_user(self, email="test@example.com", password="testpass123"):
        """Create a test user with the given credentials."""
        return Usuario.objects.create_user(
            email=email,
            password=password,
            nome_usuario="Test User"
        )
    
    def create_test_medico(self, user=None, crm="123456", cns="111111111111111"):
        """Create a test medical professional."""
        if not user:
            user = self.create_test_user()
        
        return Medico.objects.create(
            usuario=user,
            nome_medico="Dr. Test Silva",
            crm_medico=crm,
            cns_medico=cns,
            uf_medico="SP",
            cidade_medico="São Paulo",
            status_aprovacao_medico=True
        )
    
    def create_test_clinica(self, cnes="1234567"):
        """Create a test clinic."""
        return Clinica.objects.create(
            nome_clinica="Test Clinic",
            cnpj_clinica="12345678901234",
            cnes_clinica=cnes,
            endereco_clinica="Test Street, 123",
            cidade_clinica="São Paulo",
            uf_clinica="SP",
            cep_clinica="12345678",
            telefone_clinica="1134567890"
        )
    
    def create_test_emissor(self, medico=None, clinica=None):
        """Create a test emissor (doctor-clinic relationship)."""
        if not medico:
            medico = self.create_test_medico()
        if not clinica:
            clinica = self.create_test_clinica()
            
        return Emissor.objects.create(
            medico=medico,
            clinica=clinica
        )
    
    def create_test_paciente(self, cpf="12345678901"):
        """Create a test patient."""
        return Paciente.objects.create(
            nome_paciente="Test Patient",
            cpf_paciente=cpf,
            data_nascimento_paciente=datetime.date(1990, 1, 1),
            sexo_paciente="M",
            endereco_paciente="Test Address",
            cidade_paciente="São Paulo",
            uf_paciente="SP",
            cep_paciente="12345678",
            telefone_paciente="1198765432"
        )
    
    def create_test_doenca(self, nome="Test Disease", codigo="T01"):
        """Create a test disease."""
        return Doenca.objects.create(
            nome_doenca=nome,
            codigo_doenca=codigo
        )
    
    def create_test_medicamento(self, nome="Test Medicine"):
        """Create a test medication."""
        return Medicamento.objects.create(
            nome_medicamento=nome,
            forma_farmaceutica="Comprimido",
            concentracao="100mg",
            laboratorio="Test Lab"
        )
    
    def create_test_processo(self, user=None, paciente=None, doenca=None):
        """Create a test process with all relationships."""
        if not user:
            user = self.create_test_user()
        if not paciente:
            paciente = self.create_test_paciente()
        if not doenca:
            doenca = self.create_test_doenca()
            
        medico = self.create_test_medico(user=user)
        clinica = self.create_test_clinica()
        emissor = self.create_test_emissor(medico=medico, clinica=clinica)
        
        return Processo.objects.create(
            usuario=user,
            paciente=paciente,
            doenca=doenca,
            data_cadastro=datetime.date.today(),
            emissor=emissor
        )
    
    def login_test_user(self, user=None, password="testpass123"):
        """Login a test user."""
        if not user:
            user = self.create_test_user()
        self.client.login(email=user.email, password=password)
        return user


class AuthenticatedTestCase(BaseTestCase):
    """Base test case with pre-authenticated user."""
    
    def setUp(self):
        """Setup with authenticated user."""
        super().setUp()
        self.user = self.create_test_user()
        self.login_test_user(self.user)


class MedicoTestCase(AuthenticatedTestCase):
    """Base test case with authenticated medical professional."""
    
    def setUp(self):
        """Setup with authenticated medico."""
        super().setUp()
        self.medico = self.create_test_medico(user=self.user)


class CompleteSetupTestCase(MedicoTestCase):
    """Base test case with complete setup including clinic and emissor."""
    
    def setUp(self):
        """Setup with complete medical infrastructure."""
        super().setUp()
        self.clinica = self.create_test_clinica()
        self.emissor = self.create_test_emissor(
            medico=self.medico, 
            clinica=self.clinica
        )