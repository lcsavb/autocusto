# Generated by Django 3.0 on 2020-02-28 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Medico",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome_medico", models.CharField(max_length=200)),
                ("crm_medico", models.CharField(max_length=10, unique=True)),
                ("cns_medico", models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="MedicoUsuario",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "medico",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="medicos.Medico",
                    ),
                ),
            ],
        ),
    ]
