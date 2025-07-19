from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


# CustomUserManager
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    
    Security: Implements secure user creation with proper email normalization
    and password hashing using Django's built-in security mechanisms.
    """

    # create_user
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.

        Security: Uses Django's normalize_email and set_password methods
        to ensure proper email formatting and secure password hashing.

        Critique:
        - The error message for missing email is a simple string. Consider using
          Django's built-in validation mechanisms or custom exceptions for more
          consistent error handling.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        # email (normalized email address)
        email = self.normalize_email(email)
        # user (new user instance)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    # create_superuser
    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.

        Security: Ensures superuser accounts have proper staff and superuser flags
        set, preventing privilege escalation issues during user creation.

        Critique:
        - The error messages for `is_staff` and `is_superuser` are simple strings.
          Similar to `create_user`, consider using more robust error handling.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
