from django.db import models
from medicos.models import Medico
from django.conf import settings

class Clinica(models.Model):
    nome_clinica = models.CharField(max_length=200)
    cns_clinica = models.CharField(max_length=6,unique=True)
    end_clinica = models.CharField(max_length=200)
    cidade = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=9)
    telefone_clinica = models.CharField(max_length=13)
    medicos = models.ManyToManyField(Medico, through='ClinicaMedico', related_name='clinicas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

    def __str__(self):
        return f'{self.nome_clinica}'

class ClinicaMedico(models.Model):
    ativa = models.BooleanField(default=False)