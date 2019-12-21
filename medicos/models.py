from django.db import models
from django.conf import settings
from usuarios.models import Usuario
from pacientes.models import Paciente

class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_medico = models.CharField(max_length=200)
    crm_medico = models.CharField(max_length=10, unique=True)
    cns_medico = models.CharField(max_length=15, unique=True)
    #usuarios = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MedicoUsuario')

    
    def __str__(self):
        return self.crm_medico

# Aqui já tem uma relação one to one, pensar depois
# class MedicoUsuario(models.Model):
#     #DUVIDA - AQUI DEVE SER SET NULL?
#     usuario = models.ForeignKey(settings.AUTH_USER_MODEL, 
#                                 on_delete=models.SET_NULL, null=True
#                                 )
#     medico = models.ForeignKey(Medico, 
#                                 on_delete=models.SET_NULL, null=True
#                                 )
    
#     def __str__(self):
#         return f'Médico: {self.medico} e Usuário {self.usuario}'

        