from django.db import models
from django.conf import settings
from clinicas.models import Clinica


class Paciente(models.Model):
    nome_paciente = models.CharField(max_length=100)
    idade = models.CharField(max_length=100)
    sexo = models.CharField(max_length=100)
    nome_mae = models.CharField(max_length=100)
    incapaz = models.BooleanField()
    nome_responsavel = models.CharField(max_length=100)
    rg = models.CharField(max_length=100)
    peso = models.CharField(max_length=100)
    altura = models.CharField(max_length=100, default='1,70m')
    escolha_etnia = models.CharField(max_length=100)
    cpf_paciente = models.CharField(max_length=14)
    cns_paciente = models.CharField(max_length=100)
    email_paciente = models.EmailField(null=True)
    cidade_paciente = models.CharField(max_length=100)
    end_paciente = models.CharField(max_length=100)
    cep_paciente = models.CharField(max_length=100)
    telefone1_paciente = models.CharField(max_length=100)
    telefone2_paciente = models.CharField(max_length=100)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome_paciente}'