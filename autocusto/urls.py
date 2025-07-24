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
from django.contrib.auth import views as auth_views
from usuarios.forms import CustomPasswordResetForm, CustomSetPasswordForm

# English: url_patterns
urlpatterns = [
    path("", views.home, name="home"),
    path("privacidade/", views.privacy, name="privacy"),
    path("beneficios/", views.beneficios, name="beneficios"),
    path("beneficios/de/", views.beneficios_de, name="beneficios-de"),
    path("beneficios/en/", views.beneficios_en, name="beneficios-en"),
    path("admin/", admin.site.urls),
    path("medicos/", include("medicos.urls")),
    path("pacientes/", include("pacientes.urls")),
    path("processos/", include("processos.urls")),
    path("clinicas/", include("clinicas.urls")),
    path("analytics/", include("analytics.urls")),
    path("reportar-erros/", views.reportar_erros, name="reportar-erros"),
    path("solicitar-funcionalidade/", views.solicitar_funcionalidade, name="solicitar-funcionalidade"),
    path("process-feedback-ajax/", views.process_feedback_ajax, name="process-feedback-ajax"),
    
    # Password reset URLs using Django's built-in views
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html",
        email_template_name="registration/password_reset_email.txt",
        html_email_template_name="registration/password_reset_email.html",
        subject_template_name="registration/password_reset_subject.txt",
        success_url="/password_reset/done/",
        form_class=CustomPasswordResetForm
    ), name="password_reset"),
    
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"
    ), name="password_reset_done"),
    
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html",
        success_url="/reset/done/",
        form_class=CustomSetPasswordForm
    ), name="password_reset_confirm"),
    
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
