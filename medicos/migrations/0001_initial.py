# Generated by Django 3.0 on 2019-12-17 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Medico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_medico', models.CharField(max_length=200)),
                ('crm_medico', models.CharField(max_length=10, unique=True)),
                ('cns_medico', models.CharField(max_length=15, unique=True)),
                ('clinica_ativa_cns', models.CharField(max_length=6)),
                ('clinica_ativa_nome', models.CharField(max_length=200)),
                ('clinica_ativa_end', models.CharField(max_length=200)),
                ('clinica_ativa_cidade', models.CharField(max_length=30)),
                ('clinica_ativa_bairro', models.CharField(max_length=30)),
                ('clinica_ativa_cep', models.CharField(max_length=9)),
                ('clinica_ativa_telefone', models.CharField(max_length=13)),
            ],
        ),
    ]
