from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from medicos.models import Medico
from pacientes.models import Paciente
from clinicas.models import Clinica
from clinicas.models import Emissor


class Medicamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    apresentacoes = ArrayField(ArrayField(models.CharField(max_length=10)))


class Protocolo(models.Model):
    medicamentos = models.ManyToManyField(Medicamento)
    

class Doenca(models.Model):
    cid = models.CharField(max_length=6, unique=True)
    diagnostico = models.CharField(max_length=100)
    protocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE)


class Prescricao(models.Model):
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)


    
class Processo(models.Model):
    anamnese = models.TextField(max_length=600)
    diagnostico = models.CharField(max_length=200)
    medicamentos = models.ManyToManyField(Medicamento, 
    through=Prescricao, related_name='processos')
    tratou = models.BooleanField(default=False)
    tratamentos_previos = models.TextField(max_length=600)
    data1 = models.DateField(null=True)  
    preenchido_por = models.CharField(choices=(('P', 'Paciente'), ('M', 'Mãe'),
    ('R', 'Responsável'),('M', 'Médico')),
     max_length=128)
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='processos'
        )
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name='processos'
        )
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='processos'
        )
    emissor = models.ForeignKey(
        Emissor,
        on_delete=models.CASCADE,
        related_name='processos'
        )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='processos'
        )


    def __str__(self):
        return f'{self.cid, self.med1.nome}'




       