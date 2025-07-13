from django.urls import path
from . import views
from .views import ListarPacientes
from .ajax import busca_pacientes

urlpatterns = [
    path("cadastro/", views.cadastro, name="pacientes-cadastro"),
    path("listar/", ListarPacientes.as_view(), name="pacientes-listar"),
    path("ajax/busca", busca_pacientes, name="busca-pacientes"),
]
