
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('clinicas', '0002_emissor_medico'), ('pacientes', '0001_initial'), ('processos', '0001_initial')]
    operations = [migrations.AddField(model_name='emissor', name='pacientes', field=models.ManyToManyField(related_name='emissores', through='processos.Processo', to='pacientes.Paciente')), migrations.AddField(model_name='clinicausuario', name='clinica', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clinicas.Clinica'))]
