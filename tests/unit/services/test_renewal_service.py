"""
Test Renewal Service - Unit tests for prescription renewal business logic.

Testing the uncovered areas from coverage report:
- Lines 46-84: process_renewal exception handling and error paths
- Lines 88-96: _validate_renewal_eligibility method
- Lines 131-134: generate_renewal_data user validation
- Lines 147-150: Patient data fallback paths
- Lines 174, 190-191: Date validation and conditional data handling
- Lines 222-265: create_renewal_dictionary method 
- Lines 293-301: _retrieve_prescription_data method
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from datetime import date

from processos.services.prescription.renewal_service import RenewalService
from processos.models import Processo


class RenewalServiceTest(BaseTestCase):
    """Test RenewalService functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.service = RenewalService()

    def test_validate_renewal_eligibility_not_found(self):
        """Test _validate_renewal_eligibility when process not found."""
        user = self.create_test_user(is_medico=True)
        
        # Test with non-existent process
        result = self.service._validate_renewal_eligibility(999999, user)
        
        # Should return False when process not found
        self.assertFalse(result)

    @patch('processos.repositories.process_repository.ProcessRepository')
    def test_validate_renewal_eligibility_exception(self, mock_process_repo):
        """Test _validate_renewal_eligibility exception handling."""
        user = self.create_test_user(is_medico=True)
        
        # Mock repository to raise exception
        mock_process_repo.return_value.get_process_for_user.side_effect = Exception("Database error")
        
        result = self.service._validate_renewal_eligibility(123, user)
        
        # Should return False when exception occurs
        self.assertFalse(result)

    def test_generate_renewal_data_empty_date(self):
        """Test generate_renewal_data with empty renewal date."""
        # Create complete test setup
        user = self.create_test_user(is_medico=True)
        medico = self.create_test_medico(user=user)
        patient = self.create_test_patient(user=user)
        clinica = self.create_test_clinica()
        doenca = self.create_test_doenca()
        emissor = self.create_test_emissor(medico=medico, clinica=clinica)
        
        processo = self.create_test_processo(
            usuario=user,
            paciente=patient,
            medico=medico,
            clinica=clinica,
            doenca=doenca,
            emissor=emissor
        )
        
        # Should raise ValueError for empty date
        with self.assertRaises(ValueError) as context:
            self.service.generate_renewal_data("", processo.id, user)
        
        self.assertEqual(str(context.exception), "Data de renovação não pode estar vazia")

    def test_create_renewal_dictionary_no_user(self):
        """Test create_renewal_dictionary without user parameter."""
        # Create mock process
        processo = Mock()
        
        # Should raise ValueError when user not provided
        with self.assertRaises(ValueError) as context:
            self.service.create_renewal_dictionary(processo, user=None)
        
        self.assertEqual(str(context.exception), "User parameter is required for accessing patient data")

    @patch('processos.services.prescription.renewal_service.RenewalService._validate_renewal_eligibility')
    def test_process_renewal_not_eligible(self, mock_validate):
        """Test process_renewal when process not eligible for renewal."""
        user = self.create_test_user(is_medico=True)
        
        # Mock validation to return False (not eligible)
        mock_validate.return_value = False
        
        result = self.service.process_renewal("01/01/2025", 123, user)
        
        # Should return None when not eligible
        self.assertIsNone(result)

    @patch('processos.services.prescription.renewal_service.PrescriptionPDFService')
    @patch('processos.services.prescription.renewal_service.RenewalService._validate_renewal_eligibility')
    @patch('processos.services.prescription.renewal_service.RenewalService.generate_renewal_data')
    def test_process_renewal_pdf_generation_fails(self, mock_generate_data, mock_validate, mock_pdf_service):
        """Test process_renewal when PDF generation fails."""
        user = self.create_test_user(is_medico=True)
        
        # Mock validation to return True (eligible)
        mock_validate.return_value = True
        
        # Mock generate_renewal_data to return test data
        mock_generate_data.return_value = {"test": "data"}
        
        # Mock PDF service to return None (generation failed)
        mock_pdf_instance = Mock()
        mock_pdf_instance.generate_prescription_pdf.return_value = None
        mock_pdf_service.return_value = mock_pdf_instance
        
        result = self.service.process_renewal("01/01/2025", 123, user)
        
        # Should return None when PDF generation fails
        self.assertIsNone(result)

    @patch('processos.services.prescription.renewal_service.RenewalService._validate_renewal_eligibility')
    @patch('processos.services.prescription.renewal_service.RenewalService.generate_renewal_data')
    def test_process_renewal_processo_not_found(self, mock_generate_data, mock_validate):
        """Test process_renewal when Processo.DoesNotExist is raised."""
        user = self.create_test_user(is_medico=True)
        
        # Mock validation to return True (eligible)
        mock_validate.return_value = True
        
        # Mock generate_renewal_data to raise Processo.DoesNotExist
        mock_generate_data.side_effect = Processo.DoesNotExist("Process not found")
        
        # Should re-raise the exception
        with self.assertRaises(Processo.DoesNotExist):
            self.service.process_renewal("01/01/2025", 123, user)

    @patch('processos.services.prescription.renewal_service.RenewalService._validate_renewal_eligibility')
    @patch('processos.services.prescription.renewal_service.RenewalService.generate_renewal_data')
    def test_process_renewal_general_exception(self, mock_generate_data, mock_validate):
        """Test process_renewal when general exception is raised."""
        user = self.create_test_user(is_medico=True)
        
        # Mock validation to return True (eligible)
        mock_validate.return_value = True
        
        # Mock generate_renewal_data to raise general exception
        mock_generate_data.side_effect = Exception("Database connection error")
        
        # Should re-raise the exception
        with self.assertRaises(Exception):
            self.service.process_renewal("01/01/2025", 123, user)

    def test_create_renewal_dictionary_no_patient_access(self):
        """Test create_renewal_dictionary when user has no access to patient."""
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
        
        # Should raise ValueError when user has no access to patient
        with self.assertRaises(ValueError) as context:
            self.service.create_renewal_dictionary(processo, user=user2)
        
        self.assertIn("has no access to patient", str(context.exception))

    @patch('processos.repositories.medication_repository.MedicationRepository')
    @patch('processos.repositories.process_repository.ProcessRepository')
    def test_generate_renewal_data_no_user_fallback(self, mock_process_repo, mock_med_repo):
        """Test generate_renewal_data fallback path when no user provided."""
        # Create mock process with conditional data
        mock_processo = Mock()
        mock_processo.id = 123
        mock_processo.doenca.cid = 'G40.0'
        mock_processo.doenca.nome = 'Epilepsy'
        mock_processo.paciente.id = 456
        mock_processo.paciente.cpf_paciente = '12345678901'
        mock_processo.dados_condicionais = {'custom_field': 'custom_value'}
        mock_processo.prescricao = {}
        
        # Mock repository
        mock_repo_instance = Mock()
        mock_repo_instance.get_process_by_id.return_value = mock_processo
        mock_process_repo.return_value = mock_repo_instance
        
        # Mock medication repository
        mock_med_instance = Mock()
        mock_med_instance.extract_medication_ids_from_form.return_value = []
        mock_med_instance.format_medication_dosages.return_value = ({'test_field': 'test_value'}, [])
        mock_med_repo.return_value = mock_med_instance
        
        # Mock model_to_dict to return simple data with required fields
        with patch('django.forms.models.model_to_dict') as mock_model_to_dict:
            mock_model_to_dict.return_value = {
                'test_field': 'test_value',
                'logradouro': 'Test Street',
                'logradouro_num': '123'
            }
            
            # Call without user (fallback path)
            result = self.service.generate_renewal_data("01/01/2025", 123, user=None)
            
            # Should have called get_process_by_id (fallback)
            mock_repo_instance.get_process_by_id.assert_called_once_with(123)
            
            # Should contain expected fields
            self.assertIn('test_field', result)
            self.assertEqual(result['test_field'], 'test_value')

    def test_retrieve_prescription_data_with_medications(self):
        """Test _retrieve_prescription_data with medication data."""
        # Create mock process with prescription data
        mock_processo = Mock()
        mock_processo.id = 123
        mock_processo.prescricao = {
            '1': {
                'id_med1': '101',
                'med1_posologia_mes1': '1 comprimido 2x ao dia',
                'med1_quantidade_mes1': '60'
            },
            '2': {
                'id_med2': '102', 
                'med2_posologia_mes2': '500mg 1x ao dia',
                'med2_quantidade_mes2': '30'
            },
            '': {}  # Empty entry to test filtering
        }
        
        # Initial data dictionary
        dados = {'existing_field': 'existing_value'}
        
        # Call method
        result = self.service._retrieve_prescription_data(dados, mock_processo)
        
        # Should have medication data
        self.assertEqual(result['id_med1'], '101')
        self.assertEqual(result['med1_posologia_mes1'], '1 comprimido 2x ao dia')
        self.assertEqual(result['id_med2'], '102')
        self.assertEqual(result['med2_posologia_mes2'], '500mg 1x ao dia')
        
        # Should preserve existing data
        self.assertEqual(result['existing_field'], 'existing_value')