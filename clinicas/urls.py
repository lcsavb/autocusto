from django.urls import path
from . import views

urlpatterns = [
    path("cadastro/", views.cadastro, name="clinicas-cadastro"),
    path("list/", views.list_clinics, name="clinicas-list"),
    path("get/<int:clinic_id>/", views.get_clinic, name="clinicas-get"),
]
