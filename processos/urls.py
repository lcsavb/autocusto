from django.urls import path
from .views import cadastro, BuscaProcessos, renovacao_rapida, edicao
from django.conf import settings

urlpatterns = [
    path('cadastro/', cadastro, name='processos-cadastro'),
    path('busca/', BuscaProcessos.as_view(), name='processos-busca'),
    path('renovacao/', renovacao_rapida, name='processos-renovacao-rapida'),
    path('edicao/', edicao, name='processos-edicao')
] 