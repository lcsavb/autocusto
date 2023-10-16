
from django.urls import path
from .views import cadastro, busca_processos, renovacao_rapida, edicao, pdf
from .ajax import busca_doencas, verificar_1_vez
from django.conf import settings
urlpatterns = [path('cadastro/', cadastro, name='processos-cadastro'), path('busca/', search_processes, name='processos-busca'), path('renovacao/', renovacao_rapida, name='processos-renovacao-rapida'), path('edicao/', edicao, name='processos-edicao'), path('pdf/', pdf, name='processos-pdf'), path('ajax/doencas/', busca_doencas, name='busca-doencas'), path('ajax/verificar_1_vez/', verificar_1_vez, name='verificar_1_vez')]
