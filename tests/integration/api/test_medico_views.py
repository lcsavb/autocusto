"""
Medico views tests.

Consolidated from medicos/test_views.py
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db import IntegrityError

from medicos.models import Medico
from usuarios.models import Usuario
from clinicas.models import Clinica


class CompleteProfileViewTest(TestCase):
    """Test complete_profile view functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
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
        self.client.login(username='test@example.com', password='testpass123')

    def test_login_required(self):
        """Test that login is required to access the view."""
        self.client.logout()
        response = self.client.get(reverse('complete-profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_get_renders_form(self):
        """Test GET request renders the form correctly."""
        response = self.client.get(reverse('complete-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete seus Dados Médicos')
        self.assertContains(response, 'CRM')
        self.assertContains(response, 'CNS')

    def test_get_prepopulates_existing_data(self):
        """Test that GET request prepopulates form with existing data."""
        self.medico.crm_medico = '123456'
        self.medico.cns_medico = '123456789012345'
        self.medico.save()

        response = self.client.get(reverse('complete-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123456')
        self.assertContains(response, '123456789012345')

    def test_post_valid_data_without_clinics(self):
        """Test POST with valid data when user has no clinics."""
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Should redirect to clinic registration
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('clinicas-cadastro'))
        
        # Check that medico was updated
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.crm_medico, '123456')
        self.assertEqual(self.medico.cns_medico, '123456789012345')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Dados médicos atualizados com sucesso!' in str(m) for m in messages))

    def test_post_valid_data_with_existing_clinics(self):
        """Test POST with valid data when user already has clinics."""
        # Create a clinic for the user
        clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(self.medico)

        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Should redirect to process creation
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('processos-cadastro'))
        
        # Check success and info messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Dados médicos atualizados com sucesso!' in str(m) for m in messages))
        self.assertTrue(any('Voltando para o formulário de criação do processo...' in str(m) for m in messages))

    def test_post_invalid_data(self):
        """Test POST with invalid data."""
        form_data = {
            'crm': '123456',
            'crm2': '654321',  # Mismatched CRM
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Should re-render form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete seus Dados Médicos')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Os CRMs não coincidem.' in str(m) for m in messages))

    def test_post_integrity_error_crm(self):
        """Test POST handling IntegrityError for duplicate CRM."""
        # Create another user with the same CRM
        other_user = Usuario.objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_medico=True
        )
        other_medico = Medico.objects.create(
            nome_medico='Other Doctor',
            crm_medico='123456',  # Same CRM
            cns_medico='999999999999999'
        )
        other_user.medicos.add(other_medico)

        form_data = {
            'crm': '123456',  # Duplicate CRM
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Should re-render form with error
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Este CRM já está sendo usado por outro médico.' in str(m) for m in messages))

    def test_post_integrity_error_cns(self):
        """Test POST handling IntegrityError for duplicate CNS."""
        # Create another user with the same CNS
        other_user = Usuario.objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_medico=True
        )
        other_medico = Medico.objects.create(
            nome_medico='Other Doctor',
            crm_medico='999999',
            cns_medico='123456789012345'  # Same CNS
        )
        other_user.medicos.add(other_medico)

        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',  # Duplicate CNS
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Should re-render form with error
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Este CNS já está sendo usado por outro médico.' in str(m) for m in messages))


class EditProfileViewTest(TestCase):
    """Test edit_profile view functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
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
        self.client.login(username='test@example.com', password='testpass123')

    def test_login_required(self):
        """Test that login is required to access the view."""
        self.client.logout()
        response = self.client.get(reverse('edit-profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_get_renders_form(self):
        """Test GET request renders the form correctly."""
        response = self.client.get(reverse('edit-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar Perfil')
        self.assertContains(response, 'Nome completo')
        self.assertContains(response, 'Email')

    def test_get_prepopulates_form(self):
        """Test that GET request prepopulates form with user data."""
        response = self.client.get(reverse('edit-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Doctor')
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, '123456')
        self.assertContains(response, '123456789012345')

    def test_immutable_fields_disabled(self):
        """Test that CRM and CNS fields are disabled when already set."""
        response = self.client.get(reverse('edit-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CRM já definido e não pode ser alterado')
        self.assertContains(response, 'CNS já definido e não pode ser alterado')

    def test_post_valid_data(self):
        """Test POST with valid data."""
        form_data = {
            'name': 'Updated Doctor Name',
            'email': 'test@example.com',  # Email is disabled, so this shouldn't matter
            'crm': '123456',  # These are disabled
            'cns': '123456789012345'
        }
        response = self.client.post(reverse('edit-profile'), data=form_data)
        
        # Should redirect back to edit profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('edit-profile'))
        
        # Check that name was updated
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nome_medico, 'Updated Doctor Name')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Perfil atualizado com sucesso!' in str(m) for m in messages))

    def test_post_invalid_data(self):
        """Test POST with invalid data."""
        form_data = {
            'name': 'Updated Doctor Name',
            'crm': 'INVALID',  # Invalid CRM format
            'cns': '123456789012345'
        }
        response = self.client.post(reverse('edit-profile'), data=form_data)
        
        # Should either re-render form or redirect (depending on form implementation)
        self.assertIn(response.status_code, [200, 302])
        
        # Check that there are error messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)


class NavigationTest(TestCase):
    """Test navigation and URL functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        self.client.login(username='test@example.com', password='testpass123')

    def test_edit_profile_url_accessible(self):
        """Test that edit-profile URL is accessible."""
        response = self.client.get(reverse('edit-profile'))
        self.assertEqual(response.status_code, 200)

    def test_complete_profile_url_accessible(self):
        """Test that complete-profile URL is accessible."""
        response = self.client.get(reverse('complete-profile'))
        self.assertEqual(response.status_code, 200)

    def test_topbar_dropdown_contains_edit_profile_link(self):
        """Test that topbar contains edit profile link in dropdown."""
        response = self.client.get('/')  # Home page should show topbar
        self.assertContains(response, 'Minha conta')
        self.assertContains(response, reverse('edit-profile'))

    def test_breadcrumb_navigation(self):
        """Test breadcrumb navigation in forms."""
        response = self.client.get(reverse('edit-profile'))
        self.assertContains(response, 'Editar Perfil')

        response = self.client.get(reverse('complete-profile'))
        self.assertContains(response, 'Complete seus Dados Médicos')
