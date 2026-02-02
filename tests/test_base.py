"""
Centralized Test Base - Single source of truth for all test setup

This module provides:
1. Base test classes with proper isolation
2. Dynamic unique data generation to avoid constraint violations
3. Helper methods to create test objects
4. Common test data patterns

Use this instead of django_test_base.py or test_data_fixtures.py

RUNNING TESTS:
Always use --keepdb flag to avoid database recreation overhead:
  python manage.py test --keepdb
  python manage.py test tests.integration.api.test_process_views --keepdb
"""

import uuid
import random
import time
from datetime import date, datetime
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from cpf_generator import CPF

User = get_user_model()


class UniqueDataGenerator:
    """Generate unique test data to avoid database constraint violations."""
    
    @staticmethod
    def generate_unique_cns_medico():
        """Generate a unique 15-digit CNS for medico."""
        # Use timestamp + random to ensure uniqueness
        timestamp = str(int(time.time() * 1000000))[-12:]
        random_part = str(random.randint(100, 999))
        return timestamp + random_part
    
    @staticmethod
    def generate_unique_cns_paciente():
        """Generate a unique 15-digit CNS for paciente."""
        # Different prefix to avoid collisions with medico
        timestamp = str(int(time.time() * 1000000))[-12:]
        random_part = str(random.randint(100, 999))
        return random_part + timestamp
    
    @staticmethod
    def generate_unique_cns_clinica():
        """Generate a unique 7-digit CNS for clinica."""
        # Use last 4 digits of timestamp + 3 random digits
        timestamp = str(int(time.time() * 1000))[-4:]
        random_part = str(random.randint(100, 999))
        return timestamp + random_part
    
    @staticmethod
    def generate_unique_cpf():
        """Generate a unique valid CPF."""
        return CPF.generate()
    
    @staticmethod
    def generate_unique_crm():
        """Generate a unique CRM number."""
        # CRM format: 5-6 digits
        return str(random.randint(10000, 999999))
    
    @staticmethod
    def generate_unique_email():
        """Generate a unique email address."""
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time()))[-6:]
        return f"test_{unique_id}_{timestamp}@example.com"
    
    @staticmethod
    def generate_unique_cid():
        """Generate a unique CID (Classificação Internacional de Doenças) code."""
        # CID format: letter + numbers + optional decimal + numbers
        # Example: A00.0, B12.3, T001
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        letter = random.choice(letters)
        # Use timestamp to ensure uniqueness
        timestamp = str(int(time.time() * 1000))[-3:]  # Last 3 digits of timestamp
        random_part = str(random.randint(0, 9))
        return f"{letter}{timestamp}.{random_part}"


class BaseTestCase(TestCase):
    """
    Base test case with proper isolation and unique data generation.
    
    Features:
    - Automatic unique data generation
    - Helper methods for all models
    - Proper test isolation with transactions
    - Consistent test data patterns
    """
    
    def setUp(self):
        """Set up test with unique identifier."""
        super().setUp()
        self.client = Client()
        self.unique_suffix = str(uuid.uuid4())[:8]
        self.data_generator = UniqueDataGenerator()
    
    def create_test_user(self, **kwargs):
        """Create a test user with unique email."""
        defaults = {
            'email': self.data_generator.generate_unique_email(),
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        
        user = User.objects.create_user(**defaults)
        
        # Handle is_medico flag if provided
        if 'is_medico' in kwargs:
            user.is_medico = kwargs['is_medico']
            user.save()
        
        return user
    
    def create_test_medico(self, user=None, **kwargs):
        """Create a test medico with unique CNS and CRM."""
        from medicos.models import Medico
        
        defaults = {
            'nome_medico': f'Dr. Test {self.unique_suffix}',
            'crm_medico': self.data_generator.generate_unique_crm(),
            'cns_medico': self.data_generator.generate_unique_cns_medico(),
            'estado': 'SP',
            'especialidade': 'CLINICA_MEDICA'
        }
        defaults.update(kwargs)
        
        medico = Medico.objects.create(**defaults)
        
        # Associate with user if provided
        if user:
            medico.usuarios.add(user)
        
        return medico
    
    def create_test_clinica(self, **kwargs):
        """Create a test clinic with unique CNS."""
        from clinicas.models import Clinica
        
        defaults = {
            'nome_clinica': f'Test Clinic {self.unique_suffix}',
            'cns_clinica': self.data_generator.generate_unique_cns_clinica(),
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'São Paulo',
            'bairro': 'Centro',
            'cep': '01000-000',
            'telefone_clinica': '(11) 3333-4444'
        }
        defaults.update(kwargs)
        
        return Clinica.objects.create(**defaults)
    
    def create_test_clinica_with_versioning(self, user, medico, **kwargs):
        """Create a test clinic using the proper versioning system."""
        from clinicas.models import Clinica
        
        defaults = {
            'nome_clinica': f'Test Clinic {self.unique_suffix}',
            'cns_clinica': self.data_generator.generate_unique_cns_clinica(),
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'São Paulo',
            'bairro': 'Centro',
            'cep': '01000-000',
            'telefone_clinica': '(11) 3333-4444'
        }
        defaults.update(kwargs)
        
        # Use the proper versioning system
        return Clinica.create_or_update_for_user(
            user=user,
            doctor=medico,
            clinic_data=defaults
        )
    
    def ensure_clinic_version_assignments(self):
        """
        Utility method to ensure all test clinic-user relationships have version assignments.
        This fixes the common test issue where clinic relationships exist but version assignments don't.
        """
        from clinicas.models import Clinica, ClinicaUsuario, ClinicaUsuarioVersion, ClinicaVersion
        
        # Find all ClinicaUsuario relationships without version assignments
        missing_assignments = ClinicaUsuario.objects.filter(
            active_version__isnull=True
        )
        
        for cu in missing_assignments:
            if cu.clinica and cu.usuario:
                # Get or create a version for this clinic
                version = cu.clinica.versions.first()
                if not version:
                    # Create initial version if none exists
                    version = ClinicaVersion.objects.create(
                        clinica=cu.clinica,
                        version_number=1,
                        nome_clinica=cu.clinica.nome_clinica,
                        logradouro=cu.clinica.logradouro,
                        logradouro_num=cu.clinica.logradouro_num,
                        cidade=cu.clinica.cidade,
                        bairro=cu.clinica.bairro,
                        cep=cu.clinica.cep,
                        telefone_clinica=cu.clinica.telefone_clinica,
                        change_summary='Test version created automatically',
                        status='active'
                    )
                
                # Create the missing version assignment
                ClinicaUsuarioVersion.objects.create(
                    clinica_usuario=cu,
                    version=version
                )
                print(f"✅ Created version assignment: {cu.usuario.email} -> Clinic {cu.clinica.cns_clinica} Version {version.version_number}")
    
    def create_test_patient(self, user=None, **kwargs):
        """Create a test patient with unique CPF and CNS."""
        from pacientes.models import Paciente
        
        defaults = {
            'nome_paciente': f'Test Patient {self.unique_suffix}',
            'cpf_paciente': self.data_generator.generate_unique_cpf(),
            'cns_paciente': self.data_generator.generate_unique_cns_paciente(),
            'nome_mae': 'Test Mother',
            'idade': '30',
            'sexo': 'M',
            'peso': '70',
            'altura': '170',
            'incapaz': False,
            'etnia': 'Branca',
            'telefone1_paciente': '11999999999',
            'end_paciente': 'Test Address 123',
            'cidade_paciente': 'São Paulo',
            'cep_paciente': '01000-000'
        }
        defaults.update(kwargs)
        
        patient = Paciente.objects.create(**defaults)
        
        # Associate with user if provided
        if user:
            patient.usuarios.add(user)
            
            # Create patient version for proper access control
            try:
                from pacientes.models import PacienteVersion, PacienteUsuarioVersion
                # Create initial version for the patient (only with known safe fields)
                patient_version = PacienteVersion.objects.create(
                    paciente=patient,
                    nome_paciente=patient.nome_paciente,
                    cns_paciente=getattr(patient, 'cns_paciente', ''),  
                    nome_mae=getattr(patient, 'nome_mae', ''),
                    idade=getattr(patient, 'idade', ''),
                    sexo=getattr(patient, 'sexo', ''),
                    peso=getattr(patient, 'peso', ''),
                    altura=getattr(patient, 'altura', ''),
                    incapaz=getattr(patient, 'incapaz', False),
                    etnia=getattr(patient, 'etnia', ''),
                    telefone1_paciente=getattr(patient, 'telefone1_paciente', ''),
                    end_paciente=getattr(patient, 'end_paciente', ''),
                    cidade_paciente=getattr(patient, 'cidade_paciente', ''),
                    cep_paciente=getattr(patient, 'cep_paciente', ''),
                    rg=getattr(patient, 'rg', ''),
                    escolha_etnia=getattr(patient, 'escolha_etnia', getattr(patient, 'etnia', '')),
                    telefone2_paciente=getattr(patient, 'telefone2_paciente', ''),
                    nome_responsavel=getattr(patient, 'nome_responsavel', ''),
                    email_paciente=getattr(patient, 'email_paciente', ''),
                    version_number=1,
                    status='active',
                    created_by=user
                )
                
                # Create user-patient version relationship to avoid security warnings
                # Get the through relationship object
                user_patient_rel = patient.usuarios.through.objects.get(
                    paciente=patient, usuario=user
                )
                PacienteUsuarioVersion.objects.create(
                    paciente_usuario=user_patient_rel,
                    version=patient_version
                )
            except (ImportError, Exception) as e:
                # PacienteVersion model might not exist or have different fields
                # Don't silently fail - log the error for debugging
                print(f"WARNING: Failed to create patient version: {e}")
                pass
        
        return patient
    
    def create_test_protocolo(self, **kwargs):
        """Create a test protocol."""
        from processos.models import Protocolo
        
        defaults = {
            'nome': f'Test Protocol {self.unique_suffix}',
            'arquivo': 'test.pdf',
            'dados_condicionais': {}  # Required field
        }
        defaults.update(kwargs)
        
        return Protocolo.objects.create(**defaults)
    
    def create_test_doenca(self, protocolo=None, **kwargs):
        """Create a test disease with unique CID."""
        from processos.models import Doenca
        
        if not protocolo:
            protocolo = self.create_test_protocolo()
        
        # Generate unique CID if not provided
        if 'cid' not in kwargs:
            # Use pattern like T99.X where X is random
            random_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            random_num = random.randint(10, 99)
            kwargs['cid'] = f'T{random_num}.{random_letter}'
        
        defaults = {
            'nome': f'Test Disease {self.unique_suffix}',
            'protocolo': protocolo
        }
        defaults.update(kwargs)
        
        return Doenca.objects.create(**defaults)
    
    def create_test_medicamento(self, **kwargs):
        """Create a test medication."""
        from processos.models import Medicamento
        
        defaults = {
            'nome': f'Test Medication {self.unique_suffix}',
            'dosagem': '500mg',
            'apres': 'Comprimido'
        }
        defaults.update(kwargs)
        
        return Medicamento.objects.create(**defaults)
    
    def create_test_prescription_data(self, medications=None):
        """Create properly structured prescription data for testing."""
        if not medications:
            medications = [self.create_test_medicamento()]
        
        prescricao = {}
        for med_index, med in enumerate(medications, 1):
            prescricao[str(med_index)] = {
                f"id_med{med_index}": str(med.id),
                f"med{med_index}_posologia_mes1": "1 comprimido 2x ao dia",
                f"med{med_index}_posologia_mes2": "1 comprimido 2x ao dia", 
                f"med{med_index}_posologia_mes3": "1 comprimido 2x ao dia",
                f"med{med_index}_posologia_mes4": "1 comprimido 2x ao dia",
                f"med{med_index}_posologia_mes5": "1 comprimido 2x ao dia",
                f"med{med_index}_posologia_mes6": "1 comprimido 2x ao dia",
                f"qtd_med{med_index}_mes1": "60",
                f"qtd_med{med_index}_mes2": "60",
                f"qtd_med{med_index}_mes3": "60",
                f"qtd_med{med_index}_mes4": "60",
                f"qtd_med{med_index}_mes5": "60",
                f"qtd_med{med_index}_mes6": "60"
            }
            # Add administration route for first medication
            if med_index == 1:
                prescricao[str(med_index)]["med1_via"] = "oral"
        
        return prescricao
    
    def create_test_emissor(self, medico=None, clinica=None):
        """Create a test emissor (doctor-clinic association)."""
        from clinicas.models import Emissor
        
        if not medico:
            user = self.create_test_user(is_medico=True)
            medico = self.create_test_medico(user=user)
        if not clinica:
            clinica = self.create_test_clinica()
        
        return Emissor.objects.create(
            medico=medico,
            clinica=clinica
        )
    
    def create_test_processo(self, **kwargs):
        """Create a test process with all required fields."""
        from processos.models import Processo
        
        # Create dependencies if not provided
        if 'usuario' not in kwargs:
            kwargs['usuario'] = self.create_test_user(is_medico=True)
        if 'paciente' not in kwargs:
            kwargs['paciente'] = self.create_test_patient(user=kwargs['usuario'])
        if 'doenca' not in kwargs:
            kwargs['doenca'] = self.create_test_doenca()
        if 'clinica' not in kwargs:
            kwargs['clinica'] = self.create_test_clinica()
        if 'medico' not in kwargs:
            kwargs['medico'] = self.create_test_medico(user=kwargs['usuario'])
        if 'emissor' not in kwargs:
            kwargs['emissor'] = self.create_test_emissor(
                medico=kwargs['medico'], 
                clinica=kwargs['clinica']
            )
        
        defaults = {
            'anamnese': 'Test anamnese',
            'prescricao': {},
            'tratou': False,
            'tratamentos_previos': 'None',
            'data1': date.today(),
            'preenchido_por': 'M',
            'dados_condicionais': {}
        }
        
        # Update with any provided kwargs
        for key, value in kwargs.items():
            defaults[key] = value
        
        return Processo.objects.create(**defaults)
    
    def create_test_processo_with_versioned_patient(self, user, patient_data, **kwargs):
        """
        Create a test process with properly versioned patient data.
        
        This helper is specifically for testing patient versioning scenarios where
        different users need their own versions of patient data.
        
        Args:
            user: The user who will see this version of the patient
            patient_data: Dict containing patient data for this user's version
            **kwargs: Additional arguments passed to create_test_processo
        
        Returns:
            Processo: Created process with versioned patient
        """
        from pacientes.models import Paciente
        
        # Create or update patient with versioning for this specific user
        versioned_patient = Paciente.create_or_update_for_user(user, patient_data)
        
        # Use existing helper with the versioned patient
        return self.create_test_processo(
            usuario=user,
            paciente=versioned_patient,
            **kwargs
        )
    
    def login_test_user(self, user=None, password="testpass123"):
        """Login a test user."""
        if not user:
            user = self.create_test_user()
        self.client.login(email=user.email, password=password)
        return user
    
    def setup_process_session(self, cid='G40.0', patient_exists=True, patient_id=None):
        """Set up session data for process views."""
        session = self.client.session
        session['cid'] = cid
        session['paciente_existe'] = patient_exists
        if patient_id:
            session['paciente_id'] = patient_id
        if patient_exists and not patient_id:
            # Create a patient if needed
            patient = self.create_test_patient()
            session['paciente_id'] = patient.id
            session['cpf_paciente'] = patient.cpf_paciente
        session['in_setup_flow'] = True
        session.save()
    
    def setup_complete_environment(self):
        """Set up a complete test environment with all necessary objects."""
        # Create user
        self.user = self.create_test_user(email=f"doctor_{self.unique_suffix}@example.com", is_medico=True)
        
        # Create medico
        self.medico = self.create_test_medico(user=self.user)
        
        # Create clinic
        self.clinica = self.create_test_clinica()
        
        # Associate user with clinic
        from clinicas.models import ClinicaUsuario
        ClinicaUsuario.objects.create(usuario=self.user, clinica=self.clinica)
        
        # Create emissor
        self.emissor = self.create_test_emissor(medico=self.medico, clinica=self.clinica)
        
        # Create patient
        self.patient = self.create_test_patient(user=self.user)
        
        # Create protocol and disease
        self.protocolo = self.create_test_protocolo()
        self.doenca = self.create_test_doenca(protocolo=self.protocolo)
        
        # Create medications
        self.med1 = self.create_test_medicamento(nome="Medication 1")
        self.med2 = self.create_test_medicamento(nome="Medication 2")
        self.protocolo.medicamentos.add(self.med1, self.med2)
        
        # Login the user
        self.login_test_user(self.user)
        
        return {
            "user": self.user,
            "medico": self.medico,
            "clinica": self.clinica,
            "emissor": self.emissor,
            "patient": self.patient,
            "protocolo": self.protocolo,
            "doenca": self.doenca,
            "medications": [self.med1, self.med2]
        }


# Global Test Data Factory - Single source of truth for all test data patterns
class TestDataFactory:
    """
    Global factory for consistent test data across all tests.
    Use these methods instead of hardcoded values to ensure uniqueness.
    """
    
    @staticmethod
    def get_unique_cns():
        """Generate unique CNS - use this instead of hardcoded values."""
        return UniqueDataGenerator.generate_unique_cns_clinica()
    
    @staticmethod
    def get_unique_cpf():
        """Generate unique CPF - use this instead of hardcoded values."""
        return UniqueDataGenerator.generate_unique_cpf()
    
    @staticmethod
    def get_unique_email():
        """Generate unique email - use this instead of hardcoded values."""
        return UniqueDataGenerator.generate_unique_email()
    
    @staticmethod
    def get_unique_crm():
        """Generate unique CRM - use this instead of hardcoded values."""
        return UniqueDataGenerator.generate_unique_crm()
    
    @staticmethod
    def get_valid_form_data_patterns():
        """Get common form data patterns to avoid duplication."""
        return {
            'user_creation': {
                'email': UniqueDataGenerator.generate_unique_email(),
                'password1': 'ComplexPassword789!',
                'password2': 'ComplexPassword789!',
            },
            'clinic_creation': get_valid_clinic_form_data(),
            'medico_creation': get_valid_medico_form_data(),
            'prescription_creation': get_valid_prescription_form_data()
        }


class BaseTransactionTestCase(TransactionTestCase):
    """
    Base transaction test case for tests that need real database transactions.
    
    Use this for tests that need to test:
    - Database constraints
    - Concurrent access
    - Transaction rollback behavior
    """
    
    def setUp(self):
        """Set up test with unique identifier."""
        super().setUp()
        self.client = Client()
        self.unique_suffix = str(uuid.uuid4())[:8]
        self.data_generator = UniqueDataGenerator()
    
    # Include all the same helper methods as BaseTestCase
    # Python doesn't support multiple inheritance well with Django test cases,
    # so we duplicate the methods here. In a real project, we'd use a mixin.
    
    def create_test_user(self, **kwargs):
        """Create a test user with unique email."""
        defaults = {
            'email': self.data_generator.generate_unique_email(),
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        
        user = User.objects.create_user(**defaults)
        
        if 'is_medico' in kwargs:
            user.is_medico = kwargs['is_medico']
            user.save()
        
        return user
    
    def create_test_clinica(self, **kwargs):
        """Create a test clinic with unique CNS."""
        from clinicas.models import Clinica
        
        defaults = {
            'nome_clinica': f'Test Clinic {self.unique_suffix}',
            'cns_clinica': self.data_generator.generate_unique_cns_clinica(),
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'São Paulo',
            'bairro': 'Centro',
            'cep': '01000-000',
            'telefone_clinica': '(11) 3333-4444'
        }
        defaults.update(kwargs)
        
        return Clinica.objects.create(**defaults)


# Common test data patterns for form testing
def get_valid_prescription_form_data():
    """Get valid form data for prescription forms."""
    return {
        # Patient data
        'nome_paciente': 'Test Patient',
        'cpf_paciente': UniqueDataGenerator.generate_unique_cpf(),
        'nome_mae': 'Test Mother',
        'peso': '70',
        'altura': '170',
        'incapaz': False,
        'end_paciente': 'Test Address 123',
        
        # Prescription data
        'cid': 'G40.0',
        'diagnostico': 'Epilepsia',
        'anamnese': 'Test anamnese',
        'data_1': '01/01/2025',
        
        # Required fields
        'estado': 'SP',
        'especialidade': 'NEUROLOGIA'
    }


def get_valid_clinic_form_data():
    """Get valid form data for clinic forms."""
    return {
        'nome_clinica': 'Test Clinic',
        'cns_clinica': UniqueDataGenerator.generate_unique_cns_clinica(),
        'logradouro': 'Test Street',
        'logradouro_num': '123',
        'cidade': 'São Paulo',
        'bairro': 'Centro',
        'cep': '01000-000',
        'telefone_clinica': '(11) 3333-4444'
    }


def get_valid_medico_form_data():
    """Get valid form data for medico forms."""
    return {
        'nome_medico': 'Dr. Test',
        'crm_medico': UniqueDataGenerator.generate_unique_crm(),
        'cns_medico': UniqueDataGenerator.generate_unique_cns_medico(),
        'estado': 'SP',
        'especialidade': 'CLINICA_MEDICA'
    }