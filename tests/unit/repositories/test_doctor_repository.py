"""
Test Doctor Repository - Unit tests for doctor data access layer.

Testing the uncovered areas from coverage report:
- Lines 50, 52-54: get_doctor_by_user error handling
- Lines 70-86: create_doctor method  
- Lines 103, 129-134: update_doctor method
- Lines 146-151, 163-169: check methods
- Lines 197, 240-244: extract_doctor_data and check_email_exists
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django.contrib.auth import get_user_model

from medicos.repositories.doctor_repository import DoctorRepository
from medicos.models import Medico

User = get_user_model()


class DoctorRepositoryTest(BaseTestCase):
    """Test DoctorRepository functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.repository = DoctorRepository()

    def test_create_doctor_success(self):
        """Test successful doctor creation."""
        user = self.create_test_user(is_medico=True)
        doctor_data = {
            'nome_medico': f'Dr. Test {self.unique_suffix}',
            'crm_medico': self.data_generator.generate_unique_crm(),
            'cns_medico': self.data_generator.generate_unique_cns_medico(),
            'estado': 'SP',
            'especialidade': 'CARDIOLOGIA'
        }
        
        doctor = self.repository.create_doctor(user, doctor_data)
        
        # Verify doctor creation
        self.assertIsNotNone(doctor)
        self.assertEqual(doctor.nome_medico, doctor_data['nome_medico'])
        self.assertEqual(doctor.crm_medico, doctor_data['crm_medico'])
        self.assertEqual(doctor.cns_medico, doctor_data['cns_medico'])
        self.assertEqual(doctor.estado, doctor_data['estado'])
        self.assertEqual(doctor.especialidade, doctor_data['especialidade'])
        
        # Verify association with user
        self.assertIn(doctor, user.medicos.all())

    def test_check_doctor_exists_by_crm_exists(self):
        """Test checking for existing CRM+Estado combination."""
        # Create a doctor with specific CRM and Estado
        user = self.create_test_user(is_medico=True)
        crm = self.data_generator.generate_unique_crm()
        estado = 'SP'
        
        self.create_test_medico(
            user=user,
            crm_medico=crm,
            estado=estado
        )
        
        # Check if CRM+Estado exists
        exists = self.repository.check_doctor_exists_by_crm(crm, estado)
        
        # Should return True
        self.assertTrue(exists)

    def test_check_doctor_exists_by_cns_exists(self):
        """Test checking for existing CNS."""
        # Create a doctor with specific CNS
        user = self.create_test_user(is_medico=True)
        cns = self.data_generator.generate_unique_cns_medico()
        
        self.create_test_medico(
            user=user,
            cns_medico=cns
        )
        
        # Check if CNS exists
        exists = self.repository.check_doctor_exists_by_cns(cns)
        
        # Should return True
        self.assertTrue(exists)