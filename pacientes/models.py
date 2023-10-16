
from django.db import models
from django.conf import settings

class Paciente(models.Model):
    patient_name = models.CharField(max_length=100)
    age = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    incapable = models.BooleanField()
    responsible_name = models.CharField(max_length=100)
    rg = models.CharField(max_length=100)
    weight = models.CharField(max_length=100)
    height = models.CharField(max_length=100, default='1,70m')
    ethnicity_choice = models.CharField(max_length=100)
    patient_cpf = models.CharField(unique=True, max_length=14)
    patient_cns = models.CharField(max_length=100)
    patient_email = models.EmailField(null=True)
    patient_city = models.CharField(max_length=100)
    patient_address = models.CharField(max_length=100)
    patient_zip_code = models.CharField(max_length=100)
    patient_phone1 = models.CharField(max_length=100)
    patient_phone2 = models.CharField(max_length=100)
    ethnicity = models.CharField(max_length=100)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='pacientes')

    def __str__(self):
        return f'{self.patient.name}'
