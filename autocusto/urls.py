"""autocusto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

# English: url_patterns
urlpatterns = [
    path("", views.home, name="home"),
    path("privacidade/", views.privacy_policy, name="privacy-policy"),
    path("admin/", admin.site.urls),
    path("medicos/", include("medicos.urls")),
    path("pacientes/", include("pacientes.urls")),
    path("processos/", include("processos.urls")),
    path("clinicas/", include("clinicas.urls")),
    path("reportar-erros/", views.reportar_erros, name="reportar-erros"),
    path("solicitar-funcionalidade/", views.solicitar_funcionalidade, name="solicitar-funcionalidade"),
]

# Serve static files in development
# English: debug
if settings.DEBUG:
    # English: static_url
    # English: static_root
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
