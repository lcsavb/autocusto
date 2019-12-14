from django.urls import path
from .views import cadastro, ResultadosBuscaPacientes
from django.conf import settings

urlpatterns = [
    path('cadastro/', cadastro, name='processos-cadastro'),
    path('busca/', ResultadosBuscaPacientes.as_view(), name='processos-busca')
] 