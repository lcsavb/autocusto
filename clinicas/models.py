from django.db import models
from medicos.models import Medico

class Clinica(models.Model):
    nome = models.CharField(max_length=200)
    medicos = models.ManyToManyField(Medico, related_name='clinica')
    cns = models.CharField(max_length=30)
    end = models.CharField(max_length=200)
    cidade = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=30)
    telefone = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.nome}'