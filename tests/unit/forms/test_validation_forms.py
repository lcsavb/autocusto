"""
Test Validation Forms - Unit tests for validation form classes.

Testing the uncovered areas from coverage report:
- Lines 93-98: RenovacaoRapidaForm __init__ method
- Lines 102-112: clean_processo_id validation logic
- Lines 116-122: clean_data_1 validation logic
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch
from datetime import date

from processos.forms.validation_forms import PreProcesso, RenovacaoRapidaForm


class PreProcessoTest(BaseTestCase):
    """Test PreProcesso form functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

    @patch('processos.repositories.domain_repository.DomainRepository')
    def test_clean_cid_invalid(self, mock_domain_repo):
        """Test clean_cid with invalid CID."""
        # Mock domain repository to return no matching CID
        mock_domain_repo_instance = Mock()
        mock_domain_repo.return_value = mock_domain_repo_instance
        mock_disease = Mock()
        mock_disease.cid = 'G40.0'
        mock_domain_repo_instance.get_all_diseases.return_value = [mock_disease]
        
        form_data = {
            'cpf_paciente': self.data_generator.generate_unique_cpf(),
            'cid': 'INVALID_CID'  # Invalid CID
        }
        
        form = PreProcesso(data=form_data)
        
        # Should not be valid due to invalid CID
        self.assertFalse(form.is_valid())
        self.assertIn('CID "INVALID_CID" incorreto!', form.errors['cid'])


class RenovacaoRapidaFormTest(BaseTestCase):
    """Test RenovacaoRapidaForm functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

    def test_form_initialization(self):
        """Test form initialization with helper configuration."""
        form = RenovacaoRapidaForm()
        
        # Check helper configuration
        self.assertEqual(form.helper.form_method.upper(), "POST")
        self.assertFalse(form.helper.form_show_errors)
        self.assertFalse(form.helper.error_text_inline)
        self.assertTrue(form.helper.attrs.get('novalidate'))

    def test_clean_processo_id_empty(self):
        """Test clean_processo_id with empty value."""
        form_data = {
            'processo_id': '',  # Empty process ID
            'data_1': '01/01/2025',
            'edicao': False
        }
        
        form = RenovacaoRapidaForm(data=form_data)
        
        # Should not be valid due to empty process ID
        self.assertFalse(form.is_valid())
        self.assertIn('Selecione um processo para renovar.', form.errors['processo_id'])

    def test_clean_processo_id_invalid_integer(self):
        """Test clean_processo_id with invalid integer value."""
        form_data = {
            'processo_id': 'not_a_number',  # Invalid integer
            'data_1': '01/01/2025',
            'edicao': False
        }
        
        form = RenovacaoRapidaForm(data=form_data)
        
        # Should not be valid due to invalid integer
        self.assertFalse(form.is_valid())
        self.assertIn('ID do processo inválido', form.errors['processo_id'])

    def test_clean_data_1_empty(self):
        """Test clean_data_1 with empty date."""
        form_data = {
            'processo_id': '123',
            'data_1': '',  # Empty date
            'edicao': False
        }
        
        form = RenovacaoRapidaForm(data=form_data)
        
        # Should not be valid due to empty date
        self.assertFalse(form.is_valid())
        self.assertIn('Data é obrigatória.', form.errors['data_1'])