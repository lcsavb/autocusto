# Generated by Django 3.0 on 2020-02-06 15:15

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0005_auto_20200206_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protocolo',
            name='dados_condicionais',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]