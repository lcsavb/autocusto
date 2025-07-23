"""
Debug integration test to understand the redirect issue.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from usuarios.models import Usuario
from medicos.models import Medico
from medicos.seletor import medico as seletor_medico
from processos.models import Doenca


class DebugIntegrationTest(TestCase):
    """Debug the integration test issue."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            email='debug@example.com',
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Debug Doctor',
            crm_medico='',
            cns_medico=''
        )
        self.user.medicos.add(self.medico)
        self.client.login(username='debug@example.com', password='testpass123')
        
        # Create test disease for process creation
        self.doenca = Doenca.objects.create(
            cid='G35',
            nome='Debug Disease'
        )

    def test_debug_medico_relationship(self):
        """Debug the medico relationship and redirect logic."""
        print("\n=== DEBUG INFO ===")
        print(f"User: {self.user}")
        print(f"User.is_medico: {self.user.is_medico}")
        print(f"User.medicos.count(): {self.user.medicos.count()}")
        print(f"User.medicos.first(): {self.user.medicos.first()}")
        
        medico_from_selector = seletor_medico(self.user)
        print(f"seletor_medico(user): {medico_from_selector}")
        
        if medico_from_selector:
            print(f"Medico.crm_medico: '{medico_from_selector.crm_medico}'")
            print(f"Medico.cns_medico: '{medico_from_selector.cns_medico}'")
            print(f"bool(medico.crm_medico): {bool(medico_from_selector.crm_medico)}")
            print(f"bool(medico.cns_medico): {bool(medico_from_selector.cns_medico)}")
            
        # Set session data for process creation
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'G35'
        session['paciente_id'] = '123'
        session.save()
        
        print(f"Session data: {dict(session)}")

        response = self.client.get(reverse('processos-cadastro'))
        print(f"Response status: {response.status_code}")
        if response.status_code == 302:
            print(f"Redirect URL: {response.url}")
        
        # Check messages
        messages = list(get_messages(response.wsgi_request))
        for msg in messages:
            print(f"Message: {msg}")
        
        print("=== END DEBUG ===\n")
        
        # The actual assertion
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete-profile'))