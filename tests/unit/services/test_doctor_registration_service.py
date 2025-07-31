"""
Test Doctor Registration Service - Unit tests for doctor registration business logic.

Testing the uncovered areas from coverage report:
- Lines 57-82: register_new_doctor method
- Lines 94-109: _create_user_account method  
- Lines 119-128: _setup_initial_doctor_settings method
- Lines 140-167: _validate_registration_data method
- Lines 179-195: check_registration_eligibility method
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from medicos.services.doctor_registration_service import DoctorRegistrationService
from medicos.models import Medico

User = get_user_model()


class DoctorRegistrationServiceTest(BaseTestCase):
    """Test DoctorRegistrationService functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.service = DoctorRegistrationService()

    def test_register_new_doctor_success(self):
        """Test successful doctor registration workflow."""
        registration_data = {
            'email': self.data_generator.generate_unique_email(),
            'password1': 'ComplexPassword789!',
            'password2': 'ComplexPassword789!',
            'nome': f'Dr. Test {self.unique_suffix}'
        }
        
        user, doctor = self.service.register_new_doctor(registration_data)
        
        # Verify user creation
        self.assertIsNotNone(user)
        self.assertEqual(user.email, registration_data['email'])
        self.assertTrue(user.is_medico)
        self.assertEqual(user.process_count, 0)
        
        # Verify doctor creation
        self.assertIsNotNone(doctor)
        self.assertEqual(doctor.nome_medico, registration_data['nome'])
        self.assertIn(doctor, user.medicos.all())

    def test_validate_registration_data_missing_required_fields(self):
        """Test validation with missing required fields."""
        registration_data = {
            'email': self.data_generator.generate_unique_email(),
            # Missing password1, password2, nome
        }
        
        errors = self.service._validate_registration_data(registration_data)
        
        # Should have errors for missing fields
        self.assertIn('password1', errors)
        self.assertIn('password2', errors)
        self.assertIn('nome', errors)
        self.assertEqual(errors['password1'], 'password1 é obrigatório')
        self.assertEqual(errors['password2'], 'password2 é obrigatório')
        self.assertEqual(errors['nome'], 'nome é obrigatório')

    def test_validate_registration_data_password_mismatch(self):
        """Test validation with mismatched passwords."""
        registration_data = {
            'email': self.data_generator.generate_unique_email(),
            'password1': 'ComplexPassword789!',
            'password2': 'DifferentPassword456!',
            'nome': f'Dr. Test {self.unique_suffix}'
        }
        
        errors = self.service._validate_registration_data(registration_data)
        
        # Should have password mismatch error
        self.assertIn('password2', errors)
        self.assertEqual(errors['password2'], 'As senhas não coincidem')

    def test_validate_registration_data_duplicate_email(self):
        """Test validation with duplicate email."""
        # Create existing user
        existing_email = self.data_generator.generate_unique_email()
        self.create_test_user(email=existing_email, is_medico=True)
        
        registration_data = {
            'email': existing_email,  # Using same email
            'password1': 'ComplexPassword789!',
            'password2': 'ComplexPassword789!',
            'nome': f'Dr. Test {self.unique_suffix}'
        }
        
        errors = self.service._validate_registration_data(registration_data)
        
        # Should have email already exists error
        self.assertIn('email', errors)
        self.assertEqual(errors['email'], 'Este email já está cadastrado')

    def test_check_registration_eligibility_eligible_email(self):
        """Test eligibility check with new email."""
        new_email = self.data_generator.generate_unique_email()
        
        result = self.service.check_registration_eligibility(new_email)
        
        # Should be eligible
        self.assertTrue(result['eligible'])
        self.assertEqual(result['reasons'], [])

    def test_check_registration_eligibility_existing_email(self):
        """Test eligibility check with existing email."""
        # Create existing user
        existing_email = self.data_generator.generate_unique_email()
        self.create_test_user(email=existing_email, is_medico=True)
        
        result = self.service.check_registration_eligibility(existing_email)
        
        # Should not be eligible
        self.assertFalse(result['eligible'])
        self.assertIn('Email já cadastrado no sistema', result['reasons'])