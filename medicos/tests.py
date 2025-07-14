from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Medico
from .forms import MedicoCadastroFormulario

class MedicoModelTest(TestCase):

    def test_create_medico(self):
        medico = Medico.objects.create(
            nome_medico="Dr. Carlos Andrade",
            crm_medico="123456",
            cns_medico="123456789012345"
        )
        self.assertEqual(medico.nome_medico, "Dr. Carlos Andrade")


class MedicoCadastroFormularioTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_valid_form_submission(self):
        data = {
            'nome': 'Dr. Teste',
            'crm': '12345',
            'cns': '987654321012345',
            'email': 'teste@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = MedicoCadastroFormulario(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertIsNotNone(user)
        self.assertTrue(user.is_medico)
        self.assertEqual(user.email, 'teste@example.com')

        medico = Medico.objects.get(crm_medico='12345')
        self.assertIsNotNone(medico)
        self.assertEqual(medico.nome_medico, 'Dr. Teste')
        self.assertEqual(medico.cns_medico, '987654321012345')
        self.assertIn(medico, user.medicos.all())

    def test_invalid_form_missing_data(self):
        data = {
            'nome': '',
            'crm': '12345',
            'cns': '987654321012345',
            'email': 'teste@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = MedicoCadastroFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_invalid_form_mismatched_passwords(self):
        data = {
            'nome': 'Dr. Teste',
            'crm': '12345',
            'cns': '987654321012345',
            'email': 'teste@example.com',
            'password1': 'testpassword',
            'password2': 'wrongpassword',
        }
        form = MedicoCadastroFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_form_duplicate_crm(self):
        Medico.objects.create(nome_medico='Existing Doc', crm_medico='12345', cns_medico='111111111111111')
        data = {
            'nome': 'Dr. Teste',
            'crm': '12345',
            'cns': '987654321012345',
            'email': 'teste@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = MedicoCadastroFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('crm', form.errors)

    def test_invalid_form_duplicate_cns(self):
        Medico.objects.create(nome_medico='Existing Doc', crm_medico='54321', cns_medico='987654321012345')
        data = {
            'nome': 'Dr. Teste',
            'crm': '12345',
            'cns': '987654321012345',
            'email': 'teste@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = MedicoCadastroFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cns', form.errors)

    def test_invalid_form_duplicate_email(self):
        self.User.objects.create_user(email='existing@example.com', password='password123')
        data = {
            'nome': 'Dr. Teste',
            'crm': '12345',
            'cns': '987654321012345',
            'email': 'existing@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = MedicoCadastroFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
