# Generated by Django 3.0 on 2019-12-19 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0002_auto_20191219_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='cpf_paciente',
            field=models.CharField(max_length=14, unique=True),
        ),
    ]