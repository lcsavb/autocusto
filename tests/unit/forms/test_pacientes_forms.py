"""
Test Pacientes Forms - Unit tests for patient forms.

Testing the uncovered areas from coverage report:
- Lines 26-38: Form initialization and field setup
- Lines 42-48: validate_unique method override
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from django import forms

from pacientes.forms import PacienteCadastroFormulario
from pacientes.models import Paciente


class PacienteCadastroFormularioTest(BaseTestCase):
    """Test PacienteCadastroFormulario functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

    def test_form_initialization(self):
        """Test form initialization and field setup."""
        form = PacienteCadastroFormulario()
        
        # Check that form has correct fields
        expected_fields = ['nome_paciente', 'nome_mae', 'cpf_paciente']
        for field in expected_fields:
            self.assertIn(field, form.fields)
        
        # Check that form-control class is added to fields
        for field_name, field in form.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                self.assertIn('form-control', field.widget.attrs.get('class', ''))
        
        # Check crispy forms helper configuration
        self.assertEqual(form.helper.form_method.upper(), "POST")
        self.assertFalse(form.helper.form_show_errors)
        self.assertFalse(form.helper.error_text_inline)

    def test_validate_unique_skips_cpf_validation(self):
        """Test that validate_unique skips CPF uniqueness validation."""
        # Create a patient with specific CPF
        existing_cpf = self.data_generator.generate_unique_cpf()
        existing_patient = self.create_test_patient(cpf_paciente=existing_cpf)
        
        # Create form with duplicate CPF - should not raise validation error
        form_data = {
            'nome_paciente': f'Test Patient {self.unique_suffix}',
            'nome_mae': 'Test Mother',
            'cpf_paciente': existing_cpf  # Duplicate CPF
        }
        
        form = PacienteCadastroFormulario(data=form_data)
        
        # Form should be valid because CPF uniqueness is skipped
        self.assertTrue(form.is_valid())