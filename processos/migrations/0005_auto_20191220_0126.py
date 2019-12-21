# Generated by Django 3.0 on 2019-12-20 01:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinicas', '0005_emissor_pacientes'),
        ('medicos', '0002_medico_usuario'),
        ('processos', '0004_auto_20191220_0123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='clinica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='clinicas.Clinica'),
        ),
        migrations.AlterField(
            model_name='processo',
            name='emissor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='clinicas.Emissor'),
        ),
        migrations.AlterField(
            model_name='processo',
            name='medico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='medicos.Medico'),
        ),
    ]