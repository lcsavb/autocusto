# Generated by Django 3.0 on 2020-02-28 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clinica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_clinica', models.CharField(max_length=200)),
                ('cns_clinica', models.CharField(max_length=7)),
                ('logradouro', models.CharField(max_length=200)),
                ('logradouro_num', models.CharField(max_length=6)),
                ('cidade', models.CharField(max_length=30)),
                ('bairro', models.CharField(max_length=30)),
                ('cep', models.CharField(max_length=9)),
                ('telefone_clinica', models.CharField(max_length=13)),
            ],
        ),
        migrations.CreateModel(
            name='ClinicaUsuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Emissor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinicas.Clinica')),
            ],
        ),
    ]
