from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomMinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("A senha deve ter pelo menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Sua senha deve ter pelo menos %(min_length)d caracteres."
            % {'min_length': self.min_length}
        )

def isCpfValid(cpf):
    """ Add your CPF validation logic here. """
    return True
