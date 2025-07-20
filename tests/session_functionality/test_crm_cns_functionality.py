"""
Comprehensive tests for CRM/CNS functionality implemented in this session.

This consolidates all CRM/CNS related tests from different apps:
- Confirmation field validation
- Immutability features
- Form behavior and security
- User experience flows
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db import IntegrityError

from medicos.forms import ProfileCompletionForm, UserDoctorEditForm, MedicoCadastroFormulario
from medicos.models import Medico
from usuarios.models import Usuario


class CRMCNSConfirmationTest(TestCase):
    """Test CRM/CNS confirmation field functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico='',
            cns_medico=''
        )
        self.user.medicos.add(self.medico)

    def test_profile_completion_form_has_confirmation_fields(self):
        """Test that ProfileCompletionForm has CRM and CNS confirmation fields."""
        form = ProfileCompletionForm(user=self.user)
        expected_fields = ['crm', 'crm2', 'cns', 'cns2']
        
        for field in expected_fields:
            self.assertIn(field, form.fields, f"Field {field} should be present")

    def test_crm_confirmation_validation(self):
        """Test CRM confirmation field validation."""
        form_data = {
            'crm': '123456',
            'crm2': '654321',  # Different CRM
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('crm2', form.errors)
        self.assertEqual(form.errors['crm2'], ['Os CRMs não coincidem.'])

    def test_cns_confirmation_validation(self):
        """Test CNS confirmation field validation."""
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '543210987654321'  # Different CNS
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('cns2', form.errors)
        self.assertEqual(form.errors['cns2'], ['Os CNSs não coincidem.'])

    def test_valid_confirmation_passes(self):
        """Test that matching confirmation fields pass validation."""
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())


class CRMCNSImmutabilityTest(TestCase):
    """Test CRM/CNS immutability functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico='',
            cns_medico=''
        )
        self.user.medicos.add(self.medico)

    def test_fields_disabled_when_values_set(self):
        """Test that fields are disabled when values are already set."""
        # Set existing values
        self.medico.crm_medico = '123456'
        self.medico.cns_medico = '123456789012345'
        self.medico.save()

        form = ProfileCompletionForm(user=self.user)
        
        # Check that fields are disabled
        self.assertTrue(form.fields['crm'].disabled)
        self.assertTrue(form.fields['crm2'].disabled)
        self.assertTrue(form.fields['cns'].disabled)
        self.assertTrue(form.fields['cns2'].disabled)

    def test_help_text_for_disabled_fields(self):
        """Test that disabled fields show appropriate help text."""
        self.medico.crm_medico = '123456'
        self.medico.cns_medico = '123456789012345'
        self.medico.save()

        form = ProfileCompletionForm(user=self.user)
        
        self.assertEqual(form.fields['crm'].help_text, "CRM já definido e não pode ser alterado")
        self.assertEqual(form.fields['cns'].help_text, "CNS já definido e não pode ser alterado")

    def test_partial_immutability(self):
        """Test that only set fields are disabled."""
        # Set only CRM
        self.medico.crm_medico = '123456'
        self.medico.save()

        form = ProfileCompletionForm(user=self.user)
        
        # Only CRM fields should be disabled
        self.assertTrue(form.fields['crm'].disabled)
        self.assertTrue(form.fields['crm2'].disabled)
        self.assertFalse(form.fields['cns'].disabled)
        self.assertFalse(form.fields['cns2'].disabled)

    def test_save_respects_immutability(self):
        """Test that save method respects immutability."""
        # Set existing values
        self.medico.crm_medico = '999999'
        self.medico.cns_medico = '999999999999999'
        self.medico.save()

        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        form.save()
        
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.crm_medico, '999999')  # Unchanged
        self.assertEqual(self.medico.cns_medico, '999999999999999')  # Unchanged


class CRMCNSValidationTest(TestCase):
    """Test CRM/CNS format and uniqueness validation."""

    def setUp(self):
        """Set up test data."""
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico='',
            cns_medico=''
        )
        self.user.medicos.add(self.medico)

    def test_crm_format_validation(self):
        """Test CRM format validation (digits only)."""
        form_data = {
            'crm': 'ABC123',  # Invalid format
            'crm2': 'ABC123',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('crm', form.errors)
        self.assertEqual(form.errors['crm'], ['CRM deve conter apenas números.'])

    def test_cns_format_validation(self):
        """Test CNS format validation (15 digits)."""
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '12345',  # Too short
            'cns2': '12345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('cns', form.errors)
        self.assertEqual(form.errors['cns'], ['CNS deve conter exatamente 15 números.'])

    def test_crm_uniqueness_validation(self):
        """Test that CRM uniqueness is validated across different medicos."""
        # Create another user with existing CRM
        other_user = Usuario.objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_medico=True
        )
        other_medico = Medico.objects.create(
            nome_medico='Other Doctor',
            crm_medico='123456',  # This CRM is already taken
            cns_medico='999999999999999'
        )
        other_user.medicos.add(other_medico)

        form_data = {
            'crm': '123456',  # Trying to use existing CRM
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('crm', form.errors)
        self.assertEqual(form.errors['crm'], ['Este CRM já está sendo usado por outro médico.'])

    def test_cns_uniqueness_validation(self):
        """Test that CNS uniqueness is validated across different medicos."""
        # Create another user with existing CNS
        other_user = Usuario.objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_medico=True
        )
        other_medico = Medico.objects.create(
            nome_medico='Other Doctor',
            crm_medico='999999',
            cns_medico='123456789012345'  # This CNS is already taken
        )
        other_user.medicos.add(other_medico)

        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',  # Trying to use existing CNS
            'cns2': '123456789012345'
        }
        form = ProfileCompletionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('cns', form.errors)
        self.assertEqual(form.errors['cns'], ['Este CNS já está sendo usado por outro médico.'])


class RegistrationFormSimplificationTest(TestCase):
    """Test registration form simplification."""

    def test_crm_cns_fields_removed_from_registration(self):
        """Test that CRM and CNS fields were removed from registration form."""
        form = MedicoCadastroFormulario()
        
        # These fields should not be present
        self.assertNotIn('crm', form.fields)
        self.assertNotIn('cns', form.fields)
        
        # These fields should still be present
        self.assertIn('nome', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('email2', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)

    def test_registration_creates_empty_credentials(self):
        """Test that registration creates medico with empty CRM and CNS."""
        form_data = {
            'nome': 'Test Doctor',
            'email': 'test@example.com',
            'email2': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = MedicoCadastroFormulario(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        medico = user.medicos.first()
        
        self.assertIsNotNone(medico)
        self.assertEqual(medico.nome_medico, 'Test Doctor')
        self.assertEqual(medico.crm_medico, '')
        self.assertEqual(medico.cns_medico, '')


class EditProfileFormTest(TestCase):
    """Test edit profile form immutability and functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico='123456',
            cns_medico='123456789012345'
        )
        self.user.medicos.add(self.medico)

    def test_immutable_fields_in_edit_form(self):
        """Test that CRM and CNS fields are immutable in edit form."""
        form = UserDoctorEditForm(user=self.user)
        
        self.assertTrue(form.fields['crm'].disabled)
        self.assertTrue(form.fields['cns'].disabled)
        self.assertEqual(form.fields['crm'].help_text, "CRM já definido e não pode ser alterado")
        self.assertEqual(form.fields['cns'].help_text, "CNS já definido e não pode ser alterado")

    def test_email_field_always_disabled(self):
        """Test that email field is always disabled in edit form."""
        form = UserDoctorEditForm(user=self.user)
        self.assertTrue(form.fields['email'].disabled)

    def test_form_layout_has_proper_spacing(self):
        """Test that form layout includes proper spacing classes."""
        form = UserDoctorEditForm(user=self.user)
        layout = form.helper.layout
        
        # Check that each field div has mb-4 class for spacing
        for field_div in layout.fields:
            self.assertIn('mb-4', field_div.css_class)

    def test_save_respects_immutability(self):
        """Test that save doesn't overwrite existing CRM/CNS."""
        form_data = {
            'name': 'Updated Doctor',
            'crm': '999999',  # Trying to change CRM
            'cns': '999999999999999'  # Trying to change CNS
        }
        form = UserDoctorEditForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        
        self.medico.refresh_from_db()
        # Original values should be preserved
        self.assertEqual(self.medico.crm_medico, '123456')  # Unchanged
        self.assertEqual(self.medico.cns_medico, '123456789012345')  # Unchanged
        # Name should be updated
        self.assertEqual(self.medico.nome_medico, 'Updated Doctor')