from django.db import models
from django.conf import settings
from clinicas.models import Clinica

class Paciente(models.Model):
    
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=True)
    idade = models.CharField(max_length=100, null=True)
    sexo = models.CharField(max_length=100, null=True)
    nome_mae = models.CharField(max_length=100, null=True)
    incapaz = models.BooleanField(null=True)
    nome_responsavel = models.CharField(max_length=100, null=True)
    rg = models.CharField(max_length=100, null=True)
    peso = models.CharField(max_length=100, null=True)
    altura = models.CharField(max_length=100, default='1,70m')
    escolha_etnia = models.CharField(max_length=100, null=True)
    cpf_paciente = models.CharField(max_length=100, null=True)
    cns_paciente = models.CharField(max_length=100, null=True)
    email_paciente = models.EmailField(null=True)
    cidade_paciente = models.CharField(max_length=100, null=True)
    end_paciente = models.CharField(max_length=100, null=True)
    cep_paciente = models.CharField(max_length=100, null=True)
    telefone1_paciente = models.CharField(max_length=100, null=True)
    telefone2_paciente = models.CharField(max_length=100, null=True)
    medico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.nome}'

    

