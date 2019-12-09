from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Medico

@receiver(post_save, sender=User)
def criar_medico(sender, instance, created, **kwargs):
    if created:
        Medico.objects.create(medico=instance)

@receiver(post_save, sender=User)
def salvar_medico(sender, instance, created, **kwargs):
    instance.medico.save()