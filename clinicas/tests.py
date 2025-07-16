# English: ClinicaModelTest
from django.test import TestCase
# English: Clinica
from .models import Clinica
# English: ClinicaForm
from .forms import ClinicaFormulario

class ClinicaModelTest(TestCase):

    def test_create_clinica(self):
        # Create a Clinica instance with sample data
        # English: clinic
        clinica = Clinica.objects.create(
            nome_clinica="Clínica Saúde e Bem-Estar",
            cns_clinica="1234567",
            logradouro="Rua das Flores",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="1122223333"
        )
        # Assert that the clinic's name matches the expected value after creation
        self.assertEqual(clinica.nome_clinica, "Clínica Saúde e Bem-Estar")


# English: ClinicaFormTest
class ClinicaFormularioTest(TestCase):

    def test_valid_form(self):
        # English: data
        data = {
            'nome_clinica': 'Clinica Teste',
            'cns_clinica': '1234567',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '11987654321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        # English: clinic
        clinica = form.save()
        self.assertEqual(clinica.nome_clinica, 'Clinica Teste')

    def test_invalid_form_missing_data(self):
        # English: data
        data = {
            'nome_clinica': '',
            'cns_clinica': '1234567',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '11987654321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome_clinica', form.errors)

    def test_invalid_form_cns_too_long(self):
        # English: data
        data = {
            'nome_clinica': 'Clinica Teste',
            'cns_clinica': '12345678',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '11987654321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cns_clinica', form.errors)

    def test_invalid_form_cns_too_short(self):
        # English: data
        data = {
            'nome_clinica': 'Clinica Teste',
            'cns_clinica': '123456',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '11987654321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cns_clinica', form.errors)
