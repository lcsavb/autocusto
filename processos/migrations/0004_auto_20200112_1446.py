# Generated by Django 3.0 on 2020-01-12 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0003_auto_20200106_1305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processo',
            name='posologia_med5',
        ),
        migrations.AddField(
            model_name='processo',
            name='med1_repetir_posologia',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='processo',
            name='med2_repetir_posologia',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='processo',
            name='med3_repetir_posologia',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='processo',
            name='med4_repetir_posologia',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='processo',
            name='med5_repetir_posologia',
            field=models.BooleanField(default=True),
        ),
    ]
