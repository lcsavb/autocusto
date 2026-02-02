"""
Test Doctor Profile Service - Unit tests for doctor profile management business logic.

Testing the uncovered areas from coverage report:
- Lines 63, 73, 78-80: complete_doctor_profile error handling
- Lines 98-117: update_doctor_profile method
- Lines 133, 187-192: get_profile_completion_status edge cases
- Lines 204-208: get_doctor_professional_info method
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from medicos.services.doctor_profile_service import DoctorProfileService
from medicos.models import Medico

User = get_user_model()


class DoctorProfileServiceTest(BaseTestCase):
    """Test DoctorProfileService functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.service = DoctorProfileService()

    def test_complete_doctor_profile_success(self):
        """Test successful doctor profile completion."""
        # Create user with incomplete doctor profile
        user = self.create_test_user(is_medico=True)
        doctor = self.create_test_medico(
            user=user,
            nome_medico=f'Dr. Test {self.unique_suffix}',
            crm_medico=None,  # Incomplete profile
            cns_medico=None
        )
        
        profile_data = {
            'crm': self.data_generator.generate_unique_crm(),
            'cns': self.data_generator.generate_unique_cns_medico(),
            'estado': 'SP',
            'especialidade': 'CARDIOLOGIA'
        }
        
        updated_doctor = self.service.complete_doctor_profile(user, profile_data)
        
        # Verify profile completion
        self.assertIsNotNone(updated_doctor)
        self.assertEqual(updated_doctor.crm_medico, profile_data['crm'])
        self.assertEqual(updated_doctor.cns_medico, profile_data['cns'])
        self.assertEqual(updated_doctor.estado, profile_data['estado'])
        self.assertEqual(updated_doctor.especialidade, profile_data['especialidade'])

    def test_complete_doctor_profile_no_doctor_profile(self):
        """Test profile completion error when user has no doctor profile."""
        # Create user without doctor profile
        user = self.create_test_user(is_medico=True)
        
        profile_data = {
            'crm': self.data_generator.generate_unique_crm(),
            'cns': self.data_generator.generate_unique_cns_medico(),
            'estado': 'SP',
            'especialidade': 'CARDIOLOGIA'
        }
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.service.complete_doctor_profile(user, profile_data)
        
        self.assertEqual(str(context.exception), "User has no associated doctor profile")

    def test_get_profile_completion_status_no_profile(self):
        """Test profile completion status when user has no doctor profile."""
        # Create user without doctor profile
        user = self.create_test_user(is_medico=True)
        
        status = self.service.get_profile_completion_status(user)
        
        # Should indicate no profile exists
        self.assertFalse(status['has_profile'])
        self.assertFalse(status['is_complete'])
        self.assertEqual(status['missing_fields'], ['doctor_profile'])
        self.assertEqual(status['completion_percentage'], 0)