"""
Test Medication Repository - Unit tests for medication data access layer.

Testing the uncovered areas from coverage report:
- Lines 75-89: get_medication_details method with exception handling
- Lines 123-125: Medication not found in format_medication_dosages
- Lines 141-159: associate_medications_with_process method
- Lines 184-186: extract_medication_ids_from_form KeyError handling
- Lines 202-214: get_medications_by_protocol method
- Lines 226-244: validate_medication_selection method
"""

from tests.test_base import BaseTestCase
from django.test import TestCase

from processos.repositories.medication_repository import MedicationRepository
from processos.models import Medicamento, Protocolo, Processo


class MedicationRepositoryTest(BaseTestCase):
    """Test MedicationRepository functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.repository = MedicationRepository()

    def test_get_medication_details_not_found(self):
        """Test get_medication_details when medication doesn't exist."""
        # Try to get non-existent medication
        result = self.repository.get_medication_details(999999)
        
        # Should return empty dict when medication not found
        self.assertEqual(result, {})

    def test_get_medication_details_success(self):
        """Test get_medication_details with valid medication."""
        # Create test medication
        medication = self.create_test_medicamento(
            nome="Test Med",
            dosagem="500mg", 
            apres="Comprimido"
        )
        
        result = self.repository.get_medication_details(medication.id)
        
        # Should return medication details
        expected = {
            'nome': 'Test Med',
            'dosagem': '500mg',
            'apres': 'Comprimido',
            'formatted': 'Test Med 500mg (Comprimido)'
        }
        self.assertEqual(result, expected)

    def test_format_medication_dosages_medication_not_found(self):
        """Test format_medication_dosages when medication doesn't exist."""
        form_data = {}
        medication_ids = ['999999']  # Non-existent medication ID
        
        updated_form_data, cleaned_ids = self.repository.format_medication_dosages(
            form_data, medication_ids
        )
        
        # Should handle missing medication gracefully
        self.assertEqual(updated_form_data['med1'], 'Medicamento não encontrado')
        self.assertEqual(cleaned_ids, ['999999'])  # Still includes the ID

    def test_get_medications_by_protocol_not_found(self):
        """Test get_medications_by_protocol when protocol doesn't exist."""
        # Try to get medications for non-existent protocol
        result = self.repository.get_medications_by_protocol('NonExistentProtocol')
        
        # Should return empty queryset
        self.assertEqual(list(result), [])

    def test_validate_medication_selection_empty_list(self):
        """Test validate_medication_selection with empty medication list."""
        errors = self.repository.validate_medication_selection([])
        
        # Should return error for no medications selected
        self.assertIn('medications', errors)
        self.assertEqual(errors['medications'], 'Pelo menos um medicamento deve ser selecionado')