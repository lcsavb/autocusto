# Generated by Django 3.0 on 2020-02-25 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clinicas', '0001_initial'),
        ('medicos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emissor',
            name='medico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicos.Medico'),
        ),
    ]
