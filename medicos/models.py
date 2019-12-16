from django.db import models
from usuarios.models import Usuario

class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    crm = models.CharField(max_length=10, unique=True)
    cns = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return self.crm

        