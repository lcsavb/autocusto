# Generated by Django 3.0 on 2020-02-28 17:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("medicos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicousuario",
            name="usuario",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="medico",
            name="usuarios",
            field=models.ManyToManyField(
                related_name="medicos",
                through="medicos.MedicoUsuario",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
