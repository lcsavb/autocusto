
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('clinicas', '0003_auto_20200228_1704'), ('medicos', '0001_initial')]
    operations = [migrations.AddField(model_name='clinicausuario', name='usuario', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)), migrations.AddField(model_name='clinica', name='medicos', field=models.ManyToManyField(related_name='clinicas', through='clinicas.Emissor', to='medicos.Medico')), migrations.AddField(model_name='clinica', name='usuarios', field=models.ManyToManyField(related_name='clinicas', through='clinicas.ClinicaUsuario', to=settings.AUTH_USER_MODEL))]
