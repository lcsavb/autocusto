from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# English: url_patterns
urlpatterns = [
    path("cadastro/", views.cadastro, name="medicos-cadastro"),
    path("perfil/", views.perfil, name="medicos-perfil"),
    path(
        "login/",
        views.custom_login,
        name="login",
    ),
    path(
        "logout/",
        views.custom_logout,
        name="logout",
    ),
]
