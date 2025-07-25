from django.test import TestCase
from django.urls import reverse
from .models import Usuario
from .forms import CustomUserCreationForm

class UsuarioModelTest(TestCase):

    def test_create_usuario(self):
        user = Usuario.objects.create_user(
            email="test@example.com",
            password="password123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

class CustomUserCreationFormTest(TestCase):

    def test_form_valid_data(self):
        form = CustomUserCreationForm(data={
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword789!',
            'password2': 'ComplexPassword789!',
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('ComplexPassword789!'))

    def test_form_invalid_data_mismatched_passwords(self):
        form = CustomUserCreationForm(data={
            'email': 'newuser@example.com',
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
        Usuario.objects.create_user(email='existing@example.com', password='password123')
        form = CustomUserCreationForm(data={
            'email': 'existing@example.com',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
