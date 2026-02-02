"""
Test Base Forms - Unit tests for base form classes and mixins.

Testing the uncovered areas from coverage report:
- Lines 28: add_medication_error method
- Lines 32-36: setup_form_styling method
"""

from tests.test_base import BaseTestCase
from django.test import TestCase
from django import forms

from processos.forms.base_forms import PrescriptionBaseMixin


class TestPrescriptionForm(forms.Form, PrescriptionBaseMixin):
    """Test form that uses PrescriptionBaseMixin for testing."""
    
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    is_active = forms.BooleanField(required=False)


class PrescriptionBaseMixinTest(BaseTestCase):
    """Test PrescriptionBaseMixin functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

    def test_add_medication_error(self):
        """Test add_medication_error method."""
        form_data = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'is_active': True
        }
        form = TestPrescriptionForm(data=form_data)
        
        # Form should be valid initially
        self.assertTrue(form.is_valid())
        
        # Add a medication error
        form.add_medication_error(2, "Dosagem inválida")
        
        # Check that the error was added correctly
        self.assertIn("Medicamento 2: Dosagem inválida", form.non_field_errors())

    def test_setup_form_styling(self):
        """Test setup_form_styling method."""
        form = TestPrescriptionForm()
        
        # Apply styling
        form.setup_form_styling()
        
        # Check that form-control class was added to appropriate fields
        self.assertIn('form-control', form.fields['name'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['email'].widget.attrs['class'])
        
        # Check that data-crispy-field attribute was added to all fields
        self.assertEqual(form.fields['name'].widget.attrs['data-crispy-field'], 'true')
        self.assertEqual(form.fields['email'].widget.attrs['data-crispy-field'], 'true')
        self.assertEqual(form.fields['is_active'].widget.attrs['data-crispy-field'], 'true')
        
        # CheckboxInput should not get form-control class but should get data-crispy-field
        checkbox_classes = form.fields['is_active'].widget.attrs.get('class', '')
        self.assertNotIn('form-control', checkbox_classes)