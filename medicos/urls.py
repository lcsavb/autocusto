from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
        auth_views.LogoutView.as_view(template_name="medicos/logout.html"),
        name="logout",
    ),
]
