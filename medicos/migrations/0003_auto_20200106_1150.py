# Generated by Django 3.0 on 2020-01-06 11:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medicos', '0002_medico_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medico',
            name='usuario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='medico', to=settings.AUTH_USER_MODEL),
        ),
    ]
