from django.test import TestCase
from processos.models import Protocolo, Doenca
from processos.forms import PreProcesso
import random
from cpf_generator import CPF


class TestDataFactory:
    """Factory for generating valid, isolated test data with proper CPF validation."""
    
    @staticmethod
    def valid_cpfs():
        """List of valid CPFs for testing - properly calculated checksums."""
        return [
            '11144477735',  # Valid CPF
            '22255588846',  # Valid CPF  
            '33366699957',  # Valid CPF
            '44477711168',  # Valid CPF
            '55588822279',  # Valid CPF
            '66699933380',  # Valid CPF
            '77700044491',  # Valid CPF
            '88811155502',  # Valid CPF
            '99922266613',  # Valid CPF
            '12345678909',  # Valid CPF (commonly used in testing)
        ]
    
    @staticmethod
    def get_unique_cpf():
        """Get a unique valid CPF for testing using cpf-generator."""
        return CPF.generate()
    
    @staticmethod
    def get_unique_cns():
        """Get a unique CNS for testing."""
        return f"{random.randint(1000000, 9999999)}"
    
    @staticmethod
    def get_unique_email(prefix="test"):
        """Get a unique email for testing."""
        return f"{prefix}{random.randint(10000, 99999)}@example.com"


class PreProcessoFormTest(TestCase):
    def setUp(self):
        # Create a dummy Doenca for testing clean_cid
        self.protocolo = Protocolo.objects.create(nome="Protocolo Teste", arquivo="teste.pdf")
        self.doenca = Doenca.objects.create(cid="A00.0", nome="Doenca Teste", protocolo=self.protocolo)

    def test_valid_data(self):
        form = PreProcesso(data={'cpf_paciente': '93448378054', 'cid': 'A00.0'})
        self.assertTrue(form.is_valid())

    def test_invalid_cid(self):
        form = PreProcesso(data={'cpf_paciente': '93448378054', 'cid': 'Z99.9'})
        self.assertFalse(form.is_valid())
        self.assertIn('cid', form.errors)
        self.assertEqual(form.errors['cid'], ['CID "Z99.9" incorreto!'])

    def test_invalid_cpf(self):
        form = PreProcesso(data={'cpf_paciente': '123.456.789-0', 'cid': 'A00.0'}) # Invalid CPF format
        self.assertFalse(form.is_valid())
        self.assertIn('cpf_paciente', form.errors)
        self.assertEqual(form.errors['cpf_paciente'], ['CPF 123.456.789-0 inválido!'])

    def test_empty_fields(self):
        form = PreProcesso(data={'cpf_paciente': '', 'cid': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('cpf_paciente', form.errors)
        self.assertIn('cid', form.errors)
        self.assertEqual(form.errors['cpf_paciente'], ['Por favor, insira o CPF do paciente.'])
        self.assertEqual(form.errors['cid'], ['Por favor, insira o CID da doença.'])