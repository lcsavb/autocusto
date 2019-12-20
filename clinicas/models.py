from django.db import models
from medicos.models import Medico
from pacientes.models import Paciente
from django.conf import settings

class Clinica(models.Model):
    nome_clinica = models.CharField(max_length=200)
    cns_clinica = models.CharField(unique=True, max_length=6)
    end_clinica = models.CharField(max_length=200)
    cidade = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=9)
    telefone_clinica = models.CharField(max_length=13)
    medicos = models.ManyToManyField(Medico, through='Emissor', related_name='clinicas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    

    def __str__(self):
        return f'{self.nome_clinica}'

class Emissor(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    pacientes = models.ManyToManyField(Paciente, through='processos.Processo',
    through_fields=('emissor','paciente'), related_name='emissores')

    def __str__(self):
        return f'Emitido pela clínica: {self.clinica} e pelo médico com CRM: {self.medico}'