
"autocusto URL Configuration\n\nThe `urlpatterns` list routes URLs to views. For more information please see:\n    https://docs.djangoproject.com/en/2.2/topics/http/urls/\nExamples:\nFunction views\n    1. Add an import:  from my_app import views\n    2. Add a URL to urlpatterns:  path('', views.home, name='home')\nClass-based views\n    1. Add an import:  from other_app.views import Home\n    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')\nIncluding another URLconf\n    1. Import the include() function: from django.urls import include, path\n    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))\n"
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [path('', views.home, name='home'), path('admin/', admin.site.urls), path('medicos/', include('medicos.urls')), path('pacientes/', include('pacientes.urls')), path('processos/', include('processos.urls')), path('clinicas/', include('clinicas.urls'))]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
