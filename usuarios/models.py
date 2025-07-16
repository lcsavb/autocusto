from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Custom User model for the application.

    This model extends Django's `AbstractBaseUser` and `PermissionsMixin`
    to provide a custom user authentication system. It uses email as the
    primary authentication field and includes additional flags to identify
    user roles (e.g., doctor, clinic).

    Critique:
    - The `is_medico` and `is_clinica` fields are boolean flags. While functional,
      for more complex role management, a dedicated `Role` model with a ManyToMany
      relationship to `Usuario` might be more scalable and flexible. However,
      for simple doctor/clinic distinctions, this approach is acceptable.
    - The `USERNAME_FIELD` is set to `email`, which is a good practice for modern
      applications.
    - It uses a `CustomUserManager`, which is necessary for custom user models.
    """
    # English: email
    email = models.EmailField(_("email address"), unique=True)
    # English: is_staff
    is_staff = models.BooleanField(default=False)
    # English: is_active
    is_active = models.BooleanField(default=True)
    # English: date_joined
    date_joined = models.DateTimeField(default=timezone.now)

    # English: is_doctor
    is_medico = models.BooleanField("Status de Médico", default=False)
    # English: is_clinic
    is_clinica = models.BooleanField("Status de Clínica", default=False)

    USERNAME_FIELD = "email"

    # English: objects
    objects = CustomUserManager()

    def __str__(self):
        return self.email
