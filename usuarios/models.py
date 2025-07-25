from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


# User
class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the medical prescription application.

    This model extends Django's `AbstractBaseUser` and `PermissionsMixin`
    to provide a custom user authentication system. It uses email as the
    primary authentication field and includes additional flags to identify
    user roles (e.g., doctor, clinic).

    Security: Email-based authentication provides better user experience
    and reduces username enumeration attacks compared to username-based systems.

    Critique:
    - The `is_medico` and `is_clinica` fields are boolean flags. While functional,
      for more complex role management, a dedicated `Role` model with a ManyToMany
      relationship to `Usuario` might be more scalable and flexible. However,
      for simple doctor/clinic distinctions, this approach is acceptable.
    - The `USERNAME_FIELD` is set to `email`, which is a good practice for modern
      applications.
    - It uses a `CustomUserManager`, which is necessary for custom user models.
    """
    # email
    email = models.EmailField(_("email address"), unique=True)
    # is_staff
    is_staff = models.BooleanField(default=False)
    # is_active
    is_active = models.BooleanField(default=True)
    # date_joined
    date_joined = models.DateTimeField(default=timezone.now)

    # is_doctor (Doctor Status)
    is_medico = models.BooleanField("Status de Médico", default=False)
    # is_clinic (Clinic Status)
    is_clinica = models.BooleanField("Status de Clínica", default=False)
    # process_count (Number of processes created by this user)
    process_count = models.PositiveIntegerField("Número de Processos Criados", default=0)

    USERNAME_FIELD = "email"

    # objects (custom user manager)
    objects = CustomUserManager()

    def __str__(self):
        return self.email
