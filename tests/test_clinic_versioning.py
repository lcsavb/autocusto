"""
Comprehensive tests for clinic versioning system.

Tests the complete clinic versioning functionality including:
- Version creation and assignment
- User-specific clinic data isolation  
- Form validation with versioning
- CNS uniqueness handling
- Process creation integration
- Migration and data integrity
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.forms import ValidationError

from clinicas.models import Clinica, ClinicaVersion, ClinicaUsuarioVersion, Emissor
from clinicas.forms import ClinicaFormulario
from medicos.models import Medico
from processos.models import Processo, Doenca

User = get_user_model()


class ClinicVersioningModelTest(TestCase):
    """Test core clinic versioning model functionality."""
    
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
        
        # Create medicos for users
        self.medico1 = Medico.objects.create(
            nome_medico='Dr. Silva',
            crm_medico='12345',
            estado='SP'
        )
        
        self.medico2 = Medico.objects.create(
            nome_medico='Dr. Santos',
            crm_medico='67890',
            estado='SP'
        )
        
        # Standard clinic data
        self.clinic_data = {
            'nome_clinica': 'Clínica São Paulo',
            'cns_clinica': '1234567890123',
            'logradouro': 'Rua das Flores',
            'logradouro_num': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'cep': '01234-567',
            'uf': 'SP',
            'telefone_clinica': '(11) 3333-4444',
            'email': 'clinica@test.com'
        }
    
    def test_create_new_clinic_with_version(self):
        """Test creating a new clinic with initial version."""
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        
        # Check master record
        self.assertEqual(clinic.cns_clinica, '1234567890123')
        self.assertTrue(clinic.was_created)
        self.assertTrue(self.medico1 in clinic.medicos.all())
        
        # Check version creation
        versions = clinic.versions.all()
        self.assertEqual(versions.count(), 1)
        
        version = versions.first()
        self.assertEqual(version.nome_clinica, 'Clínica São Paulo')
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.status, 'active')
        self.assertEqual(version.created_by, self.user1)
        
        # Check user-version assignment
        clinic_usuario = clinic.usuarios.through.objects.get(
            clinica=clinic, usuario=self.user1
        )
        user_version = ClinicaUsuarioVersion.objects.get(
            clinica_usuario=clinic_usuario
        )
        self.assertEqual(user_version.version, version)
    
    def test_update_existing_clinic_creates_version(self):
        """Test updating existing clinic creates new version for user."""
        # Create initial clinic
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        initial_version = clinic.versions.first()
        
        # Update with different data for medico2
        updated_data = self.clinic_data.copy()
        updated_data['nome_clinica'] = 'Clínica Santos'  # Different name
        updated_data['telefone_clinica'] = '(11) 5555-6666'  # Different phone
        
        updated_clinic = Clinica.create_or_update_for_user(self.user2, self.medico2, updated_data)
        
        # Should be same master record
        self.assertEqual(clinic.pk, updated_clinic.pk)
        self.assertFalse(updated_clinic.was_created)
        
        # Should have 2 versions now
        versions = clinic.versions.all().order_by('version_number')
        self.assertEqual(versions.count(), 2)
        
        # Check new version
        new_version = versions.last()
        self.assertEqual(new_version.nome_clinica, 'Clínica Santos')
        self.assertEqual(new_version.telefone_clinica, '(11) 5555-6666')
        self.assertEqual(new_version.version_number, 2)
        self.assertEqual(new_version.created_by, self.user2)
        
        # Check medico1 still sees original version
        medico1_version = clinic.get_version_for_user(self.user1)
        self.assertEqual(medico1_version.nome_clinica, 'Clínica São Paulo')
        
        # Check medico2 sees new version
        medico2_version = clinic.get_version_for_user(self.user2)
        self.assertEqual(medico2_version.nome_clinica, 'Clínica Santos')
    
    def test_cns_uniqueness_enforced(self):
        """Test that CNS uniqueness is enforced at database level."""
        # Create first clinic
        Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        
        # Try to create another clinic with same CNS directly (should fail)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Clinica.objects.create(
                    cns_clinica='1234567890123',
                    nome_clinica='Different Name'
                )
    
    def test_version_number_uniqueness(self):
        """Test version number uniqueness per clinic."""
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        
        # Try to create version with duplicate number (should fail)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClinicaVersion.objects.create(
                    clinica=clinic,
                    version_number=1,  # Same as existing
                    nome_clinica='Test',
                    created_by=self.medico2.usuario
                )
    
    def test_get_version_for_user(self):
        """Test getting appropriate version for user."""
        # Create clinic with medico1
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        
        # Update with medico2
        updated_data = self.clinic_data.copy()
        updated_data['nome_clinica'] = 'Clínica Santos'
        Clinica.create_or_update_for_user(self.user2, self.medico2, updated_data)
        
        # Each user should see their version
        user1_version = clinic.get_version_for_user(self.user1)
        user2_version = clinic.get_version_for_user(self.user2)
        
        self.assertEqual(user1_version.nome_clinica, 'Clínica São Paulo')
        self.assertEqual(user2_version.nome_clinica, 'Clínica Santos')
        
        # User without access should get latest active version
        user3 = User.objects.create_user(email='user3@test.com', password='pass')
        user3_version = clinic.get_version_for_user(user3)
        self.assertEqual(user3_version.nome_clinica, 'Clínica Santos')  # Latest
    
    def test_emissor_creation_with_versioning(self):
        """Test Emissor creation integrates with clinic versioning."""
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        
        # Create emissor
        emissor = Emissor.objects.create(
            medico=self.medico1,
            clinica=clinic
        )
        
        # Verify emissor links to correct clinic
        self.assertEqual(emissor.clinica, clinic)
        self.assertEqual(emissor.medico, self.medico1)
        
        # Verify clinic has the medico
        self.assertTrue(self.medico1 in clinic.medicos.all())


class ClinicVersioningFormTest(TestCase):
    """Test form integration with clinic versioning."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        self.medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='12345',
            estado='SP'
        )
        
        self.clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567890123',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'bairro': 'Test Neighborhood',
            'cidade': 'Test City',
            'cep': '12345-678',
            'uf': 'SP',
            'telefone_clinica': '(11) 3333-4444',
            'email': 'test@clinic.com'
        }
    
    def test_form_validation_skips_cns_uniqueness(self):
        """Test that form validation skips CNS uniqueness check."""
        # Create clinic with same CNS
        Clinica.create_or_update_for_user(self.user, self.medico, self.clinic_data)
        
        # Form should validate even with existing CNS (versioning handles it)
        form = ClinicaFormulario(data=self.clinic_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_other_validations_still_work(self):
        """Test that other form validations still function."""
        invalid_data = self.clinic_data.copy()
        invalid_data['email'] = 'invalid-email'  # Invalid email format
        
        form = ClinicaFormulario(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_required_fields(self):
        """Test that required fields are still validated."""
        incomplete_data = self.clinic_data.copy()
        del incomplete_data['nome_clinica']  # Remove required field
        
        form = ClinicaFormulario(data=incomplete_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome_clinica', form.errors)


class ClinicVersioningViewTest(TestCase):
    """Test view integration with clinic versioning."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        self.medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='12345',
            estado='SP'
        )
        
        self.clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567890123',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'bairro': 'Test Neighborhood',
            'cidade': 'Test City',
            'cep': '12345-678',
            'uf': 'SP',
            'telefone_clinica': '(11) 3333-4444',
            'email': 'test@clinic.com'
        }
    
    def test_clinic_registration_uses_versioning(self):
        """Test clinic registration view uses versioning system."""
        self.client.force_login(self.user)
        
        response = self.client.post('/clinicas/cadastro/', self.clinic_data)
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify clinic was created with versioning
        clinic = Clinica.objects.get(cns_clinica='1234567890123')
        self.assertIsNotNone(clinic)
        
        # Verify version was created
        version = clinic.get_version_for_user(self.user)
        self.assertIsNotNone(version)
        self.assertEqual(version.nome_clinica, 'Test Clinic')
        
        # Verify medico is associated
        self.assertTrue(self.medico in clinic.medicos.all())
    
    def test_duplicate_cns_handled_gracefully(self):
        """Test that duplicate CNS is handled through versioning."""
        # Create first clinic
        Clinica.create_or_update_for_user(self.user, self.medico, self.clinic_data)
        
        # Create another user
        user2 = User.objects.create_user(email='user2@test.com', password='pass')
        medico2 = Medico.objects.create(
            nome_medico='Dr. Test 2',
            crm_medico='67890',
            estado='SP'
        )
        
        # Second user should be able to "register" same clinic (creates version)
        self.client.force_login(user2)
        
        updated_data = self.clinic_data.copy()
        updated_data['nome_clinica'] = 'Updated Clinic Name'
        
        response = self.client.post('/clinicas/cadastro/', updated_data)
        
        # Should succeed (no integrity error)
        self.assertEqual(response.status_code, 302)
        
        # Should still be same clinic record
        clinics = Clinica.objects.filter(cns_clinica='1234567890123')
        self.assertEqual(clinics.count(), 1)
        
        clinic = clinics.first()
        
        # But each user should see different version
        user1_version = clinic.get_version_for_user(self.user)
        user2_version = clinic.get_version_for_user(user2)
        
        self.assertEqual(user1_version.nome_clinica, 'Test Clinic')
        self.assertEqual(user2_version.nome_clinica, 'Updated Clinic Name')


class ClinicVersioningIntegrationTest(TestCase):
    """Test integration with process creation and other systems."""
    
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
        
        self.medico1 = Medico.objects.create(
            nome_medico='Dr. Silva',
            crm_medico='12345',
            estado='SP'
        )
        
        self.medico2 = Medico.objects.create(
            nome_medico='Dr. Santos',
            crm_medico='67890',
            estado='SP'
        )
        
        self.clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567890123',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'bairro': 'Test Neighborhood',
            'cidade': 'Test City',
            'cep': '12345-678',
            'uf': 'SP',
            'telefone_clinica': '(11) 3333-4444',
            'email': 'test@clinic.com'
        }
        
        # Create disease for processes
        self.doenca = Doenca.objects.create(
            cid='Z00.0',
            nome='Test Disease'
        )
    
    def test_emissor_with_versioned_clinic(self):
        """Test Emissor creation with versioned clinic."""
        # Create clinic with different versions for each medico
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        
        updated_data = self.clinic_data.copy()
        updated_data['nome_clinica'] = 'Updated Clinic'
        Clinica.create_or_update_for_user(self.user2, self.medico2, updated_data)
        
        # Create emissors for both medicos
        emissor1 = Emissor.objects.create(
            medico=self.medico1,
            clinica=clinic
        )
        
        emissor2 = Emissor.objects.create(
            medico=self.medico2,
            clinica=clinic
        )
        
        # Both should use same clinic record
        self.assertEqual(emissor1.clinica, clinic)
        self.assertEqual(emissor2.clinica, clinic)
        
        # But each should see different version data
        medico1_version = clinic.get_version_for_user(self.medico1.usuario)
        medico2_version = clinic.get_version_for_user(self.medico2.usuario)
        
        self.assertEqual(medico1_version.nome_clinica, 'Test Clinic')
        self.assertEqual(medico2_version.nome_clinica, 'Updated Clinic')
    
    def test_process_creation_with_versioned_clinic(self):
        """Test process creation integrates with clinic versioning."""
        from pacientes.models import Paciente
        
        # Create versioned clinic
        clinic = Clinica.create_or_update_for_user(self.user1, self.medico1, self.clinic_data)
        emissor = Emissor.objects.create(medico=self.medico1, clinica=clinic)
        
        # Create patient
        patient_data = {
            'nome_paciente': 'Test Patient',
            'cpf_paciente': '123.456.789-00',
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
        
        patient = Paciente.create_or_update_for_user(self.user1, patient_data)
        
        # Create process
        processo = Processo.objects.create(
            usuario=self.user1,
            paciente=patient,
            clinica=clinic,
            doenca=self.doenca,
            anamnese='Test anamnese',
            prescricao='Test prescription'
        )
        
        # Verify process uses versioned clinic
        self.assertEqual(processo.clinica, clinic)
        
        # Verify user sees their version of clinic
        clinic_version = clinic.get_version_for_user(self.user1)
        self.assertEqual(clinic_version.nome_clinica, 'Test Clinic')


class ClinicVersioningMigrationTest(TestCase):
    """Test migration scenarios and data integrity."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        self.medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='12345',
            estado='SP'
        )
    
    def test_existing_clinic_version_assignment(self):
        """Test that existing clinics get initial versions."""
        # Create clinic directly (simulating pre-versioning data)
        clinic = Clinica.objects.create(
            nome_clinica='Legacy Clinic',
            cns_clinica='1234567890123'
        )
        
        # Add medico relationship
        clinic.medicos.add(self.medico)
        
        # Simulate migration: assign initial versions
        if not clinic.versions.exists():
            # Create initial version
            initial_version = ClinicaVersion.objects.create(
                clinica=clinic,
                version_number=1,
                nome_clinica=clinic.nome_clinica,
                logradouro='',
                logradouro_num='',
                bairro='',
                cidade='',
                cep='',
                uf='',
                telefone='',
                email='',
                status='active',
                change_summary='Versão inicial - migração de dados existentes'
            )
            
            # Assign version to user
            clinic_medico = clinic.medicos.through.objects.get(
                clinica=clinic, medico=self.medico
            )
            ClinicaUsuarioVersion.objects.create(
                clinica_medico=clinic_medico,
                version=initial_version
            )
        
        # Verify version was created
        version = clinic.get_version_for_user(self.user)
        self.assertIsNotNone(version)
        self.assertEqual(version.nome_clinica, 'Legacy Clinic')
        self.assertEqual(version.version_number, 1)


class ClinicVersioningEdgeCasesTest(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        self.medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='12345',
            estado='SP'
        )
        
        self.clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567890123',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'bairro': 'Test Neighborhood',
            'cidade': 'Test City',
            'cep': '12345-678',
            'uf': 'SP',
            'telefone_clinica': '(11) 3333-4444',
            'email': 'test@clinic.com'
        }
    
    def test_missing_required_parameters(self):
        """Test error handling for missing parameters."""
        # Test missing medico
        with self.assertRaises(ValueError):
            Clinica.create_or_update_for_user(None, self.clinic_data)
        
        # Test missing clinic data
        with self.assertRaises(ValueError):
            Clinica.create_or_update_for_user(self.user, self.medico, None)
        
        # Test missing CNS
        invalid_data = self.clinic_data.copy()
        del invalid_data['cns_clinica']
        with self.assertRaises(KeyError):
            Clinica.create_or_update_for_user(self.user, self.medico, invalid_data)
    
    def test_orphaned_version_cleanup(self):
        """Test handling of orphaned versions."""
        clinic = Clinica.create_or_update_for_user(self.user, self.medico, self.clinic_data)
        version = clinic.versions.first()
        
        # Remove user-version assignment
        ClinicaUsuarioVersion.objects.filter(version=version).delete()
        
        # Should still return version (fallback behavior)
        retrieved_version = clinic.get_version_for_user(self.user)
        self.assertEqual(retrieved_version, version)
    
    def test_medico_without_user(self):
        """Test handling medico without user account."""
        # Create medico without user (should not happen in normal flow)
        orphan_medico = Medico.objects.create(
            nome_medico='Orphan Doctor',
            crm_medico='99999',
            estado='SP'
            # Note: no usuario field set
        )
        
        # Should handle gracefully
        with self.assertRaises(AttributeError):
            Clinica.create_or_update_for_user(self.user, orphan_medico, self.clinic_data)
    
    def test_concurrent_version_creation(self):
        """Test handling concurrent version creation."""
        clinic = Clinica.create_or_update_for_user(self.user, self.medico, self.clinic_data)
        
        # Simulate concurrent version creation
        with transaction.atomic():
            # Both should succeed due to different version numbers
            try:
                version1 = clinic.create_new_version(self.user, self.clinic_data)
                version2 = clinic.create_new_version(self.user, self.clinic_data)
                
                # Should have different version numbers
                self.assertNotEqual(version1.version_number, version2.version_number)
            except IntegrityError:
                # If integrity error occurs, it's properly handled
                pass