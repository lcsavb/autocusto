from django.urls import path
from .views import cadastro, busca_processos, renovacao_rapida, edicao, pdf, serve_pdf
from .ajax import busca_doencas, verificar_1_vez

urlpatterns = [
    path("cadastro/", cadastro, name="processos-cadastro"),
    path("busca/", busca_processos, name="processos-busca"),
    path("renovacao/", renovacao_rapida, name="processos-renovacao-rapida"),
    path("edicao/", edicao, name="processos-edicao"),
    path("pdf/", pdf, name="processos-pdf"),
    path("serve-pdf/<str:filename>/", serve_pdf, name="processos-serve-pdf"),
    path("ajax/doencas/", busca_doencas, name="busca-doencas"),
    path("ajax/verificar_1_vez/", verificar_1_vez, name="verificar_1_vez"),
]
