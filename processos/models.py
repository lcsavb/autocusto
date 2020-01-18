from django.db import models
from django.conf import settings
from medicos.models import Medico
from pacientes.models import Paciente
from clinicas.models import Clinica
from clinicas.models import Emissor
from django.conf import settings

class Processo(models.Model):
    anamnese = models.TextField(max_length=600)
    cid = models.CharField(max_length=6)
    diagnostico = models.CharField(max_length=100)
    med1 = models.CharField(max_length=100)
    med1_via = models.CharField(max_length=100)
    med1_posologia_mes1=models.CharField(max_length=300)
    med1_posologia_mes2=models.CharField(max_length=300)
    med1_posologia_mes3=models.CharField(max_length=300)
    med2 = models.CharField(max_length=100)
    med2_posologia_mes1=models.CharField(max_length=300)
    med2_posologia_mes2=models.CharField(max_length=300)
    med2_posologia_mes3=models.CharField(max_length=300)
    med3 = models.CharField(max_length=100)
    med3_posologia_mes1=models.CharField(max_length=300)
    med3_posologia_mes2=models.CharField(max_length=300)
    med3_posologia_mes3=models.CharField(max_length=300)
    med4 = models.CharField(max_length=100)
    med4_posologia_mes1=models.CharField(max_length=300)
    med4_posologia_mes2=models.CharField(max_length=300)
    med4_posologia_mes3=models.CharField(max_length=300)
    med5 = models.CharField(max_length=100)
    med5_posologia_mes1=models.CharField(max_length=300)
    med5_posologia_mes2=models.CharField(max_length=300)
    med5_posologia_mes3=models.CharField(max_length=300)
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
    med1_repetir_posologia = models.BooleanField(default=True)
    med2_repetir_posologia = models.BooleanField(default=True)
    med3_repetir_posologia = models.BooleanField(default=True)
    med4_repetir_posologia = models.BooleanField(default=True)
    med5_repetir_posologia = models.BooleanField(default=True)
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
        return f'{self.paciente.nome_paciente, self.paciente.id, self.cid, self.id}'   