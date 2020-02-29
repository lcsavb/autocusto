from django.urls import path
from .views import cadastro, busca_processos, renovacao_rapida, edicao
from .ajax import busca_doencas,verificar_1_vez
from django.conf import settings

urlpatterns = [
    path('cadastro/', cadastro, name='processos-cadastro'),
    path('busca/', busca_processos, name='processos-busca'),
    path('renovacao/', renovacao_rapida, name='processos-renovacao-rapida'),
    path('edicao/', edicao, name='processos-edicao'),
    path('ajax/doencas/', busca_doencas, name='busca-doencas'),
    path('ajax/verificar_1_vez/', verificar_1_vez, name='verificar_1_vez')
] 