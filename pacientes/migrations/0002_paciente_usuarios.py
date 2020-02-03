# Generated by Django 3.0 on 2020-02-03 04:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pacientes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='usuarios',
            field=models.ManyToManyField(related_name='pacientes', to=settings.AUTH_USER_MODEL),
        ),
    ]
