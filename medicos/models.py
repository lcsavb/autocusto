from django.db import models
from django.contrib.auth.models import User

class Medico(models.Model):
    medico = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200, default='Nome completo do médico')
    cns = models.CharField(max_length=17, default='CNS do médico')
    crm = models.CharField(max_length=10, default='CRM do médico')

    def __str__(self):
         return f'{self.medico.username}'
