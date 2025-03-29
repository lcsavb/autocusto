# Generated by Django 5.2rc1 on 2025-03-29 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicas', '0004_auto_20200228_1704'),
        ('pacientes', '0003_alter_paciente_id'),
        ('processos', '0003_alter_doenca_id_alter_medicamento_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinica',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='clinicausuario',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='emissor',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='emissor',
            name='pacientes',
            field=models.ManyToManyField(related_name='emissores', through='processos.Processo', through_fields=('emissor', 'paciente'), to='pacientes.paciente'),
        ),
    ]
