from tests.test_base import BaseTestCase
from pacientes.models import Paciente

class PacienteModelTest(BaseTestCase):

    def test_create_paciente(self):
        paciente = self.create_test_patient(
            nome_paciente="João da Silva",
            nome_mae="Maria da Silva",
            idade="30",
            sexo="M",
            peso="70.5",
            altura="1.75",
            etnia="Branca",
            end_paciente="Rua Exemplo, 123",
            rg="123456789",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="11888888888",
            nome_responsavel="",
        )
        self.assertEqual(paciente.nome_paciente, "João da Silva")