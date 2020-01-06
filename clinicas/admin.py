from django.contrib import admin
from .models import Clinica, Emissor, ClinicaUsuario

admin.site.register(Clinica)
admin.site.register(Emissor)
admin.site.register(ClinicaUsuario)