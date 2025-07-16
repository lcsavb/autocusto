from django.contrib import admin
# English: Clinic
from .models import Clinica
# English: Issuer
from .models import Emissor
# English: ClinicUser
from .models import ClinicaUsuario

admin.site.register(Clinica)
admin.site.register(Emissor)
admin.site.register(ClinicaUsuario)
