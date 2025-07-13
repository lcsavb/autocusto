from django.contrib import admin
from .models import Processo, Protocolo, Medicamento, Doenca

admin.site.register(Processo)
admin.site.register(Protocolo)
admin.site.register(Medicamento)
admin.site.register(Doenca)
