# Generated by Django 3.0 on 2020-01-06 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0002_processo_usuario'),
    ]

    operations = [
        migrations.RenameField(
            model_name='processo',
            old_name='tratamento_previo',
            new_name='tratamentos_previos',
        ),
    ]
