from django.db import models
from usuarios.models import Usuario
from pacientes.models import Paciente

class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_medico = models.CharField(max_length=200)
    crm_medico = models.CharField(max_length=10, unique=True)
    cns_medico = models.CharField(max_length=15, unique=True)
    pacientes = models.ManyToManyField(Paciente, through='Processo',
    related_name='medicos', through_fields=('paciente', 'clinica')
    )

    
    def __str__(self):
        return self.crm_medico

        