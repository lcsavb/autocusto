"""
Test Medicos Views - Unit tests for medicos views.

Testing the uncovered areas from coverage report:
- Lines 42-67: cadastro view POST handling and error cases
- Lines 120-133: perfil view service integration
- Lines 145-146: login_required_redirect view
- Lines 174-183: complete_profile error handling
- Lines 191-202: complete_profile GET with service data
- Lines 216-243: edit_profile view POST/GET handling
"""

from tests.test_base import BaseTestCase
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from unittest.mock import patch, Mock

from medicos.views import custom_login, login_required_redirect
from medicos.models import Medico

User = get_user_model()


class MedicosViewsTest(BaseTestCase):
    """Test Medicos views functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = Client()

    def test_cadastro_post_invalid_form(self):
        """Test cadastro view with invalid form data."""
        # Test with missing required fields
        form_data = {
            'nome': 'Dr. Test',
            'email': self.data_generator.generate_unique_email(),
            # Missing email2, password1, password2
        }
        
        response = self.client.post(reverse('medicos-cadastro'), form_data)
        
        # Should render the form again with errors (status 200)
        self.assertEqual(response.status_code, 200)
        
        # Check that the form is rendered with errors
        self.assertContains(response, 'form-group')
        self.assertContains(response, 'invalid-feedback')
        
        # Verify error messages are displayed (they show in the response HTML)
        self.assertContains(response, 'Confirmação de email é obrigatória')
        self.assertContains(response, 'Por favor, insira uma senha')
        self.assertContains(response, 'Por favor, confirme a senha')

    def test_login_required_redirect(self):
        """Test login_required_redirect view function directly."""
        from django.http import HttpRequest
        from django.contrib.messages.storage.fallback import FallbackStorage
        
        # Create mock request
        request = HttpRequest()
        request.method = 'GET'
        
        # Add messages framework to request
        setattr(request, 'session', self.client.session)
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Call the view function directly
        response = login_required_redirect(request)
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))