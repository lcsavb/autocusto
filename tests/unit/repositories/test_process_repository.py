"""
Test Process Repository - Unit tests for process data access layer.

Testing the uncovered areas from coverage report:
- Lines 49-54: Exception handling in get_process_for_user
- Lines 69-78: get_process_with_disease_info method
- Lines 93-101: get_process_by_id method with exception handling
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from processos.repositories.process_repository import ProcessRepository
from processos.models import Processo

User = get_user_model()


class ProcessRepositoryTest(BaseTestCase):
    """Test ProcessRepository functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.repository = ProcessRepository()

    def test_get_process_for_user_not_found(self):
        """Test get_process_for_user when process doesn't exist."""
        user = self.create_test_user(is_medico=True)
        
        # Try to get non-existent process
        result = self.repository.get_process_for_user(999999, user)
        
        # Should return None when process not found
        self.assertIsNone(result)

    def test_get_process_for_user_unauthorized(self):
        """Test get_process_for_user when user doesn't own the process."""
        # Create process for user1
        user1 = self.create_test_user(is_medico=True)
        medico1 = self.create_test_medico(user=user1)
        patient = self.create_test_patient(user=user1)
        clinica = self.create_test_clinica()
        doenca = self.create_test_doenca()
        emissor = self.create_test_emissor(medico=medico1, clinica=clinica)
        
        processo = self.create_test_processo(
            usuario=user1,
            paciente=patient,
            medico=medico1,
            clinica=clinica,
            doenca=doenca,
            emissor=emissor
        )
        
        # Try to access with different user (user2)
        user2 = self.create_test_user(is_medico=True)
        result = self.repository.get_process_for_user(processo.id, user2)
        
        # Should return None when user doesn't own process
        self.assertIsNone(result)

    def test_get_process_with_disease_info_success(self):
        """Test get_process_with_disease_info with valid process."""
        # Create complete test setup
        user = self.create_test_user(is_medico=True)
        medico = self.create_test_medico(user=user)
        patient = self.create_test_patient(user=user)
        clinica = self.create_test_clinica()
        doenca = self.create_test_doenca(cid='G40.0')  # Known CID
        emissor = self.create_test_emissor(medico=medico, clinica=clinica)
        
        processo = self.create_test_processo(
            usuario=user,
            paciente=patient,
            medico=medico,
            clinica=clinica,
            doenca=doenca,
            emissor=emissor
        )
        
        # Get process with disease info
        result_processo, result_cid = self.repository.get_process_with_disease_info(processo.id, user)
        
        # Should return process and CID
        self.assertIsNotNone(result_processo)
        self.assertEqual(result_processo.id, processo.id)
        self.assertEqual(result_cid, 'G40.0')

    def test_get_process_with_disease_info_not_found(self):
        """Test get_process_with_disease_info when process not found."""
        user = self.create_test_user(is_medico=True)
        
        # Try to get non-existent process
        result_processo, result_cid = self.repository.get_process_with_disease_info(999999, user)
        
        # Should return None, None
        self.assertIsNone(result_processo)
        self.assertIsNone(result_cid)

    def test_get_process_by_id_not_found(self):
        """Test get_process_by_id when process doesn't exist."""
        # Try to get non-existent process - should raise exception
        with self.assertRaises(Processo.DoesNotExist):
            self.repository.get_process_by_id(999999)