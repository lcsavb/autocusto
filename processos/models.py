from django.db import models
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica
from django.conf import settings

class Processo(models.Model):
    anamnese = models.TextField(max_length=600)
    cid = models.CharField(max_length=6)
    diagnostico = models.CharField(max_length=100)
    med1 = models.CharField(max_length=100)
    posologia_med1=models.CharField(max_length=300)
    med2 = models.CharField(max_length=100)
    med3 = models.CharField(max_length=100)
    med4 = models.CharField(max_length=100)
    med5 = models.CharField(max_length=100)
    qtd_med1_mes1 = models.CharField(max_length=3)
    qtd_med1_mes2 = models.CharField(max_length=3)
    qtd_med1_mes3 = models.CharField(max_length=3)
    qtd_med2_mes1 = models.CharField(max_length=3)
    qtd_med2_mes2 = models.CharField(max_length=3)
    qtd_med2_mes3 = models.CharField(max_length=3)
    qtd_med3_mes1 = models.CharField(max_length=3)
    qtd_med3_mes2 = models.CharField(max_length=3)
    qtd_med3_mes3 = models.CharField(max_length=3)
    qtd_med4_mes1 = models.CharField(max_length=3)
    qtd_med4_mes2 = models.CharField(max_length=3)
    qtd_med4_mes3 = models.CharField(max_length=3)
    qtd_med5_mes1 = models.CharField(max_length=3)
    qtd_med5_mes2 = models.CharField(max_length=3)
    qtd_med5_mes3 = models.CharField(max_length=3)
    tratou = models.BooleanField(default=False)
    tratamento_previo = models.TextField(max_length=600)
    data1 = models.DateField(null=True)  
    data2 = models.DateField(null=True)
    data3 = models.DateField(null=True)
    preenchido_por = models.CharField(choices=(('P', 'Paciente'), ('M', 'Mãe'),
    ('R', 'Responsável'),('M', 'Médico')),
     max_length=128)
    paciente = models.ForeignKey(Paciente, 
                on_delete=models.CASCADE, related_name='processos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    #clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)     

    def __str__(self):
        return f'{self.cid}'   