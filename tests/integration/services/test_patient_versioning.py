"""
Comprehensive tests for patient versioning system.

Tests the complete patient versioning functionality including:
- Version creation and assignment
- User-specific patient data isolation
- Template filter functionality
- AJAX search with versioned data
- Process creation integration
- Data integrity and constraints
"""

from django.test import TestCase, Client, override_settings
from tests.test_base import BaseTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import JsonResponse
from django.template import Context, Template
from django.db import IntegrityError, transaction
from unittest.mock import patch
import json

from pacientes.models import Paciente, PacienteVersion, PacienteUsuarioVersion
from pacientes.templatetags.patient_tags import patient_name_for_user, patient_data_for_user
from processos.models import Processo, Doenca
from medicos.models import Medico
from clinicas.models import Clinica, Emissor

User = get_user_model()


class PatientVersioningModelTest(TestCase):
    """Test core patient versioning model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com', 
            password='testpass123'
        )
        
        # Standard patient data
        self.patient_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': "11144477735",
            'idade': '35',
            'sexo': 'Masculino',
            'nome_mae': 'Maria Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'rg': '12.345.678-9',
            'peso': '70kg',
            'altura': '1,75m',
            'escolha_etnia': 'Branco',
            'cns_paciente': '123456789012345',
            'email_paciente': 'joao@test.com',
            'cidade_paciente': 'São Paulo',
            'end_paciente': 'Rua A, 123',
            'cep_paciente': '01234-567',
            'telefone1_paciente': '(11) 99999-9999',
            'telefone2_paciente': '(11) 88888-8888',
            'etnia': 'Branco'
        }
    
    def test_create_new_patient_with_version(self):
        """Test creating a new patient with initial version."""
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # Check master record
        self.assertEqual(patient.cpf_paciente, "11144477735")
        self.assertTrue(patient.was_created)
        self.assertTrue(self.user1 in patient.usuarios.all())
        
        # Check version creation
        versions = patient.versions.all()
        self.assertEqual(versions.count(), 1)
        
        version = versions.first()
        self.assertEqual(version.nome_paciente, 'João Silva')
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.status, 'active')
        self.assertEqual(version.created_by, self.user1)
        
        # Check user-version assignment
        patient_usuario = patient.usuarios.through.objects.get(
            paciente=patient, usuario=self.user1
        )
        user_version = PacienteUsuarioVersion.objects.get(
            paciente_usuario=patient_usuario
        )
        self.assertEqual(user_version.version, version)
    
    def test_update_existing_patient_creates_version(self):
        """Test updating existing patient creates new version for user."""
        # Create initial patient
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        initial_version = patient.versions.first()
        
        # Update with different data for user2
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'  # Different name
        updated_data['idade'] = '36'  # Different age
        
        updated_patient = Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Should be same master record
        self.assertEqual(patient.pk, updated_patient.pk)
        self.assertFalse(updated_patient.was_created)
        
        # Should have 2 versions now
        versions = patient.versions.all().order_by('version_number')
        self.assertEqual(versions.count(), 2)
        
        # Check new version
        new_version = versions.last()
        self.assertEqual(new_version.nome_paciente, 'João Santos')
        self.assertEqual(new_version.idade, '36')
        self.assertEqual(new_version.version_number, 2)
        self.assertEqual(new_version.created_by, self.user2)
        
        # Check user1 still sees original version
        user1_version = patient.get_version_for_user(self.user1)
        self.assertEqual(user1_version.nome_paciente, 'João Silva')
        
        # Check user2 sees new version
        user2_version = patient.get_version_for_user(self.user2)
        self.assertEqual(user2_version.nome_paciente, 'João Santos')
    
    def test_cpf_uniqueness_enforced(self):
        """Test that CPF uniqueness is enforced at database level."""
        # Create first patient
        Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # Try to create another patient with same CPF directly (should fail)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Paciente.objects.create(
                    cpf_paciente="11144477735",
                    nome_paciente='Different Name'
                ,
            incapaz=False
        )
    
    def test_version_number_uniqueness(self):
        """Test version number uniqueness per patient."""
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # Try to create version with duplicate number (should fail)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PacienteVersion.objects.create(
                    paciente=patient,
                    version_number=1,  # Same as existing
                    nome_paciente='Test',
                    created_by=self.user2
                ,
            incapaz=False
        )
    
    def test_get_version_for_user(self):
        """Test getting appropriate version for user."""
        # Create patient with user1
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # Update with user2
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Each user should see their version
        user1_version = patient.get_version_for_user(self.user1)
        user2_version = patient.get_version_for_user(self.user2)
        
        self.assertEqual(user1_version.nome_paciente, 'João Silva')
        self.assertEqual(user2_version.nome_paciente, 'João Santos')
        
        # User without access should get None (security fix)
        user3 = User.objects.create_user(email='user3@test.com', password='pass')
        user3_version = patient.get_version_for_user(user3)
        self.assertIsNone(user3_version)  # No unauthorized access allowed
    
    def test_get_patients_for_user_search(self):
        """Test searching patients with versioned data."""
        # Create patients for different users
        patient1 = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # User2 sees different name for same patient
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Create another patient for user1 only
        other_data = self.patient_data.copy()
        other_data['cpf_paciente'] = '987.654.321-00'
        other_data['nome_paciente'] = 'Maria Oliveira'
        patient2 = Paciente.create_or_update_for_user(self.user1, other_data)
        
        # Search without term - user1 should see both patients
        results = Paciente.get_patients_for_user_search(self.user1)
        self.assertEqual(len(results), 2)
        
        # Find João in results
        joao_result = next((r for r in results if r[0].cpf_paciente == "11144477735"), None)
        self.assertIsNotNone(joao_result)
        self.assertEqual(joao_result[1].nome_paciente, 'João Silva')  # User1's version
        
        # Search with term
        search_results = Paciente.get_patients_for_user_search(self.user1, 'Maria')
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0][1].nome_paciente, 'Maria Oliveira')
        
        # User2 search should show their version of João
        user2_results = Paciente.get_patients_for_user_search(self.user2, 'João')
        self.assertEqual(len(user2_results), 1)
        self.assertEqual(user2_results[0][1].nome_paciente, 'João Santos')


class PatientVersioningTemplateTest(TestCase):
    """Test template filters for patient versioning."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123' 
        )
        
        self.patient_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': "11144477735",
            'idade': '35',
            'sexo': 'Masculino',
            'nome_mae': 'Maria Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'rg': '12.345.678-9',
            'peso': '70kg',
            'altura': '1,75m',
            'escolha_etnia': 'Branco',
            'cns_paciente': '123456789012345',
            'email_paciente': 'joao@test.com',
            'cidade_paciente': 'São Paulo',
            'end_paciente': 'Rua A, 123',
            'cep_paciente': '01234-567',
            'telefone1_paciente': '(11) 99999-9999',
            'telefone2_paciente': '(11) 88888-8888',
            'etnia': 'Branco'
        }
    
    def test_patient_name_for_user_filter(self):
        """Test patient_name_for_user template filter."""
        # Create patient with different versions
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Test filter function
        user1_name = patient_name_for_user(patient, self.user1)
        user2_name = patient_name_for_user(patient, self.user2)
        
        self.assertEqual(user1_name, 'João Silva')
        self.assertEqual(user2_name, 'João Santos')
        
        # Test with None values
        self.assertEqual(patient_name_for_user(None, self.user1), '')
        self.assertEqual(patient_name_for_user(patient, None), '')
    
    def test_patient_data_for_user_filter(self):
        """Test patient_data_for_user template filter."""
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        updated_data['idade'] = '36'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Test filter function
        user1_data = patient_data_for_user(patient, self.user1)
        user2_data = patient_data_for_user(patient, self.user2)
        
        self.assertEqual(user1_data.nome_paciente, 'João Silva')
        self.assertEqual(user1_data.idade, '35')
        
        self.assertEqual(user2_data.nome_paciente, 'João Santos')
        self.assertEqual(user2_data.idade, '36')
    
    def test_template_rendering_with_filters(self):
        """Test actual template rendering with versioning filters."""
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Test template with filter
        template = Template('{% load patient_tags %}{{ paciente|patient_name_for_user:user }}')
        
        # Render for user1
        context1 = Context({'paciente': patient, 'user': self.user1})
        result1 = template.render(context1)
        self.assertEqual(result1, 'João Silva')
        
        # Render for user2
        context2 = Context({'paciente': patient, 'user': self.user2})
        result2 = template.render(context2)
        self.assertEqual(result2, 'João Santos')


@patch('analytics.signals.log_user_login')
class PatientVersioningAjaxTest(TestCase):
    """Test AJAX views with patient versioning."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        
        self.patient_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': "11144477735",
            'idade': '35',
            'sexo': 'Masculino',
            'nome_mae': 'Maria Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'rg': '12.345.678-9',
            'peso': '70kg',
            'altura': '1,75m',
            'escolha_etnia': 'Branco',
            'cns_paciente': '123456789012345',
            'email_paciente': 'joao@test.com',
            'cidade_paciente': 'São Paulo',
            'end_paciente': 'Rua A, 123',
            'cep_paciente': '01234-567',
            'telefone1_paciente': '(11) 99999-9999',
            'telefone2_paciente': '(11) 88888-8888',
            'etnia': 'Branco'
        }
    
    def test_ajax_patient_search_with_versioning(self, mock_log_login):
        """Test AJAX patient search returns versioned data."""
        # Create patient with different versions for each user
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Test search as user1
        self.client.force_login(self.user1)
        response1 = self.client.get('/pacientes/ajax/busca', {'palavraChave': 'João'})
        
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        self.assertEqual(len(data1), 1)
        self.assertEqual(data1[0]['nome_paciente'], 'João Silva')
        self.assertEqual(data1[0]['cpf_paciente'], "11144477735")
        
        # Test search as user2
        self.client.force_login(self.user2)
        response2 = self.client.get('/pacientes/ajax/busca', {'palavraChave': 'João'})
        
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(len(data2), 1)
        self.assertEqual(data2[0]['nome_paciente'], 'João Santos')  # Different version
        self.assertEqual(data2[0]['cpf_paciente'], "11144477735")  # Same CPF
    
    def test_ajax_search_without_term(self, mock_log_login):
        """Test AJAX search without search term returns all user's patients."""
        # Create multiple patients for user1
        patient1 = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        other_data = self.patient_data.copy()
        other_data['cpf_paciente'] = '987.654.321-00'
        other_data['nome_paciente'] = 'Maria Oliveira'
        patient2 = Paciente.create_or_update_for_user(self.user1, other_data)
        
        # Search without term
        self.client.force_login(self.user1)
        response = self.client.get('/pacientes/ajax/busca')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        
        names = [p['nome_paciente'] for p in data]
        self.assertIn('João Silva', names)
        self.assertIn('Maria Oliveira', names)


class PatientVersioningIntegrationTest(BaseTestCase):
    """Test integration with process creation system."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create required medical data
        self.medico1 = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='12345',
            estado='SP'
        )
        
        self.medico2 = Medico.objects.create(
            nome_medico='Dr. Test 2',
            crm_medico='67890',
            estado='SP'
        )
        
        # Create clinic and emissor
        self.clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567'  # Valid length for CNS field
        )
        
        self.emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=self.clinica
        )
        
        self.emissor2 = Emissor.objects.create(
            medico=self.medico2,
            clinica=self.clinica
        )
        
        # Create disease
        self.doenca = Doenca.objects.create(
            cid='Z00.0',
            nome='Test Disease'
        )
        
        self.patient_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': "11144477735",
            'idade': '35',
            'sexo': 'Masculino',
            'nome_mae': 'Maria Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'rg': '12.345.678-9',
            'peso': '70kg',
            'altura': '1,75m',
            'escolha_etnia': 'Branco',
            'cns_paciente': '123456789012345',
            'email_paciente': 'joao@test.com',
            'cidade_paciente': 'São Paulo',
            'end_paciente': 'Rua A, 123',
            'cep_paciente': '01234-567',
            'telefone1_paciente': '(11) 99999-9999',
            'telefone2_paciente': '(11) 88888-8888',
            'etnia': 'Branco'
        }
    
    def test_process_creation_uses_versioning(self):
        """Test that process creation integrates with patient versioning."""
        from processos.services.prescription.workflow_service import PrescriptionService
        from datetime import datetime
        
        # Prepare process data
        process_data = self.patient_data.copy()
        process_data.update({
            'data_1': datetime.now(),
            'anamnese': 'Test anamnese',
            'prescricao': 'Test prescription',
            'tratou': 'Não',
            'tratamentos_previos': '',
            'preenchido_por': 'Test'
        })
        
        # Create process using new versioned helper - this properly handles patient versioning
        processo = self.create_test_processo_with_versioned_patient(
            user=self.user1,
            patient_data=self.patient_data,
            doenca=self.doenca,
            clinica=self.emissor1.clinica,
            medico=self.emissor1.medico,
            emissor=self.emissor1,
            anamnese=process_data['anamnese']
        )
        
        # Verify process was created
        self.assertEqual(processo.usuario, self.user1)
        self.assertEqual(processo.paciente.cpf_paciente, "11144477735")
        
        # Verify patient versioning was used
        patient = processo.paciente
        version = patient.get_version_for_user(self.user1)
        self.assertIsNotNone(version)
        self.assertEqual(version.nome_paciente, 'João Silva')
        
        # Test with existing patient - user2 creates their own version
        updated_patient_data = self.patient_data.copy()
        updated_patient_data['nome_paciente'] = 'João Santos'  # Different version for user2
        
        # Create second process using versioned helper - this creates user2's version
        processo2 = self.create_test_processo_with_versioned_patient(
            user=self.user2,
            patient_data=updated_patient_data,
            doenca=self.doenca,
            clinica=self.emissor2.clinica,
            medico=self.emissor2.medico,
            emissor=self.emissor2,
            anamnese=process_data['anamnese']
        )
        
        # Verify second process uses same patient but different version
        self.assertEqual(processo2.paciente.pk, patient.pk)  # Same patient
        
        # But each user sees different version
        user1_version = patient.get_version_for_user(self.user1)
        user2_version = patient.get_version_for_user(self.user2)
        
        self.assertEqual(user1_version.nome_paciente, 'João Silva')
        self.assertEqual(user2_version.nome_paciente, 'João Santos')


class PatientVersioningFormTest(TestCase):
    """Test form initialization with versioned patient data."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        
        self.patient_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': "11144477735",
            'idade': '35',
            'sexo': 'Masculino',
            'nome_mae': 'Maria Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'rg': '12.345.678-9',
            'peso': '70kg',
            'altura': '1,75m',
            'escolha_etnia': 'Branco',
            'cns_paciente': '123456789012345',
            'email_paciente': 'joao@test.com',
            'cidade_paciente': 'São Paulo',
            'end_paciente': 'Rua A, 123',
            'cep_paciente': '01234-567',
            'telefone1_paciente': '(11) 99999-9999',
            'telefone2_paciente': '(11) 88888-8888',
            'etnia': 'Branco'
        }
    
    def test_form_initialization_uses_versioned_data(self):
        """Test that PrescriptionViewSetupService uses versioned patient data, not master record."""
        from processos.services.view_services import PrescriptionViewSetupService
        from django.test import RequestFactory
        from processos.models import Doenca
        
        # Create disease for testing
        doenca = Doenca.objects.create(cid='F20', nome='Test Disease')
        
        # Create patient with user1
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # Update patient with user2 (different version)
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        updated_data['altura'] = '1,80m'  # Different height
        updated_data['peso'] = '75kg'     # Different weight
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Create mock request for user1
        factory = RequestFactory()
        request1 = factory.get('/')
        request1.user = self.user1
        request1.session = {
            'paciente_id': patient.id,
            'cpf_paciente': patient.cpf_paciente,
            'paciente_existe': True,
            'cid': 'F20'
        }
        
        # Create mock request for user2
        request2 = factory.get('/')
        request2.user = self.user2
        request2.session = {
            'paciente_id': patient.id,
            'cpf_paciente': patient.cpf_paciente,
            'paciente_existe': True,
            'cid': 'F20'
        }
        
        # Use the service to prepare initial data
        setup_service = PrescriptionViewSetupService()
        
        # Test user1 gets their version through the service
        # The service._prepare_initial_form_data is called internally
        initial_data1 = setup_service._prepare_initial_form_data(request1, True, '01/01/2024', 'F20')
        self.assertEqual(initial_data1['nome_paciente'], 'João Silva')
        self.assertEqual(initial_data1['altura'], '1,75m')
        self.assertEqual(initial_data1['peso'], '70kg')
        
        # Test user2 gets their version through the service
        initial_data2 = setup_service._prepare_initial_form_data(request2, True, '01/01/2024', 'F20')
        self.assertEqual(initial_data2['nome_paciente'], 'João Santos')
        self.assertEqual(initial_data2['altura'], '1,80m')
        self.assertEqual(initial_data2['peso'], '75kg')
        
        # Verify both have same master record fields
        self.assertEqual(initial_data1['cpf_paciente'], "11144477735")
        self.assertEqual(initial_data2['cpf_paciente'], "11144477735")
        self.assertEqual(initial_data1['id'], patient.id)
        self.assertEqual(initial_data2['id'], patient.id)
    
    def test_renewal_data_uses_versioned_patient(self):
        """Test that renewal data generation uses versioned patient data."""
        from processos.services.prescription.renewal_service import RenewalService
        from processos.models import Processo, Doenca
        from medicos.models import Medico
        from clinicas.models import Clinica, Emissor
        
        # Create required objects
        doenca = Doenca.objects.create(cid='F20', nome='Test Disease')
        medico = Medico.objects.create(nome_medico='Dr. Test', crm_medico='12345', estado='SP')
        clinica = Clinica.objects.create(nome_clinica='Test Clinic', cns_clinica='1234567')
        emissor = Emissor.objects.create(medico=medico, clinica=clinica)
        
        # Create patient with user1
        patient = Paciente.create_or_update_for_user(self.user1, self.patient_data)
        
        # Create process
        from datetime import date
        processo = Processo.objects.create(
            anamnese='Test anamnese',
            doenca=doenca,
            prescricao={},
            tratou=False,
            tratamentos_previos='',
            data1=date(2024, 1, 1),
            preenchido_por='M',
            dados_condicionais={},
            paciente=patient,
            medico=medico,
            clinica=clinica,
            emissor=emissor,
            usuario=self.user1
        )
        
        # Update patient with user2 (different version)
        updated_data = self.patient_data.copy()
        updated_data['nome_paciente'] = 'João Santos'
        updated_data['altura'] = '1,80m'
        Paciente.create_or_update_for_user(self.user2, updated_data)
        
        # Test renewal data for user1
        renewal_service = RenewalService()
        renewal_data1 = renewal_service.generate_renewal_data('01/02/2024', processo.id, self.user1)
        self.assertEqual(renewal_data1['nome_paciente'], 'João Silva')
        self.assertEqual(renewal_data1['altura'], '1,75m')
        
        # Test renewal data for user2
        renewal_data2 = renewal_service.generate_renewal_data('01/02/2024', processo.id, self.user2)
        self.assertEqual(renewal_data2['nome_paciente'], 'João Santos')
        self.assertEqual(renewal_data2['altura'], '1,80m')
        
        # Both should have same master record CPF
        self.assertEqual(renewal_data1['cpf_paciente'], "11144477735")
        self.assertEqual(renewal_data2['cpf_paciente'], "11144477735")


class PatientVersioningEdgeCasesTest(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        self.patient_data = {
            'nome_paciente': 'Test Patient',
            'cpf_paciente': "11144477735",
            'idade': '30',
            'sexo': 'Masculino',
            'nome_mae': 'Test Mother',
            'incapaz': False,
            'nome_responsavel': '',
            'rg': '12.345.678-9',
            'peso': '70kg',
            'altura': '1,70m',
            'escolha_etnia': 'Branco',
            'cns_paciente': '123456789012345',
            'email_paciente': 'test@test.com',
            'cidade_paciente': 'Test City',
            'end_paciente': 'Test Address',
            'cep_paciente': '12345-678',
            'telefone1_paciente': '(11) 99999-9999',
            'telefone2_paciente': '(11) 88888-8888',
            'etnia': 'Branco'
        }
    
    def test_missing_required_parameters(self):
        """Test error handling for missing parameters."""
        # Test missing user
        with self.assertRaises(ValueError):
            Paciente.create_or_update_for_user(None, self.patient_data)
        
        # Test missing patient data
        with self.assertRaises(ValueError):
            Paciente.create_or_update_for_user(self.user, None)
        
        # Test missing CPF
        invalid_data = self.patient_data.copy()
        del invalid_data['cpf_paciente']
        with self.assertRaises(KeyError):
            Paciente.create_or_update_for_user(self.user, invalid_data)
    
    def test_template_filter_error_handling(self):
        """Test template filters handle errors gracefully."""
        patient = Paciente.create_or_update_for_user(self.user, self.patient_data)
        
        # Delete the version assignment to simulate error condition
        PacienteUsuarioVersion.objects.filter(
            paciente_usuario__paciente=patient
        ).delete()
        
        # Should fall back to latest active version for authorized users
        name = patient_name_for_user(patient, self.user)
        self.assertEqual(name, 'Test Patient')  # Should still work with fallback
    
    def test_orphaned_version_cleanup(self):
        """Test handling of orphaned versions."""
        patient = Paciente.create_or_update_for_user(self.user, self.patient_data)
        version = patient.versions.first()
        
        # Remove user-version assignment
        PacienteUsuarioVersion.objects.filter(version=version).delete()
        
        # Should still return version (fallback behavior for authorized users)
        retrieved_version = patient.get_version_for_user(self.user)
        self.assertEqual(retrieved_version, version)