from django.db import models
from usuarios.models import Usuario

class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_medico = models.CharField(max_length=200)
    crm_medico = models.CharField(max_length=10, unique=True)
    cns_medico = models.CharField(max_length=15, unique=True)
    clinica_ativa_cns = models.CharField(max_length=6)
    clinica_ativa_nome = models.CharField(max_length=200)
    clinica_ativa_end = models.CharField(max_length=200)
    clinica_ativa_cidade = models.CharField(max_length=30)
    clinica_ativa_bairro = models.CharField(max_length=30)
    clinica_ativa_cep = models.CharField(max_length=9)
    clinica_ativa_telefone = models.CharField(max_length=13)
    
    def __str__(self):
        return self.crm_medico

        