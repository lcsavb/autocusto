# Generated by Django 3.0 on 2020-01-06 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clinicas', '0002_emissor_medico'),
        ('medicos', '0001_initial'),
        ('pacientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anamnese', models.TextField(max_length=600)),
                ('cid', models.CharField(max_length=6)),
                ('diagnostico', models.CharField(max_length=100)),
                ('med1', models.CharField(max_length=100)),
                ('med1_posologia_mes1', models.CharField(max_length=300)),
                ('med1_posologia_mes2', models.CharField(max_length=300)),
                ('med1_posologia_mes3', models.CharField(max_length=300)),
                ('med2', models.CharField(max_length=100)),
                ('med2_posologia_mes1', models.CharField(max_length=300)),
                ('med2_posologia_mes2', models.CharField(max_length=300)),
                ('med2_posologia_mes3', models.CharField(max_length=300)),
                ('med3', models.CharField(max_length=100)),
                ('med3_posologia_mes1', models.CharField(max_length=300)),
                ('med3_posologia_mes2', models.CharField(max_length=300)),
                ('med3_posologia_mes3', models.CharField(max_length=300)),
                ('med4', models.CharField(max_length=100)),
                ('med4_posologia_mes1', models.CharField(max_length=300)),
                ('med4_posologia_mes2', models.CharField(max_length=300)),
                ('med4_posologia_mes3', models.CharField(max_length=300)),
                ('med5', models.CharField(max_length=100)),
                ('med5_posologia_mes1', models.CharField(max_length=300)),
                ('med5_posologia_mes2', models.CharField(max_length=300)),
                ('med5_posologia_mes3', models.CharField(max_length=300)),
                ('posologia_med5', models.CharField(max_length=300)),
                ('qtd_med1_mes1', models.CharField(max_length=3)),
                ('qtd_med1_mes2', models.CharField(max_length=3)),
                ('qtd_med1_mes3', models.CharField(max_length=3)),
                ('qtd_med2_mes1', models.CharField(max_length=3)),
                ('qtd_med2_mes2', models.CharField(max_length=3)),
                ('qtd_med2_mes3', models.CharField(max_length=3)),
                ('qtd_med3_mes1', models.CharField(max_length=3)),
                ('qtd_med3_mes2', models.CharField(max_length=3)),
                ('qtd_med3_mes3', models.CharField(max_length=3)),
                ('qtd_med4_mes1', models.CharField(max_length=3)),
                ('qtd_med4_mes2', models.CharField(max_length=3)),
                ('qtd_med4_mes3', models.CharField(max_length=3)),
                ('qtd_med5_mes1', models.CharField(max_length=3)),
                ('qtd_med5_mes2', models.CharField(max_length=3)),
                ('qtd_med5_mes3', models.CharField(max_length=3)),
                ('tratou', models.BooleanField(default=False)),
                ('tratamento_previo', models.TextField(max_length=600)),
                ('data1', models.DateField(null=True)),
                ('preenchido_por', models.CharField(choices=[('P', 'Paciente'), ('M', 'Mãe'), ('R', 'Responsável'), ('M', 'Médico')], max_length=128)),
                ('clinica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='clinicas.Clinica')),
                ('emissor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='clinicas.Emissor')),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='medicos.Medico')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='pacientes.Paciente')),
            ],
        ),
    ]
