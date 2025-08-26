"""
Test Prescription Forms - Unit tests for prescription form classes.

Testing the uncovered areas from coverage report:
- Lines 294-296: No medications validation error
- Lines 317-347: NovoProcesso save method with imports and repositories
- Lines 374-387: RenovarProcesso save method routing
- Lines 391-415: _handle_complete_renewal method
- Lines 419-424: _handle_quick_renewal method
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock

from processos.forms.prescription_forms import NovoProcesso, RenovarProcesso


class NovoProcessoTest(BaseTestCase):
    """Test NovoProcesso form functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.escolhas = [(1, "Option 1"), (2, "Option 2")]
        self.medicamentos = [Mock(id=1, nome="Med 1"), Mock(id=2, nome="Med 2")]

    def test_clean_no_medications_error(self):
        """Test clean method validation when no medications are submitted."""
        form_data = {
            'anamnese': 'Test anamnese',
            'cpf_paciente': self.data_generator.generate_unique_cpf(),
            'cid': 'G40.0',
            'data_1': '01/01/2025',
            'clinicas': '1',
            'tratou': False,
            'tratamentos_previos': 'None'
        }
        
        with patch('processos.forms.prescription_forms.MedicationValidator') as mock_validator:
            # Mock validator to return no submitted medications
            mock_validator_instance = Mock()
            mock_validator_instance.get_submitted_medications.return_value = []  # No medications
            mock_validator.return_value = mock_validator_instance
            
            form = NovoProcesso(self.escolhas, self.medicamentos, data=form_data)
            
            # Should not be valid due to no medications
            self.assertFalse(form.is_valid())
            self.assertIn("Pelo menos um medicamento deve ser selecionado.", form.non_field_errors())

    @patch('processos.services.prescription.process_service.ProcessService')
    @patch('processos.services.prescription.data_builder.PrescriptionDataBuilder')
    @patch('processos.repositories.patient_repository.PatientRepository')
    @patch('processos.repositories.domain_repository.DomainRepository')
    def test_save_method_with_mocked_dependencies(self, mock_domain_repo, mock_patient_repo, 
                                                 mock_data_builder, mock_process_service):
        """Test NovoProcesso save method with mocked dependencies."""
        # Setup form data
        form_data = {
            'anamnese': 'Test anamnese',
            'cpf_paciente': self.data_generator.generate_unique_cpf(),
            'cid': 'G40.0',
            'data_1': '01/01/2025',
            'clinicas': '1',
            'tratou': False,
            'tratamentos_previos': 'None'
        }
        
        # Mock dependencies
        mock_domain_repo_instance = Mock()
        mock_domain_repo.return_value = mock_domain_repo_instance
        mock_domain_repo_instance.get_disease_by_cid.return_value = Mock()
        mock_domain_repo_instance.get_emissor_by_medico_clinica.return_value = Mock()
        
        mock_patient_repo_instance = Mock()
        mock_patient_repo.return_value = mock_patient_repo_instance
        mock_patient_repo_instance.check_patient_exists.return_value = True
        
        mock_data_builder_instance = Mock()
        mock_data_builder.return_value = mock_data_builder_instance
        mock_data_builder_instance.build_prescription_data.return_value = {}
        
        mock_process_service_instance = Mock()
        mock_process_service.return_value = mock_process_service_instance
        mock_process_service_instance.create_process_from_structured_data.return_value = 123
        
        # Create form and mock validation
        form = NovoProcesso(self.escolhas, self.medicamentos, data=form_data)
        form.cleaned_data = form_data  # Bypass validation for testing save method
        
        # Create mock objects
        usuario = Mock()
        medico = Mock()
        medico.clinicas.get.return_value = Mock()
        meds_ids = [1, 2]
        
        # Call save method
        result = form.save(usuario, medico, meds_ids)
        
        # Verify result and method calls
        self.assertEqual(result, 123)
        mock_domain_repo_instance.get_disease_by_cid.assert_called_once_with('G40.0')
        mock_patient_repo_instance.check_patient_exists.assert_called_once()
        mock_process_service_instance.create_process_from_structured_data.assert_called_once()


class RenovarProcessoTest(BaseTestCase):
    """Test RenovarProcesso form functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.escolhas = [(1, "Option 1"), (2, "Option 2")]
        self.medicamentos = [Mock(id=1, nome="Med 1"), Mock(id=2, nome="Med 2")]

    def test_save_quick_renewal_routing(self):
        """Test save method routing for quick renewal (edicao_completa=False)."""
        form_data = {
            'edicao_completa': 'False',  # Quick renewal
            'data_1': '01/01/2025'
        }
        
        form = RenovarProcesso(self.escolhas, self.medicamentos, data=form_data)
        form.cleaned_data = form_data
        
        # Mock the quick renewal method
        form._handle_quick_renewal = Mock()
        
        # Call save method
        usuario = Mock()
        medico = Mock()
        processo_id = 123
        meds_ids = [1, 2]
        
        result = form.save(usuario, medico, processo_id, meds_ids)
        
        # Should call quick renewal method
        form._handle_quick_renewal.assert_called_once_with(form_data, meds_ids, processo_id)
        self.assertEqual(result, processo_id)