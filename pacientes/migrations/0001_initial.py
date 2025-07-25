# Generated by Django 3.0 on 2020-02-28 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Paciente",
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
                ("nome_paciente", models.CharField(max_length=100)),
                ("idade", models.CharField(max_length=100)),
                ("sexo", models.CharField(max_length=100)),
                ("nome_mae", models.CharField(max_length=100)),
                ("incapaz", models.BooleanField()),
                ("nome_responsavel", models.CharField(max_length=100)),
                ("rg", models.CharField(max_length=100)),
                ("peso", models.CharField(max_length=100)),
                ("altura", models.CharField(default="1,70m", max_length=100)),
                ("escolha_etnia", models.CharField(max_length=100)),
                ("cpf_paciente", models.CharField(max_length=14, unique=True)),
                ("cns_paciente", models.CharField(max_length=100)),
                ("email_paciente", models.EmailField(max_length=254, null=True)),
                ("cidade_paciente", models.CharField(max_length=100)),
                ("end_paciente", models.CharField(max_length=100)),
                ("cep_paciente", models.CharField(max_length=100)),
                ("telefone1_paciente", models.CharField(max_length=100)),
                ("telefone2_paciente", models.CharField(max_length=100)),
                ("etnia", models.CharField(max_length=100)),
            ],
        ),
    ]
