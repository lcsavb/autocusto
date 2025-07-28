from tests.test_base import BaseTestCase, TestDataFactory
from django.urls import reverse
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm

class UsuarioModelTest(BaseTestCase):

    def test_create_usuario(self):
        user = self.create_test_user()
        self.assertTrue(user.email.endswith("@example.com"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

class CustomUserCreationFormTest(BaseTestCase):

    def test_form_valid_data(self):
        form_data = TestDataFactory.get_valid_form_data_patterns()['user_creation']
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, form_data['email'])
        self.assertTrue(user.check_password('ComplexPassword789!'))

    def test_form_invalid_data_mismatched_passwords(self):
        form = CustomUserCreationForm(data={
            'email': TestDataFactory.get_unique_email(),
            'password1': 'password123',
            'password2': 'differentpassword',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_invalid_data_no_email(self):
        form = CustomUserCreationForm(data={
            'email': '',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_invalid_data_duplicate_email(self):
        existing_user = self.create_test_user()
        form = CustomUserCreationForm(data={
            'email': existing_user.email,
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
