from django.test import TestCase
from .models import Paciente

class PacienteModelTest(TestCase):

    def test_create_paciente(self):
        paciente = Paciente.objects.create(
            nome_paciente="João da Silva",
            cpf_paciente="12345678901",
            cns_paciente="987654321098765",
            nome_mae="Maria da Silva",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11999999999",
            end_paciente="Rua Exemplo, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        self.assertEqual(paciente.nome_paciente, "João da Silva")