from django.urls import path
from . import views
from .views import ListarPacientes

urlpatterns = [
    path('cadastro/', views.cadastro, name='pacientes-cadastro'),
    path('listar/', ListarPacientes.as_view(), name='pacientes-listar')
    ]