"""
Security tests for the versioning system to verify no data leaks between users.

These tests ensure that users cannot access other users' patient or clinic data
through any fallback mechanisms or security vulnerabilities.
"""

import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from cpf_generator import CPF

from pacientes.models import Paciente, PacienteVersion, PacienteUsuarioVersion
from clinicas.models import Clinica, ClinicaVersion, ClinicaUsuarioVersion
from medicos.models import Medico
from pacientes.templatetags.patient_tags import patient_name_for_user, patient_data_for_user

User = get_user_model()


class VersioningSecurityTestCase(TestCase):
    """Base test case with security-focused setup"""
    
    def setUp(self):
        # Create two users who should NOT see each other's data
        self.user1 = User.objects.create_user(email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(email='user2@test.com', password='pass123')
        
        # Create doctors for both users
        self.medico1 = Medico.objects.create(
            nome_medico='Dr. User1',
            cns_medico='1234567890123',
            crm_medico='12345-SP'
        )
        self.medico2 = Medico.objects.create(
            nome_medico='Dr. User2', 
            cns_medico='1234567890124',
            crm_medico='12346-SP'
        )
        
        # Create shared patient with different versions for each user
        self.shared_patient = Paciente.objects.create(cpf_paciente=CPF.generate(),
            incapaz=False
        )
        self.shared_patient.usuarios.add(self.user1, self.user2)
        
        # User1's version
        version1 = PacienteVersion.objects.create(
            paciente=self.shared_patient,
            version_number=1,
            created_by=self.user1,
            nome_paciente='User1 Version Name',
            idade='30',
            status='active'
        ,
            incapaz=False
        )
        
        # User2's version
        version2 = PacienteVersion.objects.create(
            paciente=self.shared_patient,
            version_number=2,
            created_by=self.user2,
            nome_paciente='User2 Version Name',
            idade='35',
            status='active'
        ,
            incapaz=False
        )
        
        # Assign versions to users
        user1_rel = self.shared_patient.usuarios.through.objects.get(
            paciente=self.shared_patient, usuario=self.user1
        )
        user2_rel = self.shared_patient.usuarios.through.objects.get(
            paciente=self.shared_patient, usuario=self.user2
        )
        
        PacienteUsuarioVersion.objects.create(paciente_usuario=user1_rel, version=version1)
        PacienteUsuarioVersion.objects.create(paciente_usuario=user2_rel, version=version2)
        
        # Create shared clinic with different versions
        self.shared_clinic = Clinica.objects.create(
            cns_clinica='1234567',
            nome_clinica='Master Clinic Name'
        )
        self.shared_clinic.usuarios.add(self.user1, self.user2)
        self.shared_clinic.medicos.add(self.medico1, self.medico2)
        
        # User1's clinic version
        clinic_version1 = ClinicaVersion.objects.create(
            clinica=self.shared_clinic,
            version_number=1,
            created_by=self.user1,
            nome_clinica='User1 Clinic Version',
            status='active'
        )
        
        # User2's clinic version  
        clinic_version2 = ClinicaVersion.objects.create(
            clinica=self.shared_clinic,
            version_number=2,
            created_by=self.user2,
            nome_clinica='User2 Clinic Version', 
            status='active'
        )
        
        # Assign clinic versions to users
        from clinicas.models import ClinicaUsuario
        user1_clinic_rel = ClinicaUsuario.objects.get(clinica=self.shared_clinic, usuario=self.user1)
        user2_clinic_rel = ClinicaUsuario.objects.get(clinica=self.shared_clinic, usuario=self.user2)
        
        ClinicaUsuarioVersion.objects.create(clinica_usuario=user1_clinic_rel, version=clinic_version1)
        ClinicaUsuarioVersion.objects.create(clinica_usuario=user2_clinic_rel, version=clinic_version2)


class PatientAjaxSecurityTest(VersioningSecurityTestCase):
    """Test AJAX patient search endpoint security"""
    
    def test_ajax_patient_search_no_cross_user_data_leak(self):
        """Test that AJAX patient search doesn't leak data between users"""
        client = Client()
        
        # Login as user1
        client.login(email='user1@test.com', password='pass123')
        
        # Make AJAX request
        response = client.get('/pacientes/ajax/busca', {'palavraChave': 'User2'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        
        # User1 should NOT see "User2 Version Name" even though they share the patient
        patient_names = [p['nome_paciente'] for p in data]
        self.assertNotIn('User2 Version Name', patient_names)
        
        # User1 should only see their own version
        if patient_names:  # If any patients returned
            self.assertIn('User1 Version Name', patient_names)
    
    def test_ajax_patient_search_without_version_access(self):
        """Test AJAX search when user has no version access to a patient"""
        # Generate valid CPF for test
        orphan_cpf = CPF.generate()
        
        # Create patient without version for user1
        orphan_patient = Paciente.objects.create(cpf_paciente=orphan_cpf,
            incapaz=False
        )
        orphan_patient.usuarios.add(self.user1)  # User has relationship but no version
        
        client = Client()
        client.login(email='user1@test.com', password='pass123')
        
        with self.assertLogs('pacientes', level='WARNING') as log:
            response = client.get('/pacientes/ajax/busca')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.content)
            
            # Should not include the orphan patient in results
            cpfs = [p['cpf_paciente'] for p in data]
            self.assertNotIn(orphan_cpf, cpfs)
            
            # Should log security warning
            self.assertTrue(any(f'Security: Patient CPF {orphan_cpf} skipped' in msg for msg in log.output))


class ClinicAjaxSecurityTest(VersioningSecurityTestCase):
    """Test clinic AJAX endpoint security"""
    
    def test_clinic_listing_no_cross_user_data_leak(self):
        """Test that clinic listing doesn't leak data between users"""
        client = Client()
        
        # Login as user1
        client.login(email='user1@test.com', password='pass123')
        
        response = client.get('/clinicas/list/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        
        # User1 should only see their clinic version
        clinic_names = [c['nome_clinica'] for c in data]
        self.assertNotIn('User2 Clinic Version', clinic_names)
        self.assertIn('User1 Clinic Version', clinic_names)
    
    def test_clinic_detail_without_version_access(self):
        """Test clinic detail endpoint when user has no version access"""
        # Create clinic without version for user1
        orphan_clinic = Clinica.objects.create(
            cns_clinica='9999999',
            nome_clinica='Orphan Clinic'
        )
        orphan_clinic.usuarios.add(self.user1)  # User has relationship but no version
        
        client = Client()
        client.login(email='user1@test.com', password='pass123')
        
        with self.assertLogs('clinicas.views', level='WARNING') as log:
            response = client.get(f'/clinicas/get/{orphan_clinic.id}/')
            
            # Should return 404 as if clinic doesn't exist
            self.assertEqual(response.status_code, 404)
            
            # Should log security warning
            self.assertTrue(any('Security: Clinic' in msg for msg in log.output))


class TemplateFilterSecurityTest(VersioningSecurityTestCase):
    """Test template filter security"""
    
    def test_patient_name_filter_no_fallback_to_master(self):
        """Test patient name filter doesn't fall back to master record"""
        # Create patient without version for user1
        orphan_patient = Paciente.objects.create(
            cpf_paciente=CPF.generate(),
            nome_paciente='MASTER RECORD NAME'
        ,
            incapaz=False
        )
        orphan_patient.usuarios.add(self.user1)
        
        with self.assertLogs('pacientes.templatetags.patient_tags', level='WARNING') as log:
            result = patient_name_for_user(orphan_patient, self.user1)
            
            # Should NOT return master record name
            self.assertNotEqual(result, 'MASTER RECORD NAME')
            self.assertEqual(result, '[Acesso Negado]')
            
            # Should log security warning
            self.assertTrue(any('Security: Template access denied' in msg for msg in log.output))
    
    def test_patient_data_filter_no_fallback_to_master(self):
        """Test patient data filter doesn't fall back to master record"""
        orphan_patient = Paciente.objects.create(
            cpf_paciente=CPF.generate(),
            nome_paciente='MASTER DATA'
        ,
            incapaz=False
        )
        orphan_patient.usuarios.add(self.user1)
        
        with self.assertLogs('pacientes.templatetags.patient_tags', level='WARNING') as log:
            result = patient_data_for_user(orphan_patient, self.user1)
            
            # Should return None, not master record
            self.assertIsNone(result)
            
            # Should log security warning
            self.assertTrue(any('Security: Template data access denied' in msg for msg in log.output))
    
    def test_cross_user_template_filter_isolation(self):
        """Test that template filters don't leak data between users"""
        # User1 should only see their version through template filter
        user1_name = patient_name_for_user(self.shared_patient, self.user1)
        user2_name = patient_name_for_user(self.shared_patient, self.user2)
        
        self.assertEqual(user1_name, 'User1 Version Name')
        self.assertEqual(user2_name, 'User2 Version Name')
        
        # Verify data isolation
        self.assertNotEqual(user1_name, user2_name)


class ModelMethodSecurityTest(VersioningSecurityTestCase):
    """Test model method security"""
    
    def test_get_name_for_user_no_fallback(self):
        """Test get_name_for_user method doesn't fall back to master record"""
        orphan_patient = Paciente.objects.create(
            cpf_paciente=CPF.generate(),
            nome_paciente='MASTER NAME'
        ,
            incapaz=False
        )
        orphan_patient.usuarios.add(self.user1)
        
        with self.assertLogs('pacientes.models', level='WARNING') as log:
            result = orphan_patient.get_name_for_user(self.user1)
            
            # Should return None, not master record name
            self.assertIsNone(result)
            
            # Should log security warning
            self.assertTrue(any('Security: Model method access denied' in msg for msg in log.output))
    
    def test_patient_search_model_method_no_fallback(self):
        """Test patient search model method doesn't include patients without versions"""
        orphan_cpf = CPF.generate()
        orphan_patient = Paciente.objects.create(cpf_paciente=orphan_cpf,
            incapaz=False
        )
        orphan_patient.usuarios.add(self.user1)
        
        with self.assertLogs('pacientes.models', level='WARNING') as log:
            results = Paciente.get_patients_for_user_search(self.user1)
            
            # Should not include orphan patient
            patient_cpfs = [p[0].cpf_paciente for p in results]
            self.assertNotIn(orphan_cpf, patient_cpfs)
            
            # Should log security warning
            self.assertTrue(any(f'Security: Patient CPF {orphan_cpf} skipped' in msg for msg in log.output))


class ComprehensiveSecurityTest(VersioningSecurityTestCase):
    """Comprehensive security tests to verify no data leaks anywhere"""
    
    def test_no_master_record_exposure_anywhere(self):
        """Comprehensive test to ensure master records are never exposed"""
        # Create patient with sensitive master record data
        sensitive_patient = Paciente.objects.create(
            cpf_paciente=CPF.generate(),
            nome_paciente='SENSITIVE_MASTER_DATA_SHOULD_NEVER_BE_VISIBLE'
        ,
            incapaz=False
        )
        sensitive_patient.usuarios.add(self.user1)
        
        # Create user version with different data
        version = PacienteVersion.objects.create(
            paciente=sensitive_patient,
            version_number=1,
            created_by=self.user1,
            nome_paciente='Safe User Version',
            status='active'
        ,
            incapaz=False
        )
        
        user_rel = sensitive_patient.usuarios.through.objects.get(
            paciente=sensitive_patient, usuario=self.user1
        )
        PacienteUsuarioVersion.objects.create(paciente_usuario=user_rel, version=version)
        
        # Test all possible access methods
        client = Client()
        client.login(email='user1@test.com', password='pass123')
        
        # 1. AJAX search
        response = client.get('/pacientes/ajax/busca')
        content = response.content.decode('utf-8')
        self.assertNotIn('SENSITIVE_MASTER_DATA', content)
        
        # 2. Template filters
        name = patient_name_for_user(sensitive_patient, self.user1)
        self.assertNotIn('SENSITIVE_MASTER_DATA', name)
        
        data = patient_data_for_user(sensitive_patient, self.user1)
        if data:
            self.assertNotIn('SENSITIVE_MASTER_DATA', str(data.nome_paciente))
        
        # 3. Model methods
        model_name = sensitive_patient.get_name_for_user(self.user1)
        if model_name:
            self.assertNotIn('SENSITIVE_MASTER_DATA', model_name)
        
        # 4. Search method
        search_results = Paciente.get_patients_for_user_search(self.user1)
        for patient, version in search_results:
            if version:
                self.assertNotIn('SENSITIVE_MASTER_DATA', version.nome_paciente)
    
    def test_complete_user_isolation(self):
        """Test complete isolation between user1 and user2 data"""
        client = Client()
        
        # Login as user2
        client.login(email='user2@test.com', password='pass123')
        
        # User2 should never see any trace of "User1 Version Name"
        
        # Check AJAX search
        response = client.get('/pacientes/ajax/busca', {'palavraChave': 'User1'})
        content = response.content.decode('utf-8') 
        self.assertNotIn('User1 Version Name', content)
        
        # Check clinic listing
        response = client.get('/clinicas/list/')
        content = response.content.decode('utf-8')
        self.assertNotIn('User1 Clinic Version', content)
        
        # Check template filters
        user2_patient_name = patient_name_for_user(self.shared_patient, self.user2)
        self.assertNotEqual(user2_patient_name, 'User1 Version Name')
        self.assertEqual(user2_patient_name, 'User2 Version Name')