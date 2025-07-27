"""
Unit Tests for PatientRepository

Tests the repository layer in isolation with minimal dependencies.
Focuses on data access patterns, query construction, and repository interface compliance.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from processos.repositories.patient_repository import PatientRepository
from pacientes.models import Paciente

User = get_user_model()


class TestPatientRepositoryUnit(TestCase):
    """Unit tests for PatientRepository data access methods."""
    
    def setUp(self):
        self.repo = PatientRepository()
        self.mock_user = Mock()
        self.mock_user.email = "test@example.com"
        self.mock_user.id = 1
        
    def test_repository_initialization(self):
        """Test repository initializes correctly."""
        repo = PatientRepository()
        self.assertIsNotNone(repo.logger)
        self.assertIsNotNone(repo.patient_versioning)
        
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_check_patient_exists_found(self, mock_objects):
        """Test check_patient_exists returns patient when found."""
        # Arrange
        mock_patient = Mock()
        mock_patient.id = 123
        mock_objects.get.return_value = mock_patient
        
        # Act
        result = self.repo.check_patient_exists("12345678901")
        
        # Assert
        mock_objects.get.assert_called_once_with(cpf_paciente="12345678901")
        self.assertEqual(result, mock_patient)
        
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_check_patient_exists_not_found(self, mock_objects):
        """Test check_patient_exists returns False when not found."""
        # Arrange
        mock_objects.get.side_effect = Paciente.DoesNotExist()
        
        # Act
        result = self.repo.check_patient_exists("12345678901")
        
        # Assert
        mock_objects.get.assert_called_once_with(cpf_paciente="12345678901")
        self.assertFalse(result)
        
    def test_extract_patient_data_complete_form(self):
        """Test extract_patient_data extracts all patient fields."""
        # Arrange
        form_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': '12345678901',
            'peso': '70kg',
            'altura': '1.75m',
            'nome_mae': 'Maria Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'etnia': 'parda',
            'telefone1_paciente': '11999999999',
            'telefone2_paciente': '1133333333',
            'email_paciente': 'joao@email.com',
            'end_paciente': 'Rua A, 123',
            'extra_field': 'should not be included'  # Non-patient field
        }
        
        # Act
        result = self.repo.extract_patient_data(form_data)
        
        # Assert
        expected_fields = [
            'nome_paciente', 'cpf_paciente', 'peso', 'altura', 'nome_mae',
            'incapaz', 'nome_responsavel', 'etnia', 'telefone1_paciente',
            'telefone2_paciente', 'email_paciente', 'end_paciente'
        ]
        
        for field in expected_fields:
            self.assertIn(field, result)
            self.assertEqual(result[field], form_data[field])
            
        # Extra field should not be included
        self.assertNotIn('extra_field', result)
        
    def test_extract_patient_data_partial_form(self):
        """Test extract_patient_data handles partial data."""
        # Arrange
        form_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': '12345678901',
            # Missing other fields
        }
        
        # Act
        result = self.repo.extract_patient_data(form_data)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result['nome_paciente'], 'João Silva')
        self.assertEqual(result['cpf_paciente'], '12345678901')
        
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_get_patients_by_user(self, mock_objects):
        """Test get_patients_by_user filters correctly."""
        # Arrange
        mock_queryset = Mock()
        mock_objects.filter.return_value.distinct.return_value = mock_queryset
        mock_queryset.count.return_value = 5
        
        # Act
        result = self.repo.get_patients_by_user(self.mock_user)
        
        # Assert
        mock_objects.filter.assert_called_once_with(versions__usuario=self.mock_user)
        self.assertEqual(result, mock_queryset)
        
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_get_patient_by_cpf_for_user_found(self, mock_objects):
        """Test get_patient_by_cpf_for_user returns patient when found."""
        # Arrange
        mock_patient = Mock()
        mock_patient.id = 123
        mock_objects.get.return_value = mock_patient
        
        # Act
        result = self.repo.get_patient_by_cpf_for_user("12345678901", self.mock_user)
        
        # Assert
        mock_objects.get.assert_called_once_with(
            cpf_paciente="12345678901",
            usuarios=self.mock_user
        )
        self.assertEqual(result, mock_patient)
        
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_get_patient_by_cpf_for_user_not_found(self, mock_objects):
        """Test get_patient_by_cpf_for_user raises exception when not found."""
        # Arrange
        mock_objects.get.side_effect = Paciente.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Paciente.DoesNotExist):
            self.repo.get_patient_by_cpf_for_user("12345678901", self.mock_user)
            
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_get_patient_by_id_found(self, mock_objects):
        """Test get_patient_by_id returns patient when found."""
        # Arrange
        mock_patient = Mock()
        mock_patient.id = 123
        mock_patient.cpf_paciente = "12345678901"
        mock_objects.get.return_value = mock_patient
        
        # Act
        result = self.repo.get_patient_by_id(123)
        
        # Assert
        mock_objects.get.assert_called_once_with(id=123)
        self.assertEqual(result, mock_patient)
        
    @patch('processos.repositories.patient_repository.Paciente.objects')
    def test_get_patient_by_id_not_found(self, mock_objects):
        """Test get_patient_by_id raises exception when not found."""
        # Arrange
        mock_objects.get.side_effect = Paciente.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Paciente.DoesNotExist):
            self.repo.get_patient_by_id(123)
            
    def test_validate_patient_data_valid(self):
        """Test validate_patient_data with valid data."""
        # Arrange
        valid_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': '12345678901',
            'email_paciente': 'joao@email.com'
        }
        
        # Act
        errors = self.repo.validate_patient_data(valid_data)
        
        # Assert
        self.assertEqual(len(errors), 0)
        
    def test_validate_patient_data_missing_required(self):
        """Test validate_patient_data with missing required fields."""
        # Arrange
        invalid_data = {
            'email_paciente': 'joao@email.com'
            # Missing nome_paciente and cpf_paciente
        }
        
        # Act
        errors = self.repo.validate_patient_data(invalid_data)
        
        # Assert
        self.assertIn('nome_paciente', errors)
        self.assertIn('cpf_paciente', errors)
        
    def test_validate_patient_data_invalid_cpf(self):
        """Test validate_patient_data with invalid CPF."""
        # Arrange
        invalid_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': '123',  # Too short
            'email_paciente': 'joao@email.com'
        }
        
        # Act
        errors = self.repo.validate_patient_data(invalid_data)
        
        # Assert
        self.assertIn('cpf_paciente', errors)
        
    def test_validate_patient_data_invalid_email(self):
        """Test validate_patient_data with invalid email."""
        # Arrange
        invalid_data = {
            'nome_paciente': 'João Silva',
            'cpf_paciente': '12345678901',
            'email_paciente': 'invalid-email'  # No @ symbol
        }
        
        # Act
        errors = self.repo.validate_patient_data(invalid_data)
        
        # Assert
        self.assertIn('email_paciente', errors)
        
    @patch('processos.repositories.patient_repository.PatientVersioningService')
    def test_get_patient_version_for_user_success(self, mock_versioning_class):
        """Test get_patient_version_for_user returns version."""
        # Arrange
        mock_patient = Mock()
        mock_patient.id = 123
        mock_patient.cpf_paciente = "12345678901"
        
        mock_version = Mock()
        mock_versioning_instance = Mock()
        mock_versioning_instance.get_patient_version_for_user.return_value = mock_version
        mock_versioning_class.return_value = mock_versioning_instance
        
        # Recreate repository to get fresh mock
        repo = PatientRepository()
        repo.patient_versioning = mock_versioning_instance
        
        # Act
        result = repo.get_patient_version_for_user(mock_patient, self.mock_user)
        
        # Assert
        mock_versioning_instance.get_patient_version_for_user.assert_called_once_with(
            "12345678901", self.mock_user
        )
        self.assertEqual(result, mock_version)
        
    @patch('processos.repositories.patient_repository.PatientVersioningService')
    def test_get_patient_version_for_user_not_found(self, mock_versioning_class):
        """Test get_patient_version_for_user raises ValueError when no version."""
        # Arrange
        mock_patient = Mock()
        mock_patient.id = 123
        mock_patient.cpf_paciente = "12345678901"
        
        mock_versioning_instance = Mock()
        mock_versioning_instance.get_patient_version_for_user.return_value = None
        mock_versioning_class.return_value = mock_versioning_instance
        
        # Recreate repository to get fresh mock
        repo = PatientRepository()
        repo.patient_versioning = mock_versioning_instance
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            repo.get_patient_version_for_user(mock_patient, self.mock_user)
            
        self.assertIn("No patient data version exists", str(context.exception))


class TestPatientRepositoryIntegration(TestCase):
    """Integration tests for PatientRepository with real database."""
    
    def setUp(self):
        self.repo = PatientRepository()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
    def test_check_patient_exists_real_database(self):
        """Test check_patient_exists with real database."""
        # Arrange
        patient = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="12345678901",
            idade="30",
            sexo="M",
            nome_mae="Maria Silva",
            incapaz=False,
            nome_responsavel="",
            rg="123456789",
            peso="70kg",
            altura="1.75m",
            escolha_etnia="parda",
            cns_paciente="12345678901234",
            email_paciente="joao@email.com",
            cidade_paciente="São Paulo",
            end_paciente="Rua A, 123",
            cep_paciente="01234567",
            telefone1_paciente="11999999999",
            telefone2_paciente="1133333333",
            etnia="parda"
        )
        
        # Act
        result = self.repo.check_patient_exists("12345678901")
        
        # Assert
        self.assertEqual(result.id, patient.id)
        self.assertEqual(result.nome_paciente, "João Silva")
        
    def test_check_patient_exists_not_found_real_database(self):
        """Test check_patient_exists returns False for non-existent patient."""
        # Act
        result = self.repo.check_patient_exists("99999999999")
        
        # Assert
        self.assertFalse(result)